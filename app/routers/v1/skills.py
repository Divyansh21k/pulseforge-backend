from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.repositories.skill_repository import ParticipantSkillRepository
from app.schemas.skill import SkillExtractRequest
from app.services.skill_extraction import SkillExtractionService
from app.utils.auth_deps import get_current_user
from app.utils.gemini_client import extract_skills

router = APIRouter(prefix="/api/skills", tags=["Skill Extraction"])


@router.post("/extract")
def preview_extraction(payload: SkillExtractRequest):
    """Stateless preview — uses Gemini when available, keyword fallback otherwise."""
    skills = extract_skills(payload.raw_text)
    return {"normalized_skills": skills}


@router.post("/extract/{participant_id}")
def extract_and_save(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    service = SkillExtractionService(db)
    try:
        skills = service.extract_for_participant(participant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {"participant_id": participant_id, "normalized_skills": skills}


@router.get("/{participant_id}")
def get_participant_skills(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = ParticipantSkillRepository(db)
    links = repo.list_for_participant(participant_id)
    return [
        {
            "skill_id": link.skill_id,
            "skill_name": link.skill.name,
            "source": link.source,
            "confidence": link.confidence,
        }
        for link in links
    ]
