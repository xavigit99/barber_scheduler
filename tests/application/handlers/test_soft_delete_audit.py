import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.delete_barber_availability_command import (
    DeleteBarberAvailabilityCommand,
)
from backend.application.commands.delete_barber_block_command import DeleteBarberBlockCommand
from backend.application.handlers.availability.delete_barber_availability_handler import (
    DeleteBarberAvailabilityHandler,
)
from backend.application.handlers.availability.delete_barber_block_handler import (
    DeleteBarberBlockHandler,
)
from backend.core.barber_availability import BarberAvailability
from repositories.base_repository import BaseRepository


class SoftDeleteAuditTestCase(unittest.IsolatedAsyncioTestCase):

    def test_base_repository_delete_stamps_deleted_at(self):
        """BaseRepository.delete() sets deleted_at when the model has that column."""
        db = MagicMock()
        query = MagicMock()
        db.query.return_value = query
        query.filter.return_value = query

        obj = MagicMock()
        obj.deleted = False
        obj.deleted_at = None
        query.first.return_value = obj

        repo = BaseRepository(BarberAvailability, db)
        result = repo.delete(1)

        self.assertTrue(result)
        self.assertTrue(obj.deleted)
        self.assertIsNotNone(obj.deleted_at)
        self.assertIsInstance(obj.deleted_at, datetime)
        db.commit.assert_called_once()

    def test_base_repository_delete_returns_false_when_not_found(self):
        db = MagicMock()
        query = MagicMock()
        db.query.return_value = query
        query.filter.return_value = query
        query.first.return_value = None

        repo = BaseRepository(BarberAvailability, db)
        result = repo.delete(99)

        self.assertFalse(result)
        db.commit.assert_not_called()

    async def test_delete_barber_availability_handler_stamps_deleted_at(self):
        """DeleteBarberAvailabilityHandler stamps deleted_at on soft-delete."""
        db = MagicMock()
        barber_query = MagicMock()
        avail_query = MagicMock()
        db.query.side_effect = [barber_query, avail_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()  # barber found

        availability = MagicMock()
        availability.deleted = False
        availability.deleted_at = None
        avail_query.filter.return_value = avail_query
        avail_query.first.return_value = availability

        handler = DeleteBarberAvailabilityHandler(db)
        result = await handler.handle(
            DeleteBarberAvailabilityCommand(barber_id=1, availability_id=2, tenant_id=10)
        )

        self.assertTrue(result)
        self.assertTrue(availability.deleted)
        self.assertIsNotNone(availability.deleted_at)
        self.assertIsInstance(availability.deleted_at, datetime)
        db.commit.assert_called_once()

    async def test_delete_barber_block_handler_stamps_deleted_at(self):
        """DeleteBarberBlockHandler stamps deleted_at on soft-delete."""
        db = MagicMock()
        barber_query = MagicMock()
        block_query = MagicMock()
        db.query.side_effect = [barber_query, block_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()  # barber found

        block = MagicMock()
        block.deleted = False
        block.deleted_at = None
        block_query.filter.return_value = block_query
        block_query.first.return_value = block

        handler = DeleteBarberBlockHandler(db)
        result = await handler.handle(
            DeleteBarberBlockCommand(barber_id=1, block_id=5, tenant_id=10)
        )

        self.assertTrue(result)
        self.assertTrue(block.deleted)
        self.assertIsNotNone(block.deleted_at)
        self.assertIsInstance(block.deleted_at, datetime)
        db.commit.assert_called_once()

    async def test_delete_barber_availability_handler_returns_false_when_barber_missing(self):
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None

        handler = DeleteBarberAvailabilityHandler(db)
        result = await handler.handle(
            DeleteBarberAvailabilityCommand(barber_id=1, availability_id=2, tenant_id=10)
        )

        self.assertFalse(result)
        db.commit.assert_not_called()

    async def test_delete_barber_block_handler_returns_false_when_barber_missing(self):
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None

        handler = DeleteBarberBlockHandler(db)
        result = await handler.handle(
            DeleteBarberBlockCommand(barber_id=1, block_id=5, tenant_id=10)
        )

        self.assertFalse(result)
        db.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
