import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=30,
    max_overflow=50,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

INDEX_STATEMENTS = (
    "CREATE INDEX IF NOT EXISTS ix_market_pairs_symbol ON market_pairs (symbol)",
    "CREATE INDEX IF NOT EXISTS ix_candles_open_time ON candles (open_time)",
    "CREATE INDEX IF NOT EXISTS ix_candles_market_pair_timeframe_open_time ON candles (market_pair_id, timeframe, open_time)",
)


def ensure_runtime_indexes() -> None:
    try:
        with engine.begin() as connection:
            for statement in INDEX_STATEMENTS:
                connection.execute(text(statement))
        logger.info("runtime_database_indexes_ensured")
    except Exception:
        logger.exception("runtime_database_index_creation_failed")
