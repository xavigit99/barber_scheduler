from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.api.webhook_http import (
    build_create_webhook_command,
    build_delete_webhook_command,
    build_list_webhooks_query,
)
from backend.core.exceptions import ValidationError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import WebhookCreate, WebhookResponse
from meditor import build_mediator

router = APIRouter(tags=["Webhooks"])


@router.get("/admin/webhooks", response_model=list[WebhookResponse])
async def list_webhooks(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    tid = require_tenant_id(tenant_id)
    mediator = build_mediator(db)
    return await mediator.send(build_list_webhooks_query(tid))


@router.post("/admin/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    payload: WebhookCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    tid = require_tenant_id(tenant_id)
    mediator = build_mediator(db)
    try:
        return await mediator.send(build_create_webhook_command(payload, tid))
    except ValidationError as exc:
        raise to_http_exception(exc) from exc


@router.delete("/admin/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    tid = require_tenant_id(tenant_id)
    mediator = build_mediator(db)
    deleted = await mediator.send(build_delete_webhook_command(webhook_id, tid))
    if not deleted:
        from fastapi import HTTPException

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
