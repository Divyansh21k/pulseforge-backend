from datetime import datetime
from typing import List

from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str
    member_ids: List[int]


class TeamAutoFormRequest(BaseModel):
    team_size: int = 4
