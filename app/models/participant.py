from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # nullable for legacy/seed records
    organization = Column(String(200), nullable=True)
    role = Column(String(50), nullable=False, default="participant")  # participant | reviewer | admin
    gender = Column(String(50), nullable=True)
    region = Column(String(100), nullable=True)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team_memberships = relationship("TeamMember", back_populates="participant")
