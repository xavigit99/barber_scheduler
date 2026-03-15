from backend.api.http_utils import (
    ensure_payload_has_changes,
    ensure_resource_deleted,
    ensure_resource_found,
)
from backend.application.commands.create_barber_command import CreateBarberCommand
from backend.application.commands.delete_barber_command import DeleteBarberCommand
from backend.application.commands.update_barber_command import UpdateBarberCommand
from backend.application.queries.get_barber_query import GetBarberQuery
from backend.application.queries.list_barbers_query import ListBarbersQuery
from backend.infrastructure.schemas import BarberCreate, BarberUpdate


def build_create_barber_command(
    payload: BarberCreate,
    tenant_id: int,
) -> CreateBarberCommand:
    return CreateBarberCommand(
        name=payload.nome,
        email=payload.email,
        tenant_id=tenant_id,
        phone=payload.telefone,
    )


def build_delete_barber_command(barber_id: int, tenant_id: int) -> DeleteBarberCommand:
    return DeleteBarberCommand(barber_id=barber_id, tenant_id=tenant_id)


def build_get_barber_query(barber_id: int, tenant_id: int) -> GetBarberQuery:
    return GetBarberQuery(barber_id=barber_id, tenant_id=tenant_id)


def build_list_barbers_query(tenant_id: int) -> ListBarbersQuery:
    return ListBarbersQuery(tenant_id=tenant_id)


def build_update_barber_command(
    barber_id: int,
    payload: BarberCreate | BarberUpdate,
    tenant_id: int,
) -> UpdateBarberCommand:
    return UpdateBarberCommand(
        barber_id=barber_id,
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
        tenant_id=tenant_id,
    )


def ensure_barber_found(barber):
    return ensure_resource_found(barber, "Barber not found")


def ensure_barber_deleted(deleted: bool) -> None:
    ensure_resource_deleted(deleted, "Barber not found")


def ensure_barber_update_payload_has_changes(payload: BarberUpdate) -> BarberUpdate:
    return ensure_payload_has_changes(payload)
