from pydantic import BaseModel, Field

from app.schemas.users import UserPublic


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=80)


class UserLogin(BaseModel):
    email: str = Field(min_length=5, max_length=120)
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
