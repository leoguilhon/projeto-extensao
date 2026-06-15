import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import HTTPException

from app.core.security import legacy_hash_password
from app.db.memory import store
from app.services.auth import get_user_by_token, issue_token, register_user
from app.services.books import create_book
from app.services.clubs import create_club, delete_club
from app.services.comments import create_comment
from app.services.meetings import create_meeting
from app.services.seed import seed_data
from app.services.users import authenticate_user, find_user_by_email


class ServiceLayerTests(unittest.TestCase):
    def setUp(self) -> None:
        store.reset()
        seed_data()

    def test_seed_data_is_idempotent(self) -> None:
        first_user_count = len(store.users)
        first_club_count = len(store.clubs)

        seed_data()

        self.assertEqual(len(store.users), first_user_count)
        self.assertEqual(len(store.clubs), first_club_count)

    def test_register_user_normalizes_fields_and_hashes_password(self) -> None:
        response = register_user("  Maria   Clara  ", "  MARIA@example.com  ", "123456")
        user = find_user_by_email("maria@example.com")

        self.assertIsNotNone(user)
        self.assertEqual(response.user.email, "maria@example.com")
        self.assertEqual(user["name"], "Maria Clara")
        self.assertEqual(user["email"], "maria@example.com")
        self.assertTrue(user["password_hash"].startswith("pbkdf2_sha256$"))

    def test_authenticate_user_rehashes_legacy_passwords(self) -> None:
        user = find_user_by_email("ana@lendojuntos.test")
        assert user is not None
        user["password_hash"] = legacy_hash_password("123456")

        authenticated = authenticate_user("ana@lendojuntos.test", "123456")

        self.assertIsNotNone(authenticated)
        self.assertTrue(user["password_hash"].startswith("pbkdf2_sha256$"))

    def test_token_expires_when_issue_time_is_past_deadline(self) -> None:
        user = find_user_by_email("ana@lendojuntos.test")
        assert user is not None

        with patch("app.services.auth.ACCESS_TOKEN_EXPIRE_MINUTES", -1):
            token = issue_token(user["id"])

        self.assertIsNone(get_user_by_token(token))

    def test_comment_rejects_only_whitespace_content(self) -> None:
        with self.assertRaises(HTTPException) as context:
            create_comment(1, 1, "     ", book_id=1)

        self.assertEqual(context.exception.status_code, 422)

    def test_only_one_book_stays_in_reading_status_per_club(self) -> None:
        club = store.clubs[1]
        new_current_book = create_book(
            club["id"],
            "Duna",
            "Frank Herbert",
            "Leitura para o proximo ciclo.",
            "em_leitura",
            club["owner_id"],
        )

        current_books = [
            book
            for book in store.books.values()
            if book["club_id"] == club["id"] and book["status"] == "em_leitura"
        ]

        self.assertEqual(len(current_books), 1)
        self.assertEqual(current_books[0]["id"], new_current_book["id"])

    def test_meeting_rejects_book_from_another_club(self) -> None:
        owner = register_user("Pedro", "pedro@example.com", "123456").user
        second_club = create_club("Clube paralelo", "Descricao valida para outro grupo.", owner.id)

        with self.assertRaises(HTTPException) as context:
            create_meeting(
                second_club["id"],
                "Encontro invalido",
                datetime.now(timezone.utc),
                "Sala virtual",
                "Discussao da leitura.",
                owner.id,
                book_id=1,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_delete_club_removes_related_records(self) -> None:
        club = store.clubs[1]

        delete_club(club["id"], club["owner_id"])

        self.assertFalse(store.clubs)
        self.assertFalse(store.club_members)
        self.assertFalse(store.books)
        self.assertFalse(store.meetings)
        self.assertFalse(store.comments)
        self.assertFalse(store.meeting_attendees)


if __name__ == "__main__":
    unittest.main()
