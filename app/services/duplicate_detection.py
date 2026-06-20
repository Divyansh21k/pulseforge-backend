from typing import List, Dict

from sqlalchemy.orm import Session

from app.repositories.participant_repository import ParticipantRepository
from app.repositories.duplicate_repository import DuplicateFlagRepository
from app.utils.fuzzy_matching import name_similarity

FUZZY_NAME_THRESHOLD = 0.85
ORG_NAME_THRESHOLD = 0.50


class DuplicateDetectionService:
    def __init__(self, db: Session):
        self.participant_repo = ParticipantRepository(db)
        self.duplicate_repo = DuplicateFlagRepository(db)

    def scan_participant(self, participant_id: int) -> List[Dict]:
        target = self.participant_repo.get_by_id(participant_id)
        if not target:
            raise ValueError(f"Participant {participant_id} not found")

        candidates = self.participant_repo.list_for_duplicate_scan()
        results = []

        for candidate in candidates:
            if candidate.id == target.id:
                continue

            match_type = None
            confidence = 0.0

            if candidate.email.lower() == target.email.lower():
                match_type = "exact_email"
                confidence = 1.0
            else:
                name_score = name_similarity(target.full_name, candidate.full_name)
                same_org = bool(target.organization) and (
                    (target.organization or "").strip().lower()
                    == (candidate.organization or "").strip().lower()
                )

                if name_score >= FUZZY_NAME_THRESHOLD:
                    match_type = "fuzzy_name"
                    confidence = min(1.0, name_score + (0.1 if same_org else 0))
                elif same_org and name_score >= ORG_NAME_THRESHOLD:
                    match_type = "organization"
                    confidence = round(0.4 + (name_score * 0.3), 2)

            if match_type:
                self.duplicate_repo.create(
                    participant_id=target.id,
                    matched_participant_id=candidate.id,
                    match_type=match_type,
                    confidence_score=round(confidence, 2),
                )
                results.append(
                    {
                        "matched_participant_id": candidate.id,
                        "matched_name": candidate.full_name,
                        "matched_email": candidate.email,
                        "match_type": match_type,
                        "confidence_score": round(confidence, 2),
                    }
                )

        return results
