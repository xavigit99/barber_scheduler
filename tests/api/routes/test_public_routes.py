import os
import unittest
from datetime import date
from unittest.mock import MagicMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.routes.public_routes import (
    public_get_slots_v2,
    public_list_barbers,
    public_list_services,
)
from backend.core.exceptions import NotFoundError


def _make_fake_repo(tenant_id: int):
    """Return a BaseRepository-like class whose instances return objects with the given tenant_id."""

    def _fake_init(self, model, db, **_kwargs):  # noqa: ANN001
        self._tenant_id = tenant_id

    def _fake_get(self, pk):  # noqa: ANN001
        obj = MagicMock()
        obj.tenant_id = self._tenant_id
        return obj

    return type("FakeRepo", (), {"__init__": _fake_init, "get": _fake_get})


class FakeMediator:

    def __init__(self, result=None, sequence=None):
        if sequence is not None:
            self.results = list(sequence)
        else:
            self.results = [result]
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if not self.results:
            return None
        next_result = self.results.pop(0)
        if isinstance(next_result, Exception):
            raise next_result
        return next_result


class TestPublicListBarbers(unittest.IsolatedAsyncioTestCase):

    async def test_returns_barber_list_for_valid_tenant(self):
        """Happy path: mediator returns a list of barbers for the given tenant."""
        barbers = [
            {"id": 1, "nome": "Carlos", "email": "carlos@example.com"},
            {"id": 2, "nome": "Ana", "email": "ana@example.com"},
        ]
        mediator = FakeMediator(barbers)

        with patch(
            "backend.api.routes.public_routes.build_mediator", return_value=mediator
        ):
            result = await public_list_barbers(tenant_id=10, db=object())

        self.assertEqual(result, barbers)
        self.assertEqual(len(mediator.requests), 1)
        sent_query = mediator.requests[0]
        self.assertEqual(sent_query.__class__.__name__, "ListBarbersQuery")
        self.assertEqual(sent_query.tenant_id, 10)

    async def test_raises_404_when_tenant_not_found(self):
        """Mediator raises NotFoundError; route must surface HTTP 404."""
        mediator = FakeMediator(NotFoundError("Tenant not found"))

        with patch(
            "backend.api.routes.public_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException) as ctx:
                await public_list_barbers(tenant_id=999, db=object())

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail, "Tenant not found")

    async def test_returns_empty_list_when_tenant_has_no_barbers(self):
        """Mediator returns an empty list; route must pass it through unchanged."""
        mediator = FakeMediator([])

        with patch(
            "backend.api.routes.public_routes.build_mediator", return_value=mediator
        ):
            result = await public_list_barbers(tenant_id=10, db=object())

        self.assertEqual(result, [])
        self.assertEqual(mediator.requests[0].tenant_id, 10)


class TestPublicListServices(unittest.IsolatedAsyncioTestCase):

    async def test_returns_service_list_for_valid_tenant(self):
        """Happy path: mediator returns a list of services for the given tenant."""
        services = [
            {"id": 1, "nome": "Corte", "duracao": 30, "preco": 10.0},
            {"id": 2, "nome": "Barba", "duracao": 20, "preco": 7.5},
        ]
        mediator = FakeMediator(services)

        with patch(
            "backend.api.routes.public_routes.build_mediator", return_value=mediator
        ):
            result = await public_list_services(tenant_id=10, db=object())

        self.assertEqual(result, services)
        self.assertEqual(len(mediator.requests), 1)
        sent_query = mediator.requests[0]
        self.assertEqual(sent_query.__class__.__name__, "ListServicesQuery")
        self.assertEqual(sent_query.tenant_id, 10)

    async def test_raises_404_when_tenant_not_found(self):
        """Mediator raises NotFoundError; route must surface HTTP 404."""
        mediator = FakeMediator(NotFoundError("Tenant not found"))

        with patch(
            "backend.api.routes.public_routes.build_mediator", return_value=mediator
        ):
            with self.assertRaises(HTTPException) as ctx:
                await public_list_services(tenant_id=999, db=object())

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail, "Tenant not found")

    async def test_returns_empty_list_when_tenant_has_no_services(self):
        """Mediator returns an empty list; route must pass it through unchanged."""
        mediator = FakeMediator([])

        with patch(
            "backend.api.routes.public_routes.build_mediator", return_value=mediator
        ):
            result = await public_list_services(tenant_id=10, db=object())

        self.assertEqual(result, [])
        self.assertEqual(mediator.requests[0].tenant_id, 10)


class TestPublicGetSlotsV2(unittest.IsolatedAsyncioTestCase):

    _TARGET_DATE = date(2026, 4, 1)
    _TENANT_ID = 10

    def _patches(self, mediator, tenant_id=None):
        """Context manager stack: patches build_mediator + BaseRepository with matching tenant."""
        tid = tenant_id if tenant_id is not None else self._TENANT_ID
        return [
            patch("backend.api.routes.public_routes.build_mediator", return_value=mediator),
            patch("backend.api.routes.public_routes.BaseRepository", new=_make_fake_repo(tid)),
        ]

    async def test_returns_slots_for_valid_barber_and_service(self):
        """Happy path: mediator returns a list of available time slots."""
        slots = ["09:00", "09:30", "10:00"]
        mediator = FakeMediator(slots)

        with patch("backend.api.routes.public_routes.build_mediator", return_value=mediator), \
             patch("backend.api.routes.public_routes.BaseRepository", new=_make_fake_repo(self._TENANT_ID)):
            result = await public_get_slots_v2(
                tenant_id=self._TENANT_ID,
                barber_id=3,
                service_id=2,
                target_date=self._TARGET_DATE,
                timezone="Europe/Lisbon",
                db=object(),
            )

        self.assertEqual(result, slots)
        self.assertEqual(len(mediator.requests), 1)
        sent_query = mediator.requests[0]
        self.assertEqual(sent_query.__class__.__name__, "GetAvailableSlotsQuery")
        self.assertEqual(sent_query.barber_id, 3)
        self.assertEqual(sent_query.service_id, 2)
        self.assertEqual(sent_query.target_date, self._TARGET_DATE)
        self.assertEqual(sent_query.timezone, "Europe/Lisbon")

    async def test_raises_404_when_barber_not_found(self):
        """BaseRepository returns None for unknown barber; route must surface HTTP 404."""
        # Simulate barber not belonging to tenant by returning wrong tenant_id
        mediator = FakeMediator([])

        wrong_tenant_repo = _make_fake_repo(tenant_id=999)  # barber.tenant_id != 10

        with patch("backend.api.routes.public_routes.build_mediator", return_value=mediator), \
             patch("backend.api.routes.public_routes.BaseRepository", new=wrong_tenant_repo):
            with self.assertRaises(HTTPException) as ctx:
                await public_get_slots_v2(
                    tenant_id=self._TENANT_ID,
                    barber_id=999,
                    service_id=2,
                    target_date=self._TARGET_DATE,
                    timezone="Europe/Lisbon",
                    db=object(),
                )

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertIn("Barber not found", ctx.exception.detail)

    async def test_uses_default_timezone_when_not_supplied(self):
        """Route signature defaults timezone to 'Europe/Lisbon'; query must reflect that."""
        mediator = FakeMediator([])

        with patch("backend.api.routes.public_routes.build_mediator", return_value=mediator), \
             patch("backend.api.routes.public_routes.BaseRepository", new=_make_fake_repo(self._TENANT_ID)):
            await public_get_slots_v2(
                tenant_id=self._TENANT_ID,
                barber_id=3,
                service_id=2,
                target_date=self._TARGET_DATE,
                # timezone omitted — default kicks in
                db=object(),
            )

        self.assertEqual(mediator.requests[0].timezone, "Europe/Lisbon")

    async def test_returns_empty_list_when_no_slots_available(self):
        """Mediator returns an empty slot list; route must pass it through unchanged."""
        mediator = FakeMediator([])

        with patch("backend.api.routes.public_routes.build_mediator", return_value=mediator), \
             patch("backend.api.routes.public_routes.BaseRepository", new=_make_fake_repo(self._TENANT_ID)):
            result = await public_get_slots_v2(
                tenant_id=self._TENANT_ID,
                barber_id=3,
                service_id=2,
                target_date=self._TARGET_DATE,
                timezone="Europe/Lisbon",
                db=object(),
            )

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
