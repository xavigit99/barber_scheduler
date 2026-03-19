import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.authenticate_user_command import AuthenticateUserCommand
from backend.application.commands.bootstrap_admin_command import BootstrapAdminCommand
from backend.application.commands.create_user_command import CreateUserCommand
from backend.application.commands.register_barber_command import RegisterBarberCommand
from backend.application.commands.register_client_command import RegisterClientCommand
from backend.application.handlers.auth.authenticate_user_handler import AuthenticateUserHandler
from backend.application.handlers.auth.bootstrap_admin_handler import BootstrapAdminHandler
from backend.application.handlers.auth.create_user_handler import CreateUserHandler
from backend.application.handlers.auth.get_user_handler import GetUserHandler
from backend.application.handlers.auth.register_barber_handler import RegisterBarberHandler
from backend.application.handlers.auth.register_client_handler import RegisterClientHandler
from backend.application.queries.get_user_query import GetUserQuery
from backend.core.barber import Barber
from backend.core.exceptions import AuthenticationError, ConflictError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE
from backend.core.security import decode_access_token, hash_password
from backend.core.user import User


class AuthHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_user_handler_persists_user_with_hashed_password(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        handler = CreateUserHandler(db)
        command = CreateUserCommand(
            username="admin",
            email="admin@example.com",
            password="password123",
            role=ADMIN_ROLE,
        )

        result = await handler.handle(command)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, "admin")
        self.assertEqual(result.email, "admin@example.com")
        self.assertEqual(result.role, ADMIN_ROLE)
        self.assertNotEqual(result.password_hash, "password123")
        db.add.assert_called_once_with(result)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)

    async def test_create_user_handler_rejects_duplicate_user(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = object()

        handler = CreateUserHandler(db)

        with self.assertRaises(ConflictError) as context:
            await handler.handle(
                CreateUserCommand(
                    username="admin",
                    email="admin@example.com",
                    password="password123",
                    role=ADMIN_ROLE,
                )
            )

        self.assertEqual(str(context.exception), "User with this username or email already exists")

    async def test_bootstrap_admin_handler_rejects_second_bootstrap(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.first.return_value = object()

        handler = BootstrapAdminHandler(db)

        with self.assertRaises(ConflictError) as context:
            await handler.handle(
                BootstrapAdminCommand(
                    username="admin",
                    email="admin@example.com",
                    password="password123",
                )
            )

        self.assertEqual(str(context.exception), "Admin bootstrap has already been completed")

    async def test_authenticate_user_handler_returns_token_payload(self):
        db = MagicMock()
        query_builder = MagicMock()
        user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("password123"),
            role=ADMIN_ROLE,
        )

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = user

        handler = AuthenticateUserHandler(db)

        result = await handler.handle(
            AuthenticateUserCommand(username="admin", password="password123")
        )

        self.assertEqual(result["token_type"], "bearer")
        self.assertEqual(result["user"], user)
        self.assertTrue(result["access_token"])
        self.assertEqual(decode_access_token(result["access_token"])["sub"], 1)

    async def test_authenticate_user_handler_rejects_invalid_password(self):
        db = MagicMock()
        query_builder = MagicMock()
        user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("password123"),
            role=ADMIN_ROLE,
        )

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = user

        handler = AuthenticateUserHandler(db)

        with self.assertRaises(AuthenticationError) as context:
            await handler.handle(
                AuthenticateUserCommand(username="admin", password="wrongpass")
            )

        self.assertEqual(str(context.exception), "Invalid credentials")

    async def test_get_user_handler_returns_user(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_user = object()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_user

        handler = GetUserHandler(db)

        result = await handler.handle(GetUserQuery(user_id=7))

        self.assertIs(result, expected_user)
        db.query.assert_called_once_with(User)

    async def test_create_user_handler_rejects_invalid_role(self):
        db = MagicMock()
        handler = CreateUserHandler(db)

        with self.assertRaises(ConflictError) as context:
            await handler.handle(
                CreateUserCommand(
                    username="unknown",
                    email="unknown@example.com",
                    password="password123",
                    role="owner",
                )
            )

        self.assertEqual(str(context.exception), "Invalid role")


    async def test_register_barber_handler_creates_user_and_barber(self):
        db = MagicMock()
        query_builder = MagicMock()
        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        added_objects = []
        db.add.side_effect = lambda obj: added_objects.append(obj)

        def flush_side_effect():
            for obj in added_objects:
                if isinstance(obj, User):
                    obj.id = 42

        db.flush.side_effect = flush_side_effect

        handler = RegisterBarberHandler(db)
        command = RegisterBarberCommand(
            username="barber1",
            email="barber1@example.com",
            password="password123",
            nome="Barbeiro Um",
            telefone="912345678",
            tenant_id=1,
        )

        result = await handler.handle(command)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, "barber1")
        self.assertEqual(result.role, BARBER_ROLE)

        barber_objects = [o for o in added_objects if isinstance(o, Barber)]
        self.assertEqual(len(barber_objects), 1)
        self.assertEqual(barber_objects[0].nome, "Barbeiro Um")
        self.assertEqual(barber_objects[0].user_id, 42)
        self.assertEqual(barber_objects[0].tenant_id, 1)

    async def test_register_barber_handler_rejects_duplicate(self):
        db = MagicMock()
        query_builder = MagicMock()
        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        existing_user = MagicMock()
        existing_user.role = "barber"
        query_builder.first.return_value = existing_user

        handler = RegisterBarberHandler(db)
        with self.assertRaises(ConflictError):
            await handler.handle(
                RegisterBarberCommand(
                    username="barber1",
                    email="barber1@example.com",
                    password="password123",
                    nome="Barbeiro Um",
                    telefone=None,
                    tenant_id=1,
                )
            )

    async def test_register_client_handler_creates_global_client_user_without_client_row(self):
        db = MagicMock()
        query_builder = MagicMock()
        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        added_objects = []
        db.add.side_effect = lambda obj: added_objects.append(obj)

        handler = RegisterClientHandler(db)
        command = RegisterClientCommand(
            username="client1",
            email="client1@example.com",
            password="password123",
            nome="Cliente Um",
        )

        result = await handler.handle(command)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, "client1")
        self.assertEqual(result.role, "client")
        self.assertEqual(len(added_objects), 1)
        self.assertIsInstance(added_objects[0], User)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)

    async def test_register_client_handler_adds_client_role_to_existing_user(self):
        db = MagicMock()
        query_builder = MagicMock()
        existing_user = User(
            id=7,
            username="staff1",
            email="staff1@example.com",
            password_hash=hash_password("password123"),
            role="barber",
        )
        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = existing_user

        handler = RegisterClientHandler(db)

        result = await handler.handle(
            RegisterClientCommand(
                username="staff1",
                email="staff1@example.com",
                password="password123",
                nome="Staff Um",
            )
        )

        self.assertIs(result, existing_user)
        self.assertEqual(result.role, "barber,client")
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)


if __name__ == "__main__":
    unittest.main()
