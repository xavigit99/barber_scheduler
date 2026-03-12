from sqlalchemy.orm import Session

from backend.application.commands.delete_client_command import DeleteClientCommand
from backend.core.client import Cliente
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class DeleteClientHandler(RequestHandler[DeleteClientCommand, bool]):

    def __init__(self, db: Session):
        self.repository = BaseRepository(Cliente, db)

    async def handle(self, command: DeleteClientCommand) -> bool:
        return self.repository.delete(command.client_id)
