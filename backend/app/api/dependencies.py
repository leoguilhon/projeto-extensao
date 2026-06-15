from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.models.entities import ClubRole
from app.services.auth import get_user_by_token
from app.services.clubs import get_member_role


def current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso ausente.")

    token = authorization.split(" ", 1)[1]
    user = get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso invalido.")

    return user


def require_member(club_id: int, user: User, db: Session) -> ClubRole:
    role = get_member_role(db, club_id, user.id)
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario nao participa deste clube.")
    return role


def require_admin(club_id: int, user: User, db: Session) -> None:
    if require_member(club_id, user, db) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acao permitida apenas para administradores.",
        )
