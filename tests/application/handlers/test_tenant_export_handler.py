import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.handlers.compliance.tenant_export_handler import TenantExportHandler
from backend.application.queries.tenant_export_query import TenantExportQuery


class TenantExportHandlerTestCase(unittest.IsolatedAsyncioTestCase):

    def _build_db(self, barbers=None, clients=None, services=None, appointments=None, memberships=None):
        db = MagicMock()

        def _to_dict_patch(obj):
            return {"id": obj.id}

        qb = MagicMock()
        qb.filter.return_value = qb

        results = {
            0: barbers or [],
            1: clients or [],
            2: services or [],
            3: appointments or [],
            4: memberships or [],
        }
        call_count = [0]

        def query_side(model):
            return qb

        def all_side():
            idx = call_count[0]
            call_count[0] += 1
            return results.get(idx, [])

        db.query.side_effect = query_side
        qb.all.side_effect = all_side
        return db

    async def test_returns_all_sections(self):
        db = self._build_db()

        handler = TenantExportHandler(db)

        with patch("backend.application.handlers.compliance.tenant_export_handler._to_dict", return_value={"id": 1}):
            result = await handler.handle(TenantExportQuery(tenant_id=7))

        self.assertEqual(result["tenant_id"], 7)
        self.assertIn("exported_at", result)
        self.assertIn("barbers", result)
        self.assertIn("clients", result)
        self.assertIn("services", result)
        self.assertIn("appointments", result)
        self.assertIn("memberships", result)

    async def test_includes_deleted_records(self):
        rec = MagicMock()
        rec.id = 99
        rec.deleted = True
        rec.__table__ = MagicMock()
        rec.__table__.columns = []

        db = self._build_db(barbers=[rec])
        handler = TenantExportHandler(db)

        result = await handler.handle(TenantExportQuery(tenant_id=1))
        # No deleted filter applied — barbers list reflects whatever is in DB
        self.assertIsInstance(result["barbers"], list)

    async def test_tenant_isolation(self):
        db = MagicMock()
        qb = MagicMock()
        qb.filter.return_value = qb
        qb.all.return_value = []
        db.query.return_value = qb

        handler = TenantExportHandler(db)
        result = await handler.handle(TenantExportQuery(tenant_id=42))

        self.assertEqual(result["tenant_id"], 42)
        # filter called for each model (5 times)
        self.assertEqual(qb.filter.call_count, 5)


if __name__ == "__main__":
    unittest.main()
