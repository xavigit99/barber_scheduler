"""Tests for Alembic migration configuration and schema sync."""

import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://sa:teste@localhost:5432/appdb")


class MigrationRevisionChainTestCase(unittest.TestCase):
    """Verify migration file consistency without touching the database."""

    def _load_script_directory(self):
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        cfg = Config("alembic.ini")
        return ScriptDirectory.from_config(cfg)

    def test_all_revisions_have_unique_ids(self):
        scripts = self._load_script_directory()
        revision_ids = [s.revision for s in scripts.walk_revisions()]
        self.assertEqual(len(revision_ids), len(set(revision_ids)))

    def test_revision_chain_has_no_gaps(self):
        """walk_revisions raises if the chain is broken."""
        scripts = self._load_script_directory()
        revisions = list(scripts.walk_revisions())
        self.assertGreater(len(revisions), 0)

    def test_head_revision_exists(self):
        scripts = self._load_script_directory()
        heads = scripts.get_heads()
        self.assertEqual(len(heads), 1, "Expected exactly one head revision")

    def test_initial_migration_has_no_parent(self):
        scripts = self._load_script_directory()
        bases = list(scripts.walk_revisions("base", "head"))
        root = bases[-1]
        self.assertIsNone(root.down_revision)


@unittest.skipUnless(
    os.environ.get("DATABASE_URL", "").startswith("postgresql"),
    "Skipped: requires a live PostgreSQL database",
)
class MigrationSchemaSyncTestCase(unittest.TestCase):
    """Verify models and database schema are in sync (requires live DB)."""

    def test_no_pending_migrations(self):
        """alembic check should report no new upgrade operations."""
        from io import StringIO
        from alembic.config import Config
        from alembic import command

        cfg = Config("alembic.ini")
        # Redirect output — command.check() prints to stdout and raises
        # SystemExit(1) if there are pending changes, so we catch that.
        try:
            command.check(cfg)
        except SystemExit as exc:
            self.fail(
                f"alembic check failed — models and DB schema are out of sync "
                f"(exit code {exc.code}). Run 'make migrate-create msg=...' to generate a migration."
            )


if __name__ == "__main__":
    unittest.main()
