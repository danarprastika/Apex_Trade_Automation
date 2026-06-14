import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
