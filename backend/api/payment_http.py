from backend.application.commands.update_appointment_payment_command import (
    UpdateAppointmentPaymentCommand,
)
from backend.infrastructure.schemas import AppointmentPaymentUpdateRequest


def build_update_appointment_payment_command(
    appointment_id: int,
    payload: AppointmentPaymentUpdateRequest,
    tenant_id: int,
) -> UpdateAppointmentPaymentCommand:
    return UpdateAppointmentPaymentCommand(
        appointment_id=appointment_id,
        payment_status=payload.payment_status,
        payment_method=payload.payment_method,
        tenant_id=tenant_id,
    )
