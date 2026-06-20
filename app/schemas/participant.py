from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class ParticipantBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    organization: Optional[str] = None
    raw_skills_text: Optional[str] = None


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantOut(ParticipantBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
