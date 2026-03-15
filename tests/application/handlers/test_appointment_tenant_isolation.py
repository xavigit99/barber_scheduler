import os
import unittest
from datetime import datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_appointment_command import CreateAppointmentCommand
from backend.application.handlers.appointment.create_appointment_handler import (
    CreateAppointmentHandler,
)
from backend.core.exceptions import NotFoundError


class AppointmentTenantIsolationTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_appointment_uses_tenant_filter(self):
        """Barber from a different tenant raises NotFoundError."""
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not found in tenant 99

        handler = CreateAppointmentHandler(db)
        command = CreateAppointmentCommand(
            barber_id=3,
            client_id=4,
            service_id=1,
            start_at=datetime(2026, 3, 16, 9, 0),
            tenant_id=99,
        )

        with self.assertRaises(NotFoundError) as context:
            await handler.handle(command)

        self.assertIn("Barber", str(context.exception))

    async def test_create_appointment_stores_tenant_id(self):
        """Created appointment carries the tenant_id from the command."""
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
        service_query.first.return_value = SimpleNamespace(id=1, duracao_minutos=30)
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
            tenant_id=5,
        )

        result = await handler.handle(command)
        self.assertEqual(result.tenant_id, 5)
