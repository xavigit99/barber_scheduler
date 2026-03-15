from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.application.commands.create_user_command import CreateUserCommand
from backend.core.exceptions import ConflictError
from backend.core.roles import ALLOWED_ROLES
from backend.core.security import hash_password
from backend.core.user import User
from diator.requests import RequestHandler


class CreateUserHandler(RequestHandler[CreateUserCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateUserCommand):
        if command.role not in ALLOWED_ROLES:
            raise ConflictError("Invalid role")

        existing_user = (
            self.db.query(User)
            .filter(
                or_(
                    User.username == command.username,
                    User.email == command.email,
                )
            )
            .first()
        )
        if existing_user is not None:
            raise ConflictError("User with this username or email already exists")

        user = User(
            username=command.username,
            email=command.email,
            password_hash=hash_password(command.password),
            role=command.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
