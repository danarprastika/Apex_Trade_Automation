import logging
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import settings

logger = logging.getLogger(__name__)


def create_db_engine_with_retry(max_retries: int = 10, retry_delay: float = 3.0):
    """Create database engine with retry logic for robust startup."""
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_size=30,
                max_overflow=50,
                pool_timeout=30,
                pool_pre_ping=True,
            )
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("database_connection_established")
            return engine
        except (OperationalError, ProgrammingError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"db_connection_attempt_{attempt + 1}_failed_waiting_{retry_delay}s", error=str(e))
                time.sleep(retry_delay)
            else:
                logger.error("database_connection_failed_after_retries", error=str(e))
                raise


engine = create_db_engine_with_retry()
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
                try:
                    connection.execute(text(statement))
                except Exception:
                    pass
        logger.info("runtime_database_indexes_ensured")
    except Exception:
        logger.exception("runtime_database_index_creation_failed")