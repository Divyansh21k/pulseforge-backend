from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.core.database import Base


class AuditTrail(Base):
    __tablename__ = "audit_trails"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    details = Column(String, nullable=True)
    category = Column(String, nullable=False)
