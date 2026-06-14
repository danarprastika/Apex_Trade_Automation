import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.base import get_db
from app.database.models.market import Candle, MarketPair
from app.integrations.binance.client import BinanceClient

logger = logging.getLogger(__name__)

BACKFILL_PAGE_DELAY_SECONDS = 0.05


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


def _get_latest_candle_close_time(db: Session, pair_id, timeframe: str) -> datetime | None:
    row = (
        db.query(Candle.open_time)
        .filter(Candle.market_pair_id == pair_id, Candle.timeframe == timeframe)
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
        pair = db.query(MarketPair).filter(MarketPair.symbol == symbol).first()
        if not pair:
            logger.warning("market_pair_not_found_skip_candle_backfill", symbol=symbol, timeframe=timeframe)
            return
        latest = _get_latest_candle_close_time(db, pair.id, timeframe)
        since_ms = int(latest.timestamp() * 1000) + 1 if latest else int(datetime(2017, 1, 1, tzinfo=UTC).timestamp() * 1000)
        timeframe_ms = _parse_timeframe_to_ms(timeframe)

        while True:
            try:
                ohlcv = await client.get_ohlcv(symbol, timeframe=timeframe, since=since_ms, limit=limit_per_request)
            except Exception as exc:
                logger.exception("binance_ohlcv_fetch_failed", symbol=symbol, timeframe=timeframe, since_ms=since_ms, error=str(exc))
                break
            if not ohlcv:
                break

            rows = []
            for candle in ohlcv:
                rows.append(
                    Candle(
                        market_pair_id=pair.id,
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

            await asyncio.sleep(BACKFILL_PAGE_DELAY_SECONDS)
    finally:
        db.close()
        await client.close()
