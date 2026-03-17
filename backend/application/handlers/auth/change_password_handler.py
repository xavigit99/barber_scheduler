from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.change_password_command import ChangePasswordCommand
from backend.core.exceptions import AuthenticationError
from backend.core.security import hash_password, verify_password
from backend.core.user import User


class ChangePasswordHandler(RequestHandler[ChangePasswordCommand, None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: ChangePasswordCommand) -> None:
        user = self.db.query(User).filter(User.id == command.user_id).first()
        if user is None:
            raise AuthenticationError("User not found")

        if not verify_password(command.current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")

        user.password_hash = hash_password(command.new_password)
        self.db.commit()
