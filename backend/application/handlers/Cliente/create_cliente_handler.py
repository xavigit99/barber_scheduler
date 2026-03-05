from backend.core.client import Cliente
from repositories.base_repository import BaseRepository
from backend.application.commands.create_cliente_command import CreateClienteCommand
from diator.requests import RequestHandler
from sqlalchemy.orm import Session 

class CreateClienteHandler(RequestHandler[CreateClienteCommand, dict]):
    
    def __init__(self, db: Session):
        self.repo = BaseRepository(Cliente, db)

    async def handle(self, command: CreateClienteCommand):

        return self.repo.create({
            "nome": command.nome,
            "email": command.email,
            "telefone": command.telefone
        })