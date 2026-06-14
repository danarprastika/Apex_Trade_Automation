import json
import logging
import uuid
from datetime import datetime
from typing import Protocol

import pandas as pd
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.core.retry import retry_sync
from app.database.base import get_db
from app.database.models.market import Candle, MarketPair
from app.database.models.portfolio import PortfolioSnapshot

logger = logging.getLogger(__name__)


class BaseSentimentEngine(Protocol):
    def analyze(self, text: str) -> dict | None:
        ...


class SentimentAnalyzer:
    def __init__(self) -> None:
        self.ollama_url = settings.OLLAMA_API_URL.rstrip("/")
        self.model_name = getattr(settings, "OLLAMA_MODEL", "llama3")

    @retry_sync
    def _generate(self, payload: dict) -> dict:
        import httpx

        resp = httpx.post(f"{self.ollama_url}/api/generate", json=payload, timeout=20)
        resp.raise_for_status()
        return resp.json()

    def analyze(self, text: str) -> dict | None:
        if not text:
            return None
        prompt = (
            "You are a financial sentiment classifier for crypto markets.\n"
            "Return ONLY a JSON object with keys: sentiment (BULLISH|BEARISH|NEUTRAL) and confidence_score (0..1).\n"
            f"Text: {text}\n"
            "JSON:\n"
        )
        payload = {"model": self.model_name, "prompt": prompt, "format": "json", "stream": False}
        try:
            data = self._generate(payload)
            response_text = data.get("response", "")
            if not response_text:
                return None
            return json.loads(response_text)
        except Exception:
            logger.exception("ollama_sentiment_analysis_failed")
            return None


async def fetch_news() -> list[dict]:
    return []


def store_articles(symbol: str, articles: list[dict]) -> None:
    db: Session = next(get_db())
    try:
        from app.database.models.intelligence import NewsArticle
        from app.database.models.portfolio import PortfolioSnapshot
        for article in articles:
            exists = db.query(NewsArticle).filter(NewsArticle.url == article.get("url")).first()
            if exists:
                continue
            row = NewsArticle(
                title=article.get("title", ""),
                url=article.get("url", ""),
                source=article.get("source", ""),
                published_at=datetime.utcnow(),
                content=article.get("content"),
            )
            db.add(row)
        db.commit()
    finally:
        db.close()
