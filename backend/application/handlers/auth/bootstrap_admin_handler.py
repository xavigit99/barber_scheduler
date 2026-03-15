from sqlalchemy.orm import Session

from backend.application.commands.bootstrap_admin_command import BootstrapAdminCommand
from backend.application.commands.create_user_command import CreateUserCommand
from backend.core.exceptions import ConflictError
from backend.core.roles import ADMIN_ROLE
from backend.core.user import User
from diator.requests import RequestHandler

from backend.application.handlers.auth.create_user_handler import CreateUserHandler


class BootstrapAdminHandler(RequestHandler[BootstrapAdminCommand, object]):

    def __init__(self, db: Session):
        self.db = db
        self.create_user_handler = CreateUserHandler(db)

    async def handle(self, command: BootstrapAdminCommand):
        has_users = self.db.query(User).first() is not None
        if has_users:
            raise ConflictError("Admin bootstrap has already been completed")

        return await self.create_user_handler.handle(
            CreateUserCommand(
                username=command.username,
                email=command.email,
                password=command.password,
                role=ADMIN_ROLE,
            )
        )
