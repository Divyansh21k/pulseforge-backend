from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate
from app.utils.auth_deps import get_current_user, require_organizer

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    repo = EventRepository(db)
    event = repo.create(
        name=payload.name,
        theme=payload.theme,
        organizer_id=current_user.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    return {
        "id": event.id,
        "name": event.name,
        "theme": event.theme,
        "organizer_id": event.organizer_id,
        "status": event.status,
        "created_at": event.created_at,
    }


@router.get("/")
def list_events(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = EventRepository(db)
    events = repo.list_all()
    return [
        {"id": e.id, "name": e.name, "theme": e.theme, "status": e.status}
        for e in events
    ]


@router.get("/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = EventRepository(db)
    event = repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return {
        "id": event.id,
        "name": event.name,
        "theme": event.theme,
        "organizer_id": event.organizer_id,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "status": event.status,
        "created_at": event.created_at,
    }


@router.post("/{event_id}/enroll")
def enroll_in_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = EventRepository(db)
    event = repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    enrollment = repo.enroll_participant(event_id, current_user.id)
    return {
        "event_id": enrollment.event_id,
        "participant_id": enrollment.participant_id,
        "enrolled_at": enrollment.enrolled_at,
    }


@router.get("/enrolled/me")
def get_enrolled_events(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = EventRepository(db)
    events = repo.get_enrolled_events(current_user.id)
    return [
        {"id": e.id, "name": e.name, "theme": e.theme, "status": e.status}
        for e in events
    ]
