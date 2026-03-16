from diator.requests import RequestHandler
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.application.commands.register_client_command import RegisterClientCommand
from backend.core.client import Client
from backend.core.exceptions import ConflictError
from backend.core.security import hash_password
from backend.core.user import User


class RegisterClientHandler(RequestHandler[RegisterClientCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: RegisterClientCommand):
        existing = (
            self.db.query(User)
            .filter(or_(User.username == command.username, User.email == command.email))
            .first()
        )
        if existing is not None:
            raise ConflictError("User with this username or email already exists")

        user = User(
            username=command.username,
            email=command.email,
            password_hash=hash_password(command.password),
            role="client",
        )
        self.db.add(user)
        self.db.flush()  # get user.id without committing

        client = Client(
            nome=command.nome,
            email=command.email,
            tenant_id=command.tenant_id,
            user_id=user.id,
        )
        self.db.add(client)
        self.db.commit()
        self.db.refresh(user)
        return user
