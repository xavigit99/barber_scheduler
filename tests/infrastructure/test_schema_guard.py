import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from backend.infrastructure.schema_guard import validate_database_schema


class SchemaGuardTestCase(unittest.TestCase):

    @patch("backend.infrastructure.schema_guard.MigrationContext")
    @patch("backend.infrastructure.schema_guard.ScriptDirectory")
    @patch("backend.infrastructure.schema_guard.Config")
    def test_validate_database_schema_accepts_current_head(
        self,
        _config_cls,
        script_directory_cls,
        migration_context_cls,
    ):
        engine = MagicMock()
        connection = engine.connect.return_value.__enter__.return_value
        script_directory_cls.from_config.return_value.get_heads.return_value = ["head-123"]
        migration_context_cls.configure.return_value.get_current_revision.return_value = "head-123"

        validate_database_schema(engine)

        migration_context_cls.configure.assert_called_once_with(connection)

    @patch("backend.infrastructure.schema_guard.MigrationContext")
    @patch("backend.infrastructure.schema_guard.ScriptDirectory")
    @patch("backend.infrastructure.schema_guard.Config")
    def test_validate_database_schema_raises_when_unversioned(
        self,
        _config_cls,
        script_directory_cls,
        migration_context_cls,
    ):
        engine = MagicMock()
        script_directory_cls.from_config.return_value.get_heads.return_value = ["head-123"]
        migration_context_cls.configure.return_value.get_current_revision.return_value = None

        with self.assertRaises(RuntimeError) as context:
            validate_database_schema(engine)

        self.assertIn("Run './venv/bin/alembic upgrade head'", str(context.exception))

    @patch("backend.infrastructure.schema_guard.MigrationContext")
    @patch("backend.infrastructure.schema_guard.ScriptDirectory")
    @patch("backend.infrastructure.schema_guard.Config")
    def test_validate_database_schema_raises_when_outdated(
        self,
        _config_cls,
        script_directory_cls,
        migration_context_cls,
    ):
        engine = MagicMock()
        script_directory_cls.from_config.return_value.get_heads.return_value = ["head-123"]
        migration_context_cls.configure.return_value.get_current_revision.return_value = "old-456"

        with self.assertRaises(RuntimeError) as context:
            validate_database_schema(engine)

        message = str(context.exception)
        self.assertIn("Current revision: old-456", message)
        self.assertIn("Expected head: head-123", message)


if __name__ == "__main__":
    unittest.main()
