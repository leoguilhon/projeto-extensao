from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.core.time_utils import normalize_datetime, now_utc, to_iso_datetime
from app.core.validation import validate_optional_text, validate_required_text
from app.db.models import Meeting, MeetingAttendance, User
from app.schemas.meetings import MeetingAttendeePublic, MeetingPublic
from app.services.books import ensure_book_belongs_to_club
from app.services.comments import count_meeting_comments


def get_meeting_or_404(db: Session, meeting_id: int) -> Meeting:
    meeting = db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encontro nao encontrado.")
    return meeting


def to_meeting_public(db: Session, meeting: Meeting) -> MeetingPublic:
    return MeetingPublic(
        id=meeting.id,
        club_id=meeting.club_id,
        title=meeting.title,
        scheduled_for=to_iso_datetime(meeting.scheduled_for),
        location=meeting.location,
        agenda=meeting.agenda,
        book_id=meeting.book_id,
        book_title=meeting.book.title if meeting.book else None,
        created_by=meeting.created_by,
        created_at=to_iso_datetime(meeting.created_at),
        comment_count=count_meeting_comments(db, meeting.id),
        attendee_count=count_meeting_attendees(db, meeting.id),
    )


def count_meeting_attendees(db: Session, meeting_id: int) -> int:
    return db.scalar(select(func.count()).select_from(MeetingAttendance).where(MeetingAttendance.meeting_id == meeting_id)) or 0


def list_meeting_attendees(db: Session, meeting_id: int) -> list[MeetingAttendeePublic]:
    rows = db.execute(
        select(MeetingAttendance.user_id, User.name)
        .join(User, User.id == MeetingAttendance.user_id)
        .where(MeetingAttendance.meeting_id == meeting_id)
        .order_by(func.lower(User.name))
    ).all()
    return [MeetingAttendeePublic(user_id=user_id, name=name) for user_id, name in rows]


def confirm_meeting_attendance(db: Session, meeting_id: int, user_id: int) -> None:
    if not db.get(MeetingAttendance, {"meeting_id": meeting_id, "user_id": user_id}):
        db.add(MeetingAttendance(meeting_id=meeting_id, user_id=user_id))
        db.commit()


def remove_meeting_attendance(db: Session, meeting_id: int, user_id: int) -> None:
    attendance = db.get(MeetingAttendance, {"meeting_id": meeting_id, "user_id": user_id})
    if attendance:
        db.delete(attendance)
        db.commit()


def create_meeting(
    db: Session,
    club_id: int,
    title: str,
    scheduled_for: datetime,
    location: str,
    agenda: str,
    created_by: int,
    book_id: int | None = None,
) -> Meeting:
    if book_id is not None:
        ensure_book_belongs_to_club(db, book_id, club_id)

    meeting = Meeting(
        club_id=club_id,
        title=validate_required_text(title, "Titulo do encontro", min_length=3, max_length=120),
        scheduled_for=normalize_datetime(scheduled_for),
        location=validate_optional_text(location, "Local do encontro", max_length=120),
        agenda=validate_optional_text(agenda, "Pauta do encontro", max_length=500),
        book_id=book_id,
        created_by=created_by,
        created_at=now_utc(),
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def update_meeting(
    db: Session,
    meeting: Meeting,
    title: str,
    scheduled_for: datetime,
    location: str,
    agenda: str,
    book_id: int | None = None,
) -> Meeting:
    if book_id is not None:
        ensure_book_belongs_to_club(db, book_id, meeting.club_id)

    meeting.title = validate_required_text(title, "Titulo do encontro", min_length=3, max_length=120)
    meeting.scheduled_for = normalize_datetime(scheduled_for)
    meeting.location = validate_optional_text(location, "Local do encontro", max_length=120)
    meeting.agenda = validate_optional_text(agenda, "Pauta do encontro", max_length=500)
    meeting.book_id = book_id
    db.commit()
    db.refresh(meeting)
    return meeting


def delete_meeting(db: Session, meeting: Meeting) -> None:
    db.delete(meeting)
    db.commit()


def list_club_meetings(db: Session, club_id: int) -> list[MeetingPublic]:
    meetings = db.scalars(select(Meeting).where(Meeting.club_id == club_id).order_by(Meeting.scheduled_for)).all()
    return [to_meeting_public(db, meeting) for meeting in meetings]


def list_book_meetings(db: Session, book_id: int) -> list[MeetingPublic]:
    meetings = db.scalars(select(Meeting).where(Meeting.book_id == book_id).order_by(Meeting.scheduled_for)).all()
    return [to_meeting_public(db, meeting) for meeting in meetings]
