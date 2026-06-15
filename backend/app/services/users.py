from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, needs_password_rehash, verify_password
from app.core.validation import normalize_email, validate_optional_text, validate_required_text
from app.db.models import User
from app.schemas.users import UserPublic


def to_user_public(user: User) -> UserPublic:
    return UserPublic(id=user.id, name=user.name, email=user.email, bio=user.bio or "")


def get_user_or_none(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def find_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = email.strip().lower()
    return db.scalar(select(User).where(User.email == normalized_email))


def email_exists(db: Session, email: str) -> bool:
    return find_user_by_email(db, email) is not None


def create_user(db: Session, name: str, email: str, password: str, bio: str = "") -> User:
    normalized_name = validate_required_text(name, "Nome", min_length=2, max_length=80)
    normalized_email = normalize_email(email)
    normalized_bio = validate_optional_text(bio, "Bio", max_length=240)

    user = User(
        name=normalized_name,
        email=normalized_email,
        password_hash=hash_password(password),
        bio=normalized_bio,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = find_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None

    if needs_password_rehash(user.password_hash):
        user.password_hash = hash_password(password)
        db.commit()
        db.refresh(user)

    return user


def update_user_profile(db: Session, user: User, name: str, bio: str) -> User:
    user.name = validate_required_text(name, "Nome", min_length=2, max_length=80)
    user.bio = validate_optional_text(bio, "Bio", max_length=240)
    db.commit()
    db.refresh(user)
    return user
