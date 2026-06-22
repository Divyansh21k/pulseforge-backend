from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.repositories.duplicate_repository import DuplicateFlagRepository
from app.services.duplicate_detection import DuplicateDetectionService
from app.utils.auth_deps import get_current_user, require_organizer

router = APIRouter(prefix="/api/duplicates", tags=["Duplicate Detection"])


from pydantic import BaseModel
from typing import Optional

class RawParticipantPayload(BaseModel):
    full_name: str
    email: str
    organization: Optional[str] = None

@router.post("/check-raw")
def check_duplicates_raw(
    payload: RawParticipantPayload,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    service = DuplicateDetectionService(db)
    matches = service.scan_raw_participant(
        full_name=payload.full_name,
        email=payload.email,
        organization=payload.organization
    )

    duplicate_detected = len(matches) > 0
    best_match = matches[0] if duplicate_detected else None

    return {
        "duplicateDetected": duplicate_detected,
        "confidenceScore": int(best_match["confidence_score"] * 100) if best_match else 0,
        "matchedParticipantId": f"p-{best_match['matched_participant_id']}" if best_match else None,
        "reason": f"Matches {best_match['matched_name']} ({best_match['matched_email']}) via {best_match['match_type']}" if best_match else "No duplicates found"
    }


@router.post("/check/{participant_id}")
def check_duplicates(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    service = DuplicateDetectionService(db)
    try:
        matches = service.scan_participant(participant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {
        "participant_id": participant_id,
        "matches_found": len(matches),
        "matches": matches,
    }


@router.get("/flags/{participant_id}")
def get_existing_flags(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = DuplicateFlagRepository(db)
    flags = repo.list_for_participant(participant_id)
    return [
        {
            "id": f.id,
            "matched_participant_id": f.matched_participant_id,
            "match_type": f.match_type,
            "confidence_score": f.confidence_score,
            "status": f.status,
            "created_at": f.created_at,
        }
        for f in flags
    ]
