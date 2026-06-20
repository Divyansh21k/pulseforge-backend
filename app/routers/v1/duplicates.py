from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.duplicate_detection import DuplicateDetectionService
from app.repositories.duplicate_repository import DuplicateFlagRepository

router = APIRouter(prefix="/api/duplicates", tags=["Duplicate Detection"])


@router.post("/check/{participant_id}")
def check_duplicates(participant_id: int, db: Session = Depends(get_db)):
    """
    Scans a participant against all others and creates DuplicateFlag
    records for any matches found (exact email / fuzzy name / organization).
    """
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
def get_existing_flags(participant_id: int, db: Session = Depends(get_db)):
    """Returns previously stored duplicate flags for a participant (no new scan)."""
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
