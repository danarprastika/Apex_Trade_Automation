import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class TradeSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    side = Column(SQLEnum(TradeSide, name="trade_side"), nullable=False)
    entry_price = Column(Numeric, nullable=False)
    exit_price = Column(Numeric, nullable=True)
    pnl = Column(Numeric, nullable=True)
    status = Column(String(20), nullable=False, default=TradeStatus.OPEN.value, index=True)
    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_paper_trades_user_symbol", "user_id", "symbol"),
    )


class RiskSettings(Base):
    __tablename__ = "risk_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    max_daily_loss = Column(Numeric, nullable=True)
    max_open_positions = Column(Numeric, nullable=True)
    risk_per_trade = Column(Numeric, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
