import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException, Response

from backend.api.routes.barbershop_routes import (
    create_barbershop,
    delete_barbershop,
    get_barbershop,
    list_barbershops,
    replace_barbershop,
    update_barbershop,
)
from backend.core.exceptions import NotFoundError
from backend.infrastructure.schemas import BarbershopCreate, BarbershopUpdate


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class BarbershopRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_create_barbershop_returns_created_payload(self):
        barbershop = {"id": 1, "nome": "Central", "owner_user_id": 5, "tenant_id": 7}
        mediator = FakeMediator(barbershop)
        current_user = type("User", (), {"id": 5, "role": "admin"})()

        with patch(
            "backend.api.routes.barbershop_routes.build_mediator",
            return_value=mediator,
        ):
            result = await create_barbershop(
                BarbershopCreate(nome="Central"),
                db=object(),
                current_user=current_user,
            )

        self.assertEqual(result["owner_user_id"], 5)
        self.assertEqual(mediator.requests[0].owner_user_id, 5)

    async def test_create_barbershop_maps_missing_owner_to_404(self):
        mediator = FakeMediator(NotFoundError("Owner user not found"))
        current_user = type("User", (), {"id": 5, "role": "admin"})()

        with patch(
            "backend.api.routes.barbershop_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as context:
                await create_barbershop(
                    BarbershopCreate(nome="Central"),
                    db=object(),
                    current_user=current_user,
                )

        self.assertEqual(context.exception.status_code, 404)

    async def test_get_barbershop_raises_not_found_when_missing(self):
        mediator = FakeMediator(None)

        with patch(
            "backend.api.routes.barbershop_routes.build_mediator",
            return_value=mediator,
        ):
            with self.assertRaises(HTTPException) as context:
                await get_barbershop(7, db=object())

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Barbershop not found")
        self.assertEqual(mediator.requests[0].barbershop_id, 7)

    async def test_list_barbershops_returns_payload(self):
        mediator = FakeMediator(
            [
                {"id": 1, "nome": "Central", "owner_user_id": 5, "tenant_id": 7},
                {"id": 2, "nome": "North", "owner_user_id": 6, "tenant_id": 8},
            ]
        )

        with patch(
            "backend.api.routes.barbershop_routes.build_mediator",
            return_value=mediator,
        ):
            result = await list_barbershops(db=object())

        self.assertEqual(len(result), 2)
        self.assertEqual(mediator.requests[0].__class__.__name__, "ListBarbershopsQuery")

    async def test_update_barbershop_requires_at_least_one_field(self):
        with patch("backend.api.routes.barbershop_routes.build_mediator") as build_mediator:
            with self.assertRaises(HTTPException) as context:
                await update_barbershop(7, BarbershopUpdate(), db=object())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")
        build_mediator.assert_not_called()

    async def test_update_barbershop_maps_partial_payload_to_command(self):
        mediator = FakeMediator(
            {"id": 7, "nome": "Central Premium", "owner_user_id": 5, "tenant_id": 7}
        )

        with patch(
            "backend.api.routes.barbershop_routes.build_mediator",
            return_value=mediator,
        ):
            result = await update_barbershop(
                7,
                BarbershopUpdate(nome="Central Premium"),
                db=object(),
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].barbershop_id, 7)
        self.assertEqual(mediator.requests[0].name, "Central Premium")

    async def test_replace_barbershop_maps_payload_to_update_command(self):
        mediator = FakeMediator({"id": 7, "nome": "Central", "owner_user_id": 5, "tenant_id": 7})

        with patch(
            "backend.api.routes.barbershop_routes.build_mediator",
            return_value=mediator,
        ):
            result = await replace_barbershop(
                7,
                BarbershopCreate(nome="Central"),
                db=object(),
            )

        self.assertEqual(result["id"], 7)
        self.assertEqual(mediator.requests[0].barbershop_id, 7)
        self.assertEqual(mediator.requests[0].name, "Central")

    async def test_delete_barbershop_returns_no_content_response(self):
        mediator = FakeMediator(True)

        with patch(
            "backend.api.routes.barbershop_routes.build_mediator",
            return_value=mediator,
        ):
            response = await delete_barbershop(4, db=object())

        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(mediator.requests[0].barbershop_id, 4)


if __name__ == "__main__":
    unittest.main()
