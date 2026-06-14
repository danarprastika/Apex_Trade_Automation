from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.database.models.intelligence import NewsArticle, Sentiment
from app.services.intelligence.news_collector import fetch_latest_news, save_articles

router = APIRouter()


@router.get("/articles")
def list_articles(db: Session = Depends(get_db)):
    rows = db.execute(select(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(200)).scalars().all()
    return [
        {
            "id": str(row.id),
            "title": row.title,
            "url": row.url,
            "source": row.source,
            "published_at": row.published_at.isoformat() if row.published_at else None,
        }
        for row in rows
    ]


@router.post("/collect")
async def collect_news():
    articles = await fetch_latest_news()
    save_articles(articles)
    return {"collected": len(articles)}
