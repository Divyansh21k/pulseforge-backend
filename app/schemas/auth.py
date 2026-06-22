from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=6)
    organization: str | None = None
    role: str = "participant"
    raw_skills_text: str | None = None
    expertise_text: str | None = None
    max_workload: int | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    participant_id: int


class UserProfile(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    organization: str | None = None
    reviewer_id: int | None = None
