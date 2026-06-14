import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    profit_factor = Column(Numeric, nullable=True)
    drawdown = Column(Numeric, nullable=True)
    win_rate = Column(Numeric, nullable=True)
    total_trades = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
