from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.application.commands.redeem_loyalty_command import RedeemLoyaltyCommand
from backend.application.queries.get_loyalty_account_query import GetLoyaltyAccountQuery
from backend.core.client import Client
from backend.core.exceptions import ConflictError, NotFoundError
from backend.core.roles import ADMIN_ROLE, CLIENT_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    LoyaltyAccountResponse,
    LoyaltyRedeemRequest,
)
from meditor import build_mediator

router = APIRouter(prefix="/loyalty", tags=["Loyalty"])


def _get_user_id(current_user):
    if isinstance(current_user, dict):
        return current_user.get("id")
    return getattr(current_user, "id", None)


@router.get("/me", response_model=LoyaltyAccountResponse)
async def get_my_loyalty(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(CLIENT_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    user_id = _get_user_id(current_user)
    client = (
        db.query(Client)
        .filter(Client.user_id == user_id, Client.deleted.is_(False))
        .first()
    )
    if client is None:
        raise NotFoundError("Client not found")
    mediator = build_mediator(db)
    return await mediator.send(
        GetLoyaltyAccountQuery(client_id=client.id, tenant_id=tenant_id)
    )


@router.post(
    "/redeem",
    response_model=LoyaltyAccountResponse,
    status_code=status.HTTP_200_OK,
)
async def redeem_loyalty_points(
    payload: LoyaltyRedeemRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(CLIENT_ROLE, ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    user_id = _get_user_id(current_user)
    client = (
        db.query(Client)
        .filter(Client.user_id == user_id, Client.deleted.is_(False))
        .first()
    )
    if client is None:
        raise NotFoundError("Client not found")
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            RedeemLoyaltyCommand(
                client_id=client.id,
                pontos=payload.pontos,
                tenant_id=tenant_id,
                descricao=payload.descricao,
            )
        )
    except (NotFoundError, ConflictError) as exc:
        raise to_http_exception(exc) from exc
