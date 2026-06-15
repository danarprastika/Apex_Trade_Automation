import logging
import time

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.database.seed import seed_default_market_pairs

logger = logging.getLogger(__name__)


def run_alembic_migrations() -> bool:
    max_retries = 10
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            config = Config("/app/alembic.ini")
            command.upgrade(config, "head")
            logger.info("alembic_migrations_completed")
            return True
        except (OperationalError, ProgrammingError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"migration_attempt_{attempt + 1}_failed_waiting_{retry_delay}s", error=str(e))
                time.sleep(retry_delay)
            else:
                logger.error("alembic_migration_failed_after_retries", error=str(e))
                raise
        except Exception as e:
            logger.error(f"migration_unexpected_error", error=str(e))
            raise
    return False


def run_startup_tasks() -> None:
    logger.info("running_startup_tasks")
    
    run_alembic_migrations()
    
    max_seed_retries = 5
    for attempt in range(max_seed_retries):
        try:
            seed_default_market_pairs()
            logger.info("database_seed_completed")
            return
        except (OperationalError, ProgrammingError) as e:
            if attempt < max_seed_retries - 1:
                logger.warning(f"seed_attempt_{attempt + 1}_failed_waiting_3s", error=str(e))
                time.sleep(3)
            else:
                logger.error("database_seed_failed_after_retries", error=str(e))
                raise
        except Exception as e:
            logger.error(f"seed_unexpected_error", error=str(e))
            raise