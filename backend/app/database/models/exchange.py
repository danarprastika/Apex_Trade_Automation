import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class ExchangeType(str, Enum):
    SPOT = "SPOT"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"


class ExchangeAccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"
    TESTNET = "TESTNET"


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    exchange_type = Column(SQLEnum(ExchangeType, name="exchange_type"), nullable=False)
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ExchangeAccount(Base):
    __tablename__ = "exchange_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False, index=True)
    api_key_encrypted = Column(Text, nullable=False)
    api_secret_encrypted = Column(Text, nullable=False)
    is_testnet = Column(Boolean, nullable=False, default=False)
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
