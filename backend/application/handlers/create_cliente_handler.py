from backend.core.client import Cliente
from repositories.base_repository import BaseRepository
from backend.application.commands.create_cliente_command import CreateClienteCommand


class CreateClienteHandler:

    def __init__(self, db):
        self.repo = BaseRepository(Cliente, db)

    def handle(self, command: CreateClienteCommand):
        return self.repo.create({
            "nome": command.nome,
            "email": command.email,
            "telefone": command.telefone
        })