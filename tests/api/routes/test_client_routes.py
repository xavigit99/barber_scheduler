import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException, Response

from backend.api.routes.client_routes import (
    create_client,
    list_clients,
    delete_client,
    get_client,
    replace_client,
    update_client,
)
from backend.infrastructure.schemas import ClientCreate, ClientUpdate


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if callable(self.result):
            return self.result(request)
        return self.result


class ClientRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_client_returns_created_payload(self):
        mediator = FakeMediator(
            {"id": 1, "nome": "John", "email": "john@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            result = await create_client(
                ClientCreate(nome="John", email="john@example.com", telefone="123", tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["email"], "john@example.com")
        self.assertEqual(mediator.requests[0].name, "John")
        self.assertEqual(mediator.requests[0].phone, "123")
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_get_client_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await get_client(7, db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Client not found")
        self.assertEqual(mediator.requests[0].client_id, 7)

    async def test_get_client_returns_payload_when_found(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "John", "email": "john@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            result = await get_client(7, db=object(), tenant_id=5)

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].client_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_list_clients_returns_payload(self):
        mediator = FakeMediator(
            [
                {"id": 1, "nome": "John", "email": "john@example.com", "telefone": "123"},
                {"id": 2, "nome": "Jane", "email": "jane@example.com", "telefone": None},
            ]
        )

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            result = await list_clients(db=object(), tenant_id=5)

        self.assertEqual(len(result), 2)
        self.assertEqual(mediator.requests[0].__class__.__name__, "ListClientsQuery")
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_update_client_requires_at_least_one_field(self):
        with patch("backend.api.routes.client_routes.build_mediator") as build_mediator:
            with self.assertRaises(HTTPException) as context:
                await update_client(7, ClientUpdate(), db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")
        build_mediator.assert_not_called()

    async def test_update_client_maps_partial_payload_to_command(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "John", "email": "john@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            result = await update_client(
                7,
                ClientUpdate(email="john@example.com"),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].client_id, 7)
        self.assertIsNone(mediator.requests[0].name)
        self.assertEqual(mediator.requests[0].email, "john@example.com")
        self.assertIsNone(mediator.requests[0].phone)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_replace_client_maps_payload_to_update_command(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "John", "email": "john@example.com", "telefone": "123"}
        )

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            result = await replace_client(
                7,
                ClientCreate(nome="John", email="john@example.com", telefone="123", tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].client_id, 7)
        self.assertEqual(mediator.requests[0].name, "John")
        self.assertEqual(mediator.requests[0].email, "john@example.com")
        self.assertEqual(mediator.requests[0].phone, "123")
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_replace_client_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await replace_client(
                    7,
                ClientCreate(nome="John", email="john@example.com", telefone="123", tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Client not found")
        self.assertEqual(mediator.requests[0].client_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_delete_client_returns_no_content_response(self):
        mediator = FakeMediator(True)

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            response = await delete_client(4, db=object(), tenant_id=5)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(mediator.requests[0].client_id, 4)

    async def test_delete_client_raises_not_found_when_missing(self):
        mediator = FakeMediator(False)

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await delete_client(4, db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Client not found")
        self.assertEqual(mediator.requests[0].client_id, 4)
        self.assertEqual(mediator.requests[0].tenant_id, 5)


if __name__ == "__main__":
    unittest.main()
