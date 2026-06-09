from pydantic import BaseModel, Field

from app.models.entities import ClubRole


class ClubCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=8, max_length=500)


class ClubPublic(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: str
    member_count: int
    current_user_role: ClubRole | None = None
    is_member: bool = False


class ClubMemberPublic(BaseModel):
    user_id: int
    name: str
    role: ClubRole
