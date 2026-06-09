from typing import Literal, TypedDict


ReadingStatus = Literal["planejado", "em_leitura", "concluido"]
ClubRole = Literal["admin", "membro"]


class UserRecord(TypedDict):
    id: int
    name: str
    email: str
    password_hash: str
    bio: str


class ClubRecord(TypedDict):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: str


class BookRecord(TypedDict):
    id: int
    club_id: int
    title: str
    author: str
    description: str
    status: ReadingStatus
    added_by: int
    created_at: str
    finished_at: str | None


class MeetingRecord(TypedDict):
    id: int
    club_id: int
    title: str
    scheduled_for: str
    location: str
    agenda: str
    book_id: int | None
    created_by: int
    created_at: str


class CommentRecord(TypedDict):
    id: int
    club_id: int
    user_id: int
    content: str
    created_at: str
    book_id: int | None
    meeting_id: int | None
