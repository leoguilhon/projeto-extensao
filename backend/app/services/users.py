from app.core.security import hash_password
from app.db.memory import store
from app.models.entities import UserRecord
from app.schemas.users import UserPublic


def to_user_public(user: UserRecord) -> UserPublic:
    return UserPublic(id=user["id"], name=user["name"], email=user["email"], bio=user.get("bio", ""))


def get_user_or_none(user_id: int) -> UserRecord | None:
    return store.users.get(user_id)


def find_user_by_email(email: str) -> UserRecord | None:
    normalized_email = email.lower()
    return next((item for item in store.users.values() if item["email"] == normalized_email), None)


def email_exists(email: str) -> bool:
    return find_user_by_email(email) is not None


def create_user(name: str, email: str, password: str, bio: str = "") -> UserRecord:
    user: UserRecord = {
        "id": store.consume_user_id(),
        "name": name,
        "email": email.lower(),
        "password_hash": hash_password(password),
        "bio": bio,
    }
    store.users[user["id"]] = user
    return user


def authenticate_user(email: str, password: str) -> UserRecord | None:
    user = find_user_by_email(email)
    if not user or user["password_hash"] != hash_password(password):
        return None
    return user


def update_user_profile(user: UserRecord, name: str, bio: str) -> UserRecord:
    user["name"] = name
    user["bio"] = bio
    return user
