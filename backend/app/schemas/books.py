from pydantic import BaseModel, Field

from app.models.entities import ReadingStatus


class BookCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    author: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    status: ReadingStatus = "planejado"


class BookStatusUpdate(BaseModel):
    status: ReadingStatus


class BookPublic(BaseModel):
    id: int
    club_id: int
    title: str
    author: str
    description: str = ""
    status: ReadingStatus
    added_by: int
    created_at: str
    finished_at: str | None = None
    like_count: int = 0
    liked_by_current_user: bool = False


class ReadingHistoryItem(BaseModel):
    club_id: int
    club_name: str
    book_id: int
    title: str
    author: str
    finished_at: str
