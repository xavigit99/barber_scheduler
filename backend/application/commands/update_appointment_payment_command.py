from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class UpdateAppointmentPaymentCommand(Request):
    appointment_id: int
    payment_status: str
    payment_method: str | None = None
    tenant_id: int | None = None
