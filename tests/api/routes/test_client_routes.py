import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException, Response

from backend.api.routes.client_routes import (
    create_client,
    delete_client,
    get_client,
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
                ClientCreate(nome="John", email="john@example.com", telefone="123"),
                db=object(),
            )

        self.assertEqual(result["email"], "john@example.com")
        self.assertEqual(mediator.requests[0].name, "John")
        self.assertEqual(mediator.requests[0].phone, "123")

    async def test_get_client_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await get_client(7, db=object())

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Client not found")
        self.assertEqual(mediator.requests[0].client_id, 7)

    async def test_update_client_requires_at_least_one_field(self):
        with patch("backend.api.routes.client_routes.build_mediator") as build_mediator:
            with self.assertRaises(HTTPException) as context:
                await update_client(7, ClientUpdate(), db=object())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")
        build_mediator.assert_not_called()

    async def test_delete_client_returns_no_content_response(self):
        mediator = FakeMediator(True)

        with patch("backend.api.routes.client_routes.build_mediator", return_value=mediator):
            response = await delete_client(4, db=object())

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(mediator.requests[0].client_id, 4)


if __name__ == "__main__":
    unittest.main()
