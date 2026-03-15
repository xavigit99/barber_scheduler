from backend.api.http_utils import (
    ensure_payload_has_changes,
    ensure_resource_deleted,
    ensure_resource_found,
)
from backend.application.commands.create_service_command import CreateServiceCommand
from backend.application.commands.delete_service_command import DeleteServiceCommand
from backend.application.commands.update_service_command import UpdateServiceCommand
from backend.application.queries.get_service_query import GetServiceQuery
from backend.application.queries.list_services_query import ListServicesQuery
from backend.infrastructure.schemas import ServiceCreate, ServiceUpdate


def build_create_service_command(
    payload: ServiceCreate,
    tenant_id: int,
) -> CreateServiceCommand:
    return CreateServiceCommand(
        name=payload.nome,
        duration_minutes=payload.duracao_minutos,
        price=payload.preco,
        tenant_id=tenant_id,
    )


def build_delete_service_command(service_id: int, tenant_id: int) -> DeleteServiceCommand:
    return DeleteServiceCommand(service_id=service_id, tenant_id=tenant_id)


def build_get_service_query(service_id: int, tenant_id: int) -> GetServiceQuery:
    return GetServiceQuery(service_id=service_id, tenant_id=tenant_id)


def build_list_services_query(tenant_id: int) -> ListServicesQuery:
    return ListServicesQuery(tenant_id=tenant_id)


def build_update_service_command(
    service_id: int,
    payload: ServiceCreate | ServiceUpdate,
    tenant_id: int,
) -> UpdateServiceCommand:
    return UpdateServiceCommand(
        service_id=service_id,
        name=payload.nome,
        duration_minutes=payload.duracao_minutos,
        price=payload.preco,
        tenant_id=tenant_id,
    )


def ensure_service_found(service):
    return ensure_resource_found(service, "Service not found")


def ensure_service_deleted(deleted: bool) -> None:
    ensure_resource_deleted(deleted, "Service not found")


def ensure_service_update_payload_has_changes(payload: ServiceUpdate) -> ServiceUpdate:
    return ensure_payload_has_changes(payload)
