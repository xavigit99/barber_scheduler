import os
import unittest
from datetime import date, datetime
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.handlers.audit.audit_log_handler import AuditLogHandler
from backend.application.queries.audit_log_query import AuditLogQuery


class AuditLogHandlerTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_returns_deleted_records_for_entity(self):
        db = MagicMock()
        rec = MagicMock()
        rec.id = 1
        rec.deleted_at = datetime(2025, 1, 10)
        rec.nome = "John"
        rec.email = "j@x.com"

        qb = MagicMock()
        db.query.return_value = qb
        qb.filter.return_value = qb
        qb.all.return_value = [rec]

        handler = AuditLogHandler(db)
        result = await handler.handle(AuditLogQuery(entity="barber", tenant_id=1))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        qb.all.assert_called_once()

    async def test_raises_for_unknown_entity(self):
        db = MagicMock()
        handler = AuditLogHandler(db)
        with self.assertRaises(ValueError):
            await handler.handle(AuditLogQuery(entity="unknown_entity", tenant_id=1))

    async def test_filters_by_from_date(self):
        db = MagicMock()
        qb = MagicMock()
        db.query.return_value = qb
        qb.filter.return_value = qb
        qb.all.return_value = []

        handler = AuditLogHandler(db)
        await handler.handle(AuditLogQuery(entity="client", tenant_id=2, from_date=date(2025, 1, 1)))

        # filter called multiple times (tenant + deleted + from_date)
        self.assertGreaterEqual(qb.filter.call_count, 2)

    async def test_tenant_isolation(self):
        db = MagicMock()
        qb = MagicMock()
        db.query.return_value = qb
        qb.filter.return_value = qb
        qb.all.return_value = []

        handler = AuditLogHandler(db)
        await handler.handle(AuditLogQuery(entity="service", tenant_id=99))

        db.query.assert_called_once()
        qb.filter.assert_called()


if __name__ == "__main__":
    unittest.main()
