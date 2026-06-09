from fastapi import HTTPException, status

from app.core.time_utils import now_iso
from app.db.memory import store
from app.models.entities import BookRecord, ReadingStatus
from app.schemas.books import BookPublic, ReadingHistoryItem
from app.services.clubs import get_club_or_404


def to_book_public(book: BookRecord) -> BookPublic:
    return BookPublic(**book)


def get_book_or_404(book_id: int) -> BookRecord:
    book = store.books.get(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    return book


def ensure_book_belongs_to_club(book_id: int, club_id: int) -> BookRecord:
    book = get_book_or_404(book_id)
    if book["club_id"] != club_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O livro informado não pertence a este clube.",
        )
    return book


def ensure_single_current_book(club_id: int, active_book_id: int) -> None:
    for book in store.books.values():
        if book["club_id"] == club_id and book["id"] != active_book_id and book["status"] == "em_leitura":
            book["status"] = "planejado"
            book["finished_at"] = None


def sorted_club_books(club_id: int) -> list[BookRecord]:
    status_order = {"em_leitura": 0, "planejado": 1, "concluido": 2}
    return sorted(
        (book for book in store.books.values() if book["club_id"] == club_id),
        key=lambda item: (status_order[item["status"]], item["created_at"]),
    )


def create_book(club_id: int, title: str, author: str, description: str, status_value: ReadingStatus, added_by: int) -> BookRecord:
    book: BookRecord = {
        "id": store.consume_book_id(),
        "club_id": club_id,
        "title": title,
        "author": author,
        "description": description,
        "status": status_value,
        "added_by": added_by,
        "created_at": now_iso(),
        "finished_at": now_iso() if status_value == "concluido" else None,
    }
    store.books[book["id"]] = book
    if status_value == "em_leitura":
        ensure_single_current_book(club_id, book["id"])
    return book


def update_book_status(book: BookRecord, status_value: ReadingStatus) -> BookRecord:
    book["status"] = status_value
    book["finished_at"] = now_iso() if status_value == "concluido" else None
    if status_value == "em_leitura":
        ensure_single_current_book(book["club_id"], book["id"])
    return book


def list_books_by_club(club_id: int) -> list[BookPublic]:
    return [to_book_public(book) for book in sorted_club_books(club_id)]


def list_reading_history(club_id: int) -> list[ReadingHistoryItem]:
    club = get_club_or_404(club_id)
    return [
        ReadingHistoryItem(
            club_id=club_id,
            club_name=club["name"],
            book_id=book["id"],
            title=book["title"],
            author=book["author"],
            finished_at=book["finished_at"],
        )
        for book in sorted_club_books(club_id)
        if book["status"] == "concluido" and book["finished_at"]
    ]
