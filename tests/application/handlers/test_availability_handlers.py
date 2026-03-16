import os
import unittest
from datetime import date, datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_barber_availability_command import (
    CreateBarberAvailabilityCommand,
)
from backend.application.commands.create_barber_block_command import CreateBarberBlockCommand
from backend.application.commands.update_barber_availability_command import (
    UpdateBarberAvailabilityCommand,
)
from backend.application.handlers.availability.create_barber_availability_handler import (
    CreateBarberAvailabilityHandler,
)
from backend.application.handlers.availability.create_barber_block_handler import (
    CreateBarberBlockHandler,
)
from backend.application.handlers.availability.get_available_slots_handler import (
    GetAvailableSlotsHandler,
)
from backend.application.handlers.availability.list_barber_availabilities_handler import (
    ListBarberAvailabilitiesHandler,
)
from backend.application.handlers.availability.update_barber_availability_handler import (
    UpdateBarberAvailabilityHandler,
)
from backend.application.queries.get_available_slots_query import GetAvailableSlotsQuery
from backend.application.queries.list_barber_availabilities_query import (
    ListBarberAvailabilitiesQuery,
)
from backend.core.barber_availability import BarberAvailability
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError


class AvailabilityHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_barber_availability_handler_persists_mapped_window(self):
        db = MagicMock()
        barber_query = MagicMock()
        availability_query = MagicMock()

        db.query.side_effect = [barber_query, availability_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        availability_query.filter.return_value = availability_query
        availability_query.all.return_value = []

        handler = CreateBarberAvailabilityHandler(db)

        result = await handler.handle(
            CreateBarberAvailabilityCommand(
                barber_id=3,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
            )
        )

        self.assertIsInstance(result, BarberAvailability)
        self.assertEqual(result.barber_id, 3)
        self.assertEqual(result.weekday, 0)
        self.assertEqual(result.start_time, time(9, 0))
        self.assertEqual(result.end_time, time(17, 0))
        db.add.assert_called_once_with(result)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)

    async def test_create_barber_availability_handler_rejects_overlap(self):
        db = MagicMock()
        barber_query = MagicMock()
        availability_query = MagicMock()

        db.query.side_effect = [barber_query, availability_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        availability_query.filter.return_value = availability_query
        availability_query.all.return_value = [
            SimpleNamespace(
                id=1,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(12, 0),
            )
        ]

        handler = CreateBarberAvailabilityHandler(db)

        with self.assertRaises(ConflictError) as context:
            await handler.handle(
                CreateBarberAvailabilityCommand(
                    barber_id=3,
                    weekday=0,
                    start_time=time(11, 0),
                    end_time=time(13, 0),
                )
            )

        self.assertEqual(str(context.exception), "Availability window overlaps an existing window")

    async def test_update_barber_availability_handler_maps_fields(self):
        db = MagicMock()
        barber_query = MagicMock()
        existing_query = MagicMock()
        overlap_query = MagicMock()
        update_query = MagicMock()
        availability = SimpleNamespace(
            id=9,
            barber_id=3,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

        db.query.side_effect = [barber_query, existing_query, overlap_query, update_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        existing_query.filter.return_value = existing_query
        existing_query.first.return_value = availability
        overlap_query.filter.return_value = overlap_query
        overlap_query.all.return_value = [availability]
        update_query.filter.return_value = update_query
        update_query.first.return_value = availability

        handler = UpdateBarberAvailabilityHandler(db)

        result = await handler.handle(
            UpdateBarberAvailabilityCommand(
                barber_id=3,
                availability_id=9,
                end_time=time(18, 0),
            )
        )

        self.assertIs(result, availability)
        self.assertEqual(availability.end_time, time(18, 0))
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(availability)

    async def test_list_barber_availabilities_handler_rejects_missing_barber(self):
        db = MagicMock()
        barber_query = MagicMock()

        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None

        handler = ListBarberAvailabilitiesHandler(db)

        with self.assertRaises(NotFoundError) as context:
            await handler.handle(ListBarberAvailabilitiesQuery(barber_id=3))

        self.assertEqual(str(context.exception), "Barber not found")

    async def test_create_barber_block_handler_rejects_invalid_kind(self):
        db = MagicMock()
        barber_query = MagicMock()

        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()

        handler = CreateBarberBlockHandler(db)

        with self.assertRaises(ValidationError) as context:
            await handler.handle(
                CreateBarberBlockCommand(
                    barber_id=3,
                    kind="holiday",
                    start_at=datetime(2026, 3, 16, 12, 0),
                    end_at=datetime(2026, 3, 16, 13, 0),
                    reason="Invalid",
                )
            )

        self.assertEqual(str(context.exception), "Invalid block type")

    async def test_get_available_slots_handler_returns_filtered_slots(self):
        db = MagicMock()
        barber_query = MagicMock()
        service_query = MagicMock()
        availability_query = MagicMock()
        blocks_query = MagicMock()

        db.query.side_effect = [barber_query, service_query, availability_query, blocks_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        service_query.filter.return_value = service_query
        service_query.first.return_value = SimpleNamespace(duracao_minutos=30)
        availability_query.filter.return_value = availability_query
        availability_query.order_by.return_value = availability_query
        availability_query.all.return_value = [
            SimpleNamespace(
                weekday=0,
                start_time=time(9, 0),
                end_time=time(11, 0),
            )
        ]
        blocks_query.filter.return_value = blocks_query
        blocks_query.order_by.return_value = blocks_query
        blocks_query.all.return_value = [
            SimpleNamespace(
                start_at=datetime(2026, 3, 16, 10, 0),
                end_at=datetime(2026, 3, 16, 10, 30),
            )
        ]

        handler = GetAvailableSlotsHandler(db)

        result = await handler.handle(
            GetAvailableSlotsQuery(
                barber_id=3,
                service_id=2,
                target_date=date(2026, 3, 16),
                timezone="Europe/Lisbon",
            )
        )

        self.assertEqual(result["barber_id"], 3)
        self.assertEqual(result["service_id"], 2)
        self.assertEqual(len(result["slots"]), 4)
        self.assertEqual(result["slots"][0]["inicio"].hour, 9)
        self.assertEqual(result["slots"][-1]["inicio"].hour, 10)
        self.assertEqual(result["slots"][-1]["inicio"].minute, 30)


if __name__ == "__main__":
    unittest.main()
