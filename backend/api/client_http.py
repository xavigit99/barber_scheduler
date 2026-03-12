from fastapi import HTTPException, status

from backend.application.commands.create_client_command import CreateClientCommand
from backend.application.commands.delete_client_command import DeleteClientCommand
from backend.application.commands.update_client_command import UpdateClientCommand
from backend.application.queries.get_client_query import GetClientQuery
from backend.application.queries.list_clients_query import ListClientsQuery
from backend.infrastructure.schemas import ClientCreate, ClientUpdate


def build_create_client_command(payload: ClientCreate) -> CreateClientCommand:
    return CreateClientCommand(
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
    )


def build_delete_client_command(client_id: int) -> DeleteClientCommand:
    return DeleteClientCommand(client_id=client_id)


def build_get_client_query(client_id: int) -> GetClientQuery:
    return GetClientQuery(client_id=client_id)


def build_list_clients_query() -> ListClientsQuery:
    return ListClientsQuery()


def build_update_client_command(
    client_id: int,
    payload: ClientCreate | ClientUpdate,
) -> UpdateClientCommand:
    return UpdateClientCommand(
        client_id=client_id,
        name=payload.nome,
        email=payload.email,
        phone=payload.telefone,
    )


def ensure_client_found(client):
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


def ensure_client_deleted(deleted: bool) -> None:
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )


def ensure_update_payload_has_changes(payload: ClientUpdate) -> ClientUpdate:
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided",
        )
    return payload
