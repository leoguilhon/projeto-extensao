from fastapi import APIRouter, Depends, status

from app.api.dependencies import current_user, require_member
from app.models.entities import UserRecord
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
def get_clubs(user: UserRecord = Depends(current_user)):
    return list_public_clubs(user["id"])


@router.post("/clubs", response_model=ClubPublic, status_code=status.HTTP_201_CREATED)
def add_club(payload: ClubCreate, user: UserRecord = Depends(current_user)):
    club = create_club(payload.name, payload.description, user["id"])
    return to_club_public(club, user["id"])


@router.get("/clubs/{club_id}", response_model=ClubPublic)
def get_club(club_id: int, user: UserRecord = Depends(current_user)):
    club = get_club_or_404(club_id)
    return to_club_public(club, user["id"])


@router.put("/clubs/{club_id}", response_model=ClubPublic)
def edit_club(club_id: int, payload: ClubUpdate, user: UserRecord = Depends(current_user)):
    club = update_club(club_id, user["id"], payload.name, payload.description)
    return to_club_public(club, user["id"])


@router.delete("/clubs/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_club(club_id: int, user: UserRecord = Depends(current_user)):
    delete_club(club_id, user["id"])


@router.post("/clubs/{club_id}/join", response_model=ClubPublic)
def add_member(club_id: int, user: UserRecord = Depends(current_user)):
    club = join_club(club_id, user)
    return to_club_public(club, user["id"])


@router.post("/clubs/{club_id}/favorite", response_model=ClubPublic)
def add_favorite_club(club_id: int, user: UserRecord = Depends(current_user)):
    club = favorite_club(club_id, user["id"])
    return to_club_public(club, user["id"])


@router.delete("/clubs/{club_id}/favorite", response_model=ClubPublic)
def remove_favorite_club(club_id: int, user: UserRecord = Depends(current_user)):
    club = unfavorite_club(club_id, user["id"])
    return to_club_public(club, user["id"])


@router.delete("/clubs/{club_id}/members/me", response_model=ClubPublic)
def remove_current_member(club_id: int, user: UserRecord = Depends(current_user)):
    club = leave_club(club_id, user["id"])
    return to_club_public(club, user["id"])


@router.get("/clubs/{club_id}/members", response_model=list[ClubMemberPublic])
def get_members(club_id: int, user: UserRecord = Depends(current_user)):
    get_club_or_404(club_id)
    require_member(club_id, user)
    return list_members(club_id)
