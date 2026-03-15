import os
import unittest
from datetime import date, datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.cancel_appointment_command import (
    CancelAppointmentCommand,
)
from backend.application.commands.create_appointment_command import CreateAppointmentCommand
from backend.application.commands.reschedule_appointment_command import (
    RescheduleAppointmentCommand,
)
from backend.application.handlers.appointment.cancel_appointment_handler import (
    CancelAppointmentHandler,
)
from backend.application.handlers.appointment.create_appointment_handler import (
    CreateAppointmentHandler,
)
from backend.application.handlers.appointment.list_barber_appointments_handler import (
    ListBarberAppointmentsHandler,
)
from backend.application.handlers.appointment.list_client_appointments_handler import (
    ListClientAppointmentsHandler,
)
from backend.application.handlers.appointment.reschedule_appointment_handler import (
    RescheduleAppointmentHandler,
)
from backend.application.queries.list_barber_appointments_query import (
    ListBarberAppointmentsQuery,
)
from backend.application.queries.list_client_appointments_query import (
    ListClientAppointmentsQuery,
)
from backend.core.exceptions import ConflictError


class AppointmentHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_appointment_handler_persists_slot(self):
        db = MagicMock()
        barber_query = MagicMock()
        client_query = MagicMock()
        service_query = MagicMock()
        availability_query = MagicMock()
        block_query = MagicMock()
        appointment_query = MagicMock()

        db.query.side_effect = [
            barber_query,
            client_query,
            service_query,
            availability_query,
            block_query,
            appointment_query,
        ]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        client_query.filter.return_value = client_query
        client_query.first.return_value = object()
        service_query.filter.return_value = service_query
        service_query.first.return_value = SimpleNamespace(
            id=1, duracao_minutos=30
        )
        availability_query.filter.return_value = availability_query
        availability_query.all.return_value = [
            SimpleNamespace(weekday=0, start_time=time(9, 0), end_time=time(17, 0))
        ]
        block_query.filter.return_value = block_query
        block_query.all.return_value = []
        appointment_query.filter.return_value = appointment_query
        appointment_query.first.return_value = None

        handler = CreateAppointmentHandler(db)
        command = CreateAppointmentCommand(
            barber_id=3,
            client_id=4,
            service_id=1,
            start_at=datetime(2026, 3, 16, 9, 0),
        )

        result = await handler.handle(command)

        self.assertEqual(result.barber_id, 3)
        self.assertEqual(result.end_at.hour, 9 + 0)
        self.assertEqual(result.end_at.minute, 30)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)

    async def test_create_appointment_handler_rejects_conflict(self):
        db = MagicMock()
        barber_query = MagicMock()
        client_query = MagicMock()
        service_query = MagicMock()
        availability_query = MagicMock()
        block_query = MagicMock()
        appointment_query = MagicMock()

        db.query.side_effect = [
            barber_query,
            client_query,
            service_query,
            availability_query,
            block_query,
            appointment_query,
        ]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        client_query.filter.return_value = client_query
        client_query.first.return_value = object()
        service_query.filter.return_value = service_query
        service_query.first.return_value = SimpleNamespace(
            id=1, duracao_minutos=30
        )
        availability_query.filter.return_value = availability_query
        availability_query.all.return_value = [
            SimpleNamespace(weekday=0, start_time=time(9, 0), end_time=time(17, 0))
        ]
        block_query.filter.return_value = block_query
        block_query.all.return_value = []
        appointment_query.filter.return_value = appointment_query
        appointment_query.first.return_value = SimpleNamespace()

        handler = CreateAppointmentHandler(db)

        with self.assertRaises(ConflictError):
            await handler.handle(
                CreateAppointmentCommand(
                    barber_id=3,
                    client_id=4,
                    service_id=1,
                    start_at=datetime(2026, 3, 16, 9, 0),
                )
            )

    async def test_reschedule_appointment_handler_updates_window(self):
        db = MagicMock()
        appointment_query_initial = MagicMock()
        appointment_query_overlap = MagicMock()
        service_query = MagicMock()
        availability_query = MagicMock()
        block_query = MagicMock()
        appointment = SimpleNamespace(
            id=2,
            barber_id=5,
            service_id=1,
            deleted=False,
            start_at=datetime(2026, 3, 16, 9, 0),
            end_at=datetime(2026, 3, 16, 9, 30),
        )
        db.query.side_effect = [
            appointment_query_initial,
            service_query,
            availability_query,
            block_query,
            appointment_query_overlap,
        ]
        appointment_query_initial.filter.return_value = appointment_query_initial
        appointment_query_initial.first.return_value = appointment
        appointment_query_overlap.filter.return_value = appointment_query_overlap
        appointment_query_overlap.first.return_value = None
        service_query.filter.return_value = service_query
        service_query.first.return_value = SimpleNamespace(
            id=1, duracao_minutos=30
        )
        availability_query.filter.return_value = availability_query
        availability_query.all.return_value = [
            SimpleNamespace(weekday=0, start_time=time(9, 0), end_time=time(17, 0))
        ]
        block_query.filter.return_value = block_query
        block_query.all.return_value = []

        handler = RescheduleAppointmentHandler(db)

        result = await handler.handle(
            RescheduleAppointmentCommand(
                appointment_id=2,
                start_at=datetime(2026, 3, 16, 10, 0),
            )
        )

        self.assertEqual(result.start_at.hour, 10)
        self.assertEqual(result.end_at.hour, 10)

    async def test_cancel_appointment_handler_marks_deleted(self):
        db = MagicMock()
        query = MagicMock()
        appointment = SimpleNamespace(deleted=False)
        db.query.return_value = query
        query.filter.return_value = query
        query.first.return_value = appointment

        handler = CancelAppointmentHandler(db)

        result = await handler.handle(CancelAppointmentCommand(appointment_id=3))

        self.assertTrue(result)
        self.assertTrue(appointment.deleted)
        db.commit.assert_called_once_with()

    async def test_list_barber_appointments_handler_filters_deleted(self):
        db = MagicMock()
        barber_query = MagicMock()
        appointment_query = MagicMock()

        db.query.side_effect = [barber_query, appointment_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        appointment_query.filter.return_value = appointment_query
        appointment_query.order_by.return_value = appointment_query
        appointment_query.all.return_value = [SimpleNamespace(id=1)]

        handler = ListBarberAppointmentsHandler(db)

        result = await handler.handle(ListBarberAppointmentsQuery(barber_id=5))

        self.assertEqual(result[0].id, 1)

    async def test_list_client_appointments_restricts_date(self):
        db = MagicMock()
        client_query = MagicMock()
        appointment_query = MagicMock()
        db.query.side_effect = [client_query, appointment_query]
        client_query.filter.return_value = client_query
        client_query.first.return_value = object()
        appointment_query.filter.return_value = appointment_query
        appointment_query.order_by.return_value = appointment_query
        appointment_query.all.return_value = [SimpleNamespace(id=7)]

        handler = ListClientAppointmentsHandler(db)

        result = await handler.handle(
            ListClientAppointmentsQuery(
                client_id=9,
                target_date=date(2026, 3, 16),
            )
        )

        self.assertEqual(result[0].id, 7)
