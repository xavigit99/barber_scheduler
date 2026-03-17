from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_barber_feedback_query import ListBarberFeedbackQuery
from backend.core.barber import Barber
from backend.core.feedback import Feedback


class ListBarberFeedbackHandler(RequestHandler[ListBarberFeedbackQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListBarberFeedbackQuery):
        barber = (
            self.db.query(Barber)
            .filter(Barber.id == query.barber_id, Barber.deleted.is_(False))
            .first()
        )
        if barber is None:
            from backend.core.exceptions import NotFoundError
            raise NotFoundError("Barber not found")

        q = self.db.query(Feedback).filter(
            Feedback.barber_id == query.barber_id,
            Feedback.deleted.is_(False),
        )
        if query.tenant_id is not None:
            q = q.filter(Feedback.tenant_id == query.tenant_id)
        return q.all()
