import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_barber_command import CreateBarberCommand
from backend.application.commands.delete_barber_command import DeleteBarberCommand
from backend.application.commands.update_barber_command import UpdateBarberCommand
from backend.application.handlers.barber.create_barber_handler import CreateBarberHandler
from backend.application.handlers.barber.delete_barber_handler import DeleteBarberHandler
from backend.application.handlers.barber.get_barber_handler import GetBarberHandler
from backend.application.handlers.barber.list_barbers_handler import ListBarbersHandler
from backend.application.handlers.barber.update_barber_handler import UpdateBarberHandler
from backend.application.queries.get_barber_query import GetBarberQuery
from backend.application.queries.list_barbers_query import ListBarbersQuery
from backend.core.barber import Barber


class BarberHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_barber_handler_persists_mapped_barber(self):
        db = MagicMock()
        handler = CreateBarberHandler(db)
        command = CreateBarberCommand(
            name="Joao",
            email="joao@example.com",
            phone="123",
            tenant_id=5,
        )

        result = await handler.handle(command)

        self.assertIsInstance(result, Barber)
        db.add.assert_called_once_with(result)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)
        self.assertEqual(result.nome, "Joao")
        self.assertEqual(result.email, "joao@example.com")
        self.assertEqual(result.telefone, "123")

    async def test_get_barber_handler_returns_barber_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_barber = object()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_barber

        handler = GetBarberHandler(db)

        result = await handler.handle(GetBarberQuery(barber_id=7, tenant_id=5))

        self.assertIs(result, expected_barber)
        db.query.assert_called_once_with(Barber)
        query_builder.first.assert_called_once_with()

    async def test_list_barbers_handler_returns_barbers_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_barbers = [object(), object()]

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.all.return_value = expected_barbers

        handler = ListBarbersHandler(db)

        result = await handler.handle(ListBarbersQuery(tenant_id=5))

        self.assertIs(result, expected_barbers)
        db.query.assert_called_once_with(Barber)
        self.assertGreaterEqual(query_builder.filter.call_count, 1)
        query_builder.all.assert_called_once_with()

    async def test_update_barber_handler_maps_english_fields_to_model_fields(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = MagicMock()
        query_builder.all.return_value = [object()]

        repository_refresh_target = query_builder.first.return_value

        handler = UpdateBarberHandler(db)
        command = UpdateBarberCommand(
            barber_id=1,
            name="Joao",
            email="joao@example.com",
            phone="123",
            tenant_id=5,
        )

        result = await handler.handle(command)

        self.assertIs(result, repository_refresh_target)
        db.query.assert_called_with(Barber)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(repository_refresh_target)
        self.assertEqual(repository_refresh_target.nome, "Joao")
        self.assertEqual(repository_refresh_target.email, "joao@example.com")
        self.assertEqual(repository_refresh_target.telefone, "123")

    async def test_delete_barber_handler_deletes_existing_barber(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_barber = MagicMock(deleted=False)

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_barber

        handler = DeleteBarberHandler(db)

        result = await handler.handle(DeleteBarberCommand(barber_id=4, tenant_id=5))

        self.assertTrue(result)
        db.query.assert_called_once_with(Barber)
        self.assertTrue(expected_barber.deleted)
        db.delete.assert_not_called()
        db.commit.assert_called_once_with()

    async def test_delete_barber_handler_returns_false_when_barber_is_missing(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        handler = DeleteBarberHandler(db)

        result = await handler.handle(DeleteBarberCommand(barber_id=4, tenant_id=5))

        self.assertFalse(result)
        db.query.assert_called_once_with(Barber)
        db.delete.assert_not_called()
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
