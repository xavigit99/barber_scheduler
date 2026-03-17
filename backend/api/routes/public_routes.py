from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.api.error_http import to_http_exception
from backend.application.commands.public_create_appointment_command import (
    PublicCreateAppointmentCommand,
)
from backend.application.queries.get_available_slots_query import GetAvailableSlotsQuery
from backend.application.queries.list_barbers_query import ListBarbersQuery
from backend.application.queries.list_barbershops_query import ListBarbershopsQuery
from backend.application.queries.list_services_query import ListServicesQuery
from backend.core.barber import Barber
from backend.core.exceptions import NotFoundError
from backend.core.service import Service
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    BarberResponse,
    BarbershopResponse,
    PublicAppointmentCreateRequest,
    ServiceResponse,
)
from meditor import build_mediator
from repositories.base_repository import BaseRepository

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/barbershops", response_model=list[BarbershopResponse])
async def public_list_barbershops(db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    return await mediator.send(ListBarbershopsQuery(tenant_id=None))


@router.get("/tenants/{tenant_id}/barbers", response_model=list[BarberResponse])
async def public_list_barbers(
    tenant_id: int,
    db: Session = Depends(get_db),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(ListBarbersQuery(tenant_id=tenant_id))
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.get("/tenants/{tenant_id}/services", response_model=list[ServiceResponse])
async def public_list_services(
    tenant_id: int,
    db: Session = Depends(get_db),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(ListServicesQuery(tenant_id=tenant_id))
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.get("/tenants/{tenant_id}/barbers/{barber_id}/slots")
async def public_get_slots_v2(
    tenant_id: int,
    barber_id: int,
    service_id: int,
    target_date: date,
    timezone: str = "Europe/Lisbon",
    db: Session = Depends(get_db),
):
    # Validate barber and service belong to the requested tenant
    barber = BaseRepository(Barber, db).get(barber_id)
    if barber is None or barber.tenant_id != tenant_id:
        raise to_http_exception(NotFoundError("Barber not found"))
    service = BaseRepository(Service, db).get(service_id)
    if service is None or service.tenant_id != tenant_id:
        raise to_http_exception(NotFoundError("Service not found"))

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


@router.get(
    "/barbershops/{barbershop_id}/barbers/{barber_id}/slots",
    deprecated=True,
)
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
