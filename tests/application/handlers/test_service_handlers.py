import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_service_command import CreateServiceCommand
from backend.application.commands.delete_service_command import DeleteServiceCommand
from backend.application.commands.update_service_command import UpdateServiceCommand
from backend.application.handlers.service.create_service_handler import CreateServiceHandler
from backend.application.handlers.service.delete_service_handler import DeleteServiceHandler
from backend.application.handlers.service.get_service_handler import GetServiceHandler
from backend.application.handlers.service.list_services_handler import ListServicesHandler
from backend.application.handlers.service.update_service_handler import UpdateServiceHandler
from backend.application.queries.get_service_query import GetServiceQuery
from backend.application.queries.list_services_query import ListServicesQuery
from backend.core.service import Service


class ServiceHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_service_handler_persists_mapped_service(self):
        db = MagicMock()
        handler = CreateServiceHandler(db)
        command = CreateServiceCommand(
            name="Corte",
            duration_minutes=30,
            price=15.0,
            tenant_id=5,
        )

        result = await handler.handle(command)

        self.assertIsInstance(result, Service)
        db.add.assert_called_once_with(result)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)
        self.assertEqual(result.nome, "Corte")
        self.assertEqual(result.duracao_minutos, 30)
        self.assertEqual(result.preco, 15.0)

    async def test_get_service_handler_returns_service_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_service = object()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_service

        handler = GetServiceHandler(db)

        result = await handler.handle(GetServiceQuery(service_id=7, tenant_id=5))

        self.assertIs(result, expected_service)
        db.query.assert_called_once_with(Service)
        query_builder.first.assert_called_once_with()

    async def test_list_services_handler_returns_services_from_repository(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_services = [object(), object()]

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.all.return_value = expected_services

        handler = ListServicesHandler(db)

        result = await handler.handle(ListServicesQuery(tenant_id=5))

        self.assertIs(result, expected_services)
        db.query.assert_called_once_with(Service)
        self.assertGreaterEqual(query_builder.filter.call_count, 1)
        query_builder.all.assert_called_once_with()

    async def test_update_service_handler_maps_english_fields_to_model_fields(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = MagicMock()
        query_builder.all.return_value = [object()]

        repository_refresh_target = query_builder.first.return_value

        handler = UpdateServiceHandler(db)
        command = UpdateServiceCommand(
            service_id=1,
            name="Corte Premium",
            duration_minutes=45,
            price=25.0,
            tenant_id=5,
        )

        result = await handler.handle(command)

        self.assertIs(result, repository_refresh_target)
        db.query.assert_called_with(Service)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(repository_refresh_target)
        self.assertEqual(repository_refresh_target.nome, "Corte Premium")
        self.assertEqual(repository_refresh_target.duracao_minutos, 45)
        self.assertEqual(repository_refresh_target.preco, 25.0)

    async def test_delete_service_handler_deletes_existing_service(self):
        db = MagicMock()
        query_builder = MagicMock()
        expected_service = MagicMock(deleted=False)

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = expected_service

        handler = DeleteServiceHandler(db)

        result = await handler.handle(DeleteServiceCommand(service_id=4, tenant_id=5))

        self.assertTrue(result)
        db.query.assert_called_once_with(Service)
        self.assertTrue(expected_service.deleted)
        db.delete.assert_not_called()
        db.commit.assert_called_once_with()

    async def test_delete_service_handler_returns_false_when_service_is_missing(self):
        db = MagicMock()
        query_builder = MagicMock()

        db.query.return_value = query_builder
        query_builder.filter.return_value = query_builder
        query_builder.first.return_value = None

        handler = DeleteServiceHandler(db)

        result = await handler.handle(DeleteServiceCommand(service_id=4, tenant_id=5))

        self.assertFalse(result)
        db.query.assert_called_once_with(Service)
        db.delete.assert_not_called()
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
