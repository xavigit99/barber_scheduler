from sqlalchemy.orm import Session

from backend.application.queries.get_user_query import GetUserQuery
from backend.core.user import User
from diator.requests import RequestHandler


class GetUserHandler(RequestHandler[GetUserQuery, object | None]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetUserQuery):
        return self.db.query(User).filter(User.id == query.user_id).first()
