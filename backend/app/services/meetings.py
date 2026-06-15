from datetime import datetime

from fastapi import HTTPException, status

from app.core.time_utils import normalize_datetime, now_iso
from app.db.memory import store
from app.models.entities import MeetingRecord
from app.schemas.meetings import MeetingAttendeePublic, MeetingPublic
from app.services.books import ensure_book_belongs_to_club
from app.services.comments import count_meeting_comments


def get_meeting_or_404(meeting_id: int) -> MeetingRecord:
    meeting = store.meetings.get(meeting_id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Encontro não encontrado.")
    return meeting


def to_meeting_public(meeting: MeetingRecord) -> MeetingPublic:
    linked_book = store.books.get(meeting["book_id"]) if meeting.get("book_id") else None
    return MeetingPublic(
        **meeting,
        book_title=linked_book["title"] if linked_book else None,
        comment_count=count_meeting_comments(meeting["id"]),
        attendee_count=count_meeting_attendees(meeting["id"]),
    )


def count_meeting_attendees(meeting_id: int) -> int:
    return len(store.meeting_attendees.get(meeting_id, set()))


def list_meeting_attendees(meeting_id: int) -> list[MeetingAttendeePublic]:
    return [
        MeetingAttendeePublic(user_id=user_id, name=store.users[user_id]["name"])
        for user_id in sorted(store.meeting_attendees.get(meeting_id, set()), key=lambda attendee_id: store.users[attendee_id]["name"].lower())
    ]


def confirm_meeting_attendance(meeting_id: int, user_id: int) -> None:
    store.meeting_attendees.setdefault(meeting_id, set()).add(user_id)


def remove_meeting_attendance(meeting_id: int, user_id: int) -> None:
    attendees = store.meeting_attendees.setdefault(meeting_id, set())
    attendees.discard(user_id)


def create_meeting(
    club_id: int,
    title: str,
    scheduled_for: datetime,
    location: str,
    agenda: str,
    created_by: int,
    book_id: int | None = None,
) -> MeetingRecord:
    if book_id is not None:
        ensure_book_belongs_to_club(book_id, club_id)

    meeting: MeetingRecord = {
        "id": store.consume_meeting_id(),
        "club_id": club_id,
        "title": title,
        "scheduled_for": normalize_datetime(scheduled_for),
        "location": location,
        "agenda": agenda,
        "book_id": book_id,
        "created_by": created_by,
        "created_at": now_iso(),
    }
    store.meetings[meeting["id"]] = meeting
    return meeting


def update_meeting(
    meeting: MeetingRecord,
    title: str,
    scheduled_for: datetime,
    location: str,
    agenda: str,
    book_id: int | None = None,
) -> MeetingRecord:
    if book_id is not None:
        ensure_book_belongs_to_club(book_id, meeting["club_id"])

    meeting["title"] = title
    meeting["scheduled_for"] = normalize_datetime(scheduled_for)
    meeting["location"] = location
    meeting["agenda"] = agenda
    meeting["book_id"] = book_id
    return meeting


def delete_meeting(meeting: MeetingRecord) -> None:
    for comment_id in [comment_id for comment_id, comment in store.comments.items() if comment.get("meeting_id") == meeting["id"]]:
        del store.comments[comment_id]
    store.meeting_attendees.pop(meeting["id"], None)
    del store.meetings[meeting["id"]]


def list_club_meetings(club_id: int) -> list[MeetingPublic]:
    ordered_meetings = sorted(
        (meeting for meeting in store.meetings.values() if meeting["club_id"] == club_id),
        key=lambda item: item["scheduled_for"],
    )
    return [to_meeting_public(meeting) for meeting in ordered_meetings]


def list_book_meetings(book_id: int) -> list[MeetingPublic]:
    ordered_meetings = sorted(
        (meeting for meeting in store.meetings.values() if meeting.get("book_id") == book_id),
        key=lambda item: item["scheduled_for"],
    )
    return [to_meeting_public(meeting) for meeting in ordered_meetings]
