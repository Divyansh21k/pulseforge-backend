from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.team import TeamCreate, TeamAutoFormRequest
from app.repositories.team_repository import TeamRepository
from app.services.team_composition import TeamCompositionService

router = APIRouter(prefix="/api/teams", tags=["Teams"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    repo = TeamRepository(db)
    team = repo.create(payload.name, payload.member_ids)
    return {
        "id": team.id,
        "name": team.name,
        "member_ids": [m.participant_id for m in team.members],
        "created_at": team.created_at,
    }


@router.get("/")
def list_teams(db: Session = Depends(get_db)):
    repo = TeamRepository(db)
    teams = repo.list_all()
    return [{"id": t.id, "name": t.name, "member_count": len(t.members)} for t in teams]


@router.get("/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db)):
    repo = TeamRepository(db)
    team = repo.get_by_id(team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return {
        "id": team.id,
        "name": team.name,
        "members": [
            {
                "participant_id": m.participant_id,
                "full_name": m.participant.full_name,
                "role": m.role,
            }
            for m in team.members
        ],
        "created_at": team.created_at,
    }


@router.get("/{team_id}/composition")
def get_team_composition(team_id: int, db: Session = Depends(get_db)):
    service = TeamCompositionService(db)
    try:
        result = service.analyze_team(team_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return result


@router.post("/auto-form")
def auto_form_teams(payload: TeamAutoFormRequest, db: Session = Depends(get_db)):
    from app.services.team_formation import TeamFormationService

    service = TeamFormationService(db)
    try:
        teams = service.form_teams(team_size=payload.team_size)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"teams_formed": len(teams), "teams": teams}

