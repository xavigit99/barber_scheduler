import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.update_client_command import UpdateClientCommand
from backend.application.handlers.client.update_client_handler import UpdateClientHandler
from backend.core.client import Cliente


class UpdateClientHandlerTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_update_client_handler_maps_english_fields_to_model_fields(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_client = object()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = MagicMock()
        query_builder.all.return_value = [expected_client]

        repository_refresh_target = query_builder.first.return_value

        handler = UpdateClientHandler(db)
        command = UpdateClientCommand(
            client_id=1,
            name="John",
            email="john@example.com",
            phone="123",
        )

        result = await handler.handle(command)

        self.assertIs(result, repository_refresh_target)
        db.query.assert_called_with(Cliente)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(repository_refresh_target)
        self.assertEqual(repository_refresh_target.nome, "John")
        self.assertEqual(repository_refresh_target.email, "john@example.com")
        self.assertEqual(repository_refresh_target.telefone, "123")


if __name__ == "__main__":
    unittest.main()
