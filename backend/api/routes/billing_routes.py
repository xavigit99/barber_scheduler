from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.billing_http import (
    build_create_billing_portal_command,
    build_create_subscription_checkout_command,
)
from backend.api.error_http import to_http_exception
from backend.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    BillingCheckoutRequest,
    BillingCheckoutResponse,
    BillingPortalResponse,
)
from meditor import build_mediator

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post(
    "/barbershops/{barbershop_id}/checkout",
    response_model=BillingCheckoutResponse,
)
async def create_subscription_checkout(
    barbershop_id: int,
    payload: BillingCheckoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_create_subscription_checkout_command(
                barbershop_id,
                payload,
                owner_user_id=current_user.id,
            )
        )
    except (ForbiddenError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.post(
    "/barbershops/{barbershop_id}/portal",
    response_model=BillingPortalResponse,
)
async def create_billing_portal(
    barbershop_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_create_billing_portal_command(
                barbershop_id,
                owner_user_id=current_user.id,
            )
        )
    except (ForbiddenError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.post("/webhook")
async def stripe_billing_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    from backend.application.handlers.payments.billing_webhook_handler import (
        handle_billing_webhook,
    )

    try:
        return handle_billing_webhook(db, payload, sig_header)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
