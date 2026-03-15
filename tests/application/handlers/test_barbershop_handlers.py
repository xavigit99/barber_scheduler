import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_barbershop_command import CreateBarbershopCommand
from backend.application.commands.delete_barbershop_command import DeleteBarbershopCommand
from backend.application.commands.update_barbershop_command import UpdateBarbershopCommand
from backend.application.handlers.barbershop.create_barbershop_handler import (
    CreateBarbershopHandler,
)
from backend.application.handlers.barbershop.delete_barbershop_handler import (
    DeleteBarbershopHandler,
)
from backend.application.handlers.barbershop.get_barbershop_handler import GetBarbershopHandler
from backend.application.handlers.barbershop.list_barbershops_handler import (
    ListBarbershopsHandler,
)
from backend.application.handlers.barbershop.update_barbershop_handler import (
    UpdateBarbershopHandler,
)
from backend.application.queries.get_barbershop_query import GetBarbershopQuery
from backend.application.queries.list_barbershops_query import ListBarbershopsQuery
from backend.core.barbershop import Barbershop
from backend.core.exceptions import NotFoundError


class BarbershopHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_barbershop_handler_persists_mapped_barbershop(self):
        db = MagicMock()
        owner_query = MagicMock()
        tenant_query = MagicMock()
        owner_user = SimpleNamespace(id=5)

        db.query.side_effect = [owner_query, tenant_query]
        owner_query.filter.return_value = owner_query
        owner_query.first.return_value = owner_user
        tenant_query.filter.return_value = tenant_query
        tenant_query.first.return_value = None

        handler = CreateBarbershopHandler(db)
        command = CreateBarbershopCommand(name="Central", owner_user_id=5)

        result = await handler.handle(command)

        self.assertIsInstance(result, Barbershop)
        self.assertEqual(result.nome, "Central")
        self.assertEqual(result.owner_user_id, 5)
        self.assertEqual(db.add.call_count, 2)
        db.flush.assert_called_once_with()
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)

    async def test_create_barbershop_handler_rejects_missing_owner_user(self):
        db = MagicMock()
        owner_query = MagicMock()

        db.query.return_value = owner_query
        owner_query.filter.return_value = owner_query
        owner_query.first.return_value = None

        handler = CreateBarbershopHandler(db)

        with self.assertRaises(NotFoundError) as context:
            await handler.handle(CreateBarbershopCommand(name="Central", owner_user_id=5))

        self.assertEqual(str(context.exception), "Owner user not found")

    async def test_get_barbershop_handler_returns_barbershop_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_barbershop = object()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_barbershop

        handler = GetBarbershopHandler(db)

        result = await handler.handle(GetBarbershopQuery(barbershop_id=7))

        self.assertIs(result, expected_barbershop)
        db.query.assert_called_once_with(Barbershop)

    async def test_list_barbershops_handler_returns_barbershops_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_barbershops = [object(), object()]

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.all.return_value = expected_barbershops

        handler = ListBarbershopsHandler(db)

        result = await handler.handle(ListBarbershopsQuery())

        self.assertIs(result, expected_barbershops)
        db.query.assert_called_once_with(Barbershop)
        query_builder.filter.assert_called_once()
        query_builder.all.assert_called_once_with()

    async def test_update_barbershop_handler_maps_fields_to_model_fields(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = MagicMock()
        query_builder.all.return_value = [object()]

        repository_refresh_target = query_builder.first.return_value

        handler = UpdateBarbershopHandler(db)

        result = await handler.handle(
            UpdateBarbershopCommand(barbershop_id=1, name="Central Premium")
        )

        self.assertIs(result, repository_refresh_target)
        db.query.assert_called_with(Barbershop)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(repository_refresh_target)
        self.assertEqual(repository_refresh_target.nome, "Central Premium")

    async def test_delete_barbershop_handler_returns_false_when_missing(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        handler = DeleteBarbershopHandler(db)

        result = await handler.handle(DeleteBarbershopCommand(barbershop_id=4))

        self.assertFalse(result)
        db.query.assert_called_once_with(Barbershop)
        db.delete.assert_not_called()
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
