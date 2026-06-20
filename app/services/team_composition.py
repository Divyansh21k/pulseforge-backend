from typing import Dict

from sqlalchemy.orm import Session

from app.repositories.team_repository import TeamRepository
from app.repositories.team_composition_repository import TeamCompositionRepository
from app.repositories.skill_repository import ParticipantSkillRepository

CORE_CATEGORIES = [
    "backend",
    "frontend",
    "mobile",
    "machine-learning",
    "data-science",
    "devops",
    "cloud",
    "ui-ux",
    "blockchain",
    "cybersecurity",
]


class TeamCompositionService:
    def __init__(self, db: Session):
        self.team_repo = TeamRepository(db)
        self.composition_repo = TeamCompositionRepository(db)
        self.participant_skill_repo = ParticipantSkillRepository(db)

    def analyze_team(self, team_id: int) -> Dict:
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise ValueError(f"Team {team_id} not found")

        all_skill_names = set()
        for member in team.members:
            links = self.participant_skill_repo.list_for_participant(member.participant_id)
            for link in links:
                all_skill_names.add(link.skill.name)

        covered = sorted(c for c in CORE_CATEGORIES if c in all_skill_names)
        gaps = sorted(c for c in CORE_CATEGORIES if c not in all_skill_names)
        diversity_score = round(len(covered) / len(CORE_CATEGORIES) * 100, 1)

        record = self.composition_repo.save_or_update(team_id, diversity_score, gaps)

        return {
            "team_id": team_id,
            "skill_diversity_score": diversity_score,
            "categories_covered": covered,
            "coverage_gaps": gaps,
            "computed_at": record.computed_at,
        }
