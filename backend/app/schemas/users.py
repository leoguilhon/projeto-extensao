from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    bio: str = ""


class UserUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    bio: str = Field(default="", max_length=240)
