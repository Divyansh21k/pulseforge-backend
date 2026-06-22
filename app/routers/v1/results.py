from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.services.results import ResultsService
from app.utils.auth_deps import get_current_user

router = APIRouter(prefix="/api/results", tags=["Results Processing"])


@router.get("/rankings")
def get_rankings(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    service = ResultsService(db)
    return {"rankings": service.generate_rankings()}


@router.get("/feedback/{project_id}")
def get_feedback(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    service = ResultsService(db)
    try:
        return service.generate_feedback(project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
