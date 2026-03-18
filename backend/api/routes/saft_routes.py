from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.application.queries.saft_export_query import SaftExportQuery
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from meditor import build_mediator

router = APIRouter(prefix="/admin", tags=["SAF-T"])


@router.get("/saft")
async def saft_export(
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    """SAF-T stub export — returns structured JSON aggregation for a fiscal year (F36)."""
    if year is None:
        year = datetime.now(UTC).year
    mediator = build_mediator(db)
    try:
        return await mediator.send(SaftExportQuery(tenant_id=tenant_id, year=year))
    except Exception as exc:
        raise to_http_exception(exc) from exc
