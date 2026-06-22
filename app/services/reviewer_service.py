from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.reviewer_repository import ReviewerRepository
from app.repositories.skill_repository import SkillRepository
from app.models.reviewer import Reviewer
from app.utils.gemini_client import extract_skills


class ReviewerService:
    def __init__(self, db: Session):
        self.db = db
        self.reviewer_repo = ReviewerRepository(db)
        self.skill_repo = SkillRepository(db)

    def create_reviewer(
        self,
        full_name: str,
        email: str,
        organization: Optional[str] = None,
        expertise_text: Optional[str] = None,
        max_workload: int = 5,
        participant_id: Optional[int] = None,
        linkedin_url: Optional[str] = None,
    ) -> Reviewer:
        existing = self.reviewer_repo.get_by_email(email)
        if existing:
            raise ValueError(f"A reviewer with email '{email}' already exists (id={existing.id}).")

        reviewer = self.reviewer_repo.create(
            full_name=full_name,
            email=email,
            organization=organization,
            expertise_text=expertise_text,
            max_workload=max_workload,
            participant_id=participant_id,
            linkedin_url=linkedin_url,
        )

        if expertise_text:
            tags = extract_skills(expertise_text)
            for tag in tags:
                skill = self.skill_repo.get_or_create(tag)
                self.reviewer_repo.add_expertise(reviewer.id, skill.id)

        return reviewer

    def update_reviewer_status(self, reviewer_id: int, status: str) -> Reviewer:
        reviewer = self.reviewer_repo.update_status(reviewer_id, status)
        if not reviewer:
            raise ValueError(f"Reviewer {reviewer_id} not found.")
        return reviewer
