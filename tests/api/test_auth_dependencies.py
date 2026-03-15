import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from backend.api.auth_dependencies import get_current_user, require_roles
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE
from backend.core.security import create_access_token


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        return self.result


class AuthDependenciesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_get_current_user_returns_user_for_valid_token(self):
        user = type("User", (), {"id": 1, "role": ADMIN_ROLE})()
        token = create_access_token(user_id=1, role=ADMIN_ROLE, username="admin")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        mediator = FakeMediator(user)

        with patch("backend.api.auth_dependencies.build_mediator", return_value=mediator):
            result = await get_current_user(credentials=credentials, db=object())

        self.assertIs(result, user)
        self.assertEqual(mediator.requests[0].user_id, 1)

    async def test_get_current_user_rejects_missing_credentials(self):
        with self.assertRaises(HTTPException) as context:
            await get_current_user(credentials=None, db=object())

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(
            context.exception.detail,
            "Authentication credentials were not provided",
        )

    async def test_get_current_user_rejects_role_mismatch(self):
        user = type("User", (), {"id": 1, "role": BARBER_ROLE})()
        token = create_access_token(user_id=1, role=ADMIN_ROLE, username="admin")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        mediator = FakeMediator(user)

        with patch("backend.api.auth_dependencies.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await get_current_user(credentials=credentials, db=object())

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid authentication credentials")

    async def test_require_roles_rejects_insufficient_permissions(self):
        dependency = require_roles(ADMIN_ROLE)
        user = type("User", (), {"role": BARBER_ROLE})()

        with self.assertRaises(HTTPException) as context:
            await dependency(current_user=user)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail, "Not enough permissions")


if __name__ == "__main__":
    unittest.main()
