import logging

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.adjust_stock_command import AdjustStockCommand
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.product import Product
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AdjustStockHandler(RequestHandler[AdjustStockCommand, object]):
    """Adds or removes stock from a product (F37)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: AdjustStockCommand) -> Product:
        repo = BaseRepository(Product, self.db, command.tenant_id)
        product = repo.get(command.product_id)
        if product is None:
            raise NotFoundError("Product not found")

        new_stock = product.stock_atual + command.delta
        if new_stock < 0:
            raise ValidationError("Stock cannot go below zero")

        product.stock_atual = new_stock
        self.db.commit()
        self.db.refresh(product)

        logger.info(
            "Stock adjusted: product=%d delta=%d reason=%s new_stock=%d",
            command.product_id,
            command.delta,
            command.reason,
            new_stock,
        )
        return product
