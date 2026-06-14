import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class StrategyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TESTING = "TESTING"
    RETIRED = "RETIRED"


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class SignalStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    version = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=StrategyStatus.ACTIVE.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class StrategyParameter(Base):
    __tablename__ = "strategy_parameters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False)
    parameter_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, index=True)
    market_pair_id = Column(UUID(as_uuid=True), ForeignKey("market_pairs.id"), nullable=False, index=True)
    signal_type = Column(SQLEnum(SignalType, name="signal_type"), nullable=False)
    confidence = Column(Numeric(5, 2), nullable=True)
    entry_price = Column(Numeric, nullable=True)
    stop_loss = Column(Numeric, nullable=True)
    take_profit = Column(Numeric, nullable=True)
    reason = Column(Text, nullable=True)
    signal_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(20), nullable=False, default=SignalStatus.PENDING.value, index=True)
