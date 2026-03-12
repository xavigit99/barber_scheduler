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
from backend.application.queries.get_client_query import GetClientQuery
from backend.application.queries.list_clients_query import ListClientsQuery
from backend.core.client import Cliente


class ClientHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_client_handler_persists_mapped_client(self):
        db = MagicMock()
        handler = CreateClientHandler(db)
        command = CreateClientCommand(
            name="John",
            email="john@example.com",
            phone="123",
        )

        result = await handler.handle(command)

        self.assertIsInstance(result, Cliente)
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

        result = await handler.handle(GetClientQuery(client_id=7))

        self.assertIs(result, expected_client)
        db.query.assert_called_once_with(Cliente)
        query_builder.filter.assert_called_once()
        query_builder.first.assert_called_once_with()

    async def test_list_clients_handler_returns_clients_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_clients = [object(), object()]

        db.query.return_value = query_builder
        query_builder.all.return_value = expected_clients

        handler = ListClientsHandler(db)

        result = await handler.handle(ListClientsQuery())

        self.assertIs(result, expected_clients)
        db.query.assert_called_once_with(Cliente)
        query_builder.all.assert_called_once_with()

    async def test_delete_client_handler_deletes_existing_client(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_client = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_client

        handler = DeleteClientHandler(db)

        result = await handler.handle(DeleteClientCommand(client_id=4))

        self.assertTrue(result)
        db.query.assert_called_once_with(Cliente)
        db.delete.assert_called_once_with(expected_client)
        db.commit.assert_called_once_with()

    async def test_delete_client_handler_returns_false_when_client_is_missing(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        handler = DeleteClientHandler(db)

        result = await handler.handle(DeleteClientCommand(client_id=4))

        self.assertFalse(result)
        db.query.assert_called_once_with(Cliente)
        db.delete.assert_not_called()
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
