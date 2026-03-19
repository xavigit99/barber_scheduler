import os
import unittest
from datetime import date, datetime, time
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException, Response

from backend.api.routes.availability_routes import (
    create_barber_availability,
    create_barber_block,
    delete_barber_availability,
    delete_barber_block,
    get_available_dates,
    get_available_slots,
    list_barber_availabilities,
    update_barber_availability,
)
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.infrastructure.schemas import (
    BarberAvailabilityCreate,
    BarberAvailabilityUpdate,
    BarberBlockCreate,
)


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class AvailabilityRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_barber_availability_returns_created_payload(self):
        mediator = FakeMediator(
            {
                "id": 1,
                "barber_id": 3,
                "weekday": 0,
                "start_time": time(9, 0),
                "end_time": time(17, 0),
            }
        )

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            result = await create_barber_availability(
                3,
                BarberAvailabilityCreate(
                    dia_semana=0,
                    hora_inicio=time(9, 0),
                    hora_fim=time(17, 0),
                ),
                db=object(),
            )

        self.assertEqual(result["barber_id"], 3)
        self.assertEqual(mediator.requests[0].weekday, 0)
        self.assertEqual(mediator.requests[0].start_time, time(9, 0))

    async def test_create_barber_availability_maps_conflict_to_409(self):
        mediator = FakeMediator(ConflictError("Availability window overlaps an existing window"))

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as context:
                await create_barber_availability(
                    3,
                    BarberAvailabilityCreate(
                        dia_semana=0,
                        hora_inicio=time(9, 0),
                        hora_fim=time(17, 0),
                    ),
                    db=object(),
                )

        self.assertEqual(context.exception.status_code, 409)

    async def test_list_barber_availabilities_returns_payload(self):
        mediator = FakeMediator(
            [
                {
                    "id": 1,
                    "barber_id": 3,
                    "weekday": 0,
                    "start_time": time(9, 0),
                    "end_time": time(17, 0),
                }
            ]
        )

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            result = await list_barber_availabilities(3, db=object())

        self.assertEqual(len(result), 1)
        self.assertEqual(mediator.requests[0].barber_id, 3)

    async def test_update_barber_availability_requires_at_least_one_field(self):
        with patch("backend.api.routes.availability_routes.build_mediator") as build_mediator:
            with self.assertRaises(HTTPException) as context:
                await update_barber_availability(
                    3,
                    9,
                    BarberAvailabilityUpdate(),
                    db=object(),
                )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")
        build_mediator.assert_not_called()

    async def test_delete_barber_availability_returns_no_content_response(self):
        mediator = FakeMediator(True)

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            response = await delete_barber_availability(3, 9, db=object())

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(mediator.requests[0].availability_id, 9)

    async def test_delete_barber_block_raises_not_found_when_missing(self):
        mediator = FakeMediator(False)

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as context:
                await delete_barber_block(3, 4, db=object())

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Availability block not found")

    async def test_create_barber_block_maps_payload_to_command(self):
        mediator = FakeMediator(
            {
                "id": 4,
                "barber_id": 3,
                "kind": "break",
                "start_at": datetime(2026, 3, 16, 12, 0),
                "end_at": datetime(2026, 3, 16, 13, 0),
                "reason": "Lunch",
            }
        )

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            result = await create_barber_block(
                3,
                BarberBlockCreate(
                    tipo="break",
                    inicio=datetime(2026, 3, 16, 12, 0),
                    fim=datetime(2026, 3, 16, 13, 0),
                    motivo="Lunch",
                ),
                db=object(),
            )

        self.assertEqual(result["barber_id"], 3)
        self.assertEqual(mediator.requests[0].kind, "break")
        self.assertEqual(mediator.requests[0].reason, "Lunch")

    async def test_get_available_slots_returns_payload(self):
        mediator = FakeMediator(
            {
                "barber_id": 3,
                "service_id": 2,
                "data": date(2026, 3, 16),
                "timezone": "Europe/Lisbon",
                "slots": [
                    {
                        "inicio": datetime(2026, 3, 16, 9, 0),
                        "fim": datetime(2026, 3, 16, 9, 30),
                    }
                ],
            }
        )

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            result = await get_available_slots(
                3,
                service_id=2,
                target_date=date(2026, 3, 16),
                timezone="Europe/Lisbon",
                db=object(),
            )

        self.assertEqual(result["service_id"], 2)
        self.assertEqual(mediator.requests[0].target_date, date(2026, 3, 16))
        self.assertEqual(mediator.requests[0].timezone, "Europe/Lisbon")

    async def test_get_available_slots_maps_validation_error_to_400(self):
        mediator = FakeMediator(ValidationError("Invalid timezone"))

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as context:
                await get_available_slots(
                    3,
                    service_id=2,
                    target_date=date(2026, 3, 16),
                    timezone="Mars/Olympus",
                    db=object(),
                )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Invalid timezone")

    async def test_get_available_slots_maps_not_found_to_404(self):
        mediator = FakeMediator(NotFoundError("Service not found"))

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as context:
                await get_available_slots(
                    3,
                    service_id=2,
                    target_date=date(2026, 3, 16),
                    timezone="Europe/Lisbon",
                    db=object(),
                )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Service not found")

    async def test_get_available_dates_returns_payload(self):
        mediator = FakeMediator(
            {
                "barber_id": 3,
                "service_id": 2,
                "start_date": date(2026, 3, 1),
                "end_date": date(2026, 3, 31),
                "timezone": "Europe/Lisbon",
                "dates": [date(2026, 3, 16), date(2026, 3, 18)],
            }
        )

        with patch(
            "backend.api.routes.availability_routes.build_mediator",
            return_value=mediator,
        ):
            result = await get_available_dates(
                3,
                service_id=2,
                start_date=date(2026, 3, 1),
                end_date=date(2026, 3, 31),
                timezone="Europe/Lisbon",
                db=object(),
            )

        self.assertEqual(result["dates"], [date(2026, 3, 16), date(2026, 3, 18)])
        self.assertEqual(mediator.requests[0].start_date, date(2026, 3, 1))
        self.assertEqual(mediator.requests[0].end_date, date(2026, 3, 31))


if __name__ == "__main__":
    unittest.main()
