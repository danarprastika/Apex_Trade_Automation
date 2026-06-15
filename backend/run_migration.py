import logging
import sys

from alembic.config import Config
from alembic import command
from alembic.exceptions import CommandError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    max_retries = 10
    for attempt in range(max_retries):
        try:
            config = Config("/app/alembic.ini")
            command.upgrade(config, "head")
            logger.info("migration_success")
            return True
        except Exception as e:
            if "database" in str(e).lower() or "connection" in str(e).lower():
                logger.warning(f"db_not_ready_retry_{attempt + 1}", error=str(e))
            else:
                logger.warning(f"migration_attempt_{attempt + 1}_failed", error=str(e))
            if attempt < max_retries - 1:
                import time
                time.sleep(5)
            else:
                logger.error("migration_failed_after_retries")
                return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)