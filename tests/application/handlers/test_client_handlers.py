import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_client_command import CreateClientCommand
from backend.application.commands.delete_client_command import DeleteClientCommand
from backend.application.handlers.client.create_client_handler import CreateClientHandler
from backend.application.handlers.client.delete_client_handler import DeleteClientHandler
from backend.application.handlers.client.get_client_handler import GetClientHandler
from backend.application.handlers.client.list_clients_handler import ListClientsHandler
from backend.application.handlers.clients.get_client_segment_handler import GetClientSegmentHandler
from backend.application.queries.get_client_segment_query import GetClientSegmentQuery
from backend.application.queries.get_client_query import GetClientQuery
from backend.application.queries.list_clients_query import ListClientsQuery
from backend.core.client import Client


class ClientHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_client_handler_persists_mapped_client(self):
        db = MagicMock()
        handler = CreateClientHandler(db)
        command = CreateClientCommand(
            name="John",
            email="john@example.com",
            phone="123",
            tenant_id=5,
        )

        result = await handler.handle(command)

        self.assertIsInstance(result, Client)
        db.add.assert_called_once_with(result)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)
        self.assertEqual(result.nome, "John")
        self.assertEqual(result.email, "john@example.com")
        self.assertEqual(result.telefone, "123")

    async def test_get_client_handler_returns_client_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_client = object()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_client

        handler = GetClientHandler(db)

        result = await handler.handle(GetClientQuery(client_id=7, tenant_id=5))

        self.assertIs(result, expected_client)
        db.query.assert_called_once_with(Client)
        self.assertTrue(query_builder.filter.called)
        query_builder.first.assert_called_once_with()

    async def test_list_clients_handler_returns_clients_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_clients = [object(), object()]

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.all.return_value = expected_clients

        handler = ListClientsHandler(db)

        result = await handler.handle(ListClientsQuery(tenant_id=5))

        self.assertIs(result, expected_clients)
        db.query.assert_called_once_with(Client)
        self.assertGreaterEqual(query_builder.filter.call_count, 1)
        query_builder.all.assert_called_once_with()

    async def test_delete_client_handler_deletes_existing_client(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_client = MagicMock(deleted=False)

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_client

        handler = DeleteClientHandler(db)

        result = await handler.handle(DeleteClientCommand(client_id=4, tenant_id=5))

        self.assertTrue(result)
        db.query.assert_called_once_with(Client)
        self.assertTrue(query_builder.filter.called)
        self.assertTrue(expected_client.deleted)
        db.delete.assert_not_called()
        db.commit.assert_called_once_with()

    async def test_delete_client_handler_returns_false_when_client_is_missing(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        handler = DeleteClientHandler(db)

        result = await handler.handle(DeleteClientCommand(client_id=4, tenant_id=5))

        self.assertFalse(result)
        db.query.assert_called_once_with(Client)
        self.assertTrue(query_builder.filter.called)
        db.delete.assert_not_called()
        db.commit.assert_not_called()

    async def test_get_client_segment_handler_returns_clients_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_clients = [object()]

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.all.return_value = expected_clients

        handler = GetClientSegmentHandler(db)

        result = await handler.handle(
            GetClientSegmentQuery(
                tenant_id=5,
                inactive_days=30,
                min_spend=50.0,
                service_id=3,
                has_birthday_this_month=True,
            )
        )

        self.assertIs(result, expected_clients)
        db.query.assert_called_once_with(Client)
        self.assertGreaterEqual(query_builder.filter.call_count, 5)
        query_builder.all.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
