import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.routes.client_route_adapters import (
    build_create_client_command,
    build_delete_client_command,
    build_get_client_query,
    build_list_clients_query,
    build_update_client_command,
    ensure_client_deleted,
    ensure_client_found,
    ensure_update_payload_has_changes,
)
from backend.infrastructure.schemas import ClientCreate, ClientUpdate


class ClientRouteAdaptersTestCase(unittest.TestCase):

    def test_build_create_client_command_maps_payload_fields(self):
        command = build_create_client_command(
            ClientCreate(nome="John", email="john@example.com", telefone="123")
        )

        self.assertEqual(command.name, "John")
        self.assertEqual(command.email, "john@example.com")
        self.assertEqual(command.phone, "123")

    def test_build_update_client_command_maps_partial_payload_fields(self):
        command = build_update_client_command(
            7,
            ClientUpdate(email="john@example.com"),
        )

        self.assertEqual(command.client_id, 7)
        self.assertIsNone(command.name)
        self.assertEqual(command.email, "john@example.com")
        self.assertIsNone(command.phone)

    def test_build_get_client_query_maps_client_id(self):
        query = build_get_client_query(9)

        self.assertEqual(query.client_id, 9)

    def test_build_delete_client_command_maps_client_id(self):
        command = build_delete_client_command(11)

        self.assertEqual(command.client_id, 11)

    def test_build_list_clients_query_returns_query_instance(self):
        query = build_list_clients_query()

        self.assertEqual(query.__class__.__name__, "ListClientsQuery")

    def test_ensure_client_found_raises_not_found_for_missing_client(self):
        with self.assertRaises(HTTPException) as context:
            ensure_client_found(None)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Client not found")

    def test_ensure_client_deleted_raises_not_found_for_missing_client(self):
        with self.assertRaises(HTTPException) as context:
            ensure_client_deleted(False)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Client not found")

    def test_ensure_update_payload_has_changes_raises_for_empty_payload(self):
        with self.assertRaises(HTTPException) as context:
            ensure_update_payload_has_changes(ClientUpdate())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")


if __name__ == "__main__":
    unittest.main()
