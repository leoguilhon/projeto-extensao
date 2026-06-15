from sqlalchemy import case, delete, func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.core.time_utils import now_utc, to_iso_datetime
from app.core.validation import validate_required_text
from app.db.models import Club, ClubMembership, FavoriteClub, Meeting, MeetingAttendance, User
from app.models.entities import ClubRole
from app.schemas.clubs import ClubMemberPublic, ClubPublic


def get_club_or_404(db: Session, club_id: int) -> Club:
    club = db.get(Club, club_id)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clube nao encontrado.")
    return club


def get_member_role(db: Session, club_id: int, user_id: int) -> ClubRole | None:
    membership = db.get(ClubMembership, {"club_id": club_id, "user_id": user_id})
    return membership.role if membership else None


def _count_members(db: Session, club_id: int) -> int:
    return db.scalar(select(func.count()).select_from(ClubMembership).where(ClubMembership.club_id == club_id)) or 0


def _is_favorite(db: Session, club_id: int, user_id: int | None) -> bool:
    if user_id is None:
        return False
    return db.get(FavoriteClub, {"club_id": club_id, "user_id": user_id}) is not None


def to_club_public(db: Session, club: Club, current_user_id: int | None = None) -> ClubPublic:
    role = get_member_role(db, club.id, current_user_id) if current_user_id is not None else None
    return ClubPublic(
        id=club.id,
        name=club.name,
        description=club.description,
        owner_id=club.owner_id,
        created_at=to_iso_datetime(club.created_at),
        member_count=_count_members(db, club.id),
        current_user_role=role,
        is_member=role is not None,
        is_favorite=_is_favorite(db, club.id, current_user_id),
    )


def create_club(db: Session, name: str, description: str, owner_id: int) -> Club:
    normalized_name = validate_required_text(name, "Nome do clube", min_length=3, max_length=100)
    normalized_description = validate_required_text(
        description,
        "Descricao do clube",
        min_length=8,
        max_length=500,
    )

    club = Club(
        name=normalized_name,
        description=normalized_description,
        owner_id=owner_id,
        created_at=now_utc(),
    )
    db.add(club)
    db.flush()
    db.add(ClubMembership(club_id=club.id, user_id=owner_id, role="admin"))
    db.commit()
    db.refresh(club)
    return club


def update_club(db: Session, club_id: int, user_id: int, name: str, description: str) -> Club:
    club = get_club_or_404(db, club_id)
    if club.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador do clube pode edita-lo.",
        )

    club.name = validate_required_text(name, "Nome do clube", min_length=3, max_length=100)
    club.description = validate_required_text(
        description,
        "Descricao do clube",
        min_length=8,
        max_length=500,
    )
    db.commit()
    db.refresh(club)
    return club


def delete_club(db: Session, club_id: int, user_id: int) -> None:
    club = get_club_or_404(db, club_id)
    if club.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o criador do clube pode exclui-lo.",
        )

    db.delete(club)
    db.commit()


def list_public_clubs(db: Session, current_user_id: int) -> list[ClubPublic]:
    clubs = db.scalars(select(Club).order_by(Club.created_at.desc())).all()
    return [to_club_public(db, club, current_user_id) for club in clubs]


def join_club(db: Session, club_id: int, user: User) -> Club:
    club = get_club_or_404(db, club_id)
    existing_membership = db.get(ClubMembership, {"club_id": club_id, "user_id": user.id})
    if existing_membership:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuario ja participa deste clube.")

    db.add(ClubMembership(club_id=club_id, user_id=user.id, role="membro"))
    db.commit()
    db.refresh(club)
    return club


def favorite_club(db: Session, club_id: int, user_id: int) -> Club:
    club = get_club_or_404(db, club_id)
    if not db.get(FavoriteClub, {"club_id": club_id, "user_id": user_id}):
        db.add(FavoriteClub(club_id=club_id, user_id=user_id))
        db.commit()
    return club


def unfavorite_club(db: Session, club_id: int, user_id: int) -> Club:
    club = get_club_or_404(db, club_id)
    favorite = db.get(FavoriteClub, {"club_id": club_id, "user_id": user_id})
    if favorite:
        db.delete(favorite)
        db.commit()
    return club


def leave_club(db: Session, club_id: int, user_id: int) -> Club:
    club = get_club_or_404(db, club_id)
    if club.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="O criador nao pode sair do proprio clube. Exclua o clube se desejar remove-lo.",
        )

    membership = db.get(ClubMembership, {"club_id": club_id, "user_id": user_id})
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario nao participa deste clube.")

    meeting_ids = select(Meeting.id).where(Meeting.club_id == club_id)
    db.execute(
        delete(MeetingAttendance).where(
            MeetingAttendance.user_id == user_id,
            MeetingAttendance.meeting_id.in_(meeting_ids),
        )
    )
    db.delete(membership)
    db.commit()
    db.refresh(club)
    return club


def list_members(db: Session, club_id: int) -> list[ClubMemberPublic]:
    rows = db.execute(
        select(ClubMembership.user_id, User.name, ClubMembership.role)
        .join(User, User.id == ClubMembership.user_id)
        .where(ClubMembership.club_id == club_id)
        .order_by(case((ClubMembership.role == "admin", 0), else_=1), func.lower(User.name))
    ).all()
    return [ClubMemberPublic(user_id=user_id, name=name, role=role) for user_id, name, role in rows]
