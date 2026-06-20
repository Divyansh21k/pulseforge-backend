from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    raw_skills_text = Column(String, nullable=True)
    role = Column(String, default="participant")  # participant | reviewer | admin
    created_at = Column(DateTime, default=datetime.utcnow)

    # Demographic fields are used ONLY in aggregate, statistical bias-detection
    # comparisons (PS1 section 6.3). Never shown to reviewers, never used in scoring.
    gender = Column(String, nullable=True)
    region = Column(String, nullable=True)

    skills = relationship("ParticipantSkill", back_populates="participant")


class ParticipantSkill(Base):
    __tablename__ = "participant_skills"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    source = Column(String, default="ai_extracted")  # ai_extracted | manual
    confidence = Column(Float, default=1.0)

    participant = relationship("Participant", back_populates="skills")
    skill = relationship("Skill")
