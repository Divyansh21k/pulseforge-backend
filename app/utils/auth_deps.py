from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.participant import Participant
from app.utils.roles import ORGANIZER, PARTICIPANT, REVIEWER, is_organizer
from app.utils.security import decode_token

bearer_scheme = HTTPBearer()
bearer_scheme_optional = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Participant:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise exc

    sub = payload.get("sub")
    if sub is None:
        raise exc

    try:
        participant_id = int(sub)
    except (ValueError, TypeError):
        raise exc

    user = db.query(Participant).filter(Participant.id == participant_id).first()
    if user is None:
        raise exc
    return user


def require_role(*roles: str):
    def _check(current_user: Participant = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {' or '.join(roles)}",
            )
        return current_user
    return _check


def require_organizer(current_user: Participant = Depends(get_current_user)) -> Participant:
    if not is_organizer(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires role: organizer",
        )
    return current_user


def require_reviewer(current_user: Participant = Depends(get_current_user)) -> Participant:
    if current_user.role not in {REVIEWER} and not is_organizer(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires role: reviewer or organizer",
        )
    return current_user


def require_participant(current_user: Participant = Depends(get_current_user)) -> Participant:
    if current_user.role not in {PARTICIPANT, REVIEWER} and not is_organizer(current_user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires role: participant, reviewer, or organizer",
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme_optional),
    db: Session = Depends(get_db),
) -> Optional[Participant]:
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        participant_id = int(sub)
    except (ValueError, TypeError):
        return None
    return db.query(Participant).filter(Participant.id == participant_id).first()


# Backward-compatible alias
require_admin = require_organizer
