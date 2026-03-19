import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.routes.payment_routes import update_appointment_payment
from backend.core.exceptions import NotFoundError, ValidationError
from backend.infrastructure.schemas import AppointmentPaymentUpdateRequest


class FakeMediator:

    def __init__(self, result):
        self.result = result
        self.requests = []

    async def send(self, request):
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class PaymentRoutesTestCase(unittest.IsolatedAsyncioTestCase):

    async def test_update_appointment_payment_returns_updated_payload(self):
        mediator = FakeMediator(
            {"id": 9, "payment_status": "paid", "payment_method": "mbway"}
        )

        with patch("backend.api.routes.payment_routes.build_mediator", return_value=mediator):
            result = await update_appointment_payment(
                9,
                AppointmentPaymentUpdateRequest(
                    payment_status="paid",
                    payment_method="mbway",
                ),
                db=object(),
                current_user={"role": "admin"},
                tenant_id=3,
            )

        self.assertEqual(result["payment_status"], "paid")
        self.assertEqual(mediator.requests[0].appointment_id, 9)
        self.assertEqual(mediator.requests[0].payment_method, "mbway")
        self.assertEqual(mediator.requests[0].tenant_id, 3)

    async def test_update_appointment_payment_maps_validation_error(self):
        mediator = FakeMediator(ValidationError("Invalid payment method"))

        with patch("backend.api.routes.payment_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await update_appointment_payment(
                    9,
                    AppointmentPaymentUpdateRequest(
                        payment_status="paid",
                        payment_method="mbway",
                    ),
                    db=object(),
                    current_user={"role": "admin"},
                    tenant_id=3,
                )

        self.assertEqual(context.exception.status_code, 400)

    async def test_update_appointment_payment_maps_not_found(self):
        mediator = FakeMediator(NotFoundError("Appointment not found"))

        with patch("backend.api.routes.payment_routes.build_mediator", return_value=mediator):
            with self.assertRaises(HTTPException) as context:
                await update_appointment_payment(
                    9,
                    AppointmentPaymentUpdateRequest(
                        payment_status="paid",
                        payment_method="cash",
                    ),
                    db=object(),
                    current_user={"role": "admin"},
                    tenant_id=3,
                )

        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
