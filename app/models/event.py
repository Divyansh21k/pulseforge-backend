from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    theme = Column(String, nullable=True)
    organizer_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default="upcoming")  # upcoming | ongoing | completed
    created_at = Column(DateTime, default=datetime.utcnow)

    organizer = relationship("Participant")

class EventEnrollment(Base):
    __tablename__ = "event_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event")
    participant = relationship("Participant")
