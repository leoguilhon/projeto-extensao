from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.time_utils import add_minutes, normalize_datetime, now_utc
from app.core.validation import normalize_email
from app.db.models import AuthToken, User
from app.schemas.auth import AuthResponse
from app.services.users import authenticate_user, create_user, email_exists, to_user_public


def issue_token(db: Session, user_id: int) -> str:
    token = token_urlsafe(32)
    expires_at = add_minutes(now_utc(), ACCESS_TOKEN_EXPIRE_MINUTES)
    db.add(AuthToken(token=token, user_id=user_id, expires_at=expires_at))
    db.commit()
    return token


def build_auth_response(db: Session, user: User) -> AuthResponse:
    return AuthResponse(access_token=issue_token(db, user.id), user=to_user_public(user))


def get_user_by_token(db: Session, token: str) -> User | None:
    auth_token = db.get(AuthToken, token)
    if not auth_token:
        return None

    if normalize_datetime(auth_token.expires_at) <= now_utc():
        db.delete(auth_token)
        db.commit()
        return None

    return db.get(User, auth_token.user_id)


def register_user(db: Session, name: str, email: str, password: str) -> AuthResponse:
    normalized_email = normalize_email(email)
    if email_exists(db, normalized_email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ja cadastrado.")

    user = create_user(db, name, normalized_email, password)
    return build_auth_response(db, user)


def login_user(db: Session, email: str, password: str) -> AuthResponse:
    user = authenticate_user(db, normalize_email(email), password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha invalidos.")

    return build_auth_response(db, user)
