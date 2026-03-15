import os
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException
from fastapi.responses import Response

from backend.api.routes.appointment_routes import (
    _authorize_user_for_appointment,
    cancel_appointment,
    create_appointment,
    get_appointment,
    list_barber_appointments,
    list_my_appointments,
    reschedule_appointment,
)
from backend.core.exceptions import ConflictError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE
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


def _barber_user(user_id=2):
    return SimpleNamespace(id=user_id, role=BARBER_ROLE)


def _client_user(user_id=4):
    return SimpleNamespace(id=user_id, role=CLIENT_ROLE)


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
                    db=MagicMock(),
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
                db=MagicMock(),
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
                    db=MagicMock(),
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

    async def test_list_barber_appointments_barber_can_view_own(self):
        db = MagicMock()
        barber_query = MagicMock()
        barber = SimpleNamespace(id=3, user_id=2)
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = barber
        mediator = FakeMediator([{"id": 1}])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            result = await list_barber_appointments(
                3, db=db, current_user=_barber_user(user_id=2)
            )

        self.assertEqual(len(result), 1)

    async def test_list_barber_appointments_barber_blocked_from_other(self):
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not linked to this user
        mediator = FakeMediator([{"id": 1}])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException) as context:
                await list_barber_appointments(
                    3, db=db, current_user=_barber_user(user_id=99)
                )

        self.assertEqual(context.exception.status_code, 403)

    async def test_list_my_appointments_returns_client_appointments(self):
        db = MagicMock()
        client_query = MagicMock()
        client = SimpleNamespace(id=4)
        db.query.return_value = client_query
        client_query.filter.return_value = client_query
        client_query.first.return_value = client

        mediator = FakeMediator([{"id": 1}])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            result = await list_my_appointments(
                db=db,
                current_user=_client_user(user_id=4),
            )

        self.assertEqual(len(result), 1)

    async def test_list_my_appointments_returns_empty_when_no_client(self):
        db = MagicMock()
        client_query = MagicMock()
        db.query.return_value = client_query
        client_query.filter.return_value = client_query
        client_query.first.return_value = None

        mediator = FakeMediator([])

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            result = await list_my_appointments(
                db=db,
                current_user=_client_user(user_id=99),
            )

        self.assertEqual(result, [])

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
                    current_user=_client_user(user_id=4),
                )

        self.assertEqual(context.exception.status_code, 403)

    async def test_get_appointment_not_found(self):
        mediator = FakeMediator(None)

        with patch(
            "backend.api.routes.appointment_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException):
                await get_appointment(5, db=object())

    async def test_authorize_admin_always_passes(self):
        db = MagicMock()
        appointment = SimpleNamespace(barber_id=1, client_id=2)
        # Should not raise
        _authorize_user_for_appointment(_admin_user(), appointment, db)
        db.query.assert_not_called()

    async def test_authorize_barber_with_matching_user_id(self):
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = SimpleNamespace(id=3)

        appointment = SimpleNamespace(barber_id=3, client_id=2)
        # Should not raise
        _authorize_user_for_appointment(_barber_user(user_id=2), appointment, db)

    async def test_authorize_barber_without_matching_raises_403(self):
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None

        appointment = SimpleNamespace(barber_id=3, client_id=2)
        with self.assertRaises(HTTPException) as context:
            _authorize_user_for_appointment(_barber_user(user_id=99), appointment, db)

        self.assertEqual(context.exception.status_code, 403)

    async def test_authorize_client_with_matching_user_id(self):
        db = MagicMock()
        client_query = MagicMock()
        db.query.return_value = client_query
        client_query.filter.return_value = client_query
        client_query.first.return_value = SimpleNamespace(id=2)

        appointment = SimpleNamespace(barber_id=3, client_id=2)
        # Should not raise
        _authorize_user_for_appointment(_client_user(user_id=4), appointment, db)

    async def test_authorize_client_without_matching_raises_403(self):
        db = MagicMock()
        client_query = MagicMock()
        db.query.return_value = client_query
        client_query.filter.return_value = client_query
        client_query.first.return_value = None

        appointment = SimpleNamespace(barber_id=3, client_id=2)
        with self.assertRaises(HTTPException) as context:
            _authorize_user_for_appointment(_client_user(user_id=99), appointment, db)

        self.assertEqual(context.exception.status_code, 403)
