from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.schemas.reviewer import ReviewerCreate, ReviewerOut, AssignmentRunRequest
from app.services.reviewer_service import ReviewerService
from app.services.reviewer_assignment import ReviewerAssignmentService
from app.repositories.reviewer_repository import ReviewerRepository, ReviewerAssignmentRepository
from app.utils.auth_deps import get_current_user, require_organizer, require_reviewer

router = APIRouter(prefix="/api/reviewers", tags=["Reviewer Intelligence"])


@router.post("/", response_model=ReviewerOut, status_code=status.HTTP_201_CREATED)
def register_reviewer(
    payload: ReviewerCreate,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    service = ReviewerService(db)
    try:
        reviewer = service.create_reviewer(
            full_name=payload.full_name,
            email=payload.email,
            organization=payload.organization,
            expertise_text=payload.expertise_text,
            max_workload=payload.max_workload,
            participant_id=payload.participant_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return reviewer


@router.get("/", response_model=List[ReviewerOut])
def list_reviewers(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = ReviewerRepository(db)
    return repo.list_all()


@router.get("/{reviewer_id}", response_model=ReviewerOut)
def get_reviewer(
    reviewer_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = ReviewerRepository(db)
    reviewer = repo.get_by_id(reviewer_id)
    if not reviewer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewer not found")
    return reviewer


@router.get("/{reviewer_id}/workload")
def get_reviewer_workload(
    reviewer_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = ReviewerRepository(db)
    assignment_repo = ReviewerAssignmentRepository(db)
    reviewer = repo.get_by_id(reviewer_id)
    if not reviewer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewer not found")

    active = assignment_repo.count_active_for_reviewer(reviewer_id)
    return {
        "reviewer_id": reviewer_id,
        "active_assignments": active,
        "max_workload": reviewer.max_workload,
        "utilization_pct": round(active / reviewer.max_workload * 100, 1) if reviewer.max_workload else 0.0,
    }


@router.post("/assign")
def run_assignment(
    payload: AssignmentRunRequest,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    service = ReviewerAssignmentService(db)
    try:
        results = service.run_assignment(reviewers_per_project=payload.reviewers_per_project)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "assignments_created": len(results),
        "assignments": results,
    }


@router.post("/reassign/{project_id}/{no_show_reviewer_id}")
def reassign_no_show(
    project_id: int,
    no_show_reviewer_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    service = ReviewerAssignmentService(db)
    try:
        result = service.reassign_no_show(project_id, no_show_reviewer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return result


@router.get("/assignments/{project_id}")
def get_assignments_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = ReviewerAssignmentRepository(db)
    assignments = repo.list_for_project(project_id)
    return [
        {
            "id": a.id,
            "reviewer_id": a.reviewer_id,
            "reviewer_name": a.reviewer.full_name,
            "expertise_score": a.expertise_score,
            "workload_score": a.workload_score,
            "conflict_score": a.conflict_score,
            "diversity_score": a.diversity_score,
            "total_score": a.total_score,
            "status": a.status,
        }
        for a in assignments
    ]
