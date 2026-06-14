import asyncio
import logging
from datetime import datetime
from typing import List

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.intelligence import NewsArticle

logger = logging.getLogger(__name__)

RSS_FEEDS = getattr(settings, "NEWS_RSS_FEEDS", "").split(",") if getattr(settings, "NEWS_RSS_FEEDS", None) else []


async def _fetch_feed(url: str) -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url.strip())
            resp.raise_for_status()
        parsed = feedparser.parse(resp.text)
        articles: List[dict] = []
        for entry in parsed.entries[:20]:
            title = getattr(entry, "title", "")
            link = getattr(entry, "link", "")
            published = getattr(entry, "published_parsed", None)
            published_at = datetime(*published[:6]) if published else datetime.utcnow()
            content = ""
            summary = getattr(entry, "summary", "")
            try:
                content = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)
            except Exception:
                content = summary
            articles.append({
                "title": title,
                "url": link,
                "source": parsed.feed.get("title", ""),
                "published_at": published_at,
                "content": content,
            })
        return articles
    except Exception as exc:
        logger.error("Failed to fetch feed %s: %s", url, exc)
        return []


async def fetch_latest_news() -> List[dict]:
    tasks = [_fetch_feed(url) for url in RSS_FEEDS]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    articles: List[dict] = []
    seen = set()
    for batch in results:
        for article in batch:
            if article["url"] and article["url"] not in seen:
                seen.add(article["url"])
                articles.append(article)
    return articles


def save_articles(articles: List[dict]) -> None:
    if not articles:
        return
    db = next(get_db())
    try:
        for article in articles:
            exists = db.query(NewsArticle).filter(NewsArticle.url == article["url"]).first()
            if exists:
                continue
            row = NewsArticle(
                title=article.get("title", ""),
                url=article.get("url", ""),
                source=article.get("source", ""),
                published_at=article.get("published_at", datetime.utcnow()),
                content=article.get("content"),
            )
            db.add(row)
        db.commit()
    finally:
        db.close()
