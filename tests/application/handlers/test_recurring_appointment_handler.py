import os
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_recurring_appointment_command import (
    CreateRecurringAppointmentCommand,
)
from backend.application.handlers.appointment.create_recurring_appointment_handler import (
    CreateRecurringAppointmentHandler,
)
from backend.core.exceptions import NotFoundError, ValidationError


def _make_barber(id=1):
    return SimpleNamespace(id=id, nome="Barber")


def _make_client(id=1):
    return SimpleNamespace(id=id, nome="Client")


def _make_service(id=1, duracao_minutos=30):
    return SimpleNamespace(id=id, nome="Corte", duracao_minutos=duracao_minutos)


def _setup_db(barber=None, client=None, service=None, overlap_results=None):
    """Build a MagicMock db for CreateRecurringAppointmentHandler.

    Query call order:
      1. Barber (via BaseRepository.get → db.query(Barber).filter().first())
      2. Client (via BaseRepository.get)
      3. Service (via BaseRepository.get)
      4..N. Appointment overlap checks (one per iteration)
    """
    db = MagicMock()

    barber_q = MagicMock()
    barber_q.filter.return_value = barber_q
    barber_q.first.return_value = barber

    client_q = MagicMock()
    client_q.filter.return_value = client_q
    client_q.first.return_value = client

    service_q = MagicMock()
    service_q.filter.return_value = service_q
    service_q.first.return_value = service

    if overlap_results is None:
        overlap_results = []

    overlap_queries = []
    for result in overlap_results:
        oq = MagicMock()
        oq.filter.return_value = oq
        oq.first.return_value = result
        overlap_queries.append(oq)

    db.query.side_effect = [barber_q, client_q, service_q, *overlap_queries]
    return db


class TestRecurringAppointmentHandler(unittest.IsolatedAsyncioTestCase):

    async def test_invalid_recurrence_raises(self):
        db = MagicMock()
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=1, client_id=1, service_id=1,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="monthly", count=4, tenant_id=1,
        )
        with self.assertRaises(ValidationError):
            await handler.handle(cmd)

    async def test_invalid_count_raises(self):
        db = MagicMock()
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=1, client_id=1, service_id=1,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="weekly", count=13, tenant_id=1,
        )
        with self.assertRaises(ValidationError):
            await handler.handle(cmd)

    async def test_barber_not_found_raises(self):
        db = _setup_db(barber=None)
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=99, client_id=1, service_id=1,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="weekly", count=3, tenant_id=1,
        )
        with self.assertRaises(NotFoundError):
            await handler.handle(cmd)

    async def test_client_not_found_raises(self):
        db = _setup_db(barber=_make_barber(), client=None)
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=1, client_id=99, service_id=1,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="weekly", count=3, tenant_id=1,
        )
        with self.assertRaises(NotFoundError):
            await handler.handle(cmd)

    async def test_service_not_found_raises(self):
        db = _setup_db(barber=_make_barber(), client=_make_client(), service=None)
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=1, client_id=1, service_id=99,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="weekly", count=3, tenant_id=1,
        )
        with self.assertRaises(NotFoundError):
            await handler.handle(cmd)

    @patch("backend.core.webhook_dispatcher.dispatch_webhook_event")
    async def test_weekly_creates_n_appointments_no_conflicts(self, mock_dispatch):
        # 3 weekly appointments, no conflicts
        db = _setup_db(
            barber=_make_barber(),
            client=_make_client(),
            service=_make_service(duracao_minutos=30),
            overlap_results=[None, None, None],
        )
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=1, client_id=1, service_id=1,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="weekly", count=3, tenant_id=1,
        )
        result = await handler.handle(cmd)

        assert len(result["created"]) == 3
        assert result["skipped_count"] == 0
        db.add_all.assert_called_once()
        db.commit.assert_called_once()

    @patch("backend.core.webhook_dispatcher.dispatch_webhook_event")
    async def test_skips_conflicting_slots(self, mock_dispatch):
        # 3 slots: first has conflict, second and third are free
        conflict = SimpleNamespace(id=99)
        db = _setup_db(
            barber=_make_barber(),
            client=_make_client(),
            service=_make_service(duracao_minutos=30),
            overlap_results=[conflict, None, None],
        )
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=1, client_id=1, service_id=1,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="weekly", count=3, tenant_id=1,
        )
        result = await handler.handle(cmd)

        assert len(result["created"]) == 2
        assert result["skipped_count"] == 1

    @patch("backend.core.webhook_dispatcher.dispatch_webhook_event")
    async def test_biweekly_spacing(self, mock_dispatch):
        # 2 biweekly appointments
        db = _setup_db(
            barber=_make_barber(),
            client=_make_client(),
            service=_make_service(duracao_minutos=60),
            overlap_results=[None, None],
        )
        handler = CreateRecurringAppointmentHandler(db)
        cmd = CreateRecurringAppointmentCommand(
            barber_id=1, client_id=1, service_id=1,
            start_at=datetime(2026, 4, 1, 10, 0),
            recurrence="biweekly", count=2, tenant_id=1,
        )
        result = await handler.handle(cmd)

        created = result["created"]
        assert len(created) == 2
        # Second appointment should be 2 weeks after first
        delta = created[1].start_at - created[0].start_at
        assert delta == timedelta(weeks=2)
