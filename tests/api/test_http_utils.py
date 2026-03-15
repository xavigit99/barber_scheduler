import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from fastapi import HTTPException

from backend.api.http_utils import (
    ensure_payload_has_changes,
    ensure_resource_deleted,
    ensure_resource_found,
)
from backend.infrastructure.schemas import ClientUpdate


class HttpUtilsTestCase(unittest.TestCase):

    def test_ensure_resource_found_returns_value(self):
        resource = object()

        result = ensure_resource_found(resource, "Resource not found")

        self.assertIs(result, resource)

    def test_ensure_resource_found_raises_not_found(self):
        with self.assertRaises(HTTPException) as context:
            ensure_resource_found(None, "Resource not found")

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Resource not found")

    def test_ensure_resource_deleted_raises_not_found(self):
        with self.assertRaises(HTTPException) as context:
            ensure_resource_deleted(False, "Resource not found")

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Resource not found")

    def test_ensure_payload_has_changes_returns_payload(self):
        payload = ClientUpdate(email="john@example.com")

        result = ensure_payload_has_changes(payload)

        self.assertIs(result, payload)

    def test_ensure_payload_has_changes_raises_bad_request(self):
        with self.assertRaises(HTTPException) as context:
            ensure_payload_has_changes(ClientUpdate())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "At least one field must be provided")


if __name__ == "__main__":
    unittest.main()
