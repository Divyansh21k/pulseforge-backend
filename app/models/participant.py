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
    created_at = Column(DateTime, default=datetime.utcnow)

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
