from fastapi import HTTPException, status

from app.core.time_utils import now_iso
from app.db.memory import store
from app.models.entities import ClubRecord, ClubRole, UserRecord
from app.schemas.clubs import ClubMemberPublic, ClubPublic


def get_club_or_404(club_id: int) -> ClubRecord:
    club = store.clubs.get(club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube não encontrado.")
    return club


def get_member_role(club_id: int, user_id: int) -> ClubRole | None:
    return store.club_members.get(club_id, {}).get(user_id)


def to_club_public(club: ClubRecord, current_user_id: int | None = None) -> ClubPublic:
    members = store.club_members.get(club["id"], {})
    role = members.get(current_user_id) if current_user_id is not None else None
    favorite_clubs = store.favorite_clubs.get(current_user_id, set()) if current_user_id is not None else set()
    return ClubPublic(
        id=club["id"],
        name=club["name"],
        description=club["description"],
        owner_id=club["owner_id"],
        created_at=club["created_at"],
        member_count=len(members),
        current_user_role=role,
        is_member=current_user_id in members if current_user_id is not None else False,
        is_favorite=club["id"] in favorite_clubs,
    )


def create_club(name: str, description: str, owner_id: int) -> ClubRecord:
    club: ClubRecord = {
        "id": store.consume_club_id(),
        "name": name,
        "description": description,
        "owner_id": owner_id,
        "created_at": now_iso(),
    }
    store.clubs[club["id"]] = club
    store.club_members[club["id"]] = {owner_id: "admin"}
    return club


def update_club(club_id: int, user_id: int, name: str, description: str) -> ClubRecord:
    club = get_club_or_404(club_id)
    if club["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador do clube pode editá-lo.",
        )

    club["name"] = name
    club["description"] = description
    return club


def delete_club(club_id: int, user_id: int) -> None:
    club = get_club_or_404(club_id)
    if club["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador do clube pode excluí-lo.",
        )

    for comment_id in [comment_id for comment_id, comment in store.comments.items() if comment["club_id"] == club_id]:
        del store.comments[comment_id]
    for meeting_id in [meeting_id for meeting_id, meeting in store.meetings.items() if meeting["club_id"] == club_id]:
        store.meeting_attendees.pop(meeting_id, None)
        del store.meetings[meeting_id]
    for book_id in [book_id for book_id, book in store.books.items() if book["club_id"] == club_id]:
        store.book_likes.pop(book_id, None)
        del store.books[book_id]

    for favorite_clubs in store.favorite_clubs.values():
        favorite_clubs.discard(club_id)
    store.club_members.pop(club_id, None)
    del store.clubs[club_id]


def list_public_clubs(current_user_id: int) -> list[ClubPublic]:
    ordered_clubs = sorted(store.clubs.values(), key=lambda item: item["created_at"], reverse=True)
    return [to_club_public(club, current_user_id) for club in ordered_clubs]


def join_club(club_id: int, user: UserRecord) -> ClubRecord:
    club = get_club_or_404(club_id)
    members = store.club_members.setdefault(club_id, {})
    if user["id"] in members:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já participa deste clube.")
    members[user["id"]] = "membro"
    return club


def favorite_club(club_id: int, user_id: int) -> ClubRecord:
    club = get_club_or_404(club_id)
    store.favorite_clubs.setdefault(user_id, set()).add(club_id)
    return club


def unfavorite_club(club_id: int, user_id: int) -> ClubRecord:
    club = get_club_or_404(club_id)
    store.favorite_clubs.setdefault(user_id, set()).discard(club_id)
    return club


def leave_club(club_id: int, user_id: int) -> ClubRecord:
    club = get_club_or_404(club_id)
    if club["owner_id"] == user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O criador não pode sair do próprio clube. Exclua o clube se desejar removê-lo.",
        )

    members = store.club_members.get(club_id, {})
    if user_id not in members:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário não participa deste clube.")

    del members[user_id]
    for meeting_id, meeting in store.meetings.items():
        if meeting["club_id"] == club_id:
            store.meeting_attendees.setdefault(meeting_id, set()).discard(user_id)
    return club


def list_members(club_id: int) -> list[ClubMemberPublic]:
    return [
        ClubMemberPublic(user_id=member_id, name=store.users[member_id]["name"], role=role)
        for member_id, role in sorted(
            store.club_members.get(club_id, {}).items(),
            key=lambda item: (0 if item[1] == "admin" else 1, store.users[item[0]]["name"].lower()),
        )
    ]
