from datetime import date

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.application.commands.purge_deleted_command import PurgeDeletedCommand
from backend.application.queries.audit_log_query import AuditLogQuery
from backend.application.queries.tenant_export_query import TenantExportQuery
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import PurgeRequest
from meditor import build_mediator

router = APIRouter(prefix="/admin", tags=["Audit"])


@router.get("/audit")
async def audit_log(
    entity: str,
    from_date: date | None = None,
    to_date: date | None = None,
    x_tenant_id: int = Header(..., alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            AuditLogQuery(entity=entity, tenant_id=x_tenant_id, from_date=from_date, to_date=to_date)
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.delete("/purge")
async def purge_deleted(
    body: PurgeRequest,
    x_tenant_id: int = Header(..., alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            PurgeDeletedCommand(entity=body.entity, older_than_days=body.older_than_days, tenant_id=x_tenant_id)
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.get("/export")
async def export_tenant(
    x_tenant_id: int = Header(..., alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(TenantExportQuery(tenant_id=x_tenant_id))
    except Exception as exc:
        raise to_http_exception(exc) from exc
