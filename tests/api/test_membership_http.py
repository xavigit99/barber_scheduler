import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.membership_http import (
    build_create_membership_command,
    build_delete_membership_command,
    build_list_memberships_query,
    ensure_membership_deleted,
    ensure_membership_found,
)
from backend.application.commands.create_membership_command import CreateMembershipCommand
from backend.application.commands.delete_membership_command import DeleteMembershipCommand
from backend.application.queries.list_memberships_query import ListMembershipsQuery
from backend.core.membership_roles import (
    ALLOWED_MEMBERSHIP_ROLES,
    MEMBERSHIP_MEMBER,
    MEMBERSHIP_OWNER,
)
from backend.infrastructure.schemas import MembershipCreate


class TestMembershipRoles(unittest.TestCase):

    def test_membership_owner_constant_value(self):
        """MEMBERSHIP_OWNER must equal the string 'owner'."""
        self.assertEqual(MEMBERSHIP_OWNER, "owner")

    def test_membership_member_constant_value(self):
        """MEMBERSHIP_MEMBER must equal the string 'member'."""
        self.assertEqual(MEMBERSHIP_MEMBER, "member")

    def test_allowed_roles_contains_owner(self):
        """ALLOWED_MEMBERSHIP_ROLES must include the owner role."""
        self.assertIn(MEMBERSHIP_OWNER, ALLOWED_MEMBERSHIP_ROLES)

    def test_allowed_roles_contains_member(self):
        """ALLOWED_MEMBERSHIP_ROLES must include the member role."""
        self.assertIn(MEMBERSHIP_MEMBER, ALLOWED_MEMBERSHIP_ROLES)

    def test_allowed_roles_has_exactly_two_entries(self):
        """ALLOWED_MEMBERSHIP_ROLES must contain exactly two entries (owner and member)."""
        self.assertEqual(len(ALLOWED_MEMBERSHIP_ROLES), 2)

    def test_allowed_roles_is_a_set(self):
        """ALLOWED_MEMBERSHIP_ROLES must be a set (no duplicates, O(1) membership test)."""
        self.assertIsInstance(ALLOWED_MEMBERSHIP_ROLES, (set, frozenset))


class TestBuildCreateMembershipCommand(unittest.TestCase):

    def _make_payload(self, barber_id: int = 3, role: str = "owner") -> MembershipCreate:
        return MembershipCreate(barber_id=barber_id, role=role)

    def test_returns_create_membership_command_instance(self):
        """Builder must return a CreateMembershipCommand dataclass instance."""
        payload = self._make_payload()
        result = build_create_membership_command(barbershop_id=10, payload=payload, tenant_id=1)
        self.assertIsInstance(result, CreateMembershipCommand)

    def test_barber_id_mapped_from_payload(self):
        """barber_id on the command must come from the payload."""
        payload = self._make_payload(barber_id=7)
        result = build_create_membership_command(barbershop_id=10, payload=payload, tenant_id=1)
        self.assertEqual(result.barber_id, 7)

    def test_barbershop_id_mapped_from_path_param(self):
        """barbershop_id on the command must come from the path parameter, not the payload."""
        payload = self._make_payload()
        result = build_create_membership_command(barbershop_id=42, payload=payload, tenant_id=1)
        self.assertEqual(result.barbershop_id, 42)

    def test_role_mapped_from_payload(self):
        """role on the command must come from the payload."""
        payload = self._make_payload(role="member")
        result = build_create_membership_command(barbershop_id=10, payload=payload, tenant_id=1)
        self.assertEqual(result.role, "member")

    def test_tenant_id_mapped_from_keyword_arg(self):
        """tenant_id on the command must come from the keyword argument."""
        payload = self._make_payload()
        result = build_create_membership_command(barbershop_id=10, payload=payload, tenant_id=99)
        self.assertEqual(result.tenant_id, 99)

    def test_command_is_immutable(self):
        """CreateMembershipCommand must be frozen (immutable dataclass)."""
        payload = self._make_payload()
        result = build_create_membership_command(barbershop_id=10, payload=payload, tenant_id=1)
        with self.assertRaises(Exception):
            result.barber_id = 999  # type: ignore[misc]


class TestBuildDeleteMembershipCommand(unittest.TestCase):

    def test_returns_delete_membership_command_instance(self):
        """Builder must return a DeleteMembershipCommand dataclass instance."""
        result = build_delete_membership_command(barbershop_id=1, membership_id=5, tenant_id=2)
        self.assertIsInstance(result, DeleteMembershipCommand)

    def test_membership_id_mapped_correctly(self):
        """membership_id on the command must match the argument passed."""
        result = build_delete_membership_command(barbershop_id=1, membership_id=17, tenant_id=2)
        self.assertEqual(result.membership_id, 17)

    def test_tenant_id_mapped_correctly(self):
        """tenant_id on the command must match the keyword argument passed."""
        result = build_delete_membership_command(barbershop_id=1, membership_id=5, tenant_id=88)
        self.assertEqual(result.tenant_id, 88)

    def test_command_is_immutable(self):
        """DeleteMembershipCommand must be frozen (immutable dataclass)."""
        result = build_delete_membership_command(barbershop_id=1, membership_id=5, tenant_id=2)
        with self.assertRaises(Exception):
            result.membership_id = 999  # type: ignore[misc]


class TestBuildListMembershipsQuery(unittest.TestCase):

    def test_returns_list_memberships_query_instance(self):
        """Builder must return a ListMembershipsQuery dataclass instance."""
        result = build_list_memberships_query(barbershop_id=4, tenant_id=3)
        self.assertIsInstance(result, ListMembershipsQuery)

    def test_barbershop_id_mapped_correctly(self):
        """barbershop_id on the query must match the argument passed."""
        result = build_list_memberships_query(barbershop_id=22, tenant_id=3)
        self.assertEqual(result.barbershop_id, 22)

    def test_tenant_id_mapped_correctly(self):
        """tenant_id on the query must match the keyword argument passed."""
        result = build_list_memberships_query(barbershop_id=4, tenant_id=55)
        self.assertEqual(result.tenant_id, 55)


class TestEnsureMembershipFound(unittest.TestCase):

    def test_returns_resource_when_not_none(self):
        """ensure_membership_found must return the resource unchanged when it exists."""
        resource = {"id": 1, "barber_id": 3, "barbershop_id": 10, "role": "owner"}
        result = ensure_membership_found(resource)
        self.assertIs(result, resource)

    def test_raises_404_when_none(self):
        """ensure_membership_found must raise HTTP 404 when the resource is None."""
        with self.assertRaises(HTTPException) as ctx:
            ensure_membership_found(None)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_raises_404_with_correct_detail(self):
        """ensure_membership_found must include 'Membership not found' in the 404 detail."""
        with self.assertRaises(HTTPException) as ctx:
            ensure_membership_found(None)
        self.assertEqual(ctx.exception.detail, "Membership not found")

    def test_truthy_non_dict_resource_returned_unchanged(self):
        """ensure_membership_found must return any truthy resource as-is."""
        resource = object()
        result = ensure_membership_found(resource)
        self.assertIs(result, resource)


class TestEnsureMembershipDeleted(unittest.TestCase):

    def test_does_not_raise_when_deleted_is_true(self):
        """ensure_membership_deleted must not raise when deleted=True."""
        try:
            ensure_membership_deleted(True)
        except HTTPException:
            self.fail("ensure_membership_deleted raised HTTPException unexpectedly for deleted=True")

    def test_raises_404_when_deleted_is_false(self):
        """ensure_membership_deleted must raise HTTP 404 when deleted=False."""
        with self.assertRaises(HTTPException) as ctx:
            ensure_membership_deleted(False)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_raises_404_with_correct_detail(self):
        """ensure_membership_deleted must include 'Membership not found' in the 404 detail."""
        with self.assertRaises(HTTPException) as ctx:
            ensure_membership_deleted(False)
        self.assertEqual(ctx.exception.detail, "Membership not found")

    def test_returns_none_when_deleted_is_true(self):
        """ensure_membership_deleted must return None (implicitly) on success."""
        result = ensure_membership_deleted(True)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
