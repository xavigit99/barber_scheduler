from datetime import date

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.api.appointment_http import (
    build_cancel_appointment_command,
    build_create_appointment_command,
    build_get_appointment_query,
    build_list_barber_appointments_query,
    build_list_client_appointments_query,
    build_reschedule_appointment_command,
    ensure_appointment_found,
)
from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.core.barber import Barber
from backend.core.client import Client
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    AppointmentCreateRequest,
    AppointmentRescheduleRequest,
    AppointmentResponse,
)
from meditor import build_mediator

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _get_user_id(current_user):
    if isinstance(current_user, dict):
        return current_user.get("id")
    return getattr(current_user, "id", None)


def _get_user_role(current_user):
    if isinstance(current_user, dict):
        return current_user.get("role")
    return getattr(current_user, "role", None)


def _authorize_user_for_appointment(current_user, appointment, db: Session):
    role = _get_user_role(current_user)
    user_id = _get_user_id(current_user)

    if role == ADMIN_ROLE:
        return

    if role == BARBER_ROLE:
        barber = (
            db.query(Barber)
            .filter(
                Barber.user_id == user_id,
                Barber.id == appointment.barber_id,
                Barber.deleted.is_(False),
            )
            .first()
        )
        if barber is not None:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    if role == CLIENT_ROLE:
        client = (
            db.query(Client)
            .filter(
                Client.user_id == user_id,
                Client.id == appointment.client_id,
                Client.deleted.is_(False),
            )
            .first()
        )
        if client is not None:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions",
    )


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    user_id = _get_user_id(current_user)
    role = _get_user_role(current_user)
    if role == CLIENT_ROLE:
        own_client = (
            db.query(Client)
            .filter(Client.user_id == user_id, Client.deleted.is_(False))
            .first()
        )
        if own_client is None or own_client.id != payload.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clients may only create their own appointments",
            )
    try:
        return await mediator.send(build_create_appointment_command(payload, tenant_id))
    except (ConflictError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: int,
    payload: AppointmentRescheduleRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE)),
):
    mediator = build_mediator(db)
    appointment = await mediator.send(build_get_appointment_query(appointment_id))
    ensure_appointment_found(appointment)
    _authorize_user_for_appointment(current_user, appointment, db)
    try:
        return await mediator.send(
            build_reschedule_appointment_command(appointment_id, payload)
        )
    except (ConflictError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE)),
):
    mediator = build_mediator(db)
    appointment = await mediator.send(build_get_appointment_query(appointment_id))
    ensure_appointment_found(appointment)
    _authorize_user_for_appointment(current_user, appointment, db)
    deleted = await mediator.send(build_cancel_appointment_command(appointment_id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/barbers/{barber_id}",
    response_model=list[AppointmentResponse],
)
async def list_barber_appointments(
    barber_id: int,
    target_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    role = _get_user_role(current_user)
    user_id = _get_user_id(current_user)

    if role == BARBER_ROLE:
        # Barbers can only view their own schedule
        barber = (
            db.query(Barber)
            .filter(
                Barber.user_id == user_id,
                Barber.id == barber_id,
                Barber.deleted.is_(False),
            )
            .first()
        )
        if barber is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    mediator = build_mediator(db)
    appointments = await mediator.send(
        build_list_barber_appointments_query(barber_id, target_date, tenant_id)
    )
    return appointments


@router.get("/clients/me/appointments", response_model=list[AppointmentResponse])
async def list_my_appointments(
    target_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(CLIENT_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    user_id = _get_user_id(current_user)

    # Look up the client entity linked to this user
    client = (
        db.query(Client)
        .filter(
            Client.user_id == user_id,
            Client.deleted.is_(False),
        )
        .first()
    )
    if client is None:
        return []

    mediator = build_mediator(db)
    return await mediator.send(
        build_list_client_appointments_query(client.id, target_date, tenant_id)
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE)),
):
    mediator = build_mediator(db)
    appointment = await mediator.send(build_get_appointment_query(appointment_id))
    return ensure_appointment_found(appointment)
