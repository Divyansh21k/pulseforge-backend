from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("TeamMember", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    role = Column(String, default="member")

    team = relationship("Team", back_populates="members")
    participant = relationship("Participant")


class TeamCompositionScore(Base):
    __tablename__ = "team_composition_scores"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, unique=True)
    skill_diversity_score = Column(Float, nullable=False)
    coverage_gaps_json = Column(String, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow)
