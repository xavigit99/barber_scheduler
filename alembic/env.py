"""Alembic environment configuration.

Loads DATABASE_URL from .env and registers all SQLAlchemy models
so that autogenerate can detect schema changes.
"""

import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Load environment variables from .env (project root)
# ---------------------------------------------------------------------------
load_dotenv()

DATABASE_URL: str = os.environ["DATABASE_URL"]

# ---------------------------------------------------------------------------
# Alembic Config object — provides access to alembic.ini values
# ---------------------------------------------------------------------------
config = context.config

# Override sqlalchemy.url from environment so we never store credentials
# in alembic.ini.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Setup Python logging from the .ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import models so they register on Base.metadata
# ---------------------------------------------------------------------------
import backend.core  # noqa: E402, F401 — registers all models on Base.metadata
from backend.infrastructure.database import Base  # noqa: E402

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Only manage tables that are defined in our SQLAlchemy models.
# This prevents Alembic from trying to drop legacy tables (e.g. Prisma)
# that exist in the database but are not part of our model layer.
# ---------------------------------------------------------------------------
MANAGED_TABLES = set(target_metadata.tables.keys())


def include_object(
    object: object,  # noqa: A002
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: object | None,
) -> bool:
    """Filter callback for autogenerate.

    Only include tables (and their columns/indexes/constraints) that are
    defined in our SQLAlchemy models. Reflected-only objects from the DB
    are excluded so we never generate DROP statements for unmanaged tables.
    """
    if type_ == "table" and reflected and name not in MANAGED_TABLES:
        return False
    return True


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine,
    so a DBAPI is not required.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
