from fastapi import APIRouter, Depends

from app.api.dependencies import current_user
from app.models.entities import UserRecord
from app.schemas.users import UserPublic, UserUpdate
from app.services.users import to_user_public, update_user_profile


router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserPublic)
def get_profile(user: UserRecord = Depends(current_user)):
    return to_user_public(user)


@router.put("/users/me", response_model=UserPublic)
def update_profile(payload: UserUpdate, user: UserRecord = Depends(current_user)):
    updated_user = update_user_profile(user, payload.name, payload.bio)
    return to_user_public(updated_user)
