from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_my_feedback_query import ListMyFeedbackQuery
from backend.core.client import Client
from backend.core.feedback import Feedback


class ListMyFeedbackHandler(RequestHandler[ListMyFeedbackQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListMyFeedbackQuery):
        client = (
            self.db.query(Client)
            .filter(Client.user_id == query.user_id, Client.deleted.is_(False))
            .first()
        )
        if client is None:
            return []

        q = self.db.query(Feedback).filter(
            Feedback.client_id == client.id,
            Feedback.deleted.is_(False),
        )
        if query.tenant_id is not None:
            q = q.filter(Feedback.tenant_id == query.tenant_id)
        return q.all()
