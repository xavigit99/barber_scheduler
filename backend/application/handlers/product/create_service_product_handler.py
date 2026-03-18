from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_service_product_command import (
    CreateServiceProductCommand,
)
from backend.core.exceptions import NotFoundError
from backend.core.product import Product, ServiceProduct
from backend.core.service import Service
from repositories.base_repository import BaseRepository


class CreateServiceProductHandler(RequestHandler[CreateServiceProductCommand, object]):
    """Links a product to a service with quantity consumed per execution (F37)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateServiceProductCommand) -> ServiceProduct:
        service_repo = BaseRepository(Service, self.db, command.tenant_id)
        if service_repo.get(command.service_id) is None:
            raise NotFoundError("Service not found")

        product_repo = BaseRepository(Product, self.db, command.tenant_id)
        if product_repo.get(command.product_id) is None:
            raise NotFoundError("Product not found")

        link = ServiceProduct(
            service_id=command.service_id,
            product_id=command.product_id,
            quantidade=command.quantidade,
            tenant_id=command.tenant_id,
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link
