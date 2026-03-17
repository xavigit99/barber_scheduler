import os
import unittest
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from backend.core.notifications import (
    AppointmentNotification,
    LogNotificationService,
    SmtpNotificationService,
    build_notification_service,
)

NOTIF = AppointmentNotification(
    client_name="João Silva",
    client_email="joao@example.com",
    barber_name="Miguel",
    service_name="Corte",
    start_at=datetime(2026, 4, 1, 10, 0, tzinfo=UTC),
    appointment_id=42,
)


class TestBuildNotificationService(unittest.TestCase):

    def test_returns_log_service_when_no_smtp_host(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SMTP_HOST", None)
            svc = build_notification_service()
        self.assertIsInstance(svc, LogNotificationService)

    def test_returns_smtp_service_when_smtp_host_set(self):
        env = {"SMTP_HOST": "smtp.example.com", "SMTP_USERNAME": "u", "SMTP_PASSWORD": "p"}
        with patch.dict(os.environ, env):
            svc = build_notification_service()
        self.assertIsInstance(svc, SmtpNotificationService)

    def test_smtp_service_reads_port(self):
        env = {"SMTP_HOST": "smtp.example.com", "SMTP_PORT": "465", "SMTP_USERNAME": "u", "SMTP_PASSWORD": "p"}
        with patch.dict(os.environ, env):
            svc = build_notification_service()
        assert isinstance(svc, SmtpNotificationService)
        self.assertEqual(svc.port, 465)

    def test_smtp_service_use_tls_false(self):
        env = {"SMTP_HOST": "smtp.example.com", "SMTP_USE_TLS": "false", "SMTP_USERNAME": "u", "SMTP_PASSWORD": "p"}
        with patch.dict(os.environ, env):
            svc = build_notification_service()
        assert isinstance(svc, SmtpNotificationService)
        self.assertFalse(svc.use_tls)


class TestSmtpNotificationService(unittest.TestCase):

    def _make_svc(self) -> SmtpNotificationService:
        return SmtpNotificationService(
            host="smtp.test.com",
            port=587,
            username="user",
            password="pass",
            sender="no-reply@test.com",
            use_tls=True,
        )

    def test_send_confirmation_sends_email(self):
        svc = self._make_svc()
        with patch("backend.core.notifications.smtplib.SMTP") as MockSmtp:
            instance = MockSmtp.return_value.__enter__.return_value = MagicMock()
            svc.send_confirmation(NOTIF)
            instance.sendmail.assert_called_once()
            args = instance.sendmail.call_args[0]
            self.assertEqual(args[1], ["joao@example.com"])
            self.assertIn("confirmado", args[2])

    def test_send_cancellation_sends_email(self):
        svc = self._make_svc()
        with patch("backend.core.notifications.smtplib.SMTP") as MockSmtp:
            instance = MockSmtp.return_value.__enter__.return_value = MagicMock()
            svc.send_cancellation(NOTIF)
            instance.sendmail.assert_called_once()
            args = instance.sendmail.call_args[0]
            self.assertIn("cancelado", args[2])

    def test_send_reschedule_sends_email(self):
        svc = self._make_svc()
        with patch("backend.core.notifications.smtplib.SMTP") as MockSmtp:
            instance = MockSmtp.return_value.__enter__.return_value = MagicMock()
            svc.send_reschedule(NOTIF)
            instance.sendmail.assert_called_once()
            args = instance.sendmail.call_args[0]
            self.assertIn("remarcado", args[2])

    def test_starttls_called_when_use_tls_true(self):
        svc = self._make_svc()
        with patch("backend.core.notifications.smtplib.SMTP") as MockSmtp:
            instance = MockSmtp.return_value.__enter__.return_value = MagicMock()
            svc.send_confirmation(NOTIF)
            instance.starttls.assert_called_once()

    def test_starttls_not_called_when_use_tls_false(self):
        svc = self._make_svc()
        svc.use_tls = False
        with patch("backend.core.notifications.smtplib.SMTP") as MockSmtp:
            instance = MockSmtp.return_value.__enter__.return_value = MagicMock()
            svc.send_confirmation(NOTIF)
            instance.starttls.assert_not_called()

    def test_smtp_failure_propagates(self):
        """Handlers swallow exceptions — the service itself should let them bubble."""
        svc = self._make_svc()
        with patch("backend.core.notifications.smtplib.SMTP", side_effect=ConnectionRefusedError):
            with self.assertRaises(ConnectionRefusedError):
                svc.send_confirmation(NOTIF)


if __name__ == "__main__":
    unittest.main()
