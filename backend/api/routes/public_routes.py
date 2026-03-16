from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.api.error_http import to_http_exception
from backend.application.commands.public_create_appointment_command import (
    PublicCreateAppointmentCommand,
)
from backend.application.queries.get_available_slots_query import GetAvailableSlotsQuery
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import PublicAppointmentCreateRequest
from meditor import build_mediator

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/barbershops/{barbershop_id}/barbers/{barber_id}/slots")
async def public_get_slots(
    barbershop_id: int,
    barber_id: int,
    service_id: int,
    target_date: date,
    timezone: str = "Europe/Lisbon",
    db: Session = Depends(get_db),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            GetAvailableSlotsQuery(
                barber_id=barber_id,
                service_id=service_id,
                target_date=target_date,
                timezone=timezone,
            )
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.post("/appointments", status_code=status.HTTP_201_CREATED)
async def public_create_appointment(
    payload: PublicAppointmentCreateRequest,
    db: Session = Depends(get_db),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            PublicCreateAppointmentCommand(
                barber_id=payload.barber_id,
                service_id=payload.service_id,
                start_at=payload.start_at,
                tenant_id=payload.tenant_id,
                client_name=payload.client_name,
                client_email=payload.client_email,
                client_phone=payload.client_phone or "",
            )
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc
