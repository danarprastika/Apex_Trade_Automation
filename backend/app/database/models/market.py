import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class AssetType(str, Enum):
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    STOCK = "STOCK"
    ETF = "ETF"
    COMMODITY = "COMMODITY"
    INDEX = "INDEX"


class AssetStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DELISTED = "DELISTED"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(30), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    asset_type = Column(SQLEnum(AssetType, name="asset_type"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=AssetStatus.ACTIVE.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MarketPairStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DELISTED = "DELISTED"
    HALTED = "HALTED"


class MarketPair(Base):
    __tablename__ = "market_pairs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False, index=True)
    base_asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    quote_asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="ACTIVE", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_market_pairs_exchange_symbol", "exchange_id", "symbol"),
    )


class Candle(Base):
    __tablename__ = "candles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_pair_id = Column(UUID(as_uuid=True), ForeignKey("market_pairs.id"), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    open = Column(Numeric, nullable=False)
    high = Column(Numeric, nullable=False)
    low = Column(Numeric, nullable=False)
    close = Column(Numeric, nullable=False)
    volume = Column(Numeric, nullable=False)
    open_time = Column(DateTime, nullable=False, index=True)
    close_time = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("ix_candles_pair_tf_time", "market_pair_id", "timeframe", "open_time"),
    )
