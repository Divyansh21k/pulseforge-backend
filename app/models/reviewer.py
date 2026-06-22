from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Reviewer(Base):
    """A reviewer profile. Kept separate from Participant since reviewers
    in a real hackathon are often staff/faculty/industry mentors, not
    necessarily registered participants -- but we link to Participant
    when a participant is *also* acting as reviewer, to reuse identity."""

    __tablename__ = "reviewers"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    organization = Column(String, nullable=True)  # used for conflict-of-interest detection
    expertise_text = Column(Text, nullable=True)  # raw free text, e.g. "ML, computer vision, react"
    max_workload = Column(Integer, default=5)  # max projects this reviewer can take
    linkedin_url = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending | approved | rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    expertise_tags = relationship("ReviewerExpertise", back_populates="reviewer")
    assignments = relationship("ReviewerAssignment", back_populates="reviewer")


class ReviewerExpertise(Base):
    """Normalized expertise tags extracted from a reviewer's free-text bio,
    using the same skill taxonomy as participant skill extraction. This is
    what makes expertise-matching an apples-to-apples NLP comparison."""

    __tablename__ = "reviewer_expertise"

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("reviewers.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    reviewer = relationship("Reviewer", back_populates="expertise_tags")
    skill = relationship("Skill")


class ReviewerAssignment(Base):
    """A reviewer<->project pairing produced by the assignment optimizer.
    Stores the score breakdown so the assignment is explainable/auditable,
    which directly supports the transparency requirement in PS1 section 6.3."""

    __tablename__ = "reviewer_assignments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("reviewers.id"), nullable=False)

    expertise_score = Column(Float, nullable=False)
    workload_score = Column(Float, nullable=False)
    conflict_score = Column(Float, nullable=False)  # 1.0 = no conflict, 0.0 = full conflict
    diversity_score = Column(Float, nullable=False)
    total_score = Column(Float, nullable=False)

    status = Column(String, default="assigned")  # assigned | reassigned | completed
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="assignments")
    reviewer = relationship("Reviewer", back_populates="assignments")
