import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException, Response

from backend.api.routes.membership_routes import (
    create_membership,
    delete_membership,
    list_memberships,
)
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.infrastructure.schemas import MembershipCreate


class FakeMediator:
    """Minimal mediator stub that records sent requests and returns a preset result."""

    def __init__(self, result):
        self.result = result
        self.requests: list = []

    async def send(self, request):
        """Record the request, then return the preset result or raise if it is an exception."""
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def _make_user(role: str = "admin"):
    """Return a minimal fake user object with id and role attributes."""
    return type("User", (), {"id": 1, "role": role})()


def _membership_payload(barber_id: int = 3, role: str = "owner") -> MembershipCreate:
    """Return a MembershipCreate payload with sensible defaults."""
    return MembershipCreate(barber_id=barber_id, role=role)


def _membership_dict(
    *,
    id: int = 10,
    barber_id: int = 3,
    barbershop_id: int = 5,
    role: str = "owner",
) -> dict:
    """Return a dict that represents a membership as returned by the handler."""
    return {
        "id": id,
        "barber_id": barber_id,
        "barbershop_id": barbershop_id,
        "role": role,
    }


class TestCreateMembershipRoute(unittest.IsolatedAsyncioTestCase):

    async def test_returns_membership_on_success(self):
        """create_membership must return the mediator result when the command succeeds."""
        expected = _membership_dict()
        mediator = FakeMediator(expected)

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            result = await create_membership(
                barbershop_id=5,
                payload=_membership_payload(barber_id=3, role="owner"),
                db=object(),
                current_user=_make_user(),
                x_tenant_id=1,
            )

        self.assertEqual(result, expected)

    async def test_command_carries_correct_fields(self):
        """The command sent to the mediator must carry barbershop_id, barber_id, role, tenant_id."""
        mediator = FakeMediator(_membership_dict())

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            await create_membership(
                barbershop_id=7,
                payload=_membership_payload(barber_id=11, role="member"),
                db=object(),
                current_user=_make_user(),
                x_tenant_id=42,
            )

        cmd = mediator.requests[0]
        self.assertEqual(cmd.barbershop_id, 7)
        self.assertEqual(cmd.barber_id, 11)
        self.assertEqual(cmd.role, "member")
        self.assertEqual(cmd.tenant_id, 42)

    async def test_raises_400_when_tenant_id_missing(self):
        """create_membership must raise HTTP 400 when the X-Tenant-Id header is absent."""
        with patch("backend.api.routes.membership_routes.build_mediator"):
            with self.assertRaises(HTTPException) as ctx:
                await create_membership(
                    barbershop_id=5,
                    payload=_membership_payload(),
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=None,
                )
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_raises_404_on_not_found_error(self):
        """create_membership must map NotFoundError to HTTP 404."""
        mediator = FakeMediator(NotFoundError("Barber not found"))

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as ctx:
                await create_membership(
                    barbershop_id=5,
                    payload=_membership_payload(),
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=1,
                )
        self.assertEqual(ctx.exception.status_code, 404)

    async def test_raises_409_on_conflict_error(self):
        """create_membership must map ConflictError to HTTP 409."""
        mediator = FakeMediator(ConflictError("Membership already exists"))

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as ctx:
                await create_membership(
                    barbershop_id=5,
                    payload=_membership_payload(),
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=1,
                )
        self.assertEqual(ctx.exception.status_code, 409)

    async def test_raises_400_on_validation_error(self):
        """create_membership must map ValidationError to HTTP 400 (business rule violation)."""
        mediator = FakeMediator(ValidationError("Invalid role"))

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as ctx:
                await create_membership(
                    barbershop_id=5,
                    payload=_membership_payload(),
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=1,
                )
        self.assertEqual(ctx.exception.status_code, 400)


class TestListMembershipsRoute(unittest.IsolatedAsyncioTestCase):

    async def test_returns_list_on_success(self):
        """list_memberships must return the full list from the mediator."""
        memberships = [_membership_dict(id=1), _membership_dict(id=2)]
        mediator = FakeMediator(memberships)

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            result = await list_memberships(
                barbershop_id=5,
                db=object(),
                current_user=_make_user(),
                x_tenant_id=1,
            )

        self.assertEqual(result, memberships)
        self.assertEqual(len(result), 2)

    async def test_query_carries_correct_fields(self):
        """The query sent to the mediator must carry barbershop_id and tenant_id."""
        mediator = FakeMediator([])

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            await list_memberships(
                barbershop_id=99,
                db=object(),
                current_user=_make_user(),
                x_tenant_id=77,
            )

        query = mediator.requests[0]
        self.assertEqual(query.barbershop_id, 99)
        self.assertEqual(query.tenant_id, 77)

    async def test_returns_empty_list_when_no_memberships(self):
        """list_memberships must return an empty list when the barbershop has no members."""
        mediator = FakeMediator([])

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            result = await list_memberships(
                barbershop_id=5,
                db=object(),
                current_user=_make_user(),
                x_tenant_id=1,
            )

        self.assertEqual(result, [])

    async def test_raises_400_when_tenant_id_missing(self):
        """list_memberships must raise HTTP 400 when X-Tenant-Id header is absent."""
        with patch("backend.api.routes.membership_routes.build_mediator"):
            with self.assertRaises(HTTPException) as ctx:
                await list_memberships(
                    barbershop_id=5,
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=None,
                )
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_raises_404_on_not_found_error(self):
        """list_memberships must map NotFoundError (e.g. barbershop missing) to HTTP 404."""
        mediator = FakeMediator(NotFoundError("Barbershop not found"))

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as ctx:
                await list_memberships(
                    barbershop_id=5,
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=1,
                )
        self.assertEqual(ctx.exception.status_code, 404)


class TestDeleteMembershipRoute(unittest.IsolatedAsyncioTestCase):

    async def test_returns_204_response_on_success(self):
        """delete_membership must return a Response with status 204 when deleted=True."""
        mediator = FakeMediator(True)

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            response = await delete_membership(
                barbershop_id=5,
                membership_id=10,
                db=object(),
                current_user=_make_user(),
                x_tenant_id=1,
            )

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)

    async def test_command_carries_correct_fields(self):
        """The command sent to the mediator must carry membership_id and tenant_id."""
        mediator = FakeMediator(True)

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            await delete_membership(
                barbershop_id=5,
                membership_id=33,
                db=object(),
                current_user=_make_user(),
                x_tenant_id=88,
            )

        cmd = mediator.requests[0]
        self.assertEqual(cmd.membership_id, 33)
        self.assertEqual(cmd.tenant_id, 88)

    async def test_raises_404_when_mediator_returns_false(self):
        """delete_membership must raise HTTP 404 when the handler returns False (not found)."""
        mediator = FakeMediator(False)

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as ctx:
                await delete_membership(
                    barbershop_id=5,
                    membership_id=10,
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=1,
                )
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail, "Membership not found")

    async def test_raises_400_when_tenant_id_missing(self):
        """delete_membership must raise HTTP 400 when X-Tenant-Id header is absent."""
        with patch("backend.api.routes.membership_routes.build_mediator"):
            with self.assertRaises(HTTPException) as ctx:
                await delete_membership(
                    barbershop_id=5,
                    membership_id=10,
                    db=object(),
                    current_user=_make_user(),
                    x_tenant_id=None,
                )
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_barbershop_id_path_param_is_accepted(self):
        """delete_membership must accept barbershop_id as a path param without error."""
        mediator = FakeMediator(True)

        with patch(
            "backend.api.routes.membership_routes.build_mediator",
            return_value=mediator,
        ):
            response = await delete_membership(
                barbershop_id=99,
                membership_id=10,
                db=object(),
                current_user=_make_user(),
                x_tenant_id=1,
            )

        self.assertEqual(response.status_code, 204)


if __name__ == "__main__":
    unittest.main()
