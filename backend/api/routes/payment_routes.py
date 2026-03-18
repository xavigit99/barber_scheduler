import os

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.application.commands.create_checkout_command import CreateCheckoutCommand
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import CheckoutRequest, CheckoutResponse
from meditor import build_mediator

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, CLIENT_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    if not os.getenv("STRIPE_SECRET_KEY"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe payments are not configured",
        )
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    try:
        return await mediator.send(
            CreateCheckoutCommand(appointment_id=payload.appointment_id, tenant_id=tid)
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not os.getenv("STRIPE_WEBHOOK_SECRET"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe webhook is not configured",
        )
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    from backend.application.handlers.payments.stripe_webhook_handler import (
        handle_stripe_webhook,
    )

    try:
        result = handle_stripe_webhook(db, payload, sig_header)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
