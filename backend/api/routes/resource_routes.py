from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.application.commands.create_resource_command import CreateResourceCommand
from backend.application.commands.delete_resource_command import DeleteResourceCommand
from backend.application.queries.list_resources_query import ListResourcesQuery
from backend.core.exceptions import NotFoundError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import ResourceCreate, ResourceResponse
from meditor import build_mediator

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    payload: ResourceCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            CreateResourceCommand(
                nome=payload.nome,
                tipo=payload.tipo,
                tenant_id=tenant_id,
            )
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.get("", response_model=list[ResourceResponse])
async def list_resources(
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    return await mediator.send(ListResourcesQuery(tenant_id=tenant_id))


@router.delete("/{resource_id}", status_code=status.HTTP_200_OK)
async def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            DeleteResourceCommand(resource_id=resource_id, tenant_id=tenant_id)
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc
