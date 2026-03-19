"""add payment method to appointments

Revision ID: f2b4d6e8a1c3
Revises: e5f6a7b8c9d0
Create Date: 2026-03-19 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

revision = "f2b4d6e8a1c3"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "appointments",
        sa.Column("payment_method", sa.String(), nullable=True),
    )
    op.create_index(
        "ix_appointments_payment_method",
        "appointments",
        ["payment_method"],
    )


def downgrade() -> None:
    op.drop_index("ix_appointments_payment_method", table_name="appointments")
    op.drop_column("appointments", "payment_method")
