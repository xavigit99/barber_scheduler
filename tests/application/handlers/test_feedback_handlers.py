import os
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_feedback_command import CreateFeedbackCommand
from backend.application.handlers.feedback.create_feedback_handler import CreateFeedbackHandler
from backend.application.handlers.feedback.list_admin_feedback_handler import (
    ListAdminFeedbackHandler,
)
from backend.application.handlers.feedback.list_barber_feedback_handler import (
    ListBarberFeedbackHandler,
)
from backend.application.handlers.feedback.list_my_feedback_handler import ListMyFeedbackHandler
from backend.application.queries.list_admin_feedback_query import ListAdminFeedbackQuery
from backend.application.queries.list_barber_feedback_query import ListBarberFeedbackQuery
from backend.application.queries.list_my_feedback_query import ListMyFeedbackQuery
from backend.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError


def _make_appointment(client_id=1, barber_id=2, tenant_id=10, end_at=None):
    if end_at is None:
        end_at = datetime(2020, 1, 1, 10, 0)  # past
    return SimpleNamespace(
        id=5,
        client_id=client_id,
        barber_id=barber_id,
        tenant_id=tenant_id,
        end_at=end_at,
    )


def _make_client(id=1, user_id=100):
    return SimpleNamespace(id=id, user_id=user_id)


def _setup_create_db(appointment=None, client=None, existing_feedback=None):
    """Return a MagicMock db configured for CreateFeedbackHandler queries."""
    db = MagicMock()

    # query call order: Appointment (via BaseRepository), Client, Feedback
    appt_q = MagicMock()
    appt_q.filter.return_value = appt_q
    appt_q.first.return_value = appointment

    client_q = MagicMock()
    client_q.filter.return_value = client_q
    client_q.first.return_value = client

    feedback_q = MagicMock()
    feedback_q.filter.return_value = feedback_q
    feedback_q.first.return_value = existing_feedback

    db.query.side_effect = [appt_q, client_q, feedback_q]
    return db


class CreateFeedbackHandlerTest(unittest.IsolatedAsyncioTestCase):

    async def test_create_persists_feedback(self):
        appointment = _make_appointment()
        client = _make_client()
        db = _setup_create_db(appointment=appointment, client=client)

        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(
            appointment_id=5, rating=4, user_id=100, tenant_id=10, comentario="Ótimo!"
        )
        await handler.handle(cmd)

        db.add.assert_called_once()
        db.commit.assert_called_once()
        added = db.add.call_args[0][0]
        assert added.rating == 4
        assert added.comentario == "Ótimo!"
        assert added.client_id == 1
        assert added.barber_id == 2

    async def test_create_rating_zero_raises_validation(self):
        db = MagicMock()
        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(appointment_id=5, rating=0, user_id=100, tenant_id=10)
        with self.assertRaises(ValidationError):
            await handler.handle(cmd)

    async def test_create_rating_six_raises_validation(self):
        db = MagicMock()
        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(appointment_id=5, rating=6, user_id=100, tenant_id=10)
        with self.assertRaises(ValidationError):
            await handler.handle(cmd)

    async def test_create_appointment_not_found_raises(self):
        db = _setup_create_db(appointment=None)
        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(appointment_id=99, rating=3, user_id=100, tenant_id=10)
        with self.assertRaises(NotFoundError):
            await handler.handle(cmd)

    async def test_create_client_not_owner_raises_forbidden(self):
        # appointment belongs to client_id=1, but user resolves to client_id=2
        appointment = _make_appointment(client_id=1)
        client = _make_client(id=2, user_id=100)
        db = _setup_create_db(appointment=appointment, client=client)
        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(appointment_id=5, rating=3, user_id=100, tenant_id=10)
        with self.assertRaises(ForbiddenError):
            await handler.handle(cmd)

    async def test_create_future_appointment_raises_validation(self):
        future = datetime(2099, 1, 1, 10, 0)
        appointment = _make_appointment(end_at=future)
        client = _make_client()
        db = _setup_create_db(appointment=appointment, client=client)
        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(appointment_id=5, rating=3, user_id=100, tenant_id=10)
        with self.assertRaises(ValidationError):
            await handler.handle(cmd)

    async def test_create_duplicate_raises_conflict(self):
        appointment = _make_appointment()
        client = _make_client()
        existing = SimpleNamespace(id=7)
        db = _setup_create_db(appointment=appointment, client=client, existing_feedback=existing)
        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(appointment_id=5, rating=3, user_id=100, tenant_id=10)
        with self.assertRaises(ConflictError):
            await handler.handle(cmd)


class ListBarberFeedbackHandlerTest(unittest.IsolatedAsyncioTestCase):

    async def test_returns_feedback_list(self):
        db = MagicMock()
        barber_q = MagicMock()
        barber_q.filter.return_value = barber_q
        barber_q.first.return_value = SimpleNamespace(id=2)

        feedback_q = MagicMock()
        feedback_q.filter.return_value = feedback_q
        feedback_q.all.return_value = [SimpleNamespace(id=1), SimpleNamespace(id=2)]

        db.query.side_effect = [barber_q, feedback_q]

        handler = ListBarberFeedbackHandler(db)
        result = await handler.handle(ListBarberFeedbackQuery(barber_id=2, tenant_id=10))
        assert len(result) == 2

    async def test_barber_not_found_raises(self):
        db = MagicMock()
        barber_q = MagicMock()
        barber_q.filter.return_value = barber_q
        barber_q.first.return_value = None
        db.query.return_value = barber_q

        handler = ListBarberFeedbackHandler(db)
        with self.assertRaises(NotFoundError):
            await handler.handle(ListBarberFeedbackQuery(barber_id=99, tenant_id=10))


class ListMyFeedbackHandlerTest(unittest.IsolatedAsyncioTestCase):

    async def test_returns_feedback_list(self):
        db = MagicMock()
        client_q = MagicMock()
        client_q.filter.return_value = client_q
        client_q.first.return_value = SimpleNamespace(id=1)

        feedback_q = MagicMock()
        feedback_q.filter.return_value = feedback_q
        feedback_q.all.return_value = [SimpleNamespace(id=1)]

        db.query.side_effect = [client_q, feedback_q]

        handler = ListMyFeedbackHandler(db)
        result = await handler.handle(ListMyFeedbackQuery(user_id=100, tenant_id=10))
        assert len(result) == 1

    async def test_client_not_found_returns_empty(self):
        db = MagicMock()
        client_q = MagicMock()
        client_q.filter.return_value = client_q
        client_q.first.return_value = None
        db.query.return_value = client_q

        handler = ListMyFeedbackHandler(db)
        result = await handler.handle(ListMyFeedbackQuery(user_id=999, tenant_id=10))
        assert result == []


class ListAdminFeedbackHandlerTest(unittest.IsolatedAsyncioTestCase):

    async def test_returns_all_tenant_feedback(self):
        db = MagicMock()
        feedback_q = MagicMock()
        feedback_q.filter.return_value = feedback_q
        feedback_q.all.return_value = [
            SimpleNamespace(id=1),
            SimpleNamespace(id=2),
            SimpleNamespace(id=3),
        ]
        db.query.return_value = feedback_q

        handler = ListAdminFeedbackHandler(db)
        result = await handler.handle(ListAdminFeedbackQuery(tenant_id=10))
        assert len(result) == 3
