"""Demo mode: seed sample dataset and report status."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.participant_repository import ParticipantRepository
from app.utils.auth_deps import get_optional_user
from app.utils.roles import is_organizer
from app.models.participant import Participant

router = APIRouter(prefix="/api/demo", tags=["Demo Mode"])


@router.get("/status")
def demo_status(db: Session = Depends(get_db)):
    repo = ParticipantRepository(db)
    count = len(repo.list_all(limit=10000))
    return {
        "database_empty": count == 0,
        "participant_count": count,
        "demo_accounts_available": count > 0,
        "demo_credentials": {
            "organizer": {"email": "organizer@pulseforge.dev", "password": "demo1234"},
            "reviewer": {"email": "reviewer@pulseforge.dev", "password": "demo1234"},
            "participant": {"email": "participant@pulseforge.dev", "password": "demo1234"},
        },
    }


@router.post("/seed")
def seed_demo(
    db: Session = Depends(get_db),
    current_user: Participant | None = Depends(get_optional_user),
):
    """
    Load the full demo dataset. Public when DB is empty; requires organizer when data exists.
    Idempotent — skips if participants already present unless force=true via query (organizer only).
    """
    from scripts.seed_data import run as run_seed

    repo = ParticipantRepository(db)
    existing = len(repo.list_all(limit=1))
    if existing > 0:
        if current_user is None or not is_organizer(current_user.role):
            return {
                "seeded": False,
                "message": "Database already contains data. Login as organizer to re-seed.",
                "participant_count": existing,
            }

    run_seed()
    new_count = len(repo.list_all(limit=10000))
    return {
        "seeded": True,
        "message": "Demo dataset loaded successfully.",
        "participant_count": new_count,
    }
