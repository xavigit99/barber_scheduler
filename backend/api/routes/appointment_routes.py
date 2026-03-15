from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
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
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    AppointmentCreateRequest,
    AppointmentResponse,
    AppointmentRescheduleRequest,
)
from meditor import build_mediator

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def _get_user_id(current_user):
    if isinstance(current_user, dict):
        return current_user.get("id")
    return getattr(current_user, "id", None)


def _authorize_user_for_appointment(current_user, appointment):
    user_id = _get_user_id(current_user)
    role = getattr(current_user, "role", None) if not isinstance(current_user, dict) else current_user.get("role")
    if role == ADMIN_ROLE:
        return
    if role == BARBER_ROLE and appointment.barber_id == user_id:
        return
    if role == CLIENT_ROLE and appointment.client_id == user_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE)),
):
    mediator = build_mediator(db)
    user_id = _get_user_id(current_user)
    if getattr(current_user, "role", None) == CLIENT_ROLE and payload.client_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clients may only create their own appointments",
        )
    try:
        return await mediator.send(build_create_appointment_command(payload))
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
    _authorize_user_for_appointment(current_user, appointment)
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
    _authorize_user_for_appointment(current_user, appointment)
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
):
    mediator = build_mediator(db)
    appointments = await mediator.send(
        build_list_barber_appointments_query(barber_id, target_date)
    )
    return appointments


@router.get("/clients/me/appointments", response_model=list[AppointmentResponse])
async def list_my_appointments(
    target_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(CLIENT_ROLE)),
):
    mediator = build_mediator(db)
    user_id = _get_user_id(current_user)
    return await mediator.send(
        build_list_client_appointments_query(user_id, target_date)
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
