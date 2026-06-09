from uuid import uuid4

from fastapi import HTTPException, status

from app.db.memory import store
from app.models.entities import UserRecord
from app.schemas.auth import AuthResponse
from app.services.users import authenticate_user, create_user, email_exists, to_user_public


def issue_token(user_id: int) -> str:
    token = str(uuid4())
    store.tokens[token] = user_id
    return token


def build_auth_response(user: UserRecord) -> AuthResponse:
    return AuthResponse(access_token=issue_token(user["id"]), user=to_user_public(user))


def get_user_by_token(token: str) -> UserRecord | None:
    user_id = store.tokens.get(token)
    if not user_id:
        return None
    return store.users.get(user_id)


def register_user(name: str, email: str, password: str) -> AuthResponse:
    if email_exists(email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado.")

    user = create_user(name, email, password)
    return build_auth_response(user)


def login_user(email: str, password: str) -> AuthResponse:
    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos.")

    return build_auth_response(user)
