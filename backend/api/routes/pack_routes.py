from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.application.commands.create_service_pack_command import CreateServicePackCommand
from backend.application.commands.purchase_client_pack_command import PurchaseClientPackCommand
from backend.application.queries.list_client_packs_query import ListClientPacksQuery
from backend.application.queries.list_service_packs_query import ListServicePacksQuery
from backend.core.client_profiles import get_client_profile_for_user
from backend.core.exceptions import NotFoundError
from backend.core.roles import ADMIN_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    ClientPackCreate,
    ClientPackResponse,
    ServicePackCreate,
    ServicePackResponse,
)
from meditor import build_mediator

router = APIRouter(prefix="/packs", tags=["Packs"])


def _get_user_id(current_user):
    if isinstance(current_user, dict):
        return current_user.get("id")
    return getattr(current_user, "id", None)


# ── Service Packs (admin) ─────────────────────────────────────────────────────


@router.post(
    "/services",
    response_model=ServicePackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service_pack(
    payload: ServicePackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            CreateServicePackCommand(
                nome=payload.nome,
                service_id=payload.service_id,
                n_sessoes=payload.n_sessoes,
                preco=payload.preco,
                tenant_id=tenant_id,
            )
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.get("/services", response_model=list[ServicePackResponse])
async def list_service_packs(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    return await mediator.send(ListServicePacksQuery(tenant_id=tenant_id))


# ── Client Packs ──────────────────────────────────────────────────────────────


@router.post(
    "/purchase",
    response_model=ClientPackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def purchase_client_pack(
    payload: ClientPackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            PurchaseClientPackCommand(
                client_id=payload.client_id,
                service_pack_id=payload.service_pack_id,
                tenant_id=tenant_id,
                expira_em=payload.expira_em,
            )
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.get("/me", response_model=list[ClientPackResponse])
async def list_my_packs(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(CLIENT_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    user_id = _get_user_id(current_user)
    client = get_client_profile_for_user(db, user_id=user_id, tenant_id=tenant_id)
    if client is None:
        return []
    mediator = build_mediator(db)
    return await mediator.send(
        ListClientPacksQuery(client_id=client.id, tenant_id=tenant_id)
    )
