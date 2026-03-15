import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.core.exceptions import AuthenticationError
from backend.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class SecurityTestCase(unittest.TestCase):

    def test_hash_password_and_verify_password_roundtrip(self):
        password_hash = hash_password("password123")

        self.assertNotEqual(password_hash, "password123")
        self.assertTrue(verify_password("password123", password_hash))
        self.assertFalse(verify_password("wrongpass", password_hash))

    def test_create_and_decode_access_token_roundtrip(self):
        token = create_access_token(user_id=1, role="admin", username="admin")

        payload = decode_access_token(token)

        self.assertEqual(payload["sub"], 1)
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["username"], "admin")

    def test_decode_access_token_rejects_invalid_signature(self):
        token = create_access_token(user_id=1, role="admin", username="admin")
        tampered_token = f"{token}tampered"

        with self.assertRaises(AuthenticationError) as context:
            decode_access_token(tampered_token)

        self.assertEqual(str(context.exception), "Invalid authentication credentials")

    def test_decode_access_token_rejects_expired_token(self):
        with patch("backend.core.security.get_auth_token_ttl_seconds", return_value=-1):
            token = create_access_token(user_id=1, role="admin", username="admin")

        with self.assertRaises(AuthenticationError) as context:
            decode_access_token(token)

        self.assertEqual(str(context.exception), "Token has expired")


if __name__ == "__main__":
    unittest.main()
