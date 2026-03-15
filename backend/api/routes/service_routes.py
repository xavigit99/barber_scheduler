from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.service_http import (
    build_create_service_command,
    build_delete_service_command,
    build_get_service_query,
    build_list_services_query,
    build_update_service_command,
    ensure_service_deleted,
    ensure_service_found,
    ensure_service_update_payload_has_changes,
)
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import ServiceCreate, ServiceResponse, ServiceUpdate
from meditor import build_mediator

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    return await mediator.send(build_create_service_command(payload, tenant_id))


@router.get("/", response_model=list[ServiceResponse])
async def list_services(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    return await mediator.send(build_list_services_query(tenant_id))


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    service = await mediator.send(build_get_service_query(service_id, tenant_id))
    return ensure_service_found(service)


@router.put("/{service_id}", response_model=ServiceResponse)
async def replace_service(
    service_id: int,
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    service = await mediator.send(build_update_service_command(service_id, payload, tenant_id))
    return ensure_service_found(service)


@router.patch("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    payload = ensure_service_update_payload_has_changes(payload)
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    service = await mediator.send(build_update_service_command(service_id, payload, tenant_id))
    return ensure_service_found(service)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tenant_id = require_tenant_id(tenant_id)
    deleted = await mediator.send(build_delete_service_command(service_id, tenant_id))
    ensure_service_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
