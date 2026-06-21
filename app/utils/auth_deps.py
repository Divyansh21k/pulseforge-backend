from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.utils.security import decode_token
from app.models.participant import Participant

bearer_scheme = HTTPBearer()


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


require_admin = require_role("admin")
require_reviewer = require_role("reviewer", "admin")
require_participant = require_role("participant", "reviewer", "admin")
