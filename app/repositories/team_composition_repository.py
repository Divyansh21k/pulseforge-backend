import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.team import TeamCompositionScore


class TeamCompositionRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_or_update(self, team_id: int, score: float, gaps: List[str]) -> TeamCompositionScore:
        existing = (
            self.db.query(TeamCompositionScore)
            .filter(TeamCompositionScore.team_id == team_id)
            .first()
        )
        if existing:
            existing.skill_diversity_score = score
            existing.coverage_gaps_json = json.dumps(gaps)
            existing.computed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing

        record = TeamCompositionScore(
            team_id=team_id,
            skill_diversity_score=score,
            coverage_gaps_json=json.dumps(gaps),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
