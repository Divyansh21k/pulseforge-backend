from typing import List

from sqlalchemy.orm import Session

from app.models.duplicate import DuplicateFlag


class DuplicateFlagRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        participant_id: int,
        matched_participant_id: int,
        match_type: str,
        confidence_score: float,
    ) -> DuplicateFlag:
        flag = DuplicateFlag(
            participant_id=participant_id,
            matched_participant_id=matched_participant_id,
            match_type=match_type,
            confidence_score=confidence_score,
        )
        self.db.add(flag)
        self.db.commit()
        self.db.refresh(flag)
        return flag

    def list_for_participant(self, participant_id: int) -> List[DuplicateFlag]:
        return (
            self.db.query(DuplicateFlag)
            .filter(DuplicateFlag.participant_id == participant_id)
            .all()
        )
