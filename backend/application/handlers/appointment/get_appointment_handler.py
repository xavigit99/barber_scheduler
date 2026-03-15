from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.get_appointment_query import GetAppointmentQuery
from backend.core.appointment import Appointment
from backend.core.exceptions import NotFoundError


class GetAppointmentHandler(RequestHandler[GetAppointmentQuery, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: GetAppointmentQuery):
        appointment = (
            self.db.query(Appointment)
            .filter(
                Appointment.id == query.appointment_id,
                Appointment.deleted.is_(False),
            )
            .first()
        )
        if appointment is None:
            raise NotFoundError("Appointment not found")
        return appointment
