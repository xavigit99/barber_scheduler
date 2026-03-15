from backend.application.commands.create_client_command import CreateClientCommand
from backend.application.commands.delete_client_command import DeleteClientCommand
from backend.application.commands.update_client_command import UpdateClientCommand
from backend.application.queries.get_client_query import GetClientQuery
from backend.application.queries.list_clients_query import ListClientsQuery
from backend.api.http_utils import (
    ensure_payload_has_changes,
    ensure_resource_deleted,
    ensure_resource_found,
)
from backend.infrastructure.schemas import ClientCreate, ClientUpdate


def build_create_client_command(payload: ClientCreate, tenant_id: int) -> CreateClientCommand:
    return CreateClientCommand(
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
        tenant_id=tenant_id,
    )


def build_delete_client_command(client_id: int, tenant_id: int) -> DeleteClientCommand:
    return DeleteClientCommand(client_id=client_id, tenant_id=tenant_id)


def build_get_client_query(client_id: int, tenant_id: int) -> GetClientQuery:
    return GetClientQuery(client_id=client_id, tenant_id=tenant_id)


def build_list_clients_query(tenant_id: int) -> ListClientsQuery:
    return ListClientsQuery(tenant_id=tenant_id)


def build_update_client_command(
    client_id: int,
    payload: ClientCreate | ClientUpdate,
    tenant_id: int,
) -> UpdateClientCommand:
    return UpdateClientCommand(
        client_id=client_id,
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
        tenant_id=tenant_id,
    )


def ensure_client_found(client):
    return ensure_resource_found(client, "Client not found")


def ensure_client_deleted(deleted: bool) -> None:
    ensure_resource_deleted(deleted, "Client not found")


def ensure_update_payload_has_changes(payload: ClientUpdate) -> ClientUpdate:
    return ensure_payload_has_changes(payload)
