from datetime import date

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.application.queries.report_daily_query import ReportDailyQuery
from backend.application.queries.report_revenue_query import ReportRevenueQuery
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from meditor import build_mediator

router = APIRouter(prefix="/admin/reports", tags=["Reports"])


@router.get("/daily")
async def report_daily(
    target_date: date,
    x_tenant_id: int = Header(..., alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(ReportDailyQuery(target_date=target_date, tenant_id=x_tenant_id))
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.get("/revenue")
async def report_revenue(
    start_date: date,
    end_date: date,
    x_tenant_id: int = Header(..., alias="X-Tenant-Id"),
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            ReportRevenueQuery(start_date=start_date, end_date=end_date, tenant_id=x_tenant_id)
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc
