from backend.api.http_utils import (
    ensure_payload_has_changes,
    ensure_resource_deleted,
    ensure_resource_found,
)
from backend.application.commands.create_barbershop_command import CreateBarbershopCommand
from backend.application.commands.delete_barbershop_command import DeleteBarbershopCommand
from backend.application.commands.update_barbershop_command import UpdateBarbershopCommand
from backend.application.queries.get_barbershop_query import GetBarbershopQuery
from backend.application.queries.list_barbershops_query import ListBarbershopsQuery
from backend.infrastructure.schemas import BarbershopCreate, BarbershopUpdate


def build_create_barbershop_command(
    payload: BarbershopCreate,
    *,
    owner_user_id: int,
) -> CreateBarbershopCommand:
    return CreateBarbershopCommand(
        name=payload.nome,
        owner_user_id=owner_user_id,
    )


def build_delete_barbershop_command(
    barbershop_id: int,
    *,
    tenant_id: int | None = None,
) -> DeleteBarbershopCommand:
    return DeleteBarbershopCommand(barbershop_id=barbershop_id, tenant_id=tenant_id)


def build_get_barbershop_query(
    barbershop_id: int,
    *,
    tenant_id: int | None = None,
) -> GetBarbershopQuery:
    return GetBarbershopQuery(barbershop_id=barbershop_id, tenant_id=tenant_id)


def build_list_barbershops_query(*, tenant_id: int | None = None) -> ListBarbershopsQuery:
    return ListBarbershopsQuery(tenant_id=tenant_id)


def build_update_barbershop_command(
    barbershop_id: int,
    payload: BarbershopCreate | BarbershopUpdate,
    *,
    tenant_id: int | None = None,
) -> UpdateBarbershopCommand:
    return UpdateBarbershopCommand(
        barbershop_id=barbershop_id,
        name=payload.nome,
        tenant_id=tenant_id,
    )


def ensure_barbershop_found(barbershop):
    return ensure_resource_found(barbershop, "Barbershop not found")


def ensure_barbershop_deleted(deleted: bool) -> None:
    ensure_resource_deleted(deleted, "Barbershop not found")


def ensure_barbershop_update_payload_has_changes(
    payload: BarbershopUpdate,
) -> BarbershopUpdate:
    return ensure_payload_has_changes(payload)
