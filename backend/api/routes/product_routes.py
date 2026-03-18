from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from backend.api.auth_dependencies import require_roles
from backend.api.error_http import to_http_exception
from backend.api.tenant_header import TENANT_HEADER_ALIAS
from backend.application.commands.adjust_stock_command import AdjustStockCommand
from backend.application.commands.create_product_command import CreateProductCommand
from backend.application.commands.create_service_product_command import (
    CreateServiceProductCommand,
)
from backend.application.commands.delete_product_command import DeleteProductCommand
from backend.application.commands.update_product_command import UpdateProductCommand
from backend.application.queries.list_products_query import ListProductsQuery
from backend.application.queries.list_service_products_query import (
    ListServiceProductsQuery,
)
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.roles import ADMIN_ROLE
from backend.infrastructure.database import get_db
from backend.infrastructure.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ServiceProductCreate,
    ServiceProductResponse,
    StockAdjustRequest,
)
from meditor import build_mediator

router = APIRouter(tags=["Products"])


# ── Products ─────────────────────────────────────────────────────────────────


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            CreateProductCommand(
                nome=payload.nome,
                descricao=payload.descricao,
                stock_atual=payload.stock_atual,
                stock_minimo=payload.stock_minimo,
                preco_unitario=payload.preco_unitario,
                tenant_id=tenant_id,
            )
        )
    except Exception as exc:
        raise to_http_exception(exc) from exc


@router.get("/products", response_model=list[ProductResponse])
async def list_products(
    low_stock: bool = False,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    return await mediator.send(
        ListProductsQuery(tenant_id=tenant_id, low_stock=low_stock)
    )


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            UpdateProductCommand(
                product_id=product_id,
                nome=payload.nome,
                descricao=payload.descricao,
                stock_atual=payload.stock_atual,
                stock_minimo=payload.stock_minimo,
                preco_unitario=payload.preco_unitario,
                tenant_id=tenant_id,
            )
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


@router.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            DeleteProductCommand(product_id=product_id, tenant_id=tenant_id)
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.post("/products/{product_id}/stock", response_model=ProductResponse)
async def adjust_stock(
    product_id: int,
    payload: StockAdjustRequest,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            AdjustStockCommand(
                product_id=product_id,
                delta=payload.delta,
                reason=payload.reason,
                tenant_id=tenant_id,
            )
        )
    except (NotFoundError, ValidationError) as exc:
        raise to_http_exception(exc) from exc


# ── Service-Product links ────────────────────────────────────────────────────


@router.post(
    "/service-products",
    response_model=ServiceProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service_product(
    payload: ServiceProductCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    try:
        return await mediator.send(
            CreateServiceProductCommand(
                service_id=payload.service_id,
                product_id=payload.product_id,
                quantidade=payload.quantidade,
                tenant_id=tenant_id,
            )
        )
    except NotFoundError as exc:
        raise to_http_exception(exc) from exc


@router.get(
    "/service-products/{service_id}",
    response_model=list[ServiceProductResponse],
)
async def list_service_products(
    service_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(ADMIN_ROLE)),
    tenant_id: int = Header(..., alias=TENANT_HEADER_ALIAS),
):
    mediator = build_mediator(db)
    return await mediator.send(
        ListServiceProductsQuery(service_id=service_id, tenant_id=tenant_id)
    )
