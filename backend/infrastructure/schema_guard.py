from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine


def validate_database_schema(engine: Engine) -> None:
    """Fail fast when the connected database is behind Alembic migrations."""
    cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(cfg)
    expected_heads = set(script.get_heads())

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_revision = context.get_current_revision()

    if current_revision is None:
        raise RuntimeError(
            "Database schema is not versioned. Run './venv/bin/alembic upgrade head' "
            "before starting the API."
        )

    if current_revision not in expected_heads:
        expected = ", ".join(sorted(expected_heads))
        raise RuntimeError(
            "Database schema is outdated. "
            f"Current revision: {current_revision}. Expected head: {expected}. "
            "Run './venv/bin/alembic upgrade head' before starting the API."
        )
