from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.payment_http import build_update_appointment_payment_command
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    AppointmentPaymentResponse,
    AppointmentPaymentUpdateRequest,
)
from meditor import build_mediator

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.patch("/appointments/{appointment_id}", response_model=AppointmentPaymentResponse)
async def update_appointment_payment(
    appointment_id: int,
    payload: AppointmentPaymentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    try:
        return await mediator.send(
            build_update_appointment_payment_command(
                appointment_id=appointment_id,
                payload=payload,
                tenant_id=tid,
            )
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc
