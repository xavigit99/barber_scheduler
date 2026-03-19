import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.api.payment_http import build_update_appointment_payment_command
from backend.infrastructure.schemas import AppointmentPaymentUpdateRequest


class PaymentHttpTestCase(unittest.TestCase):

    def test_build_update_appointment_payment_command_maps_fields(self):
        command = build_update_appointment_payment_command(
            appointment_id=7,
            payload=AppointmentPaymentUpdateRequest(
                payment_status="paid",
                payment_method="mbway",
            ),
            tenant_id=5,
        )

        self.assertEqual(command.appointment_id, 7)
        self.assertEqual(command.payment_status, "paid")
        self.assertEqual(command.payment_method, "mbway")
        self.assertEqual(command.tenant_id, 5)


if __name__ == "__main__":
    unittest.main()
