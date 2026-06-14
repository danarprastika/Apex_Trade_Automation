from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_timeout=30,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
