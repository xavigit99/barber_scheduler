from datetime import date, datetime

from backend.application.commands.cancel_appointment_command import CancelAppointmentCommand
from backend.application.commands.create_appointment_command import CreateAppointmentCommand
from backend.application.commands.reschedule_appointment_command import (
    RescheduleAppointmentCommand,
)
from backend.application.queries.get_appointment_query import GetAppointmentQuery
from backend.application.queries.list_barber_appointments_query import (
    ListBarberAppointmentsQuery,
)
from backend.application.queries.list_client_appointments_query import (
    ListClientAppointmentsQuery,
)
from backend.infrastructure.schemas import (
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentRescheduleRequest,
)


def build_create_appointment_command(payload: AppointmentCreateRequest) -> CreateAppointmentCommand:
    return CreateAppointmentCommand(
        barber_id=payload.barber_id,
        client_id=payload.client_id,
        service_id=payload.service_id,
        start_at=payload.data_inicio,
    )


def build_reschedule_appointment_command(
    appointment_id: int, payload: AppointmentRescheduleRequest
) -> RescheduleAppointmentCommand:
    return RescheduleAppointmentCommand(
        appointment_id=appointment_id,
        start_at=payload.nova_data_inicio,
    )


def build_cancel_appointment_command(appointment_id: int) -> CancelAppointmentCommand:
    return CancelAppointmentCommand(appointment_id=appointment_id)


def build_get_appointment_query(appointment_id: int) -> GetAppointmentQuery:
    return GetAppointmentQuery(appointment_id=appointment_id)


def build_list_barber_appointments_query(
    barber_id: int, target_date: date | None = None
) -> ListBarberAppointmentsQuery:
    return ListBarberAppointmentsQuery(barber_id=barber_id, target_date=target_date)


def build_list_client_appointments_query(
    client_id: int, target_date: date | None = None
) -> ListClientAppointmentsQuery:
    return ListClientAppointmentsQuery(client_id=client_id, target_date=target_date)


def ensure_appointment_found(appointment):
    if appointment is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return appointment
