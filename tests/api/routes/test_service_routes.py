import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException, Response

from backend.api.routes.service_routes import (
    create_service,
    delete_service,
    get_service,
    list_services,
    replace_service,
    update_service,
)
from backend.infrastructure.schemas import ServiceCreate, ServiceUpdate


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if callable(self.result):
            return self.result(request)
        return self.result


class ServiceRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_service_returns_created_payload(self):
        mediator = FakeMediator(
            {"id": 1, "nome": "Corte", "duracao_minutos": 30, "preco": 15.0}
        )

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            result = await create_service(
                ServiceCreate(nome="Corte", duracao_minutos=30, preco=15.0, tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["preco"], 15.0)
        self.assertEqual(mediator.requests[0].name, "Corte")
        self.assertEqual(mediator.requests[0].duration_minutes, 30)
        self.assertEqual(mediator.requests[0].price, 15.0)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_get_service_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await get_service(7, db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Service not found")
        self.assertEqual(mediator.requests[0].service_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_get_service_returns_payload_when_found(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "Barba", "duracao_minutos": 20, "preco": 10.0}
        )

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            result = await get_service(7, db=object(), tenant_id=5)

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].service_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_list_services_returns_payload(self):
        mediator = FakeMediator(
            [
                {"id": 1, "nome": "Corte", "duracao_minutos": 30, "preco": 15.0},
                {"id": 2, "nome": "Barba", "duracao_minutos": 20, "preco": 10.0},
            ]
        )

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            result = await list_services(db=object(), tenant_id=5)

        self.assertEqual(len(result), 2)
        self.assertEqual(mediator.requests[0].__class__.__name__, "ListServicesQuery")
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_update_service_requires_at_least_one_field(self):
        with patch("backend.api.routes.service_routes.build_mediator") as build_mediator:
            with self.assertRaises(HTTPException) as context:
                await update_service(7, ServiceUpdate(), db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")
        build_mediator.assert_not_called()

    async def test_update_service_maps_partial_payload_to_command(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "Corte", "duracao_minutos": 30, "preco": 20.0}
        )

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            result = await update_service(
                7,
                ServiceUpdate(preco=20.0, tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].service_id, 7)
        self.assertIsNone(mediator.requests[0].name)
        self.assertIsNone(mediator.requests[0].duration_minutes)
        self.assertEqual(mediator.requests[0].price, 20.0)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_replace_service_maps_payload_to_update_command(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "Corte", "duracao_minutos": 30, "preco": 15.0}
        )

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            result = await replace_service(
                7,
                ServiceCreate(nome="Corte", duracao_minutos=30, preco=15.0, tenant_id=5),
                db=object(),
                tenant_id=5,
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].service_id, 7)
        self.assertEqual(mediator.requests[0].name, "Corte")
        self.assertEqual(mediator.requests[0].duration_minutes, 30)
        self.assertEqual(mediator.requests[0].price, 15.0)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_replace_service_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await replace_service(
                    7,
                    ServiceCreate(nome="Corte", duracao_minutos=30, preco=15.0, tenant_id=5),
                    db=object(),
                    tenant_id=5,
                )

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Service not found")
        self.assertEqual(mediator.requests[0].service_id, 7)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_delete_service_returns_no_content_response(self):
        mediator = FakeMediator(True)

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            response = await delete_service(4, db=object(), tenant_id=5)

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(mediator.requests[0].service_id, 4)
        self.assertEqual(mediator.requests[0].tenant_id, 5)

    async def test_delete_service_raises_not_found_when_missing(self):
        mediator = FakeMediator(False)

        with patch("backend.api.routes.service_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await delete_service(4, db=object(), tenant_id=5)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Service not found")
        self.assertEqual(mediator.requests[0].service_id, 4)
        self.assertEqual(mediator.requests[0].tenant_id, 5)


if __name__ == "__main__":
    unittest.main()
