import os
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException
from fastapi.responses import Response

from backend.api.routes.appointment_routes import (
    cancel_appointment,
    create_appointment,
    get_appointment,
    list_barber_appointments,
    list_my_appointments,
    reschedule_appointment,
)
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.schemas import (
    AppointmentCreateRequest,
    AppointmentRescheduleRequest,
)


class FakeMediator:

    def __init__(self, result=None, sequence=None):
        if sequence is not None:
            self.results = list(sequence)
        else:
            self.results = [result]
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if not self.results:
            return None
        next_result = self.results.pop(0)
        if isinstance(next_result, Exception):
            raise next_result
        return next_result


def _admin_user():
    return SimpleNamespace(id=1, role=ADMIN_ROLE)


class AppointmentRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_appointment_returns_created_payload(self):
        now = datetime(2026, 3, 16, 9, 0)
        payload = AppointmentCreateRequest(
            barber_id=3,
            client_id=4,
            service_id=2,
            data_inicio=now,
        )
        mediator = FakeMediator({"id": 1, "start_at": now})

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            result = await create_appointment(payload, db=object())

        self.assertEqual(result["start_at"], now)
        self.assertEqual(mediator.requests[0].barber_id, 3)

    async def test_create_appointment_conflict(self):
        mediator = FakeMediator(ConflictError("Appointment overlaps an existing booking"))
        payload = AppointmentCreateRequest(
            barber_id=3,
            client_id=4,
            service_id=2,
            data_inicio=datetime(2026, 3, 16, 9, 0),
        )

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException) as context:
                await create_appointment(payload, db=object())

        self.assertEqual(context.exception.status_code, 409)

    async def test_reschedule_appointment_maps_conflict(self):
        appointment = SimpleNamespace(id=2, barber_id=3, client_id=4)
        mediator = FakeMediator(
            sequence=[
                appointment,
                ConflictError("Appointment overlaps an existing booking"),
            ]
        )
        payload = AppointmentRescheduleRequest(nova_data_inicio=datetime(2026, 3, 16, 10, 0))

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException) as context:
                await reschedule_appointment(
                    2,
                    payload,
                    db=object(),
                    current_user=_admin_user(),
                )

        self.assertEqual(context.exception.status_code, 409)

    async def test_cancel_appointment_returns_no_content(self):
        appointment = SimpleNamespace(barber_id=3, client_id=4)
        mediator = FakeMediator(sequence=[appointment, True])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            response = await cancel_appointment(
                3,
                db=object(),
                current_user=_admin_user(),
            )

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)

    async def test_cancel_appointment_not_found(self):
        appointment = SimpleNamespace(barber_id=3, client_id=4)
        mediator = FakeMediator(sequence=[appointment, False])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException) as context:
                await cancel_appointment(
                    3,
                    db=object(),
                    current_user=_admin_user(),
                )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Appointment not found")

    async def test_list_barber_appointments_returns_payload(self):
        mediator = FakeMediator([{"id": 1}, {"id": 2}])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            result = await list_barber_appointments(3, db=object())

        self.assertEqual(len(result), 2)

    async def test_list_barber_appointments_filters_date(self):
        mediator = FakeMediator([{"id": 1}])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            result = await list_barber_appointments(
                3, target_date=datetime(2026, 3, 16).date(), db=object()
            )

        self.assertEqual(len(result), 1)

    async def test_list_my_appointments_requires_client_role(self):
        mediator = FakeMediator([{"id": 1}])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            result = await list_my_appointments(
                db=object(),
                current_user=type("User", (), {"id": 4, "role": "client"})(),
            )

        self.assertEqual(len(result), 1)

    async def test_create_appointment_blocks_client_if_mismatch(self):
        mediator = FakeMediator({"id": 1})
        payload = AppointmentCreateRequest(
            barber_id=3,
            client_id=5,
            service_id=2,
            data_inicio=datetime(2026, 3, 16, 9, 0),
        )

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException) as context:
                await create_appointment(
                    payload,
                    db=object(),
                    current_user=type("User", (), {"id": 4, "role": "client"})(),
                )

        self.assertEqual(context.exception.status_code, 403)

    async def test_get_appointment_not_found(self):
        mediator = FakeMediator(None)

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException):
                await get_appointment(5, db=object())
