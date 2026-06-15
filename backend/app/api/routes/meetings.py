from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import current_user, require_admin, require_member
from app.db.models import User
from app.db.session import get_db
from app.schemas.comments import CommentCreate, CommentPublic
from app.schemas.meetings import MeetingAttendeePublic, MeetingCreate, MeetingPublic, MeetingUpdate
from app.services.clubs import get_club_or_404
from app.services.comments import create_comment, list_meeting_comments, to_comment_public
from app.services.meetings import (
    confirm_meeting_attendance,
    create_meeting,
    delete_meeting,
    get_meeting_or_404,
    list_club_meetings,
    list_meeting_attendees,
    remove_meeting_attendance,
    to_meeting_public,
    update_meeting,
)


router = APIRouter(tags=["meetings"])


@router.get("/clubs/{club_id}/meetings", response_model=list[MeetingPublic])
def get_club_meetings(club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_club_or_404(db, club_id)
    require_member(club_id, user, db)
    return list_club_meetings(db, club_id)


@router.get("/meetings/{meeting_id}", response_model=MeetingPublic)
def get_meeting(meeting_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    require_member(meeting.club_id, user, db)
    return to_meeting_public(db, meeting)


@router.get("/meetings/{meeting_id}/attendees", response_model=list[MeetingAttendeePublic])
def get_meeting_attendees(meeting_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    require_member(meeting.club_id, user, db)
    return list_meeting_attendees(db, meeting_id)


@router.post("/clubs/{club_id}/meetings", response_model=MeetingPublic, status_code=status.HTTP_201_CREATED)
def add_club_meeting(payload: MeetingCreate, club_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    get_club_or_404(db, club_id)
    require_admin(club_id, user, db)
    meeting = create_meeting(
        db,
        club_id,
        payload.title,
        payload.scheduled_for,
        payload.location,
        payload.agenda,
        user.id,
        payload.book_id,
    )
    return to_meeting_public(db, meeting)


@router.put("/meetings/{meeting_id}", response_model=MeetingPublic)
def edit_meeting(
    meeting_id: int,
    payload: MeetingUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    meeting = get_meeting_or_404(db, meeting_id)
    require_admin(meeting.club_id, user, db)
    updated_meeting = update_meeting(
        db,
        meeting,
        payload.title,
        payload.scheduled_for,
        payload.location,
        payload.agenda,
        payload.book_id,
    )
    return to_meeting_public(db, updated_meeting)


@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_meeting(meeting_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    require_admin(meeting.club_id, user, db)
    delete_meeting(db, meeting)


@router.get("/meetings/{meeting_id}/comments", response_model=list[CommentPublic])
def get_meeting_comments(meeting_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    require_member(meeting.club_id, user, db)
    return list_meeting_comments(db, meeting_id)


@router.post("/meetings/{meeting_id}/comments", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
def add_comment_to_meeting(
    meeting_id: int,
    payload: CommentCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    meeting = get_meeting_or_404(db, meeting_id)
    require_member(meeting.club_id, user, db)
    comment = create_comment(db, meeting.club_id, user.id, payload.content, meeting_id=meeting_id)
    return to_comment_public(comment)


@router.post("/meetings/{meeting_id}/attendance", response_model=list[MeetingAttendeePublic])
def confirm_attendance(meeting_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    require_member(meeting.club_id, user, db)
    confirm_meeting_attendance(db, meeting_id, user.id)
    return list_meeting_attendees(db, meeting_id)


@router.delete("/meetings/{meeting_id}/attendance", response_model=list[MeetingAttendeePublic])
def remove_attendance(meeting_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    require_member(meeting.club_id, user, db)
    remove_meeting_attendance(db, meeting_id, user.id)
    return list_meeting_attendees(db, meeting_id)
