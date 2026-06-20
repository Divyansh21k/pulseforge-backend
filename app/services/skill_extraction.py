from typing import List

from sqlalchemy.orm import Session

from app.repositories.participant_repository import ParticipantRepository
from app.repositories.skill_repository import SkillRepository, ParticipantSkillRepository
from app.utils.gemini_client import extract_skills


class SkillExtractionService:
    def __init__(self, db: Session):
        self.participant_repo = ParticipantRepository(db)
        self.skill_repo = SkillRepository(db)
        self.participant_skill_repo = ParticipantSkillRepository(db)

    def extract_for_participant(self, participant_id: int) -> List[str]:
        participant = self.participant_repo.get_by_id(participant_id)
        if not participant:
            raise ValueError(f"Participant {participant_id} not found")

        skill_names = extract_skills(participant.raw_skills_text or "")

        for name in skill_names:
            skill = self.skill_repo.get_or_create(name)
            self.participant_skill_repo.add_skill(participant_id, skill.id)

        return skill_names
