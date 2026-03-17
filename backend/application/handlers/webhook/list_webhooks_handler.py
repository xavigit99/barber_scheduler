from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.queries.list_webhooks_query import ListWebhooksQuery
from backend.core.webhook import Webhook


class ListWebhooksHandler(RequestHandler[ListWebhooksQuery, list]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, query: ListWebhooksQuery) -> list:
        return (
            self.db.query(Webhook)
            .filter(
                Webhook.tenant_id == query.tenant_id,
                Webhook.deleted.is_(False),
            )
            .all()
        )
