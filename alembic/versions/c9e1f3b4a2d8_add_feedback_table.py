"""add feedback table

Revision ID: c9e1f3b4a2d8
Revises: a8f4c2e9b3d7
Create Date: 2026-03-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9e1f3b4a2d8"
down_revision: Union[str, Sequence[str], None] = "a8f4c2e9b3d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — idempotent via IF NOT EXISTS guards."""
    conn = op.get_bind()

    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL NOT NULL,
            appointment_id INTEGER NOT NULL REFERENCES appointments(id),
            client_id INTEGER NOT NULL REFERENCES clientes(id),
            barber_id INTEGER NOT NULL REFERENCES barbeiros(id),
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            rating INTEGER NOT NULL,
            comentario TEXT,
            created_at TIMESTAMP NOT NULL,
            deleted BOOLEAN NOT NULL DEFAULT FALSE,
            deleted_at TIMESTAMP,
            CONSTRAINT pk_feedback PRIMARY KEY (id),
            CONSTRAINT uq_feedback_appointment UNIQUE (appointment_id)
        )
    """))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_feedback_id ON feedback (id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_feedback_appointment_id ON feedback (appointment_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_feedback_client_id ON feedback (client_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_feedback_barber_id ON feedback (barber_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_feedback_tenant_id ON feedback (tenant_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_feedback_deleted ON feedback (deleted)"
    ))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS feedback"))
