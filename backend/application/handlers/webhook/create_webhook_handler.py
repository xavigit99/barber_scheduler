from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_webhook_command import CreateWebhookCommand
from backend.core.exceptions import ValidationError
from backend.core.webhook import Webhook

ALLOWED_EVENTS = {"appointment.created", "appointment.cancelled", "appointment.rescheduled"}


class CreateWebhookHandler(RequestHandler[CreateWebhookCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateWebhookCommand):
        invalid = set(command.events) - ALLOWED_EVENTS
        if invalid:
            raise ValidationError(f"Invalid webhook events: {', '.join(sorted(invalid))}")

        webhook = Webhook(
            tenant_id=command.tenant_id,
            url=command.url,
            secret=command.secret,
            events=command.events,
            created_at=datetime.now(UTC),
        )
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        return webhook
