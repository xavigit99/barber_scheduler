from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_service_products_query import (
    ListServiceProductsQuery,
)
from backend.core.product import ServiceProduct


class ListServiceProductsHandler(RequestHandler[ListServiceProductsQuery, list]):
    """Lists products linked to a service (F37)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListServiceProductsQuery) -> list[ServiceProduct]:
        q = self.db.query(ServiceProduct).filter(
            ServiceProduct.service_id == query.service_id,
            ServiceProduct.deleted.is_(False),
        )
        if query.tenant_id is not None:
            q = q.filter(ServiceProduct.tenant_id == query.tenant_id)
        return q.all()
