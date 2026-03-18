"""f25-f26-f27: reminders, presence confirmation, group appointments

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-18 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # F26 — Presence confirmation fields on appointments
    op.add_column("appointments", sa.Column("status", sa.String(), nullable=False, server_default="pending"))
    op.add_column("appointments", sa.Column("confirmation_token", sa.String(), nullable=True))
    op.add_column("appointments", sa.Column("confirmed_at", sa.DateTime(), nullable=True))
    op.create_index("ix_appointments_confirmation_token", "appointments", ["confirmation_token"], unique=True)
    op.create_index("ix_appointments_status", "appointments", ["status"])

    # F25 — Reminder tracking
    op.add_column("appointments", sa.Column("reminder_sent_at", sa.DateTime(), nullable=True))

    # F27 — Group appointments
    op.add_column("appointments", sa.Column("group_id", sa.String(), nullable=True))
    op.create_index("ix_appointments_group_id", "appointments", ["group_id"])

    # F27 — Service capacity
    op.add_column("servicos", sa.Column("max_capacity", sa.Integer(), nullable=False, server_default="1"))


def downgrade() -> None:
    op.drop_index("ix_appointments_group_id", table_name="appointments")
    op.drop_column("appointments", "group_id")
    op.drop_column("appointments", "reminder_sent_at")
    op.drop_index("ix_appointments_status", table_name="appointments")
    op.drop_index("ix_appointments_confirmation_token", table_name="appointments")
    op.drop_column("appointments", "confirmed_at")
    op.drop_column("appointments", "confirmation_token")
    op.drop_column("appointments", "status")
    op.drop_column("servicos", "max_capacity")
