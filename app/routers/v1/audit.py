from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.audit import AuditTrail
from app.models.participant import Participant
from app.utils.auth_deps import get_current_user

router = APIRouter(prefix="/api/audit", tags=["Audit Trail"])


class AuditCreate(BaseModel):
    action: str
    user_role: str
    details: str
    category: str


class AuditOut(BaseModel):
    id: int
    timestamp: str
    action: str
    userRole: str
    details: str
    category: str


@router.post("/")
def create_audit_record(
    payload: AuditCreate,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    record = AuditTrail(
        action=payload.action,
        user_role=payload.user_role,
        details=payload.details,
        category=payload.category,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"status": "ok", "id": record.id}


@router.get("/", response_model=List[AuditOut])
def list_audit_records(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    records = db.query(AuditTrail).order_by(AuditTrail.timestamp.desc()).all()
    return [
        AuditOut(
            id=r.id,
            timestamp=r.timestamp.isoformat(),
            action=r.action,
            userRole=r.user_role,
            details=r.details or "",
            category=r.category,
        )
        for r in records
    ]
