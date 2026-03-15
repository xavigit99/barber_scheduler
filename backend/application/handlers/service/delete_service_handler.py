from sqlalchemy.orm import Session

from backend.application.commands.delete_service_command import DeleteServiceCommand
from backend.core.service import Service
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class DeleteServiceHandler(RequestHandler[DeleteServiceCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteServiceCommand) -> bool:
        repository = BaseRepository(Service, self.db, tenant_id=command.tenant_id)
        return repository.delete(command.service_id)
