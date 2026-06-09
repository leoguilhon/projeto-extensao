from fastapi import Header, HTTPException, status

from app.models.entities import ClubRole, UserRecord
from app.services.auth import get_user_by_token
from app.services.clubs import get_member_role


def current_user(authorization: str | None = Header(default=None)) -> UserRecord:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso ausente.")

    token = authorization.split(" ", 1)[1]
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso inválido.")

    return user


def require_member(club_id: int, user: UserRecord) -> ClubRole:
    role = get_member_role(club_id, user["id"])
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não participa deste clube.")
    return role


def require_admin(club_id: int, user: UserRecord) -> None:
    if require_member(club_id, user) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação permitida apenas para administradores.",
        )
