from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS, require_tenant_id
from backend.application.commands.create_campaign_command import CreateCampaignCommand
from backend.application.commands.send_campaign_command import SendCampaignCommand
from backend.application.queries.get_campaign_query import GetCampaignQuery
from backend.application.queries.list_campaigns_query import ListCampaignsQuery
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import CampaignCreate, CampaignResponse
from meditor import build_mediator

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    return await mediator.send(
        CreateCampaignCommand(
            nome=payload.nome,
            subject=payload.subject,
            body_template=payload.body_template,
            segment_filters=payload.segment_filters,
            tenant_id=tid,
        )
    )


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    return await mediator.send(ListCampaignsQuery(tenant_id=tid))


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    campaign = await mediator.send(GetCampaignQuery(campaign_id=campaign_id, tenant_id=tid))
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post("/{campaign_id}/send", response_model=CampaignResponse)
async def send_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int | None = Header(None, alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    tid = require_tenant_id(tenant_id)
    try:
        return await mediator.send(
            SendCampaignCommand(campaign_id=campaign_id, tenant_id=tid)
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc
