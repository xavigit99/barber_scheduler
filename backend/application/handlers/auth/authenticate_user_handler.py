from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.authenticate_user_command import AuthenticateUserCommand
from backend.core.exceptions import AuthenticationError
from backend.core.security import create_access_token, verify_password
from backend.core.user import User


class AuthenticateUserHandler(RequestHandler[AuthenticateUserCommand, dict]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: AuthenticateUserCommand):
        user = self.db.query(User).filter(User.username == command.username).first()
        if user is None or not verify_password(command.password, user.password_hash):
            raise AuthenticationError("Invalid credentials")

        return {
            "access_token": create_access_token(
                user_id=user.id,
                role=user.role,
                username=user.username,
            ),
            "token_type": "bearer",
            "user": user,
        }
