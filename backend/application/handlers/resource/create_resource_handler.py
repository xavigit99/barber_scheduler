from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_resource_command import CreateResourceCommand
from backend.core.resource import Resource


class CreateResourceHandler(RequestHandler[CreateResourceCommand, object]):
    """Creates a new room/resource (F38)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateResourceCommand) -> Resource:
        resource = Resource(
            nome=command.nome,
            tipo=command.tipo,
            tenant_id=command.tenant_id,
        )
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource
