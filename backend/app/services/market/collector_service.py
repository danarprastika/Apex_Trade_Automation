import asyncio
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.market import Candle
from app.integrations.binance.client import BinanceClient


def _parse_timeframe_to_ms(timeframe: str) -> int:
    unit = timeframe[-1]
    value = int(timeframe[:-1])
    if unit == "m":
        return value * 60 * 1000
    if unit == "h":
        return value * 60 * 60 * 1000
    if unit == "d":
        return value * 24 * 60 * 60 * 1000
    raise ValueError(f"Unsupported timeframe: {timeframe}")


def _get_latest_candle_close_time(db: Session, symbol: str, timeframe: str) -> datetime | None:
    row = (
        db.query(Candle.open_time)
        .join(Candle.__table__.columns, Candle.timeframe == timeframe)
        .filter(Candle.timeframe == timeframe)
        .order_by(Candle.open_time.desc())
        .first()
    )
    return row[0] if row else None


async def fetch_and_store_candles(symbol: str, timeframe: str = "1h", limit_per_request: int = 1000):
    client = BinanceClient(
        api_key=settings.BINANCE_API_KEY or None,
        api_secret=settings.BINANCE_API_SECRET or None,
        testnet=False,
    )

    db: Session = next(get_db())

    try:
        latest = _get_latest_candle_close_time(db, symbol, timeframe)
        since_ms = int(latest.timestamp() * 1000) + 1 if latest else int(datetime(2017, 1, 1, tzinfo=UTC).timestamp() * 1000)
        timeframe_ms = _parse_timeframe_to_ms(timeframe)

        while True:
            ohlcv = await client.get_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=limit_per_request)
            if not ohlcv:
                break

            rows = []
            for candle in ohlcv:
                rows.append(
                    Candle(
                        market_pair_id=None,
                        timeframe=timeframe,
                        open=candle["open"],
                        high=candle["high"],
                        low=candle["low"],
                        close=candle["close"],
                        volume=candle["volume"],
                        open_time=datetime.fromtimestamp(candle["timestamp"] / 1000, tz=UTC),
                        close_time=datetime.fromtimestamp((candle["timestamp"] + timeframe_ms) / 1000, tz=UTC),
                    )
                )
                since_ms = candle["timestamp"] + timeframe_ms

            db.bulk_save_objects(rows, return_defaults=False)
            db.commit()

            if len(ohlcv) < limit_per_request:
                break

            await asyncio.sleep(1.5)
    finally:
        db.close()
        await client.close()
