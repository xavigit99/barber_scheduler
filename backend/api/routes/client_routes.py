from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
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
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import ClientCreate, ClientResponse, ClientUpdate
from meditor import build_mediator

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    return await mediator.send(build_create_client_command(payload, tenant_id))


@router.get("/", response_model=list[ClientResponse])
async def list_clients(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    return await mediator.send(build_list_clients_query(tenant_id))


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    client = await mediator.send(build_get_client_query(client_id, tenant_id))
    return ensure_client_found(client)


@router.put("/{client_id}", response_model=ClientResponse)
async def replace_client(
    client_id: int,
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    client = await mediator.send(build_update_client_command(client_id, payload, tenant_id))
    return ensure_client_found(client)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    payload = ensure_update_payload_has_changes(payload)
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    client = await mediator.send(build_update_client_command(client_id, payload, tenant_id))
    return ensure_client_found(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    deleted = await mediator.send(build_delete_client_command(client_id, tenant_id))
    ensure_client_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
