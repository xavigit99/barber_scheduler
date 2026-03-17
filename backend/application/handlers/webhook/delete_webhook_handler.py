from datetime import UTC, datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.delete_webhook_command import DeleteWebhookCommand
from backend.core.webhook import Webhook


class DeleteWebhookHandler(RequestHandler[DeleteWebhookCommand, bool]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: DeleteWebhookCommand) -> bool:
        webhook = (
            self.db.query(Webhook)
            .filter(
                Webhook.id == command.webhook_id,
                Webhook.tenant_id == command.tenant_id,
                Webhook.deleted.is_(False),
            )
            .first()
        )
        if webhook is None:
            return False

        webhook.deleted = True
        webhook.deleted_at = datetime.now(UTC)
        self.db.commit()
        return True
