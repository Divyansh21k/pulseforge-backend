from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.participant import Participant


class ParticipantRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        full_name: str,
        email: str,
        phone: Optional[str],
        organization: Optional[str],
        raw_skills_text: Optional[str],
    ) -> Participant:
        participant = Participant(
            full_name=full_name,
            email=email,
            phone=phone,
            organization=organization,
            raw_skills_text=raw_skills_text,
        )
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def get_by_id(self, participant_id: int) -> Optional[Participant]:
        return self.db.query(Participant).filter(Participant.id == participant_id).first()

    def get_by_email(self, email: str) -> Optional[Participant]:
        return self.db.query(Participant).filter(Participant.email == email).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Participant]:
        return self.db.query(Participant).offset(skip).limit(limit).all()

    def list_for_duplicate_scan(self) -> List[Participant]:
        # Returns full participant set for fuzzy-name / org comparison in Step 5
        return self.db.query(Participant).all()
