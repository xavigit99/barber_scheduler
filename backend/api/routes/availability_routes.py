from datetime import date

from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.availability_http import (
    build_create_barber_availability_command,
    build_create_barber_block_command,
    build_delete_barber_availability_command,
    build_delete_barber_block_command,
    build_get_available_dates_query,
    build_get_available_slots_query,
    build_list_barber_availabilities_query,
    build_list_barber_blocks_query,
    build_update_barber_availability_command,
    ensure_barber_availability_deleted,
    ensure_barber_availability_update_payload_has_changes,
    ensure_barber_block_deleted,
)
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    AvailableDatesResponse,
    AvailableSlotsResponse,
    BarberAvailabilityCreate,
    BarberAvailabilityResponse,
    BarberAvailabilityUpdate,
    BarberBlockCreate,
    BarberBlockResponse,
)
from meditor import build_mediator

router = APIRouter(prefix="/barbers/{barber_id}/availability", tags=["Availability"])


@router.post(
    "/windows",
    response_model=BarberAvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_barber_availability(
    barber_id: int,
    payload: BarberAvailabilityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_create_barber_availability_command(barber_id, payload, tenant_id=tenant_id)
        )
    except (ConflictError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.get("/windows", response_model=list[BarberAvailabilityResponse])
async def list_barber_availabilities(
    barber_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_list_barber_availabilities_query(barber_id, tenant_id=tenant_id)
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.patch("/windows/{availability_id}", response_model=BarberAvailabilityResponse)
async def update_barber_availability(
    barber_id: int,
    availability_id: int,
    payload: BarberAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    payload = ensure_barber_availability_update_payload_has_changes(payload)
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_update_barber_availability_command(barber_id, availability_id, payload, tenant_id=tenant_id)
        )
    except (ConflictError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.delete("/windows/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_barber_availability(
    barber_id: int,
    availability_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    deleted = await mediator.send(
        build_delete_barber_availability_command(barber_id, availability_id, tenant_id=tenant_id)
    )
    ensure_barber_availability_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/blocks", response_model=BarberBlockResponse, status_code=status.HTTP_201_CREATED)
async def create_barber_block(
    barber_id: int,
    payload: BarberBlockCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_create_barber_block_command(barber_id, payload, tenant_id=tenant_id)
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.get("/blocks", response_model=list[BarberBlockResponse])
async def list_barber_blocks(
    barber_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(build_list_barber_blocks_query(barber_id, tenant_id=tenant_id))
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.delete("/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_barber_block(
    barber_id: int,
    block_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    x_tenant_id: int | None = Header(default=None, alias=TENANT_HEADER_ALIAS),
):
    tenant_id = require_tenant_id(x_tenant_id)
    mediator = build_mediator(db)
    deleted = await mediator.send(
        build_delete_barber_block_command(barber_id, block_id, tenant_id=tenant_id)
    )
    ensure_barber_block_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/slots", response_model=AvailableSlotsResponse)
async def get_available_slots(
    barber_id: int,
    service_id: int,
    target_date: date,
    timezone: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_get_available_slots_query(
                barber_id=barber_id,
                service_id=service_id,
                target_date=target_date,
                timezone=timezone,
            )
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.get("/dates", response_model=AvailableDatesResponse)
async def get_available_dates(
    barber_id: int,
    service_id: int,
    start_date: date,
    end_date: date,
    timezone: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_get_available_dates_query(
                barber_id=barber_id,
                service_id=service_id,
                start_date=start_date,
                end_date=end_date,
                timezone=timezone,
            )
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc
