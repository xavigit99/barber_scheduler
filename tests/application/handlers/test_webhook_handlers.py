import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.application.commands.create_webhook_command import CreateWebhookCommand
from backend.application.commands.delete_webhook_command import DeleteWebhookCommand
from backend.application.handlers.webhook.create_webhook_handler import CreateWebhookHandler
from backend.application.handlers.webhook.delete_webhook_handler import DeleteWebhookHandler
from backend.application.handlers.webhook.list_webhooks_handler import ListWebhooksHandler
from backend.application.queries.list_webhooks_query import ListWebhooksQuery
from backend.core.exceptions import ValidationError


class CreateWebhookHandlerTest(unittest.IsolatedAsyncioTestCase):

    async def test_create_webhook_success(self):
        db = MagicMock()
        handler = CreateWebhookHandler(db)
        cmd = CreateWebhookCommand(
            tenant_id=1,
            url="https://example.com/hook",
            secret="s3cret",
            events=["appointment.created"],
        )
        await handler.handle(cmd)

        db.add.assert_called_once()
        db.commit.assert_called_once()
        added = db.add.call_args[0][0]
        assert added.url == "https://example.com/hook"
        assert added.secret == "s3cret"
        assert added.events == ["appointment.created"]
        assert added.tenant_id == 1

    async def test_create_webhook_invalid_event_raises(self):
        db = MagicMock()
        handler = CreateWebhookHandler(db)
        cmd = CreateWebhookCommand(
            tenant_id=1,
            url="https://example.com/hook",
            secret="s3cret",
            events=["appointment.created", "invalid.event"],
        )
        with self.assertRaises(ValidationError):
            await handler.handle(cmd)

    async def test_create_webhook_all_valid_events(self):
        db = MagicMock()
        handler = CreateWebhookHandler(db)
        cmd = CreateWebhookCommand(
            tenant_id=1,
            url="https://example.com/hook",
            secret="s3cret",
            events=["appointment.created", "appointment.cancelled", "appointment.rescheduled"],
        )
        await handler.handle(cmd)
        db.add.assert_called_once()


class DeleteWebhookHandlerTest(unittest.IsolatedAsyncioTestCase):

    async def test_delete_webhook_soft_deletes(self):
        webhook = SimpleNamespace(id=1, tenant_id=1, deleted=False, deleted_at=None)
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value = q
        q.first.return_value = webhook
        db.query.return_value = q

        handler = DeleteWebhookHandler(db)
        result = await handler.handle(DeleteWebhookCommand(webhook_id=1, tenant_id=1))

        assert result is True
        assert webhook.deleted is True
        assert webhook.deleted_at is not None
        db.commit.assert_called_once()

    async def test_delete_webhook_not_found_returns_false(self):
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value = q
        q.first.return_value = None
        db.query.return_value = q

        handler = DeleteWebhookHandler(db)
        result = await handler.handle(DeleteWebhookCommand(webhook_id=999, tenant_id=1))

        assert result is False
        db.commit.assert_not_called()


class ListWebhooksHandlerTest(unittest.IsolatedAsyncioTestCase):

    async def test_list_webhooks_returns_non_deleted(self):
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = [
            SimpleNamespace(id=1, url="https://a.com"),
            SimpleNamespace(id=2, url="https://b.com"),
        ]
        db.query.return_value = q

        handler = ListWebhooksHandler(db)
        result = await handler.handle(ListWebhooksQuery(tenant_id=1))

        assert len(result) == 2

    async def test_list_webhooks_empty(self):
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value = q
        q.all.return_value = []
        db.query.return_value = q

        handler = ListWebhooksHandler(db)
        result = await handler.handle(ListWebhooksQuery(tenant_id=1))

        assert result == []
