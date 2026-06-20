from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float

from app.core.database import Base


class DuplicateFlag(Base):
    __tablename__ = "duplicate_flags"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    matched_participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    match_type = Column(String, nullable=False)  # exact_email | fuzzy_name | organization
    confidence_score = Column(Float, nullable=False)
    status = Column(String, default="flagged")  # flagged | reviewed | dismissed
    created_at = Column(DateTime, default=datetime.utcnow)
