from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.barber_http import (
    build_create_barber_command,
    build_delete_barber_command,
    build_get_barber_query,
    build_list_barbers_query,
    build_update_barber_command,
    ensure_barber_deleted,
    ensure_barber_found,
    ensure_barber_update_payload_has_changes,
)
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import BarberCreate, BarberResponse, BarberUpdate
from meditor import build_mediator
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id

router = APIRouter(prefix="/barbers", tags=["Barbers"])


@router.post("/", response_model=BarberResponse, status_code=status.HTTP_201_CREATED)
async def create_barber(
    payload: BarberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    return await mediator.send(build_create_barber_command(payload, tenant_id))


@router.get("/", response_model=list[BarberResponse])
async def list_barbers(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    return await mediator.send(build_list_barbers_query(tenant_id))


@router.get("/{barber_id}", response_model=BarberResponse)
async def get_barber(
    barber_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    barber = await mediator.send(build_get_barber_query(barber_id, tenant_id))
    return ensure_barber_found(barber)


@router.put("/{barber_id}", response_model=BarberResponse)
async def replace_barber(
    barber_id: int,
    payload: BarberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    barber = await mediator.send(build_update_barber_command(barber_id, payload, tenant_id))
    return ensure_barber_found(barber)


@router.patch("/{barber_id}", response_model=BarberResponse)
async def update_barber(
    barber_id: int,
    payload: BarberUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    payload = ensure_barber_update_payload_has_changes(payload)
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    barber = await mediator.send(build_update_barber_command(barber_id, payload, tenant_id))
    return ensure_barber_found(barber)


@router.delete("/{barber_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_barber(
    barber_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    deleted = await mediator.send(build_delete_barber_command(barber_id, tenant_id))
    ensure_barber_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
