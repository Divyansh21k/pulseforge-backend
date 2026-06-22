"""
Reviewer Assignment Intelligence (PS1 section 4.4 / 6.2)

Implements a multi-objective greedy assignment algorithm that balances:
  - Expertise match (40%): overlap between reviewer expertise tags and
    project tech-stack / description skill tags (NLP-normalized via the
    same skill taxonomy used for participant skill extraction).
  - Workload balance (30%): prefers reviewers further from their max
    workload, so assignments don't pile onto a few people.
  - Conflict avoidance (20%): same-organization conflicts are detected
    and heavily penalized (modeling "graph theory for conflict detection"
    from the hint -- the conflict relationship is the edge; here it's a
    simple shared-organization rule, extensible to co-authorship etc).
  - Diversity promotion (10%): mild bonus for spreading projects across
    reviewers who haven't already reviewed something from the same team.

This is a greedy multi-objective optimizer rather than a global solver
(e.g. linear assignment / Hungarian algorithm) -- chosen deliberately for
a 24-48h build: it is O(projects * reviewers), fully deterministic,
explainable (every assignment stores its score breakdown), and fast
enough to comfortably clear the "<60 seconds for 100+ projects" target
in section 6.2. A global optimum (Hungarian algorithm) is noted as a
future-work upgrade in the README.
"""
from typing import List, Dict, Set

from sqlalchemy.orm import Session

from app.repositories.project_repository import ProjectRepository
from app.repositories.reviewer_repository import ReviewerRepository, ReviewerAssignmentRepository
from app.repositories.skill_repository import ParticipantSkillRepository
from app.models.reviewer import Reviewer
from app.models.project import Project

EXPERTISE_WEIGHT = 0.40
WORKLOAD_WEIGHT = 0.30
CONFLICT_WEIGHT = 0.20
DIVERSITY_WEIGHT = 0.10

SKILL_VOCAB = [
    "backend", "frontend", "mobile", "machine-learning", "data-science",
    "devops", "cloud", "ui-ux", "blockchain", "cybersecurity",
    "python", "javascript", "java", "react", "nodejs", "sql",
]


def _tags_from_text(text: str) -> Set[str]:
    """Lightweight keyword-overlap tagging against the shared skill
    vocabulary. Used so expertise<->project matching doesn't require a
    live LLM call per pair (keeps the optimizer fast and offline-safe);
    the heavier LLM-based extraction is still used for participant
    skills in app.utils.gemini_client."""
    text_lower = (text or "").lower()
    return {tag for tag in SKILL_VOCAB if tag.replace("-", " ") in text_lower or tag in text_lower}


class ReviewerAssignmentService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.reviewer_repo = ReviewerRepository(db)
        self.assignment_repo = ReviewerAssignmentRepository(db)
        self.participant_skill_repo = ParticipantSkillRepository(db)

    def _expertise_score(self, reviewer: Reviewer, project: Project) -> float:
        reviewer_tags = _tags_from_text(reviewer.expertise_text or "")
        project_tags = _tags_from_text(
            f"{project.title} {project.description} {project.tech_stack_text or ''}"
        )
        if not reviewer_tags or not project_tags:
            return 0.3  # neutral score when there isn't enough text to compare
        overlap = reviewer_tags & project_tags
        return round(len(overlap) / len(project_tags), 3) if project_tags else 0.3

    def _workload_score(self, reviewer: Reviewer, current_load: Dict[int, int]) -> float:
        load = current_load.get(reviewer.id, 0)
        if reviewer.max_workload <= 0:
            return 0.0
        remaining_capacity = max(0, reviewer.max_workload - load)
        return round(remaining_capacity / reviewer.max_workload, 3)

    def _conflict_score(self, reviewer: Reviewer, project: Project) -> float:
        """1.0 = no detected conflict. 0.0 = same organization as the
        submitting team (a hard conflict-of-interest signal)."""
        team = project.team
        if not team or not reviewer.organization:
            return 1.0
        member_orgs = {
            (m.participant.organization or "").strip().lower()
            for m in team.members
            if m.participant and m.participant.organization
        }
        if reviewer.organization.strip().lower() in member_orgs:
            return 0.0
        return 1.0

    def _diversity_score(self, reviewer: Reviewer, project: Project, seen_teams: Dict[int, Set[int]]) -> float:
        """Bonus for not having already reviewed this same team's other
        projects (spreads exposure across more reviewers)."""
        reviewed_teams = seen_teams.get(reviewer.id, set())
        return 0.0 if project.team_id in reviewed_teams else 1.0

    def run_assignment(self, reviewers_per_project: int = 2) -> List[Dict]:
        """Assigns `reviewers_per_project` reviewers to every project that
        doesn't already have assignments, using greedy multi-objective
        scoring. Returns the full breakdown for transparency/audit."""
        projects = self.project_repo.list_all()
        reviewers = [r for r in self.reviewer_repo.list_all() if r.status == "approved"]

        if not reviewers:
            raise ValueError("No reviewers available to assign")
        if not projects:
            raise ValueError("No projects available to assign reviewers to")

        current_load: Dict[int, int] = {
            r.id: self.assignment_repo.count_active_for_reviewer(r.id) for r in reviewers
        }
        seen_teams: Dict[int, Set[int]] = {r.id: set() for r in reviewers}
        results = []

        for project in projects:
            existing = self.assignment_repo.list_for_project(project.id)
            if existing:
                continue  # don't double-assign; use reassign_no_show for changes

            scored = []
            for reviewer in reviewers:
                expertise = self._expertise_score(reviewer, project)
                workload = self._workload_score(reviewer, current_load)
                conflict = self._conflict_score(reviewer, project)
                diversity = self._diversity_score(reviewer, project, seen_teams)

                if conflict == 0.0:
                    continue  # hard exclusion: never assign a conflicted reviewer

                total = round(
                    expertise * EXPERTISE_WEIGHT
                    + workload * WORKLOAD_WEIGHT
                    + conflict * CONFLICT_WEIGHT
                    + diversity * DIVERSITY_WEIGHT,
                    4,
                )
                scored.append((total, reviewer, expertise, workload, conflict, diversity))

            scored.sort(key=lambda x: x[0], reverse=True)
            picks = scored[:reviewers_per_project]

            for total, reviewer, expertise, workload, conflict, diversity in picks:
                assignment = self.assignment_repo.create(
                    project_id=project.id,
                    reviewer_id=reviewer.id,
                    expertise_score=expertise,
                    workload_score=workload,
                    conflict_score=conflict,
                    diversity_score=diversity,
                    total_score=total,
                )
                current_load[reviewer.id] = current_load.get(reviewer.id, 0) + 1
                seen_teams.setdefault(reviewer.id, set()).add(project.team_id)

                results.append(
                    {
                        "project_id": project.id,
                        "project_title": project.title,
                        "reviewer_id": reviewer.id,
                        "reviewer_name": reviewer.full_name,
                        "expertise_score": expertise,
                        "workload_score": workload,
                        "conflict_score": conflict,
                        "diversity_score": diversity,
                        "total_score": total,
                    }
                )

        return results

    def reassign_no_show(self, project_id: int, no_show_reviewer_id: int) -> Dict:
        """Removes a no-show reviewer's assignment for a project and picks
        the next-best available reviewer, supporting dynamic reassignment
        per PS1 section 4.4."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        existing_assignments = self.assignment_repo.list_for_project(project_id)
        already_assigned_ids = {a.reviewer_id for a in existing_assignments}

        target = next((a for a in existing_assignments if a.reviewer_id == no_show_reviewer_id), None)
        if not target:
            raise ValueError(f"Reviewer {no_show_reviewer_id} is not assigned to project {project_id}")

        target.status = "reassigned"
        self.db.commit()

        reviewers = [r for r in self.reviewer_repo.list_all() if r.id not in already_assigned_ids and r.status == "approved"]
        current_load = {
            r.id: self.assignment_repo.count_active_for_reviewer(r.id) for r in reviewers
        }

        best = None
        for reviewer in reviewers:
            expertise = self._expertise_score(reviewer, project)
            workload = self._workload_score(reviewer, current_load)
            conflict = self._conflict_score(reviewer, project)
            if conflict == 0.0:
                continue
            diversity = self._diversity_score(reviewer, project, {})
            total = round(
                expertise * EXPERTISE_WEIGHT
                + workload * WORKLOAD_WEIGHT
                + conflict * CONFLICT_WEIGHT
                + diversity * DIVERSITY_WEIGHT,
                4,
            )
            if best is None or total > best[0]:
                best = (total, reviewer, expertise, workload, conflict, diversity)

        if not best:
            raise ValueError("No eligible replacement reviewer found")

        total, reviewer, expertise, workload, conflict, diversity = best
        new_assignment = self.assignment_repo.create(
            project_id=project_id,
            reviewer_id=reviewer.id,
            expertise_score=expertise,
            workload_score=workload,
            conflict_score=conflict,
            diversity_score=diversity,
            total_score=total,
        )

        return {
            "project_id": project_id,
            "replaced_reviewer_id": no_show_reviewer_id,
            "new_reviewer_id": reviewer.id,
            "new_reviewer_name": reviewer.full_name,
            "total_score": total,
        }
