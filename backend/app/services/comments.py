from fastapi import HTTPException, status

from app.core.time_utils import now_iso
from app.core.validation import validate_required_text
from app.db.memory import store
from app.models.entities import CommentRecord
from app.schemas.comments import CommentPublic


def to_comment_public(comment: CommentRecord) -> CommentPublic:
    return CommentPublic(
        **comment,
        user_name=store.users[comment["user_id"]]["name"],
    )


def create_comment(
    club_id: int,
    user_id: int,
    content: str,
    *,
    book_id: int | None = None,
    meeting_id: int | None = None,
) -> CommentRecord:
    if book_id is None and meeting_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comentario deve estar vinculado a um livro ou encontro.",
        )

    normalized_content = validate_required_text(content, "Comentario", min_length=2, max_length=500)
    comment: CommentRecord = {
        "id": store.consume_comment_id(),
        "club_id": club_id,
        "user_id": user_id,
        "content": normalized_content,
        "created_at": now_iso(),
        "book_id": book_id,
        "meeting_id": meeting_id,
    }
    store.comments[comment["id"]] = comment
    return comment


def count_meeting_comments(meeting_id: int) -> int:
    return sum(1 for comment in store.comments.values() if comment.get("meeting_id") == meeting_id)


def list_book_comments(book_id: int) -> list[CommentPublic]:
    ordered_comments = sorted(
        (comment for comment in store.comments.values() if comment.get("book_id") == book_id),
        key=lambda item: item["created_at"],
    )
    return [to_comment_public(comment) for comment in ordered_comments]


def list_meeting_comments(meeting_id: int) -> list[CommentPublic]:
    ordered_comments = sorted(
        (comment for comment in store.comments.values() if comment.get("meeting_id") == meeting_id),
        key=lambda item: item["created_at"],
    )
    return [to_comment_public(comment) for comment in ordered_comments]
