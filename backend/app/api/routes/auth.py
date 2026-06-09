from fastapi import APIRouter, status

from app.schemas.auth import AuthResponse, UserCreate, UserLogin
from app.services.auth import login_user, register_user


router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate):
    return register_user(payload.name, payload.email, payload.password)


@router.post("/auth/login", response_model=AuthResponse)
def login(payload: UserLogin):
    return login_user(payload.email, payload.password)
