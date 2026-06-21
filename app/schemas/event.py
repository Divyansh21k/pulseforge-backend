from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventCreate(BaseModel):
    name: str
    theme: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
