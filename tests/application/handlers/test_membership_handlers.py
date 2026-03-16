import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_membership_command import CreateMembershipCommand
from backend.application.commands.delete_membership_command import DeleteMembershipCommand
from backend.application.handlers.membership.create_membership_handler import (
    CreateMembershipHandler,
)
from backend.application.handlers.membership.delete_membership_handler import (
    DeleteMembershipHandler,
)
from backend.application.handlers.membership.list_memberships_handler import (
    ListMembershipsHandler,
)
from backend.application.queries.list_memberships_query import ListMembershipsQuery
from backend.core.barbershop_membership import BarbershopMembership
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError


class MembershipHandlersTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_membership_rejects_missing_barber(self):
        db = MagicMock()
        barber_query = MagicMock()
        db.query.return_value = barber_query
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = None

        handler = CreateMembershipHandler(db)
        command = CreateMembershipCommand(barber_id=1, barbershop_id=2, role="member", tenant_id=10)

        with self.assertRaises(NotFoundError) as ctx:
            await handler.handle(command)
        self.assertIn("Barber", str(ctx.exception))

    async def test_create_membership_rejects_missing_barbershop(self):
        db = MagicMock()
        barber_query = MagicMock()
        shop_query = MagicMock()
        db.query.side_effect = [barber_query, shop_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = None

        handler = CreateMembershipHandler(db)
        command = CreateMembershipCommand(barber_id=1, barbershop_id=2, role="member", tenant_id=10)

        with self.assertRaises(NotFoundError) as ctx:
            await handler.handle(command)
        self.assertIn("Barbershop", str(ctx.exception))

    async def test_create_membership_rejects_invalid_role(self):
        db = MagicMock()
        barber_query = MagicMock()
        shop_query = MagicMock()
        db.query.side_effect = [barber_query, shop_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = object()

        handler = CreateMembershipHandler(db)
        command = CreateMembershipCommand(
            barber_id=1, barbershop_id=2, role="superadmin", tenant_id=10
        )

        with self.assertRaises(ValidationError):
            await handler.handle(command)

    async def test_create_membership_rejects_duplicate(self):
        db = MagicMock()
        barber_query = MagicMock()
        shop_query = MagicMock()
        existing_query = MagicMock()
        db.query.side_effect = [barber_query, shop_query, existing_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = object()
        existing_query.filter.return_value = existing_query
        existing_query.first.return_value = object()  # duplicate found

        handler = CreateMembershipHandler(db)
        command = CreateMembershipCommand(barber_id=1, barbershop_id=2, role="member", tenant_id=10)

        with self.assertRaises(ConflictError):
            await handler.handle(command)

    async def test_create_membership_persists_on_success(self):
        db = MagicMock()
        barber_query = MagicMock()
        shop_query = MagicMock()
        existing_query = MagicMock()
        db.query.side_effect = [barber_query, shop_query, existing_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = object()
        existing_query.filter.return_value = existing_query
        existing_query.first.return_value = None

        handler = CreateMembershipHandler(db)
        command = CreateMembershipCommand(barber_id=1, barbershop_id=2, role="member", tenant_id=10)

        result = await handler.handle(command)

        self.assertIsInstance(result, BarbershopMembership)
        self.assertEqual(result.barber_id, 1)
        self.assertEqual(result.barbershop_id, 2)
        self.assertEqual(result.role, "member")
        db.add.assert_called_once()
        db.commit.assert_called_once()

    async def test_create_membership_accepts_owner_role(self):
        db = MagicMock()
        barber_query = MagicMock()
        shop_query = MagicMock()
        existing_query = MagicMock()
        db.query.side_effect = [barber_query, shop_query, existing_query]
        barber_query.filter.return_value = barber_query
        barber_query.first.return_value = object()
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = object()
        existing_query.filter.return_value = existing_query
        existing_query.first.return_value = None

        handler = CreateMembershipHandler(db)
        command = CreateMembershipCommand(barber_id=1, barbershop_id=2, role="owner", tenant_id=10)

        result = await handler.handle(command)
        self.assertEqual(result.role, "owner")

    async def test_delete_membership_returns_false_when_not_found(self):
        db = MagicMock()
        mem_query = MagicMock()
        db.query.return_value = mem_query
        mem_query.filter.return_value = mem_query
        mem_query.first.return_value = None

        handler = DeleteMembershipHandler(db)
        result = await handler.handle(DeleteMembershipCommand(membership_id=99, barbershop_id=2, tenant_id=10))

        self.assertFalse(result)

    async def test_delete_membership_returns_false_for_wrong_tenant(self):
        db = MagicMock()
        mem_query = MagicMock()
        shop_query = MagicMock()
        membership = SimpleNamespace(id=1, barbershop_id=2, deleted=False)
        db.query.side_effect = [mem_query, shop_query]
        mem_query.filter.return_value = mem_query
        mem_query.first.return_value = membership
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = None  # barbershop not in tenant

        handler = DeleteMembershipHandler(db)
        result = await handler.handle(DeleteMembershipCommand(membership_id=1, barbershop_id=2, tenant_id=99))

        self.assertFalse(result)

    async def test_delete_membership_soft_deletes_with_deleted_at(self):
        db = MagicMock()
        mem_query = MagicMock()
        shop_query = MagicMock()
        membership = SimpleNamespace(id=1, barbershop_id=2, deleted=False, deleted_at=None)
        db.query.side_effect = [mem_query, shop_query]
        mem_query.filter.return_value = mem_query
        mem_query.first.return_value = membership
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = object()  # barbershop found in tenant

        handler = DeleteMembershipHandler(db)
        result = await handler.handle(DeleteMembershipCommand(membership_id=1, barbershop_id=2, tenant_id=10))

        self.assertTrue(result)
        self.assertTrue(membership.deleted)
        self.assertIsNotNone(membership.deleted_at)
        db.commit.assert_called_once()

    async def test_list_memberships_rejects_missing_barbershop(self):
        db = MagicMock()
        shop_query = MagicMock()
        db.query.return_value = shop_query
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = None

        handler = ListMembershipsHandler(db)

        with self.assertRaises(NotFoundError) as ctx:
            await handler.handle(ListMembershipsQuery(barbershop_id=2, tenant_id=10))
        self.assertIn("Barbershop", str(ctx.exception))

    async def test_list_memberships_returns_active_memberships(self):
        db = MagicMock()
        shop_query = MagicMock()
        mem_query = MagicMock()
        expected = [object(), object()]
        db.query.side_effect = [shop_query, mem_query]
        shop_query.filter.return_value = shop_query
        shop_query.first.return_value = object()
        mem_query.filter.return_value = mem_query
        mem_query.all.return_value = expected

        handler = ListMembershipsHandler(db)
        result = await handler.handle(ListMembershipsQuery(barbershop_id=2, tenant_id=10))

        self.assertIs(result, expected)


if __name__ == "__main__":
    unittest.main()
