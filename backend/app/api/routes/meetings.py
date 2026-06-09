from fastapi import APIRouter, Depends, status

from app.api.dependencies import current_user, require_admin, require_member
from app.models.entities import UserRecord
from app.schemas.comments import CommentCreate, CommentPublic
from app.schemas.meetings import MeetingCreate, MeetingPublic
from app.services.clubs import get_club_or_404
from app.services.comments import create_comment, list_meeting_comments, to_comment_public
from app.services.meetings import create_meeting, get_meeting_or_404, list_club_meetings, to_meeting_public


router = APIRouter(tags=["meetings"])


@router.get("/clubs/{club_id}/meetings", response_model=list[MeetingPublic])
def get_club_meetings(club_id: int, user: UserRecord = Depends(current_user)):
    get_club_or_404(club_id)
    require_member(club_id, user)
    return list_club_meetings(club_id)


@router.post("/clubs/{club_id}/meetings", response_model=MeetingPublic, status_code=status.HTTP_201_CREATED)
def add_club_meeting(payload: MeetingCreate, club_id: int, user: UserRecord = Depends(current_user)):
    get_club_or_404(club_id)
    require_admin(club_id, user)
    meeting = create_meeting(
        club_id,
        payload.title,
        payload.scheduled_for,
        payload.location,
        payload.agenda,
        user["id"],
        payload.book_id,
    )
    return to_meeting_public(meeting)


@router.get("/meetings/{meeting_id}/comments", response_model=list[CommentPublic])
def get_meeting_comments(meeting_id: int, user: UserRecord = Depends(current_user)):
    meeting = get_meeting_or_404(meeting_id)
    require_member(meeting["club_id"], user)
    return list_meeting_comments(meeting_id)


@router.post("/meetings/{meeting_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
def add_comment_to_meeting(meeting_id: int, payload: CommentCreate, user: UserRecord = Depends(current_user)):
    meeting = get_meeting_or_404(meeting_id)
    require_member(meeting["club_id"], user)
    comment = create_comment(meeting["club_id"], user["id"], payload.content, meeting_id=meeting_id)
    return to_comment_public(comment)
