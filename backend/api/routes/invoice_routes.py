from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.application.commands.create_invoice_command import CreateInvoiceCommand
from backend.application.queries.get_invoice_query import GetInvoiceQuery
from backend.application.queries.list_invoices_query import ListInvoicesQuery
from backend.core.exceptions import NotFoundError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import InvoiceCreate, InvoiceResponse
from meditor import build_mediator

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    try:
        return await mediator.send(
            CreateInvoiceCommand(appointment_id=payload.appointment_id, tenant_id=tid)
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    return await mediator.send(ListInvoicesQuery(tenant_id=tid))


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    invoice = await mediator.send(GetInvoiceQuery(invoice_id=invoice_id, tenant_id=tid))
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
