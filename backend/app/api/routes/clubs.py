from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import current_user, require_member
from app.db.models import User
from app.db.session import get_db
from app.schemas.clubs import ClubCreate, ClubMemberPublic, ClubPublic, ClubUpdate
from app.services.clubs import (
    create_club,
    delete_club,
    favorite_club,
    get_club_or_404,
    join_club,
    leave_club,
    list_members,
    list_public_clubs,
    to_club_public,
    unfavorite_club,
    update_club,
)


router = APIRouter(tags=["clubs"])


@router.get("/clubs", response_model=list[ClubPublic])
def get_clubs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list_public_clubs(db, user.id)


@router.post("/clubs", response_model=ClubPublic, status_code=status.HTTP_201_CREATED)
def add_club(payload: ClubCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    club = create_club(db, payload.name, payload.description, user.id)
    return to_club_public(db, club, user.id)


@router.get("/clubs/{club_id}", response_model=ClubPublic)
def get_club(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    club = get_club_or_404(db, club_id)
    return to_club_public(db, club, user.id)


@router.put("/clubs/{club_id}", response_model=ClubPublic)
def edit_club(
    club_id: int,
    payload: ClubUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    club = update_club(db, club_id, user.id, payload.name, payload.description)
    return to_club_public(db, club, user.id)


@router.delete("/clubs/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_club(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    delete_club(db, club_id, user.id)


@router.post("/clubs/{club_id}/join", response_model=ClubPublic)
def add_member(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    club = join_club(db, club_id, user)
    return to_club_public(db, club, user.id)


@router.post("/clubs/{club_id}/favorite", response_model=ClubPublic)
def add_favorite_club(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    club = favorite_club(db, club_id, user.id)
    return to_club_public(db, club, user.id)


@router.delete("/clubs/{club_id}/favorite", response_model=ClubPublic)
def remove_favorite_club(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    club = unfavorite_club(db, club_id, user.id)
    return to_club_public(db, club, user.id)


@router.delete("/clubs/{club_id}/members/me", response_model=ClubPublic)
def remove_current_member(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    club = leave_club(db, club_id, user.id)
    return to_club_public(db, club, user.id)


@router.get("/clubs/{club_id}/members", response_model=list[ClubMemberPublic])
def get_members(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_club_or_404(db, club_id)
    require_member(club_id, user, db)
    return list_members(db, club_id)
