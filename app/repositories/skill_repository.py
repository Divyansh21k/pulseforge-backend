from typing import List

from sqlalchemy.orm import Session

from app.models.skill import Skill
from app.models.participant import ParticipantSkill


class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, name: str) -> Skill:
        existing = self.db.query(Skill).filter(Skill.name == name).first()
        if existing:
            return existing
        skill = Skill(name=name)
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def list_all(self) -> List[Skill]:
        return self.db.query(Skill).all()


class ParticipantSkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_skill(
        self,
        participant_id: int,
        skill_id: int,
        source: str = "ai_extracted",
        confidence: float = 1.0,
    ) -> ParticipantSkill:
        existing = (
            self.db.query(ParticipantSkill)
            .filter(
                ParticipantSkill.participant_id == participant_id,
                ParticipantSkill.skill_id == skill_id,
            )
            .first()
        )
        if existing:
            return existing

        link = ParticipantSkill(
            participant_id=participant_id,
            skill_id=skill_id,
            source=source,
            confidence=confidence,
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def list_for_participant(self, participant_id: int) -> List[ParticipantSkill]:
        return (
            self.db.query(ParticipantSkill)
            .filter(ParticipantSkill.participant_id == participant_id)
            .all()
        )
