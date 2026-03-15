import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException, Response

from backend.api.routes.barber_routes import (
    create_barber,
    delete_barber,
    get_barber,
    list_barbers,
    replace_barber,
    update_barber,
)
from backend.infrastructure.schemas import BarberCreate, BarberUpdate


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if callable(self.result):
            return self.result(request)
        return self.result


class BarberRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_barber_returns_created_payload(self):
        mediator = FakeMediator(
            {"id": 1, "nome": "Joao", "email": "joao@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            result = await create_barber(
                BarberCreate(nome="Joao", email="joao@example.com", telefone="123", tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["email"], "joao@example.com")
        self.assertEqual(mediator.requests[0].name, "Joao")
        self.assertEqual(mediator.requests[0].phone, "123")
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_get_barber_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await get_barber(7, db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barber not found")
        self.assertEqual(mediator.requests[0].barber_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_get_barber_returns_payload_when_found(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "Joao", "email": "joao@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            result = await get_barber(7, db=object(), tenant_id=5)

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].barber_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_list_barbers_returns_payload(self):
        mediator = FakeMediator(
            [
                {"id": 1, "nome": "Joao", "email": "joao@example.com", "telefone": "123"},
                {"id": 2, "nome": "Mario", "email": "mario@example.com", "telefone": None},
            ]
        )

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            result = await list_barbers(db=object(), tenant_id=5)

        self.assertEqual(len(result), 2)
        self.assertEqual(mediator.requests[0].__class__.__name__, "ListBarbersQuery")
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_update_barber_requires_at_least_one_field(self):
        with patch("backend.api.routes.barber_routes.build_mediator") as build_mediator:
            with self.assertRaises(HTTPException) as context:
                await update_barber(7, BarberUpdate(), db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")
        build_mediator.assert_not_called()

    async def test_update_barber_maps_partial_payload_to_command(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "Joao", "email": "joao@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            result = await update_barber(
                7,
                BarberUpdate(email="joao@example.com", tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].barber_id, 7)
        self.assertIsNone(mediator.requests[0].name)
        self.assertEqual(mediator.requests[0].email, "joao@example.com")
        self.assertIsNone(mediator.requests[0].phone)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_replace_barber_maps_payload_to_update_command(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "Joao", "email": "joao@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            result = await replace_barber(
                7,
                BarberCreate(nome="Joao", email="joao@example.com", telefone="123", tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].barber_id, 7)
        self.assertEqual(mediator.requests[0].name, "Joao")
        self.assertEqual(mediator.requests[0].email, "joao@example.com")
        self.assertEqual(mediator.requests[0].phone, "123")
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_replace_barber_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await replace_barber(
                    7,
                    BarberCreate(nome="Joao", email="joao@example.com", telefone="123", tenant_id=5),
                    db=object(),
                    tenant_id=5,
                )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barber not found")
        self.assertEqual(mediator.requests[0].barber_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_delete_barber_returns_no_content_response(self):
        mediator = FakeMediator(True)

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            response = await delete_barber(4, db=object(), tenant_id=5)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(mediator.requests[0].barber_id, 4)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_delete_barber_raises_not_found_when_missing(self):
        mediator = FakeMediator(False)

        with patch("backend.api.routes.barber_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await delete_barber(4, db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barber not found")
        self.assertEqual(mediator.requests[0].barber_id, 4)
        self.assertEqual(mediator.requests[0].tenant_id, 5)


if __name__ == "__main__":
    unittest.main()
