import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.routes.auth_routes import (
    bootstrap_admin,
    create_user,
    get_me,
    login,
    register_barber,
)
from backend.core.exceptions import AuthenticationError, ConflictError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE
from backend.infrastructure.schemas import (
    AuthLoginRequest,
    BarberRegisterRequest,
    BootstrapAdminRequest,
    UserCreateRequest,
)


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class AuthRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_bootstrap_admin_returns_created_user(self):
        user = {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": ADMIN_ROLE,
        }
        mediator = FakeMediator(user)

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            result = await bootstrap_admin(
                BootstrapAdminRequest(
                    username="admin",
                    email="admin@example.com",
                    password="password123",
                ),
                db=object(),
            )

        self.assertEqual(result["role"], ADMIN_ROLE)
        self.assertEqual(mediator.requests[0].username, "admin")

    async def test_bootstrap_admin_maps_conflict_to_409(self):
        mediator = FakeMediator(ConflictError("Admin bootstrap has already been completed"))

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await bootstrap_admin(
                    BootstrapAdminRequest(
                        username="admin",
                        email="admin@example.com",
                        password="password123",
                    ),
                    db=object(),
                )

        self.assertEqual(context.exception.status_code, 409)

    async def test_login_returns_token_payload(self):
        auth_payload = {
            "access_token": "token",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "role": ADMIN_ROLE,
            },
        }
        mediator = FakeMediator(auth_payload)

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            result = await login(
                AuthLoginRequest(username="admin", password="password123"),
                db=object(),
            )

        self.assertEqual(result["token_type"], "bearer")
        self.assertEqual(mediator.requests[0].username, "admin")

    async def test_login_maps_authentication_error_to_401(self):
        mediator = FakeMediator(AuthenticationError("Invalid credentials"))

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await login(
                    AuthLoginRequest(username="admin", password="password123"),
                    db=object(),
                )

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid credentials")

    async def test_get_me_returns_current_user(self):
        user = {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": ADMIN_ROLE,
        }

        result = await get_me(current_user=user)

        self.assertEqual(result["username"], "admin")

    async def test_create_user_returns_created_user(self):
        user = {
            "id": 2,
            "username": "barber",
            "email": "barber@example.com",
            "role": BARBER_ROLE,
        }
        mediator = FakeMediator(user)

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            result = await create_user(
                UserCreateRequest(
                    username="barber",
                    email="barber@example.com",
                    password="password123",
                    role=BARBER_ROLE,
                ),
                db=object(),
                current_user={"role": ADMIN_ROLE},
            )

        self.assertEqual(result["role"], BARBER_ROLE)
        self.assertEqual(mediator.requests[0].username, "barber")

    async def test_create_user_maps_conflict_to_409(self):
        mediator = FakeMediator(ConflictError("User with this username or email already exists"))

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await create_user(
                    UserCreateRequest(
                        username="barber",
                        email="barber@example.com",
                        password="password123",
                        role=BARBER_ROLE,
                    ),
                    db=object(),
                    current_user={"role": ADMIN_ROLE},
                )

        self.assertEqual(context.exception.status_code, 409)


    async def test_register_barber_returns_created_user(self):
        user = {
            "id": 3,
            "username": "barber1",
            "email": "barber1@example.com",
            "role": BARBER_ROLE,
        }
        mediator = FakeMediator(user)

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            result = await register_barber(
                BarberRegisterRequest(
                    username="barber1",
                    email="barber1@example.com",
                    password="password123",
                    nome="Barbeiro Um",
                    tenant_id=1,
                ),
                db=object(),
                current_user={"role": ADMIN_ROLE},
            )

        self.assertEqual(result["role"], BARBER_ROLE)
        self.assertEqual(mediator.requests[0].username, "barber1")
        self.assertEqual(mediator.requests[0].nome, "Barbeiro Um")

    async def test_register_barber_maps_conflict_to_409(self):
        mediator = FakeMediator(ConflictError("User with this username or email already exists"))

        with patch("backend.api.routes.auth_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await register_barber(
                    BarberRegisterRequest(
                        username="barber1",
                        email="barber1@example.com",
                        password="password123",
                        nome="Barbeiro Um",
                        tenant_id=1,
                    ),
                    db=object(),
                    current_user={"role": ADMIN_ROLE},
                )

        self.assertEqual(context.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
