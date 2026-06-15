import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import event, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine

from app.core.security import legacy_hash_password
from app.db.models import Base, Book, Club, Comment, Meeting, User
from app.services.auth import get_user_by_token, issue_token, register_user
from app.services.books import create_book
from app.services.clubs import create_club, delete_club
from app.services.comments import create_comment
from app.services.meetings import create_meeting
from app.services.seed import seed_data
from app.services.users import authenticate_user, find_user_by_email


class ServiceLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        @event.listens_for(self.engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)
        self.db = self.SessionLocal()
        seed_data(self.db)

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_seed_data_is_idempotent(self) -> None:
        first_user_count = self.db.scalar(select(func.count()).select_from(User))
        first_club_count = self.db.scalar(select(func.count()).select_from(Club))

        seed_data(self.db)

        self.assertEqual(self.db.scalar(select(func.count()).select_from(User)), first_user_count)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Club)), first_club_count)

    def test_register_user_normalizes_fields_and_hashes_password(self) -> None:
        response = register_user(self.db, "  Maria   Clara  ", "  MARIA@example.com  ", "123456")
        user = find_user_by_email(self.db, "maria@example.com")

        self.assertIsNotNone(user)
        self.assertEqual(response.user.email, "maria@example.com")
        self.assertEqual(user.name, "Maria Clara")
        self.assertEqual(user.email, "maria@example.com")
        self.assertTrue(user.password_hash.startswith("pbkdf2_sha256$"))

    def test_authenticate_user_rehashes_legacy_passwords(self) -> None:
        user = find_user_by_email(self.db, "ana@lendojuntos.test")
        assert user is not None
        user.password_hash = legacy_hash_password("123456")
        self.db.commit()

        authenticated = authenticate_user(self.db, "ana@lendojuntos.test", "123456")

        self.assertIsNotNone(authenticated)
        self.assertTrue(user.password_hash.startswith("pbkdf2_sha256$"))

    def test_token_expires_when_issue_time_is_past_deadline(self) -> None:
        user = find_user_by_email(self.db, "ana@lendojuntos.test")
        assert user is not None

        with patch("app.services.auth.ACCESS_TOKEN_EXPIRE_MINUTES", -1):
            token = issue_token(self.db, user.id)

        self.assertIsNone(get_user_by_token(self.db, token))

    def test_comment_rejects_only_whitespace_content(self) -> None:
        with self.assertRaises(HTTPException) as context:
            create_comment(self.db, 1, 1, "     ", book_id=1)

        self.assertEqual(context.exception.status_code, 422)

    def test_only_one_book_stays_in_reading_status_per_club(self) -> None:
        club = self.db.get(Club, 1)
        assert club is not None

        new_current_book = create_book(
            self.db,
            club.id,
            "Duna",
            "Frank Herbert",
            "Leitura para o proximo ciclo.",
            "em_leitura",
            club.owner_id,
        )

        current_books = self.db.scalars(select(Book).where(Book.club_id == club.id, Book.status == "em_leitura")).all()

        self.assertEqual(len(current_books), 1)
        self.assertEqual(current_books[0].id, new_current_book.id)

    def test_meeting_rejects_book_from_another_club(self) -> None:
        owner = register_user(self.db, "Pedro", "pedro@example.com", "123456").user
        second_club = create_club(self.db, "Clube paralelo", "Descricao valida para outro grupo.", owner.id)

        with self.assertRaises(HTTPException) as context:
            create_meeting(
                self.db,
                second_club.id,
                "Encontro invalido",
                datetime.now(timezone.utc),
                "Sala virtual",
                "Discussao da leitura.",
                owner.id,
                book_id=1,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_delete_club_removes_related_records(self) -> None:
        club = self.db.get(Club, 1)
        assert club is not None

        delete_club(self.db, club.id, club.owner_id)

        self.assertEqual(self.db.scalar(select(func.count()).select_from(Club)), 0)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Book)), 0)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Meeting)), 0)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(Comment)), 0)


if __name__ == "__main__":
    unittest.main()
