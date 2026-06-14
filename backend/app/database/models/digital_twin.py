import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database.base import Base


class TwinScenarioType(str, Enum):
    AGGRESSIVE = "AGGRESSIVE"
    MODERATE = "MODERATE"
    CONSERVATIVE = "CONSERVATIVE"


class DigitalTwinRun(Base):
    __tablename__ = "digital_twin_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(30), nullable=False, index=True)
    scenario_type = Column(SQLEnum(TwinScenarioType, name="twin_scenario_type"), nullable=False, index=True)
    simulated_pnl = Column(JSONB, nullable=True)
    simulated_drawdown = Column(JSONB, nullable=True)
    parameters = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
