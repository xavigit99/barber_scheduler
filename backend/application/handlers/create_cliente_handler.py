# Em backend/application/handlers/seu_arquivo.py

from backend.core.client import Cliente
from repositories.base_repository import BaseRepository
from backend.application.commands.create_cliente_command import CreateClienteCommand
from diator.requests import RequestHandler
from sqlalchemy.orm import Session # Importe a Session

class CreateClienteHandler(RequestHandler[CreateClienteCommand, dict]):
   
    request_type = CreateClienteCommand 

    def __init__(self, db: Session): # Tipar como Session ajuda o 'di'
        self.repo = BaseRepository(Cliente, db)

    async def handle(self, command: CreateClienteCommand):

        return self.repo.create({
            "nome": command.nome,
            "email": command.email,
            "telefone": command.telefone
        })