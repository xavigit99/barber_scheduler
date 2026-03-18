"""add telefone to barbeiros

Revision ID: a1b2c3d4e5f6
Revises: f1a3c5e7b9d2
Create Date: 2026-03-18 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "f1a3c5e7b9d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("barbeiros", sa.Column("telefone", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("barbeiros", "telefone")
