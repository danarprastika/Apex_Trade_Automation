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


class AgentRoleType(str, Enum):
    MARKET = "MARKET"
    RISK = "RISK"
    SENTIMENT = "SENTIMENT"
    EXECUTION = "EXECUTION"
    RESEARCH = "RESEARCH"
    GOVERNANCE = "GOVERNANCE"


class AgentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"


class DecisionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    NO_TRADE = "NO_TRADE"
    REDUCE_EXPOSURE = "REDUCE_EXPOSURE"
    EMERGENCY_EXIT = "EMERGENCY_EXIT"


class AIAgent(Base):
    __tablename__ = "ai_agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    role_type = Column(SQLEnum(AgentRoleType, name="agent_role_type"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=AgentStatus.ACTIVE.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("ai_agents.id"), nullable=False, index=True)
    symbol = Column(String(30), nullable=False, index=True)
    decision = Column(SQLEnum(DecisionAction, name="decision_action"), nullable=False)
    confidence = Column(String(10), nullable=False)
    reasoning_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class FinalDecision(Base):
    __tablename__ = "final_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(30), nullable=False, index=True)
    final_action = Column(SQLEnum(DecisionAction, name="final_decision_action"), nullable=False)
    consensus_score = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
