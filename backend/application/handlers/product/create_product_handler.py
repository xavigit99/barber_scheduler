from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_product_command import CreateProductCommand
from backend.core.product import Product


class CreateProductHandler(RequestHandler[CreateProductCommand, object]):
    """Creates a new product in stock (F37)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateProductCommand) -> Product:
        product = Product(
            nome=command.nome,
            descricao=command.descricao,
            stock_atual=command.stock_atual,
            stock_minimo=command.stock_minimo,
            preco_unitario=command.preco_unitario,
            tenant_id=command.tenant_id,
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
