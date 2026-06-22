from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.reviewer import Reviewer, ReviewerExpertise, ReviewerAssignment


class ReviewerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        full_name: str,
        email: str,
        organization: Optional[str] = None,
        expertise_text: Optional[str] = None,
        max_workload: int = 5,
        participant_id: Optional[int] = None,
        linkedin_url: Optional[str] = None,
    ) -> Reviewer:
        reviewer = Reviewer(
            full_name=full_name,
            email=email,
            organization=organization,
            expertise_text=expertise_text,
            max_workload=max_workload,
            participant_id=participant_id,
            linkedin_url=linkedin_url,
            status="pending",
        )
        self.db.add(reviewer)
        self.db.commit()
        self.db.refresh(reviewer)
        return reviewer

    def get_by_id(self, reviewer_id: int) -> Optional[Reviewer]:
        return self.db.query(Reviewer).filter(Reviewer.id == reviewer_id).first()

    def get_by_email(self, email: str) -> Optional[Reviewer]:
        return self.db.query(Reviewer).filter(Reviewer.email == email).first()

    def list_all(self) -> List[Reviewer]:
        return self.db.query(Reviewer).all()

    def update_status(self, reviewer_id: int, status: str) -> Optional[Reviewer]:
        reviewer = self.get_by_id(reviewer_id)
        if reviewer:
            reviewer.status = status
            self.db.commit()
            self.db.refresh(reviewer)
        return reviewer

    def add_expertise(self, reviewer_id: int, skill_id: int) -> ReviewerExpertise:
        existing = (
            self.db.query(ReviewerExpertise)
            .filter(
                ReviewerExpertise.reviewer_id == reviewer_id,
                ReviewerExpertise.skill_id == skill_id,
            )
            .first()
        )
        if existing:
            return existing
        link = ReviewerExpertise(reviewer_id=reviewer_id, skill_id=skill_id)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def list_expertise(self, reviewer_id: int) -> List[ReviewerExpertise]:
        return (
            self.db.query(ReviewerExpertise)
            .filter(ReviewerExpertise.reviewer_id == reviewer_id)
            .all()
        )


class ReviewerAssignmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        project_id: int,
        reviewer_id: int,
        expertise_score: float,
        workload_score: float,
        conflict_score: float,
        diversity_score: float,
        total_score: float,
    ) -> ReviewerAssignment:
        assignment = ReviewerAssignment(
            project_id=project_id,
            reviewer_id=reviewer_id,
            expertise_score=expertise_score,
            workload_score=workload_score,
            conflict_score=conflict_score,
            diversity_score=diversity_score,
            total_score=total_score,
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def list_for_project(self, project_id: int) -> List[ReviewerAssignment]:
        return (
            self.db.query(ReviewerAssignment)
            .filter(ReviewerAssignment.project_id == project_id)
            .all()
        )

    def list_for_reviewer(self, reviewer_id: int) -> List[ReviewerAssignment]:
        return (
            self.db.query(ReviewerAssignment)
            .filter(ReviewerAssignment.reviewer_id == reviewer_id)
            .all()
        )

    def count_active_for_reviewer(self, reviewer_id: int) -> int:
        return (
            self.db.query(ReviewerAssignment)
            .filter(
                ReviewerAssignment.reviewer_id == reviewer_id,
                ReviewerAssignment.status == "assigned",
            )
            .count()
        )

    def list_all(self) -> List[ReviewerAssignment]:
        return self.db.query(ReviewerAssignment).all()

    def delete_for_project(self, project_id: int) -> int:
        """Clears prior assignments before a re-run, returns count deleted."""
        rows = (
            self.db.query(ReviewerAssignment)
            .filter(ReviewerAssignment.project_id == project_id)
            .all()
        )
        count = len(rows)
        for row in rows:
            self.db.delete(row)
        self.db.commit()
        return count
