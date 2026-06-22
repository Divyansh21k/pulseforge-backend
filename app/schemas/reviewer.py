from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class ReviewerCreate(BaseModel):
    full_name: str
    email: EmailStr
    organization: Optional[str] = None
    expertise_text: Optional[str] = None
    max_workload: int = 5
    participant_id: Optional[int] = None
    linkedin_url: Optional[str] = None


class ReviewerOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    organization: Optional[str] = None
    expertise_text: Optional[str] = None
    max_workload: int
    linkedin_url: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssignmentRunRequest(BaseModel):
    """Optional knobs for an assignment run; defaults match PS1 section 6.2 weights."""

    reviewers_per_project: int = 2
    expertise_weight: float = 0.40
    workload_weight: float = 0.30
    conflict_weight: float = 0.20
    diversity_weight: float = 0.10
