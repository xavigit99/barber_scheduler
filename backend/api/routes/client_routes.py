from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from backend.api.client_http import (
    build_create_client_command,
    build_delete_client_command,
    build_get_client_query,
    build_list_clients_query,
    build_update_client_command,
    ensure_client_deleted,
    ensure_client_found,
    ensure_update_payload_has_changes,
)
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import ClientCreate, ClientResponse, ClientUpdate
from meditor import build_mediator

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    return await mediator.send(build_create_client_command(payload))


@router.get("/", response_model=list[ClientResponse])
async def list_clients(db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    return await mediator.send(build_list_clients_query())


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    client = await mediator.send(build_get_client_query(client_id))
    return ensure_client_found(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def replace_client(
    client_id: int,
    payload: ClientCreate,
    db: Session = Depends(get_db),
):
    mediator = build_mediator(db)
    client = await mediator.send(build_update_client_command(client_id, payload))
    return ensure_client_found(client)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
):
    payload = ensure_update_payload_has_changes(payload)
    mediator = build_mediator(db)
    client = await mediator.send(build_update_client_command(client_id, payload))
    return ensure_client_found(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    deleted = await mediator.send(build_delete_client_command(client_id))
    ensure_client_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
