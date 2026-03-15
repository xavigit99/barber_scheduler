from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from backend.application.queries.list_client_appointments_query import (
    ListClientAppointmentsQuery,
)
from backend.core.appointment import Appointment
from backend.core.client import Client
from backend.core.exceptions import NotFoundError
from diator.requests import RequestHandler
from repositories.base_repository import BaseRepository


class ListClientAppointmentsHandler(RequestHandler[ListClientAppointmentsQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListClientAppointmentsQuery) -> list:
        client_repository = BaseRepository(Client, self.db, query.tenant_id)
        if client_repository.get(query.client_id) is None:
            raise NotFoundError("Client not found")

        appointment_query = (
            self.db.query(Appointment)
            .filter(
                Appointment.client_id == query.client_id,
                Appointment.deleted.is_(False),
            )
        )

        if query.target_date:
            day_start = datetime.combine(query.target_date, time.min)
            day_end = day_start + timedelta(days=1)
            appointment_query = appointment_query.filter(
                Appointment.start_at >= day_start, Appointment.start_at < day_end
            )

        return appointment_query.order_by(Appointment.start_at).all()
