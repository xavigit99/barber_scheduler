from datetime import date

from backend.api.http_utils import ensure_payload_has_changes, ensure_resource_deleted
from backend.application.commands.create_barber_availability_command import (
    CreateBarberAvailabilityCommand,
)
from backend.application.commands.create_barber_block_command import CreateBarberBlockCommand
from backend.application.commands.delete_barber_availability_command import (
    DeleteBarberAvailabilityCommand,
)
from backend.application.commands.delete_barber_block_command import DeleteBarberBlockCommand
from backend.application.commands.update_barber_availability_command import (
    UpdateBarberAvailabilityCommand,
)
from backend.application.queries.get_available_slots_query import GetAvailableSlotsQuery
from backend.application.queries.list_barber_availabilities_query import (
    ListBarberAvailabilitiesQuery,
)
from backend.application.queries.list_barber_blocks_query import ListBarberBlocksQuery
from backend.infrastructure.schemas import (
    BarberAvailabilityCreate,
    BarberAvailabilityUpdate,
    BarberBlockCreate,
)


def build_create_barber_availability_command(
    barber_id: int,
    payload: BarberAvailabilityCreate,
    *,
    tenant_id: int | None = None,
) -> CreateBarberAvailabilityCommand:
    return CreateBarberAvailabilityCommand(
        barber_id=barber_id,
        weekday=payload.dia_semana,
        start_time=payload.hora_inicio,
        end_time=payload.hora_fim,
        tenant_id=tenant_id,
    )


def build_update_barber_availability_command(
    barber_id: int,
    availability_id: int,
    payload: BarberAvailabilityUpdate,
    *,
    tenant_id: int | None = None,
) -> UpdateBarberAvailabilityCommand:
    return UpdateBarberAvailabilityCommand(
        barber_id=barber_id,
        availability_id=availability_id,
        weekday=payload.dia_semana,
        start_time=payload.hora_inicio,
        end_time=payload.hora_fim,
        tenant_id=tenant_id,
    )


def build_delete_barber_availability_command(
    barber_id: int,
    availability_id: int,
    *,
    tenant_id: int | None = None,
) -> DeleteBarberAvailabilityCommand:
    return DeleteBarberAvailabilityCommand(
        barber_id=barber_id,
        availability_id=availability_id,
        tenant_id=tenant_id,
    )


def build_list_barber_availabilities_query(
    barber_id: int,
    *,
    tenant_id: int | None = None,
) -> ListBarberAvailabilitiesQuery:
    return ListBarberAvailabilitiesQuery(barber_id=barber_id, tenant_id=tenant_id)


def build_create_barber_block_command(
    barber_id: int,
    payload: BarberBlockCreate,
    *,
    tenant_id: int | None = None,
) -> CreateBarberBlockCommand:
    return CreateBarberBlockCommand(
        barber_id=barber_id,
        kind=payload.tipo,
        start_at=payload.inicio,
        end_at=payload.fim,
        reason=payload.motivo,
        tenant_id=tenant_id,
    )


def build_delete_barber_block_command(
    barber_id: int,
    block_id: int,
    *,
    tenant_id: int | None = None,
) -> DeleteBarberBlockCommand:
    return DeleteBarberBlockCommand(
        barber_id=barber_id,
        block_id=block_id,
        tenant_id=tenant_id,
    )


def build_list_barber_blocks_query(
    barber_id: int,
    *,
    tenant_id: int | None = None,
) -> ListBarberBlocksQuery:
    return ListBarberBlocksQuery(barber_id=barber_id, tenant_id=tenant_id)


def build_get_available_slots_query(
    barber_id: int,
    service_id: int,
    target_date: date,
    timezone: str,
) -> GetAvailableSlotsQuery:
    return GetAvailableSlotsQuery(
        barber_id=barber_id,
        service_id=service_id,
        target_date=target_date,
        timezone=timezone,
    )


def ensure_barber_availability_deleted(deleted: bool) -> None:
    ensure_resource_deleted(deleted, "Availability window not found")


def ensure_barber_block_deleted(deleted: bool) -> None:
    ensure_resource_deleted(deleted, "Availability block not found")


def ensure_barber_availability_update_payload_has_changes(
    payload: BarberAvailabilityUpdate,
) -> BarberAvailabilityUpdate:
    return ensure_payload_has_changes(payload)
