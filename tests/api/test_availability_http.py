import os
import unittest
from datetime import date, datetime, time

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.availability_http import (
    build_create_barber_availability_command,
    build_create_barber_block_command,
    build_delete_barber_availability_command,
    build_delete_barber_block_command,
    build_get_available_slots_query,
    build_list_barber_availabilities_query,
    build_list_barber_blocks_query,
    build_update_barber_availability_command,
    ensure_barber_availability_deleted,
    ensure_barber_availability_update_payload_has_changes,
    ensure_barber_block_deleted,
)
from backend.infrastructure.schemas import (
    BarberAvailabilityCreate,
    BarberAvailabilityUpdate,
    BarberBlockCreate,
)


class AvailabilityHttpTestCase(unittest.TestCase):

    def test_build_create_barber_availability_command_maps_payload_fields(self):
        command = build_create_barber_availability_command(
            3,
            BarberAvailabilityCreate(
                dia_semana=0,
                hora_inicio=time(9, 0),
                hora_fim=time(17, 0),
            ),
        )

        self.assertEqual(command.barber_id, 3)
        self.assertEqual(command.weekday, 0)
        self.assertEqual(command.start_time, time(9, 0))
        self.assertEqual(command.end_time, time(17, 0))

    def test_build_update_barber_availability_command_maps_partial_payload_fields(self):
        command = build_update_barber_availability_command(
            3,
            7,
            BarberAvailabilityUpdate(hora_fim=time(18, 0)),
        )

        self.assertEqual(command.barber_id, 3)
        self.assertEqual(command.availability_id, 7)
        self.assertIsNone(command.weekday)
        self.assertIsNone(command.start_time)
        self.assertEqual(command.end_time, time(18, 0))

    def test_build_delete_barber_availability_command_maps_ids(self):
        command = build_delete_barber_availability_command(3, 9)

        self.assertEqual(command.barber_id, 3)
        self.assertEqual(command.availability_id, 9)

    def test_build_list_barber_availabilities_query_maps_barber_id(self):
        query = build_list_barber_availabilities_query(5)

        self.assertEqual(query.barber_id, 5)

    def test_build_create_barber_block_command_maps_payload_fields(self):
        command = build_create_barber_block_command(
            3,
            BarberBlockCreate(
                tipo="break",
                inicio=datetime(2026, 3, 16, 12, 0),
                fim=datetime(2026, 3, 16, 13, 0),
                motivo="Lunch",
            ),
        )

        self.assertEqual(command.barber_id, 3)
        self.assertEqual(command.kind, "break")
        self.assertEqual(command.start_at, datetime(2026, 3, 16, 12, 0))
        self.assertEqual(command.end_at, datetime(2026, 3, 16, 13, 0))
        self.assertEqual(command.reason, "Lunch")

    def test_build_delete_barber_block_command_maps_ids(self):
        command = build_delete_barber_block_command(3, 11)

        self.assertEqual(command.barber_id, 3)
        self.assertEqual(command.block_id, 11)

    def test_build_list_barber_blocks_query_maps_barber_id(self):
        query = build_list_barber_blocks_query(7)

        self.assertEqual(query.barber_id, 7)

    def test_build_get_available_slots_query_maps_request_fields(self):
        query = build_get_available_slots_query(3, 4, date(2026, 3, 16), "Europe/Lisbon")

        self.assertEqual(query.barber_id, 3)
        self.assertEqual(query.service_id, 4)
        self.assertEqual(query.target_date, date(2026, 3, 16))
        self.assertEqual(query.timezone, "Europe/Lisbon")

    def test_ensure_barber_availability_deleted_raises_not_found_when_missing(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barber_availability_deleted(False)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Availability window not found")

    def test_ensure_barber_block_deleted_raises_not_found_when_missing(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barber_block_deleted(False)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Availability block not found")

    def test_ensure_barber_availability_update_payload_has_changes_raises_for_empty_payload(self):
        with self.assertRaises(HTTPException) as context:
            ensure_barber_availability_update_payload_has_changes(BarberAvailabilityUpdate())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")


if __name__ == "__main__":
    unittest.main()
