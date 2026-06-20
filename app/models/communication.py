from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, index=True)
    template_key = Column(String(100), nullable=False)
    channel = Column(String(20), nullable=False, default="email")
    subject = Column(String(300), nullable=True)
    body = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="sent")
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    participant = relationship("Participant", backref="communications")
