from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.services.communication_service import (
    send_notification,
    get_notifications_for_participant,
    get_all_notifications,
    TEMPLATES,
)
from app.utils.auth_deps import get_current_user, require_organizer

router = APIRouter(prefix="/api/communications", tags=["communications"])


class SendRequest(BaseModel):
    participant_id: int
    template_key: str
    context: dict = {}


@router.post("/send", status_code=201)
def send(
    payload: SendRequest,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    try:
        r = send_notification(db, payload.participant_id, payload.template_key, payload.context)
        return {"id": r.id, "status": r.status, "subject": r.subject}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/participant/{participant_id}")
def for_participant(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    if current_user.role == "participant" and current_user.id != participant_id:
        raise HTTPException(status_code=403, detail="Cannot view another participant's notifications")
    return [
        {"id": r.id, "template_key": r.template_key, "subject": r.subject,
         "status": r.status, "sent_at": r.sent_at}
        for r in get_notifications_for_participant(db, participant_id)
    ]


@router.get("/all")
def all_notifications(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    return [
        {"id": r.id, "participant_id": r.participant_id, "template_key": r.template_key,
         "subject": r.subject, "status": r.status, "sent_at": r.sent_at}
        for r in get_all_notifications(db, limit)
    ]


@router.get("/templates")
def list_templates(current_user: Participant = Depends(require_organizer)):
    return list(TEMPLATES.keys())
