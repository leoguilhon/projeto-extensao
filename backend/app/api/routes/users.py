from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.users import UserPublic, UserUpdate
from app.services.users import to_user_public, update_user_profile


router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserPublic)
def get_profile(user: User = Depends(current_user)):
    return to_user_public(user)


@router.put("/users/me", response_model=UserPublic)
def update_profile(payload: UserUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    updated_user = update_user_profile(db, user, payload.name, payload.bio)
    return to_user_public(updated_user)
