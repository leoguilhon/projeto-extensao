from secrets import token_urlsafe

from fastapi import HTTPException, status

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.time_utils import add_minutes, now_utc, parse_iso_datetime
from app.core.validation import normalize_email
from app.db.memory import store
from app.models.entities import UserRecord
from app.schemas.auth import AuthResponse
from app.services.users import authenticate_user, create_user, email_exists, to_user_public


def issue_token(user_id: int) -> str:
    token = token_urlsafe(32)
    expires_at = add_minutes(now_utc(), ACCESS_TOKEN_EXPIRE_MINUTES).isoformat()
    store.tokens[token] = {"user_id": user_id, "expires_at": expires_at}
    return token


def build_auth_response(user: UserRecord) -> AuthResponse:
    return AuthResponse(access_token=issue_token(user["id"]), user=to_user_public(user))


def get_user_by_token(token: str) -> UserRecord | None:
    session = store.tokens.get(token)
    if not session:
        return None

    if parse_iso_datetime(session["expires_at"]) <= now_utc():
        store.tokens.pop(token, None)
        return None

    return store.users.get(session["user_id"])


def register_user(name: str, email: str, password: str) -> AuthResponse:
    normalized_email = normalize_email(email)
    if email_exists(normalized_email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail ja cadastrado.")

    user = create_user(name, normalized_email, password)
    return build_auth_response(user)


def login_user(email: str, password: str) -> AuthResponse:
    user = authenticate_user(normalize_email(email), password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha invalidos.")

    return build_auth_response(user)
