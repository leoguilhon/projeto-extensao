from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str] = mapped_column(String(240), nullable=False, default="")

    memberships: Mapped[list[ClubMembership]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorite_links: Mapped[list[FavoriteClub]] = relationship(back_populates="user", cascade="all, delete-orphan")
    book_like_links: Mapped[list[BookLike]] = relationship(back_populates="user", cascade="all, delete-orphan")
    meeting_attendance_links: Mapped[list[MeetingAttendance]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list[Comment]] = relationship(back_populates="user", cascade="all, delete-orphan")
    auth_tokens: Mapped[list[AuthToken]] = relationship(back_populates="user", cascade="all, delete-orphan")
    owned_clubs: Mapped[list[Club]] = relationship(back_populates="owner", foreign_keys="Club.owner_id")
    added_books: Mapped[list[Book]] = relationship(back_populates="added_by_user", foreign_keys="Book.added_by")
    created_meetings: Mapped[list[Meeting]] = relationship(
        back_populates="created_by_user",
        foreign_keys="Meeting.created_by",
    )


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    owner: Mapped[User] = relationship(back_populates="owned_clubs", foreign_keys=[owner_id])
    memberships: Mapped[list[ClubMembership]] = relationship(back_populates="club", cascade="all, delete-orphan")
    favorite_links: Mapped[list[FavoriteClub]] = relationship(back_populates="club", cascade="all, delete-orphan")
    books: Mapped[list[Book]] = relationship(back_populates="club", cascade="all, delete-orphan")
    meetings: Mapped[list[Meeting]] = relationship(back_populates="club", cascade="all, delete-orphan")


class ClubMembership(Base):
    __tablename__ = "club_memberships"

    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    club: Mapped[Club] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="memberships")


class FavoriteClub(Base):
    __tablename__ = "favorite_clubs"

    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    club: Mapped[Club] = relationship(back_populates="favorite_links")
    user: Mapped[User] = relationship(back_populates="favorite_links")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    added_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    club: Mapped[Club] = relationship(back_populates="books")
    added_by_user: Mapped[User] = relationship(back_populates="added_books", foreign_keys=[added_by])
    meetings: Mapped[list[Meeting]] = relationship(back_populates="book")
    comments: Mapped[list[Comment]] = relationship(back_populates="book", cascade="all, delete-orphan")
    like_links: Mapped[list[BookLike]] = relationship(back_populates="book", cascade="all, delete-orphan")


class BookLike(Base):
    __tablename__ = "book_likes"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    book: Mapped[Book] = relationship(back_populates="like_links")
    user: Mapped[User] = relationship(back_populates="book_like_links")


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    agenda: Mapped[str] = mapped_column(Text, nullable=False, default="")
    book_id: Mapped[int | None] = mapped_column(ForeignKey("books.id", ondelete="SET NULL"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    club: Mapped[Club] = relationship(back_populates="meetings")
    book: Mapped[Book | None] = relationship(back_populates="meetings")
    created_by_user: Mapped[User] = relationship(back_populates="created_meetings", foreign_keys=[created_by])
    comments: Mapped[list[Comment]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    attendance_links: Mapped[list[MeetingAttendance]] = relationship(
        back_populates="meeting",
        cascade="all, delete-orphan",
    )


class MeetingAttendance(Base):
    __tablename__ = "meeting_attendances"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    meeting: Mapped[Meeting] = relationship(back_populates="attendance_links")
    user: Mapped[User] = relationship(back_populates="meeting_attendance_links")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    book_id: Mapped[int | None] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    meeting_id: Mapped[int | None] = mapped_column(ForeignKey("meetings.id", ondelete="CASCADE"), nullable=True)

    user: Mapped[User] = relationship(back_populates="comments")
    book: Mapped[Book | None] = relationship(back_populates="comments")
    meeting: Mapped[Meeting | None] = relationship(back_populates="comments")


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    token: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="auth_tokens")
