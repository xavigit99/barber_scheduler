from datetime import date

from backend.application.commands.cancel_appointment_command import CancelAppointmentCommand
from backend.application.commands.confirm_appointment_command import ConfirmAppointmentCommand
from backend.application.commands.create_appointment_command import CreateAppointmentCommand
from backend.application.commands.create_group_appointment_command import (
    CreateGroupAppointmentCommand,
)
from backend.application.commands.create_recurring_appointment_command import (
    CreateRecurringAppointmentCommand,
)
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
    AppointmentRescheduleRequest,
    GroupAppointmentRequest,
    RecurringAppointmentRequest,
)


def build_create_appointment_command(
    payload: AppointmentCreateRequest,
    tenant_id: int | None = None,
) -> CreateAppointmentCommand:
    return CreateAppointmentCommand(
        barber_id=payload.barber_id,
        client_id=payload.client_id,
        service_id=payload.service_id,
        start_at=payload.data_inicio,
        tenant_id=tenant_id,
        resource_id=payload.resource_id,
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
    barber_id: int,
    target_date: date | None = None,
    tenant_id: int | None = None,
) -> ListBarberAppointmentsQuery:
    return ListBarberAppointmentsQuery(
        barber_id=barber_id,
        target_date=target_date,
        tenant_id=tenant_id,
    )


def build_list_client_appointments_query(
    client_id: int,
    target_date: date | None = None,
    tenant_id: int | None = None,
) -> ListClientAppointmentsQuery:
    return ListClientAppointmentsQuery(
        client_id=client_id,
        target_date=target_date,
        tenant_id=tenant_id,
    )


def build_create_recurring_appointment_command(
    payload: RecurringAppointmentRequest,
    tenant_id: int | None = None,
) -> CreateRecurringAppointmentCommand:
    return CreateRecurringAppointmentCommand(
        barber_id=payload.barber_id,
        client_id=payload.client_id,
        service_id=payload.service_id,
        start_at=payload.data_inicio,
        recurrence=payload.recurrence,
        count=payload.count,
        tenant_id=tenant_id,
    )


def build_confirm_appointment_command(token: str) -> ConfirmAppointmentCommand:
    return ConfirmAppointmentCommand(token=token)


def build_create_group_appointment_command(
    payload: GroupAppointmentRequest,
    tenant_id: int | None = None,
) -> CreateGroupAppointmentCommand:
    return CreateGroupAppointmentCommand(
        barber_id=payload.barber_id,
        service_id=payload.service_id,
        start_at=payload.data_inicio,
        client_ids=payload.client_ids,
        tenant_id=tenant_id,
    )


def ensure_appointment_found(appointment):
    if appointment is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    return appointment
