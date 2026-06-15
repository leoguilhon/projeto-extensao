from dataclasses import dataclass, field

from app.models.entities import BookRecord, ClubRecord, ClubRole, CommentRecord, MeetingRecord, UserRecord


@dataclass
class MemoryStore:
    users: dict[int, UserRecord] = field(default_factory=dict)
    clubs: dict[int, ClubRecord] = field(default_factory=dict)
    club_members: dict[int, dict[int, ClubRole]] = field(default_factory=dict)
    books: dict[int, BookRecord] = field(default_factory=dict)
    meetings: dict[int, MeetingRecord] = field(default_factory=dict)
    comments: dict[int, CommentRecord] = field(default_factory=dict)
    favorite_clubs: dict[int, set[int]] = field(default_factory=dict)
    book_likes: dict[int, set[int]] = field(default_factory=dict)
    tokens: dict[str, int] = field(default_factory=dict)
    next_user_id: int = 1
    next_club_id: int = 1
    next_book_id: int = 1
    next_meeting_id: int = 1
    next_comment_id: int = 1

    def consume_user_id(self) -> int:
        current = self.next_user_id
        self.next_user_id += 1
        return current

    def consume_club_id(self) -> int:
        current = self.next_club_id
        self.next_club_id += 1
        return current

    def consume_book_id(self) -> int:
        current = self.next_book_id
        self.next_book_id += 1
        return current

    def consume_meeting_id(self) -> int:
        current = self.next_meeting_id
        self.next_meeting_id += 1
        return current

    def consume_comment_id(self) -> int:
        current = self.next_comment_id
        self.next_comment_id += 1
        return current


store = MemoryStore()
