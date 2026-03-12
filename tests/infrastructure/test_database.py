import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.infrastructure.database import get_database_url


class DatabaseConfigTestCase(unittest.TestCase):

    def test_get_database_url_prefers_uppercase_variable(self):
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "sqlite:///preferred.db", "databse_url": "sqlite:///legacy.db"},
            clear=False,
        ):
            self.assertEqual(get_database_url(), "sqlite:///preferred.db")

    def test_get_database_url_falls_back_to_legacy_variable(self):
        with patch.dict(os.environ, {"databse_url": "sqlite:///legacy.db"}, clear=True):
            self.assertEqual(get_database_url(), "sqlite:///legacy.db")


if __name__ == "__main__":
    unittest.main()
