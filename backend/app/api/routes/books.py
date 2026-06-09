from fastapi import APIRouter, Depends, status

from app.api.dependencies import current_user, require_admin, require_member
from app.models.entities import UserRecord
from app.schemas.books import BookCreate, BookPublic, BookStatusUpdate, ReadingHistoryItem
from app.schemas.comments import CommentCreate, CommentPublic
from app.schemas.meetings import MeetingPublic
from app.services.books import (
    create_book,
    get_book_or_404,
    list_books_by_club,
    list_reading_history,
    to_book_public,
    update_book_status,
)
from app.services.clubs import get_club_or_404
from app.services.comments import create_comment, list_book_comments, to_comment_public
from app.services.meetings import list_book_meetings


router = APIRouter(tags=["books"])


@router.get("/clubs/{club_id}/books", response_model=list[BookPublic])
def get_club_books(club_id: int, user: UserRecord = Depends(current_user)):
    get_club_or_404(club_id)
    require_member(club_id, user)
    return list_books_by_club(club_id)


@router.post("/clubs/{club_id}/books", response_model=BookPublic, status_code=status.HTTP_201_CREATED)
def add_club_book(payload: BookCreate, club_id: int, user: UserRecord = Depends(current_user)):
    get_club_or_404(club_id)
    require_admin(club_id, user)
    book = create_book(club_id, payload.title, payload.author, payload.description, payload.status, user["id"])
    return to_book_public(book)


@router.get("/books/{book_id}", response_model=BookPublic)
def get_book(book_id: int, user: UserRecord = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    return to_book_public(book)


@router.patch("/books/{book_id}/status", response_model=BookPublic)
def patch_book_status(book_id: int, payload: BookStatusUpdate, user: UserRecord = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_admin(book["club_id"], user)
    updated_book = update_book_status(book, payload.status)
    return to_book_public(updated_book)


@router.get("/books/{book_id}/comments", response_model=list[CommentPublic])
def get_book_comments(book_id: int, user: UserRecord = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    return list_book_comments(book_id)


@router.post("/books/{book_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
def add_book_comment(book_id: int, payload: CommentCreate, user: UserRecord = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    comment = create_comment(book["club_id"], user["id"], payload.content, book_id=book_id)
    return to_comment_public(comment)


@router.get("/books/{book_id}/meetings", response_model=list[MeetingPublic])
def get_book_meetings(book_id: int, user: UserRecord = Depends(current_user)):
    book = get_book_or_404(book_id)
    require_member(book["club_id"], user)
    return list_book_meetings(book_id)


@router.get("/clubs/{club_id}/reading-history", response_model=list[ReadingHistoryItem])
def get_reading_history(club_id: int, user: UserRecord = Depends(current_user)):
    get_club_or_404(club_id)
    require_member(club_id, user)
    return list_reading_history(club_id)
