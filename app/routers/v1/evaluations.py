from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.repositories.reviewer_repository import ReviewerRepository
from app.schemas.evaluation import EvaluationCreate
from app.services.evaluation_service import EvaluationService
from app.services.bias_detection import ScoreNormalizationService, BiasDetectionService
from app.repositories.evaluation_repository import EvaluationRepository, BiasFlagRepository
from app.utils.auth_deps import get_current_user, require_organizer, require_reviewer
from app.utils.roles import is_organizer

router = APIRouter(prefix="/api/evaluations", tags=["Evaluation Workflow"])


def _verify_reviewer_identity(db: Session, current_user: Participant, reviewer_id: int) -> None:
    if is_organizer(current_user.role):
        return
    reviewer = ReviewerRepository(db).get_by_id(reviewer_id)
    if not reviewer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewer not found")
    if reviewer.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may only submit evaluations as your own reviewer profile",
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def submit_evaluation(
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_reviewer),
):
    _verify_reviewer_identity(db, current_user, payload.reviewer_id)
    service = EvaluationService(db)
    try:
        evaluation = service.submit_evaluation(
            project_id=payload.project_id,
            reviewer_id=payload.reviewer_id,
            innovation_score=payload.innovation_score,
            technical_score=payload.technical_score,
            impact_score=payload.impact_score,
            presentation_score=payload.presentation_score,
            feedback_text=payload.feedback_text,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {
        "id": evaluation.id,
        "project_id": evaluation.project_id,
        "reviewer_id": evaluation.reviewer_id,
        "raw_score": evaluation.raw_score,
        "created_at": evaluation.created_at,
    }


@router.get("/project/{project_id}")
def list_evaluations_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = EvaluationRepository(db)
    evals = repo.list_for_project(project_id)
    return [
        {
            "id": e.id,
            "reviewer_id": e.reviewer_id,
            "innovation_score": e.innovation_score,
            "technical_score": e.technical_score,
            "impact_score": e.impact_score,
            "presentation_score": e.presentation_score,
            "raw_score": e.raw_score,
            "normalized_score": e.normalized_score,
            "feedback_text": e.feedback_text,
        }
        for e in evals
    ]


@router.post("/normalize")
def normalize_scores(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    service = ScoreNormalizationService(db)
    updated = service.normalize_all()
    return {"evaluations_normalized": updated}


@router.post("/bias-scan")
def run_bias_scan(
    db: Session = Depends(get_db),
    current_user: Participant = Depends(require_organizer),
):
    service = BiasDetectionService(db)
    cohort_flags = service.detect_cohort_bias()
    reviewer_flags = service.detect_reviewer_outliers()

    return {
        "cohort_flags": cohort_flags,
        "reviewer_flags": reviewer_flags,
        "total_flags": len(cohort_flags) + len(reviewer_flags),
    }


@router.get("/bias-flags")
def list_bias_flags(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: Participant = Depends(get_current_user),
):
    repo = BiasFlagRepository(db)
    flags = repo.list_all(status=status_filter)
    return [
        {
            "id": f.id,
            "dimension": f.dimension,
            "scope": f.scope,
            "reviewer_id": f.reviewer_id,
            "description": f.description,
            "severity": f.severity,
            "statistic": f.statistic,
            "confidence": f.confidence,
            "status": f.status,
            "created_at": f.created_at,
        }
        for f in flags
    ]
