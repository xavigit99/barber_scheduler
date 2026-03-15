import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.barbershop_http import (
    build_create_barbershop_command,
    build_delete_barbershop_command,
    build_get_barbershop_query,
    build_list_barbershops_query,
    build_update_barbershop_command,
    ensure_barbershop_deleted,
    ensure_barbershop_found,
    ensure_barbershop_update_payload_has_changes,
)
from backend.infrastructure.schemas import BarbershopCreate, BarbershopUpdate


class BarbershopHttpTestCase(unittest.TestCase):

    def test_build_create_barbershop_command_maps_payload_fields(self):
        command = build_create_barbershop_command(
            BarbershopCreate(nome="Central"),
            owner_user_id=5,
        )

        self.assertEqual(command.name, "Central")
        self.assertEqual(command.owner_user_id, 5)

    def test_build_update_barbershop_command_maps_partial_payload_fields(self):
        command = build_update_barbershop_command(
            7,
            BarbershopUpdate(nome="Central Premium"),
        )

        self.assertEqual(command.barbershop_id, 7)
        self.assertEqual(command.name, "Central Premium")

    def test_build_get_barbershop_query_maps_barbershop_id(self):
        query = build_get_barbershop_query(9)

        self.assertEqual(query.barbershop_id, 9)

    def test_build_delete_barbershop_command_maps_barbershop_id(self):
        command = build_delete_barbershop_command(11)

        self.assertEqual(command.barbershop_id, 11)

    def test_build_list_barbershops_query_returns_query_instance(self):
        query = build_list_barbershops_query()

        self.assertEqual(query.__class__.__name__, "ListBarbershopsQuery")

    def test_ensure_barbershop_found_raises_not_found_for_missing_barbershop(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barbershop_found(None)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barbershop not found")

    def test_ensure_barbershop_deleted_raises_not_found_for_missing_barbershop(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barbershop_deleted(False)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barbershop not found")

    def test_ensure_barbershop_update_payload_has_changes_raises_for_empty_payload(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barbershop_update_payload_has_changes(BarbershopUpdate())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")


if __name__ == "__main__":
    unittest.main()
