import os
import unittest
from datetime import time
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from datetime import datetime

from backend.application.commands.create_barber_availability_command import (
    CreateBarberAvailabilityCommand,
)
from backend.application.commands.create_barber_block_command import CreateBarberBlockCommand
from backend.application.commands.delete_barber_availability_command import (
    DeleteBarberAvailabilityCommand,
)
from backend.application.commands.delete_barber_block_command import DeleteBarberBlockCommand
from backend.application.commands.delete_barbershop_command import DeleteBarbershopCommand
from backend.application.commands.update_barbershop_command import UpdateBarbershopCommand
from backend.application.handlers.availability.create_barber_availability_handler import (
    CreateBarberAvailabilityHandler,
)
from backend.application.handlers.availability.create_barber_block_handler import (
    CreateBarberBlockHandler,
)
from backend.application.handlers.availability.delete_barber_availability_handler import (
    DeleteBarberAvailabilityHandler,
)
from backend.application.handlers.availability.delete_barber_block_handler import (
    DeleteBarberBlockHandler,
)
from backend.application.handlers.availability.list_barber_availabilities_handler import (
    ListBarberAvailabilitiesHandler,
)
from backend.application.handlers.availability.list_barber_blocks_handler import (
    ListBarberBlocksHandler,
)
from backend.application.handlers.barbershop.delete_barbershop_handler import (
    DeleteBarbershopHandler,
)
from backend.application.handlers.barbershop.update_barbershop_handler import (
    UpdateBarbershopHandler,
)
from backend.application.queries.list_barber_availabilities_query import (
    ListBarberAvailabilitiesQuery,
)
from backend.application.queries.list_barber_blocks_query import ListBarberBlocksQuery
from backend.core.exceptions import NotFoundError


class TenantIsolationTestCase(unittest.IsolatedAsyncioTestCase):

    # ── Barbershop ────────────────────────────────────────────────────────────

    async def test_delete_barbershop_returns_false_for_wrong_tenant(self):
        """Barbershop belonging to another tenant cannot be deleted."""
        db = MagicMock()
        query = MagicMock()
        db.query.return_value = query
        query.filter.return_value = query
        query.first.return_value = None  # not found in tenant 99

        handler = DeleteBarbershopHandler(db)
        result = await handler.handle(DeleteBarbershopCommand(barbershop_id=1, tenant_id=99))

        self.assertFalse(result)

    async def test_update_barbershop_returns_none_for_wrong_tenant(self):
        """Barbershop belonging to another tenant cannot be updated."""
        db = MagicMock()
        query = MagicMock()
        db.query.return_value = query
        query.filter.return_value = query
        query.first.return_value = None  # not found in tenant 99

        handler = UpdateBarbershopHandler(db)
        result = await handler.handle(
            UpdateBarbershopCommand(barbershop_id=1, name="X", tenant_id=99)
        )

        self.assertIsNone(result)

    # ── Availability ──────────────────────────────────────────────────────────

    async def test_create_availability_rejects_barber_from_wrong_tenant(self):
        """Creating availability for a barber from another tenant raises NotFoundError."""
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not in tenant 99

        handler = CreateBarberAvailabilityHandler(db)

        with self.assertRaises(NotFoundError) as ctx:
            await handler.handle(
                CreateBarberAvailabilityCommand(
                    barber_id=1,
                    weekday=1,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    tenant_id=99,
                )
            )
        self.assertIn("Barber", str(ctx.exception))

    async def test_delete_availability_returns_false_for_barber_from_wrong_tenant(self):
        """Deleting availability for a barber from another tenant returns False."""
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not in tenant 99

        handler = DeleteBarberAvailabilityHandler(db)
        result = await handler.handle(
            DeleteBarberAvailabilityCommand(barber_id=1, availability_id=2, tenant_id=99)
        )

        self.assertFalse(result)

    async def test_list_availabilities_rejects_barber_from_wrong_tenant(self):
        """Listing availabilities for a barber from another tenant raises NotFoundError."""
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not in tenant 99

        handler = ListBarberAvailabilitiesHandler(db)

        with self.assertRaises(NotFoundError):
            await handler.handle(ListBarberAvailabilitiesQuery(barber_id=1, tenant_id=99))

    # ── Block ─────────────────────────────────────────────────────────────────

    async def test_create_block_rejects_barber_from_wrong_tenant(self):
        """Creating a block for a barber from another tenant raises NotFoundError."""
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not in tenant 99

        handler = CreateBarberBlockHandler(db)

        with self.assertRaises(NotFoundError) as ctx:
            await handler.handle(
                CreateBarberBlockCommand(
                    barber_id=1,
                    kind="break",
                    start_at=datetime(2026, 3, 16, 10, 0),
                    end_at=datetime(2026, 3, 16, 11, 0),
                    tenant_id=99,
                )
            )
        self.assertIn("Barber", str(ctx.exception))

    async def test_delete_block_returns_false_for_barber_from_wrong_tenant(self):
        """Deleting a block for a barber from another tenant returns False."""
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not in tenant 99

        handler = DeleteBarberBlockHandler(db)
        result = await handler.handle(
            DeleteBarberBlockCommand(barber_id=1, block_id=5, tenant_id=99)
        )

        self.assertFalse(result)

    async def test_list_blocks_rejects_barber_from_wrong_tenant(self):
        """Listing blocks for a barber from another tenant raises NotFoundError."""
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None  # barber not in tenant 99

        handler = ListBarberBlocksHandler(db)

        with self.assertRaises(NotFoundError):
            await handler.handle(ListBarberBlocksQuery(barber_id=1, tenant_id=99))


if __name__ == "__main__":
    unittest.main()
