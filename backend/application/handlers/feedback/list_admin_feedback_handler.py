from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_admin_feedback_query import ListAdminFeedbackQuery
from backend.core.feedback import Feedback
from repositories.base_repository import BaseRepository


class ListAdminFeedbackHandler(RequestHandler[ListAdminFeedbackQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListAdminFeedbackQuery):
        repo = BaseRepository(Feedback, self.db, query.tenant_id)
        return repo.list()
