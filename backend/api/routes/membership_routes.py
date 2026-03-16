from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.membership_http import (
    build_create_membership_command,
    build_delete_membership_command,
    build_list_memberships_query,
    ensure_membership_deleted,
)
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import MembershipCreate, MembershipResponse
from meditor import build_mediator

router = APIRouter(prefix="/barbershops", tags=["Memberships"])


@router.post(
    "/{barbershop_id}/memberships",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_membership(
    barbershop_id: int,
    payload: MembershipCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_create_membership_command(barbershop_id, payload, tenant_id=tenant_id)
        )
    except (ConflictError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.get("/{barbershop_id}/memberships", response_model=list[MembershipResponse])
async def list_memberships(
    barbershop_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(build_list_memberships_query(barbershop_id, tenant_id=tenant_id))
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.delete(
    "/{barbershop_id}/memberships/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_membership(
    barbershop_id: int,
    membership_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    deleted = await mediator.send(
        build_delete_membership_command(barbershop_id, membership_id, tenant_id=tenant_id)
    )
    ensure_membership_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
