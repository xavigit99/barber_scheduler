from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.delete_product_command import DeleteProductCommand
from backend.core.exceptions import NotFoundError
from backend.core.product import Product
from repositories.base_repository import BaseRepository


class DeleteProductHandler(RequestHandler[DeleteProductCommand, object]):
    """Soft-deletes a product (F37)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteProductCommand) -> dict:
        repo = BaseRepository(Product, self.db, command.tenant_id)
        deleted = repo.delete(command.product_id)
        if not deleted:
            raise NotFoundError("Product not found")
        return {"deleted": True}
