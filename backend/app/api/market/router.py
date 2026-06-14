from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.base import get_db
from app.database.models.market import Candle, MarketPair

router = APIRouter()


@router.get("/candles/{symbol}")
def get_candles(symbol: str, timeframe: str = "1h", limit: int = 500, db: Session = Depends(get_db)):
    pair = db.query(MarketPair).filter(MarketPair.symbol == symbol.upper()).first()
    if not pair:
        return {"success": True, "data": []}

    rows = (
        db.query(Candle)
        .filter(Candle.market_pair_id == pair.id, Candle.timeframe == timeframe)
        .order_by(Candle.open_time.asc())
        .limit(limit)
        .all()
    )

    data = [
        [
            int(row.open_time.replace(tzinfo=datetime.now().astimezone().tzinfo).timestamp() * 1000) if row.open_time.tzinfo is None else int(row.open_time.timestamp() * 1000),
            float(row.open),
            float(row.close),
            float(row.low),
            float(row.high),
        ]
        for row in rows
    ]

    return {"success": True, "data": data}
