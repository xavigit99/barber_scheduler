import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.service_http import (
    build_create_service_command,
    build_delete_service_command,
    build_get_service_query,
    build_list_services_query,
    build_update_service_command,
    ensure_service_deleted,
    ensure_service_found,
    ensure_service_update_payload_has_changes,
)
from backend.infrastructure.schemas import ServiceCreate, ServiceUpdate


class ServiceHttpTestCase(unittest.TestCase):

    def test_build_create_service_command_maps_payload_fields(self):
        command = build_create_service_command(
            ServiceCreate(nome="Corte", duracao_minutos=30, preco=15.0, tenant_id=5),
            tenant_id=5,
        )

        self.assertEqual(command.name, "Corte")
        self.assertEqual(command.duration_minutes, 30)
        self.assertEqual(command.price, 15.0)
        self.assertEqual(command.tenant_id, 5)

    def test_build_update_service_command_maps_partial_payload_fields(self):
        command = build_update_service_command(
            7,
            ServiceUpdate(preco=20.0, tenant_id=5),
            tenant_id=5,
        )

        self.assertEqual(command.service_id, 7)
        self.assertIsNone(command.name)
        self.assertIsNone(command.duration_minutes)
        self.assertEqual(command.price, 20.0)
        self.assertEqual(command.tenant_id, 5)

    def test_build_get_service_query_maps_service_id(self):
        query = build_get_service_query(9, tenant_id=5)

        self.assertEqual(query.service_id, 9)
        self.assertEqual(query.tenant_id, 5)

    def test_build_delete_service_command_maps_service_id(self):
        command = build_delete_service_command(11, tenant_id=5)

        self.assertEqual(command.service_id, 11)
        self.assertEqual(command.tenant_id, 5)

    def test_build_list_services_query_returns_query_instance(self):
        query = build_list_services_query(tenant_id=5)

        self.assertEqual(query.__class__.__name__, "ListServicesQuery")
        self.assertEqual(query.tenant_id, 5)

    def test_ensure_service_found_raises_not_found_for_missing_service(self):
        with self.assertRaises(HTTPException) as context:
            ensure_service_found(None)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Service not found")

    def test_ensure_service_deleted_raises_not_found_for_missing_service(self):
        with self.assertRaises(HTTPException) as context:
            ensure_service_deleted(False)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Service not found")

    def test_ensure_service_update_payload_has_changes_raises_for_empty_payload(self):
        with self.assertRaises(HTTPException) as context:
            ensure_service_update_payload_has_changes(ServiceUpdate())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")


if __name__ == "__main__":
    unittest.main()
