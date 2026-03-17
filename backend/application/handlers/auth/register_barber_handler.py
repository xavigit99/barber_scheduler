from diator.requests import RequestHandler
from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.application.commands.register_barber_command import RegisterBarberCommand
from backend.core.barber import Barber
from backend.core.exceptions import ConflictError
from backend.core.security import hash_password
from backend.core.user import User


class RegisterBarberHandler(RequestHandler[RegisterBarberCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: RegisterBarberCommand):
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
            role="barber",
        )
        self.db.add(user)
        self.db.flush()

        barber = Barber(
            nome=command.nome,
            email=command.email,
            telefone=command.telefone,
            tenant_id=command.tenant_id,
            user_id=user.id,
        )
        self.db.add(barber)
        self.db.commit()
        self.db.refresh(user)
        return user
