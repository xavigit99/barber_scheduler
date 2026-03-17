"""f19: add user_id to barbeiros

Revision ID: e5a2c8f1b9d3
Revises: c9e1f3b4a2d8
Create Date: 2026-03-17 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "e5a2c8f1b9d3"
down_revision: str | Sequence[str] | None = "c9e1f3b4a2d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("barbeiros")]
    if "user_id" not in columns:
        op.add_column(
            "barbeiros",
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        )
        op.create_index("ix_barbeiros_user_id", "barbeiros", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_barbeiros_user_id", table_name="barbeiros")
    op.drop_column("barbeiros", "user_id")
