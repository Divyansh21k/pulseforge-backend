from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.repositories.reviewer_repository import ReviewerRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserProfile
from app.services.reviewer_service import ReviewerService
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.auth_deps import get_current_user
from app.utils.roles import SELF_REGISTER_ROLES, normalize_role

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: Participant) -> TokenResponse:
    role = normalize_role(user.role)
    token = create_access_token({"sub": str(user.id), "role": role})
    return TokenResponse(access_token=token, role=role, participant_id=user.id)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Participant).filter(Participant.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if payload.role not in SELF_REGISTER_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Self-registration allowed for participant or reviewer only. Organizer accounts are provisioned by administrators.",
        )

    user = Participant(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        organization=payload.organization,
        raw_skills_text=payload.raw_skills_text,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if payload.role == "reviewer":
        rev_service = ReviewerService(db)
        try:
            rev_service.create_reviewer(
                full_name=payload.full_name,
                email=payload.email,
                organization=payload.organization,
                expertise_text=payload.expertise_text or payload.raw_skills_text,
                max_workload=payload.max_workload or 5,
                participant_id=user.id,
            )
        except ValueError:
            pass

    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Participant).filter(Participant.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_response(user)


@router.get("/me", response_model=UserProfile)
def me(current_user: Participant = Depends(get_current_user), db: Session = Depends(get_db)):
    reviewer_id = None
    if current_user.role == "reviewer":
        reviewer = ReviewerRepository(db).get_by_email(current_user.email)
        if reviewer:
            reviewer_id = reviewer.id

    return UserProfile(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=normalize_role(current_user.role),
        organization=current_user.organization,
        reviewer_id=reviewer_id,
    )
