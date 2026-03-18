from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_products_query import ListProductsQuery
from backend.core.product import Product
from repositories.base_repository import BaseRepository


class ListProductsHandler(RequestHandler[ListProductsQuery, list]):
    """Lists products for a tenant, optionally filtered by low stock (F37)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListProductsQuery) -> list[Product]:
        repo = BaseRepository(Product, self.db, query.tenant_id)
        products = repo.list()

        if query.low_stock:
            products = [p for p in products if p.stock_atual <= p.stock_minimo]

        return products
