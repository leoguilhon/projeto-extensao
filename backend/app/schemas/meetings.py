from datetime import datetime

from pydantic import BaseModel, Field


class MeetingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    scheduled_for: datetime
    location: str = Field(default="", max_length=120)
    agenda: str = Field(default="", max_length=500)
    book_id: int | None = None


class MeetingPublic(BaseModel):
    id: int
    club_id: int
    title: str
    scheduled_for: str
    location: str = ""
    agenda: str = ""
    book_id: int | None = None
    book_title: str | None = None
    created_by: int
    created_at: str
    comment_count: int = 0
