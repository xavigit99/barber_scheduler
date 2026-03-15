import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.barber_http import (
    build_create_barber_command,
    build_delete_barber_command,
    build_get_barber_query,
    build_list_barbers_query,
    build_update_barber_command,
    ensure_barber_deleted,
    ensure_barber_found,
    ensure_barber_update_payload_has_changes,
)
from backend.infrastructure.schemas import BarberCreate, BarberUpdate


class BarberHttpTestCase(unittest.TestCase):

    def test_build_create_barber_command_maps_payload_fields(self):
        command = build_create_barber_command(
            BarberCreate(nome="Joao", email="joao@example.com", telefone="123", tenant_id=5),
            tenant_id=5,
        )

        self.assertEqual(command.name, "Joao")
        self.assertEqual(command.email, "joao@example.com")
        self.assertEqual(command.phone, "123")
        self.assertEqual(command.tenant_id, 5)

    def test_build_update_barber_command_maps_partial_payload_fields(self):
        command = build_update_barber_command(
            7,
            BarberUpdate(email="joao@example.com", tenant_id=5),
            tenant_id=5,
        )

        self.assertEqual(command.barber_id, 7)
        self.assertIsNone(command.name)
        self.assertEqual(command.email, "joao@example.com")
        self.assertIsNone(command.phone)
        self.assertEqual(command.tenant_id, 5)

    def test_build_get_barber_query_maps_barber_id(self):
        query = build_get_barber_query(9, tenant_id=5)

        self.assertEqual(query.barber_id, 9)
        self.assertEqual(query.tenant_id, 5)

    def test_build_delete_barber_command_maps_barber_id(self):
        command = build_delete_barber_command(11, tenant_id=5)

        self.assertEqual(command.barber_id, 11)
        self.assertEqual(command.tenant_id, 5)

    def test_build_list_barbers_query_returns_query_instance(self):
        query = build_list_barbers_query(tenant_id=5)

        self.assertEqual(query.__class__.__name__, "ListBarbersQuery")
        self.assertEqual(query.tenant_id, 5)

    def test_ensure_barber_found_raises_not_found_for_missing_barber(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barber_found(None)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barber not found")

    def test_ensure_barber_deleted_raises_not_found_for_missing_barber(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barber_deleted(False)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barber not found")

    def test_ensure_barber_update_payload_has_changes_raises_for_empty_payload(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barber_update_payload_has_changes(BarberUpdate())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")


if __name__ == "__main__":
    unittest.main()
