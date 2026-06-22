from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.repositories.evaluation_repository import BiasFlagRepository
from app.utils.auth_deps import get_current_user, require_organizer

router = APIRouter(prefix="/api/bias-stream", tags=["Bias Stream"])


@router.get("/flags/live")
def stream_bias_flags(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = BiasFlagRepository(db)
    flags = repo.list_all()
    data = [
        {
            "id": f.id,
            "dimension": f.dimension,
            "scope": f.scope,
            "reviewer_id": f.reviewer_id,
            "description": f.description,
            "severity": f.severity,
            "statistic": f.statistic,
            "confidence": f.confidence,
            "status": f.status,
            "created_at": str(f.created_at),
        }
        for f in flags
    ]
    return {"flags": data, "total": len(data)}


@router.get("/summary")
def bias_summary(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    repo = BiasFlagRepository(db)
    all_flags = repo.list_all()
    active = [f for f in all_flags if f.status == "open"]
    critical = [f for f in active if f.severity == "high"]
    return {
        "total_flags": len(all_flags),
        "active_flags": len(active),
        "critical_flags": len(critical),
        "dimensions": list({f.dimension for f in active}),
    }
