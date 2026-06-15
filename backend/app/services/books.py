from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.core.time_utils import now_utc, to_iso_datetime
from app.core.validation import validate_optional_text, validate_required_text
from app.db.models import Book, BookLike
from app.models.entities import ReadingStatus
from app.schemas.books import BookPublic, ReadingHistoryItem
from app.services.clubs import get_club_or_404


def _status_order_value(status_value: str) -> int:
    return {"em_leitura": 0, "planejado": 1, "concluido": 2}.get(status_value, 99)


def to_book_public(db: Session, book: Book, current_user_id: int | None = None) -> BookPublic:
    like_count = db.scalar(select(func.count()).select_from(BookLike).where(BookLike.book_id == book.id)) or 0
    liked_by_current_user = False
    if current_user_id is not None:
        liked_by_current_user = db.get(BookLike, {"book_id": book.id, "user_id": current_user_id}) is not None

    return BookPublic(
        id=book.id,
        club_id=book.club_id,
        title=book.title,
        author=book.author,
        description=book.description,
        status=book.status,
        added_by=book.added_by,
        created_at=to_iso_datetime(book.created_at),
        finished_at=to_iso_datetime(book.finished_at),
        like_count=like_count,
        liked_by_current_user=liked_by_current_user,
    )


def get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro nao encontrado.")
    return book


def ensure_book_belongs_to_club(db: Session, book_id: int, club_id: int) -> Book:
    book = get_book_or_404(db, book_id)
    if book.club_id != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O livro informado nao pertence a este clube.",
        )
    return book


def ensure_single_current_book(db: Session, club_id: int, active_book_id: int) -> None:
    books = db.scalars(select(Book).where(Book.club_id == club_id, Book.id != active_book_id, Book.status == "em_leitura")).all()
    for book in books:
        book.status = "planejado"
        book.finished_at = None


def sorted_club_books(db: Session, club_id: int) -> list[Book]:
    books = db.scalars(select(Book).where(Book.club_id == club_id)).all()
    return sorted(books, key=lambda item: (_status_order_value(item.status), item.created_at))


def create_book(
    db: Session,
    club_id: int,
    title: str,
    author: str,
    description: str,
    status_value: ReadingStatus,
    added_by: int,
) -> Book:
    normalized_title = validate_required_text(title, "Titulo do livro", min_length=2, max_length=120)
    normalized_author = validate_required_text(author, "Autor", min_length=2, max_length=100)
    normalized_description = validate_optional_text(description, "Descricao do livro", max_length=500)

    book = Book(
        club_id=club_id,
        title=normalized_title,
        author=normalized_author,
        description=normalized_description,
        status=status_value,
        added_by=added_by,
        created_at=now_utc(),
        finished_at=now_utc() if status_value == "concluido" else None,
    )
    db.add(book)
    db.flush()
    if status_value == "em_leitura":
        ensure_single_current_book(db, club_id, book.id)
    db.commit()
    db.refresh(book)
    return book


def update_book_status(db: Session, book: Book, status_value: ReadingStatus) -> Book:
    book.status = status_value
    book.finished_at = now_utc() if status_value == "concluido" else None
    if status_value == "em_leitura":
        ensure_single_current_book(db, book.club_id, book.id)
    db.commit()
    db.refresh(book)
    return book


def like_book(db: Session, book: Book, user_id: int) -> Book:
    if not db.get(BookLike, {"book_id": book.id, "user_id": user_id}):
        db.add(BookLike(book_id=book.id, user_id=user_id))
        db.commit()
    return book


def unlike_book(db: Session, book: Book, user_id: int) -> Book:
    like = db.get(BookLike, {"book_id": book.id, "user_id": user_id})
    if like:
        db.delete(like)
        db.commit()
    return book


def list_books_by_club(db: Session, club_id: int, current_user_id: int | None = None) -> list[BookPublic]:
    return [to_book_public(db, book, current_user_id) for book in sorted_club_books(db, club_id)]


def list_reading_history(db: Session, club_id: int) -> list[ReadingHistoryItem]:
    club = get_club_or_404(db, club_id)
    return [
        ReadingHistoryItem(
            club_id=club_id,
            club_name=club.name,
            book_id=book.id,
            title=book.title,
            author=book.author,
            finished_at=to_iso_datetime(book.finished_at),
        )
        for book in sorted_club_books(db, club_id)
        if book.status == "concluido" and book.finished_at
    ]
