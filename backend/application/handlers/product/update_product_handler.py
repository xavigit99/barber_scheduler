from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.update_product_command import UpdateProductCommand
from backend.core.exceptions import NotFoundError
from backend.core.product import Product
from repositories.base_repository import BaseRepository


class UpdateProductHandler(RequestHandler[UpdateProductCommand, object]):
    """Updates an existing product (F37)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: UpdateProductCommand) -> Product:
        repo = BaseRepository(Product, self.db, command.tenant_id)
        product = repo.get(command.product_id)
        if product is None:
            raise NotFoundError("Product not found")

        updates = {
            k: v
            for k, v in {
                "nome": command.nome,
                "descricao": command.descricao,
                "stock_atual": command.stock_atual,
                "stock_minimo": command.stock_minimo,
                "preco_unitario": command.preco_unitario,
            }.items()
            if v is not None
        }

        for key, value in updates.items():
            setattr(product, key, value)

        self.db.commit()
        self.db.refresh(product)
        return product
