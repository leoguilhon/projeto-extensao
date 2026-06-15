from app.core.security import hash_password, needs_password_rehash, verify_password
from app.core.validation import normalize_email, validate_optional_text, validate_required_text
from app.db.memory import store
from app.models.entities import UserRecord
from app.schemas.users import UserPublic


def to_user_public(user: UserRecord) -> UserPublic:
    return UserPublic(id=user["id"], name=user["name"], email=user["email"], bio=user.get("bio", ""))


def get_user_or_none(user_id: int) -> UserRecord | None:
    return store.users.get(user_id)


def find_user_by_email(email: str) -> UserRecord | None:
    normalized_email = email.strip().lower()
    return next((item for item in store.users.values() if item["email"] == normalized_email), None)


def email_exists(email: str) -> bool:
    return find_user_by_email(email) is not None


def create_user(name: str, email: str, password: str, bio: str = "") -> UserRecord:
    normalized_name = validate_required_text(name, "Nome", min_length=2, max_length=80)
    normalized_email = normalize_email(email)
    normalized_bio = validate_optional_text(bio, "Bio", max_length=240)
    user: UserRecord = {
        "id": store.consume_user_id(),
        "name": normalized_name,
        "email": normalized_email,
        "password_hash": hash_password(password),
        "bio": normalized_bio,
    }
    store.users[user["id"]] = user
    return user


def authenticate_user(email: str, password: str) -> UserRecord | None:
    user = find_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    if needs_password_rehash(user["password_hash"]):
        user["password_hash"] = hash_password(password)
    return user


def update_user_profile(user: UserRecord, name: str, bio: str) -> UserRecord:
    user["name"] = validate_required_text(name, "Nome", min_length=2, max_length=80)
    user["bio"] = validate_optional_text(bio, "Bio", max_length=240)
    return user
