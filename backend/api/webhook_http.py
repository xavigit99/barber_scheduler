from backend.application.commands.create_webhook_command import CreateWebhookCommand
from backend.application.commands.delete_webhook_command import DeleteWebhookCommand
from backend.application.queries.list_webhooks_query import ListWebhooksQuery
from backend.infrastructure.schemas import WebhookCreate


def build_create_webhook_command(
    payload: WebhookCreate,
    tenant_id: int,
) -> CreateWebhookCommand:
    return CreateWebhookCommand(
        tenant_id=tenant_id,
        url=payload.url,
        secret=payload.secret,
        events=payload.events,
    )


def build_delete_webhook_command(
    webhook_id: int,
    tenant_id: int,
) -> DeleteWebhookCommand:
    return DeleteWebhookCommand(webhook_id=webhook_id, tenant_id=tenant_id)


def build_list_webhooks_query(
    tenant_id: int,
) -> ListWebhooksQuery:
    return ListWebhooksQuery(tenant_id=tenant_id)
