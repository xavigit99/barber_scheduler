from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.barbershop_http import (
    build_create_barbershop_command,
    build_delete_barbershop_command,
    build_get_barbershop_query,
    build_list_barbershops_query,
    build_update_barbershop_command,
    ensure_barbershop_deleted,
    ensure_barbershop_found,
    ensure_barbershop_update_payload_has_changes,
)
from backend.api.error_http import to_http_exception
from backend.core.exceptions import NotFoundError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    BarbershopCreate,
    BarbershopResponse,
    BarbershopUpdate,
)
from meditor import build_mediator

router = APIRouter(prefix="/barbershops", tags=["Barbershops"])


@router.post("/", response_model=BarbershopResponse, status_code=status.HTTP_201_CREATED)
async def create_barbershop(
    payload: BarbershopCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            build_create_barbershop_command(payload, owner_user_id=current_user.id)
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.get("/", response_model=list[BarbershopResponse])
async def list_barbershops(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    return await mediator.send(build_list_barbershops_query())


@router.get("/{barbershop_id}", response_model=BarbershopResponse)
async def get_barbershop(
    barbershop_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    barbershop = await mediator.send(build_get_barbershop_query(barbershop_id))
    return ensure_barbershop_found(barbershop)


@router.put("/{barbershop_id}", response_model=BarbershopResponse)
async def replace_barbershop(
    barbershop_id: int,
    payload: BarbershopCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    barbershop = await mediator.send(build_update_barbershop_command(barbershop_id, payload))
    return ensure_barbershop_found(barbershop)


@router.patch("/{barbershop_id}", response_model=BarbershopResponse)
async def update_barbershop(
    barbershop_id: int,
    payload: BarbershopUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    payload = ensure_barbershop_update_payload_has_changes(payload)
    mediator = build_mediator(db)
    barbershop = await mediator.send(build_update_barbershop_command(barbershop_id, payload))
    return ensure_barbershop_found(barbershop)


@router.delete("/{barbershop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_barbershop(
    barbershop_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    deleted = await mediator.send(build_delete_barbershop_command(barbershop_id))
    ensure_barbershop_deleted(deleted)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
