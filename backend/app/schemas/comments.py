from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=2, max_length=500)


class CommentPublic(BaseModel):
    id: int
    club_id: int
    user_id: int
    user_name: str
    content: str
    created_at: str
    book_id: int | None = None
    meeting_id: int | None = None
