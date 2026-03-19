import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.core.client import Client
from backend.core.client_profiles import (
    get_client_profile_for_user,
    get_or_create_client_profile_for_user,
)
from backend.core.user import User


class ClientProfilesTestCase(unittest.TestCase):

    def test_get_client_profile_filters_by_tenant_when_provided(self):
        db = MagicMock()
        query = MagicMock()
        filtered = MagicMock()
        ordered = MagicMock()
        expected = object()

        db.query.return_value = query
        query.filter.return_value = filtered
        filtered.filter.return_value = filtered
        filtered.order_by.return_value = ordered
        ordered.first.return_value = expected

        result = get_client_profile_for_user(db, user_id=7, tenant_id=9)

        self.assertIs(result, expected)
        db.query.assert_called_once_with(Client)
        self.assertEqual(filtered.filter.call_count, 1)
        filtered.order_by.assert_called_once()

    def test_get_or_create_returns_existing_profile(self):
        db = MagicMock()
        query = MagicMock()
        filtered = MagicMock()
        ordered = MagicMock()
        existing = Client(
            id=5,
            nome="Joao",
            email="joao@example.com",
            tenant_id=3,
            user_id=7,
        )

        db.query.return_value = query
        query.filter.return_value = filtered
        filtered.filter.return_value = filtered
        filtered.order_by.return_value = ordered
        ordered.first.return_value = existing

        result = get_or_create_client_profile_for_user(db, user_id=7, tenant_id=3)

        self.assertIs(result, existing)
        db.add.assert_not_called()
        db.commit.assert_not_called()

    def test_get_or_create_builds_profile_from_user_when_missing(self):
        db = MagicMock()
        client_query = MagicMock()
        client_filtered = MagicMock()
        client_ordered = MagicMock()
        user_query = MagicMock()
        user_filtered = MagicMock()

        user = User(
            id=7,
            username="joaosilva",
            email="joao@example.com",
            password_hash="hashed",
            role="client",
        )

        db.query.side_effect = [client_query, user_query, client_query]
        client_query.filter.return_value = client_filtered
        client_filtered.filter.return_value = client_filtered
        client_filtered.order_by.return_value = client_ordered
        client_ordered.first.side_effect = [None, None]
        user_query.filter.return_value = user_filtered
        user_filtered.first.return_value = user

        added = []
        db.add.side_effect = lambda obj: added.append(obj)
        db.refresh.side_effect = lambda obj: setattr(obj, "id", 11)

        result = get_or_create_client_profile_for_user(db, user_id=7, tenant_id=3)

        self.assertIsInstance(result, Client)
        self.assertEqual(result.user_id, 7)
        self.assertEqual(result.tenant_id, 3)
        self.assertEqual(result.nome, "joaosilva")
        self.assertEqual(result.email, "joao@example.com")
        self.assertEqual(len(added), 1)
        db.commit.assert_called_once_with()
        db.refresh.assert_called_once_with(result)


if __name__ == "__main__":
    unittest.main()
