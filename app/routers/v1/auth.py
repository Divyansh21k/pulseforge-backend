from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.participant import Participant
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.auth_deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Participant).filter(Participant.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if payload.role not in {"participant", "reviewer", "admin"}:
        raise HTTPException(status_code=400, detail="Role must be participant, reviewer, or admin")
    user = Participant(name=payload.name, email=payload.email, hashed_password=hash_password(payload.password), organization=payload.organization, role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token, role=user.role, participant_id=user.id)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Participant).filter(Participant.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token, role=user.role, participant_id=user.id)

@router.get("/me")
def me(current_user: Participant = Depends(get_current_user)):
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email, "role": current_user.role, "organization": current_user.organization}
