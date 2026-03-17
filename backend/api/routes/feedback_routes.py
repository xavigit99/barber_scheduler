from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.feedback_http import (
    build_create_feedback_command,
    build_list_admin_feedback_query,
    build_list_barber_feedback_query,
    build_list_my_feedback_query,
)
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import FeedbackCreate, FeedbackResponse, PublicFeedbackResponse
from meditor import build_mediator

router = APIRouter(tags=["Feedback"])


def _get_user_id(current_user) -> int:
    if isinstance(current_user, dict):
        return current_user["id"]
    return current_user.id


@router.post("/feedback", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(CLIENT_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    user_id = _get_user_id(current_user)
    try:
        return await mediator.send(build_create_feedback_command(payload, user_id, tenant_id))
    except (ConflictError, ForbiddenError, NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.get("/feedback/barber/{barber_id}", response_model=list[PublicFeedbackResponse])
async def list_barber_feedback(
    barber_id: int,
    db: Session = Depends(get_db),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(build_list_barber_feedback_query(barber_id, tenant_id))
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.get("/feedback/me", response_model=list[FeedbackResponse])
async def list_my_feedback(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(CLIENT_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    user_id = _get_user_id(current_user)
    return await mediator.send(build_list_my_feedback_query(user_id, tenant_id))


@router.get("/admin/feedback", response_model=list[FeedbackResponse])
async def list_admin_feedback(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    return await mediator.send(build_list_admin_feedback_query(tenant_id))
