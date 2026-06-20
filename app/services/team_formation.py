import math
from typing import Dict, List

from sqlalchemy.orm import Session

from app.repositories.participant_repository import ParticipantRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.skill_repository import ParticipantSkillRepository
from app.services.team_composition import TeamCompositionService, CORE_CATEGORIES
from app.utils.gemini_client import generate_team_rationale


class TeamFormationService:
    def __init__(self, db: Session):
        self.participant_repo = ParticipantRepository(db)
        self.team_repo = TeamRepository(db)
        self.participant_skill_repo = ParticipantSkillRepository(db)
        self.composition_service = TeamCompositionService(db)

    def get_unassigned_participants(self):
        assigned_ids = self.team_repo.get_assigned_participant_ids()
        all_participants = self.participant_repo.list_all(skip=0, limit=10000)
        return [p for p in all_participants if p.id not in assigned_ids]

    def _greedy_group(self, participants, skills_map: Dict[int, set], team_size: int) -> List[List[int]]:
        num_teams = max(1, math.ceil(len(participants) / team_size))
        teams: List[List[int]] = [[] for _ in range(num_teams)]
        team_skill_sets = [set() for _ in range(num_teams)]

        sorted_participants = sorted(
            participants,
            key=lambda p: -len(skills_map.get(p.id, set()) & set(CORE_CATEGORIES)),
        )

        for p in sorted_participants:
            p_categories = skills_map.get(p.id, set()) & set(CORE_CATEGORIES)
            candidates = [i for i in range(num_teams) if len(teams[i]) < team_size]
            if not candidates:
                candidates = list(range(num_teams))

            best_team = max(
                candidates,
                key=lambda i: (len(p_categories - team_skill_sets[i]), -len(teams[i])),
            )
            teams[best_team].append(p.id)
            team_skill_sets[best_team] |= p_categories

        return [t for t in teams if t]

    def form_teams(self, team_size: int = 4) -> List[Dict]:
        unassigned = self.get_unassigned_participants()
        if not unassigned:
            raise ValueError("No unassigned participants available to form teams")

        skills_map = {
            p.id: {link.skill.name for link in self.participant_skill_repo.list_for_participant(p.id)}
            for p in unassigned
        }

        groups = self._greedy_group(unassigned, skills_map, team_size)
        name_lookup = {p.id: p.full_name for p in unassigned}

        results = []
        for idx, group in enumerate(groups, start=1):
            team = self.team_repo.create(name=f"Auto Team {idx}", member_ids=group)
            composition = self.composition_service.analyze_team(team.id)
            rationale = generate_team_rationale(
                composition["categories_covered"], composition["coverage_gaps"]
            )
            results.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "member_ids": group,
                    "member_names": [name_lookup[pid] for pid in group],
                    "skill_diversity_score": composition["skill_diversity_score"],
                    "categories_covered": composition["categories_covered"],
                    "coverage_gaps": composition["coverage_gaps"],
                    "ai_rationale": rationale,
                }
            )
        return results
