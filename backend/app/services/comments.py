from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.core.time_utils import now_utc, to_iso_datetime
from app.core.validation import validate_required_text
from app.db.models import Comment
from app.schemas.comments import CommentPublic


def to_comment_public(comment: Comment) -> CommentPublic:
    return CommentPublic(
        id=comment.id,
        club_id=comment.club_id,
        user_id=comment.user_id,
        user_name=comment.user.name,
        content=comment.content,
        created_at=to_iso_datetime(comment.created_at),
        book_id=comment.book_id,
        meeting_id=comment.meeting_id,
    )


def create_comment(
    db: Session,
    club_id: int,
    user_id: int,
    content: str,
    *,
    book_id: int | None = None,
    meeting_id: int | None = None,
) -> Comment:
    if book_id is None and meeting_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comentario deve estar vinculado a um livro ou encontro.",
        )

    normalized_content = validate_required_text(content, "Comentario", min_length=2, max_length=500)
    comment = Comment(
        club_id=club_id,
        user_id=user_id,
        content=normalized_content,
        created_at=now_utc(),
        book_id=book_id,
        meeting_id=meeting_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def count_meeting_comments(db: Session, meeting_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Comment).where(Comment.meeting_id == meeting_id)) or 0


def list_book_comments(db: Session, book_id: int) -> list[CommentPublic]:
    comments = db.scalars(select(Comment).where(Comment.book_id == book_id).order_by(Comment.created_at)).all()
    return [to_comment_public(comment) for comment in comments]


def list_meeting_comments(db: Session, meeting_id: int) -> list[CommentPublic]:
    comments = db.scalars(select(Comment).where(Comment.meeting_id == meeting_id).order_by(Comment.created_at)).all()
    return [to_comment_public(comment) for comment in comments]
