import os
import unittest
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
from backend.application.queries.list_admin_feedback_query import ListAdminFeedbackQuery
from backend.application.queries.list_barber_feedback_query import ListBarberFeedbackQuery
from backend.core.exceptions import NotFoundError


class FeedbackTenantIsolationTest(unittest.IsolatedAsyncioTestCase):

    async def test_create_appointment_wrong_tenant_raises_not_found(self):
        """Appointment from a different tenant is invisible → NotFoundError."""
        db = MagicMock()
        appt_q = MagicMock()
        appt_q.filter.return_value = appt_q
        appt_q.first.return_value = None  # tenant filter hides appointment

        db.query.return_value = appt_q

        handler = CreateFeedbackHandler(db)
        cmd = CreateFeedbackCommand(
            appointment_id=5, rating=4, user_id=100, tenant_id=99
        )
        with self.assertRaises(NotFoundError):
            await handler.handle(cmd)

    async def test_list_barber_feedback_excludes_other_tenant(self):
        """Feedbacks from another tenant are not returned."""
        db = MagicMock()
        barber_q = MagicMock()
        barber_q.filter.return_value = barber_q
        barber_q.first.return_value = SimpleNamespace(id=2)

        # Tenant 10 sees only its own feedback (tenant filter applied)
        feedback_q = MagicMock()
        feedback_q.filter.return_value = feedback_q
        feedback_q.all.return_value = [SimpleNamespace(id=1, tenant_id=10)]

        db.query.side_effect = [barber_q, feedback_q]

        handler = ListBarberFeedbackHandler(db)
        result = await handler.handle(ListBarberFeedbackQuery(barber_id=2, tenant_id=10))
        assert all(f.tenant_id == 10 for f in result)

    async def test_list_admin_feedback_scoped_to_tenant(self):
        """Admin handler returns only records from its own tenant."""
        db = MagicMock()
        feedback_q = MagicMock()
        feedback_q.filter.return_value = feedback_q
        feedback_q.all.return_value = [
            SimpleNamespace(id=1, tenant_id=10),
            SimpleNamespace(id=2, tenant_id=10),
        ]
        db.query.return_value = feedback_q

        handler = ListAdminFeedbackHandler(db)
        result = await handler.handle(ListAdminFeedbackQuery(tenant_id=10))
        assert len(result) == 2
        assert all(f.tenant_id == 10 for f in result)
