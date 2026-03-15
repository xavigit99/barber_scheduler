from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import get_current_user, require_roles
from backend.api.auth_http import (
    build_authenticate_user_command,
    build_bootstrap_admin_command,
    build_create_user_command,
)
from backend.core.exceptions import AuthenticationError, ConflictError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    AuthLoginRequest,
    AuthTokenResponse,
    BootstrapAdminRequest,
    UserCreateRequest,
    UserResponse,
)
from meditor import build_mediator

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/bootstrap-admin",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bootstrap_admin(payload: BootstrapAdminRequest, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    try:
        return await mediator.send(build_bootstrap_admin_command(payload))
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: AuthLoginRequest, db: Session = Depends(get_db)):
    mediator = build_mediator(db)
    try:
        return await mediator.send(build_authenticate_user_command(payload))
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(build_create_user_command(payload))
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
