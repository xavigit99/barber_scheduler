"""add webhooks table

Revision ID: f1a3c5e7b9d2
Revises: e5a2c8f1b9d3
Create Date: 2026-03-17 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a3c5e7b9d2"
down_revision: str | Sequence[str] | None = "e5a2c8f1b9d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema — idempotent via IF NOT EXISTS guards."""
    conn = op.get_bind()

    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS webhooks (
            id SERIAL NOT NULL,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            url TEXT NOT NULL,
            secret TEXT NOT NULL,
            events JSON NOT NULL DEFAULT '[]',
            deleted BOOLEAN NOT NULL DEFAULT FALSE,
            deleted_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL,
            CONSTRAINT pk_webhooks PRIMARY KEY (id)
        )
    """))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_webhooks_tenant_id ON webhooks (tenant_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_webhooks_deleted ON webhooks (deleted)"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS webhooks"))
