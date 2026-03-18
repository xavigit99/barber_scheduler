from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_feedback_command import CreateFeedbackCommand
from backend.core.appointment import Appointment
from backend.core.client import Client
from backend.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from backend.core.feedback import Feedback
from repositories.base_repository import BaseRepository


class CreateFeedbackHandler(RequestHandler[CreateFeedbackCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateFeedbackCommand):
        if command.rating < 1 or command.rating > 5:
            raise ValidationError("Rating must be between 1 and 5")

        tenant_id = command.tenant_id
        appointment_repo = BaseRepository(Appointment, self.db, tenant_id)
        appointment = appointment_repo.get(command.appointment_id)
        if appointment is None:
            raise NotFoundError("Appointment not found")

        client = (
            self.db.query(Client)
            .filter(Client.user_id == command.user_id, Client.deleted.is_(False))
            .first()
        )
        if client is None:
            raise NotFoundError("Client not found")

        if client.id != appointment.client_id:
            raise ForbiddenError("You can only review your own appointments")

        if appointment.end_at > datetime.now(UTC).replace(tzinfo=None):
            raise ValidationError("Cannot review a future appointment")

        existing = (
            self.db.query(Feedback)
            .filter(
                Feedback.appointment_id == command.appointment_id,
                Feedback.deleted.is_(False),
            )
            .first()
        )
        if existing is not None:
            raise ConflictError("Feedback already exists for this appointment")

        feedback = Feedback(
            appointment_id=command.appointment_id,
            client_id=client.id,
            barber_id=appointment.barber_id,
            tenant_id=appointment.tenant_id,
            rating=command.rating,
            comentario=command.comentario,
            created_at=datetime.now(),
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
