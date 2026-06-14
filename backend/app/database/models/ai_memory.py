import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class AIModel(Base):
    __tablename__ = "ai_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    architecture = Column(String(100), nullable=False)
    target_asset = Column(String(30), nullable=False, index=True)
    accuracy_score = Column(Numeric, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ai_models.id"), nullable=False, index=True)
    symbol = Column(String(30), nullable=False, index=True)
    predicted_direction = Column(String(20), nullable=False)
    confidence_score = Column(Numeric, nullable=False)
    actual_direction = Column(String(20), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
