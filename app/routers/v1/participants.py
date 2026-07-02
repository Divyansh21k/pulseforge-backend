from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.repositories.participant_repository import ParticipantRepository
from app.schemas.participant import ParticipantCreate, ParticipantOut
from app.utils.auth_deps import get_current_user, require_organizer
from app.services.communication_service import send_notification

router = APIRouter(prefix="/api/participants", tags=["Participants"])


@router.post("/", response_model=ParticipantOut, status_code=status.HTTP_201_CREATED)
def register_participant(
    payload: ParticipantCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    repo = ParticipantRepository(db)

    existing = repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A participant with email '{payload.email}' is already registered (id={existing.id}).",
        )

    participant = repo.create(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        organization=payload.organization,
        raw_skills_text=payload.raw_skills_text,
    )
    
    # Queue confirmation email to run in the background
    background_tasks.add_task(
        send_notification,
        db=db,
        participant_id=participant.id,
        template_key="registration_confirmed",
        context={"name": participant.full_name}
    )
    
    return participant


@router.get("/", response_model=List[ParticipantOut])
def list_participants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = ParticipantRepository(db)
    return repo.list_all(skip=skip, limit=limit)


@router.get("/{participant_id}", response_model=ParticipantOut)
def get_participant(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = ParticipantRepository(db)
    participant = repo.get_by_id(participant_id)
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    return participant
