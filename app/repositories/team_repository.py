from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.team import Team, TeamMember


class TeamRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, member_ids: List[int]) -> Team:
        team = Team(name=name)
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)

        for pid in member_ids:
            self.db.add(TeamMember(team_id=team.id, participant_id=pid, role="member"))
        self.db.commit()
        self.db.refresh(team)
        return team

    def get_by_id(self, team_id: int) -> Optional[Team]:
        return self.db.query(Team).filter(Team.id == team_id).first()

    def list_all(self) -> List[Team]:
        return self.db.query(Team).all()


    def get_assigned_participant_ids(self):
        rows = self.db.query(TeamMember.participant_id).distinct().all()
        return {row[0] for row in rows}
