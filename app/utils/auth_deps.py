from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import decode_token
from app.models.participant import Participant

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Participant:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    payload = decode_token(token)
    if payload is None:
        raise exc
    participant_id = payload.get("sub")
    if participant_id is None:
        raise exc
    user = db.query(Participant).filter(Participant.id == participant_id).first()
    if user is None:
        raise exc
    return user

def require_role(*roles: str):
    def _check(current_user: Participant = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires role: {' or '.join(roles)}")
        return current_user
    return _check

require_admin = require_role("admin")
require_reviewer = require_role("reviewer", "admin")
require_participant = require_role("participant", "reviewer", "admin")
