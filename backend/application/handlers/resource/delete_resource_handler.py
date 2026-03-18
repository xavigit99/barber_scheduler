from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.delete_resource_command import DeleteResourceCommand
from backend.core.exceptions import NotFoundError
from backend.core.resource import Resource
from repositories.base_repository import BaseRepository


class DeleteResourceHandler(RequestHandler[DeleteResourceCommand, object]):
    """Soft-deletes a resource (F38)."""

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteResourceCommand) -> dict:
        repo = BaseRepository(Resource, self.db, command.tenant_id)
        deleted = repo.delete(command.resource_id)
        if not deleted:
            raise NotFoundError("Resource not found")
        return {"deleted": True}
