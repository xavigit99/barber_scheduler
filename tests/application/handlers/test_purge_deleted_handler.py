import os
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.purge_deleted_command import PurgeDeletedCommand
from backend.application.handlers.retention.purge_deleted_handler import PurgeDeletedHandler


class PurgeDeletedHandlerTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_hard_deletes_old_deleted_records(self):
        db = MagicMock()
        old_time = datetime.now(UTC) - timedelta(days=100)

        rec1 = MagicMock()
        rec1.deleted = True
        rec1.deleted_at = old_time
        rec1.tenant_id = 1

        qb = MagicMock()
        db.query.return_value = qb
        qb.filter.return_value = qb
        qb.all.return_value = [rec1]

        handler = PurgeDeletedHandler(db)
        result = await handler.handle(PurgeDeletedCommand(entity="barber", older_than_days=90, tenant_id=1))

        db.delete.assert_called_once_with(rec1)
        db.commit.assert_called_once()
        self.assertEqual(result["purged_count"], 1)
        self.assertEqual(result["entity"], "barber")

    async def test_does_not_touch_other_tenant(self):
        db = MagicMock()
        qb = MagicMock()
        db.query.return_value = qb
        qb.filter.return_value = qb
        qb.all.return_value = []

        handler = PurgeDeletedHandler(db)
        result = await handler.handle(PurgeDeletedCommand(entity="client", older_than_days=30, tenant_id=5))

        db.delete.assert_not_called()
        db.commit.assert_not_called()
        self.assertEqual(result["purged_count"], 0)

    async def test_raises_for_unknown_entity(self):
        db = MagicMock()
        handler = PurgeDeletedHandler(db)
        with self.assertRaises(ValueError):
            await handler.handle(PurgeDeletedCommand(entity="nonexistent", older_than_days=30, tenant_id=1))

    async def test_no_commit_when_nothing_to_purge(self):
        db = MagicMock()
        qb = MagicMock()
        db.query.return_value = qb
        qb.filter.return_value = qb
        qb.all.return_value = []

        handler = PurgeDeletedHandler(db)
        await handler.handle(PurgeDeletedCommand(entity="service", older_than_days=90, tenant_id=1))

        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
