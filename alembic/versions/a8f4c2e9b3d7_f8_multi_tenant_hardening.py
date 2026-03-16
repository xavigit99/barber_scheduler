"""f8 multi-tenant hardening

Revision ID: a8f4c2e9b3d7
Revises: ddfd6b03d05e
Create Date: 2026-03-16 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8f4c2e9b3d7"
down_revision: Union[str, Sequence[str], None] = "ddfd6b03d05e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add deleted_at to 7 existing tables
    for table in (
        "barbeiros",
        "clientes",
        "servicos",
        "barbershops",
        "appointments",
        "barber_availabilities",
        "barber_blocks",
    ):
        op.add_column(table, sa.Column("deleted_at", sa.DateTime(), nullable=True))

    # 2. Fix appointments.tenant_id — fill NULLs then enforce NOT NULL
    # Guard: only backfill if there are tenants to assign to
    op.execute(sa.text(
        "UPDATE appointments SET tenant_id = (SELECT id FROM tenants ORDER BY id LIMIT 1) "
        "WHERE tenant_id IS NULL AND (SELECT COUNT(*) FROM tenants) > 0"
    ))
    op.alter_column("appointments", "tenant_id", existing_type=sa.INTEGER(), nullable=False)

    # 3. Create barbershop_memberships table
    op.create_table(
        "barbershop_memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("barber_id", sa.Integer(), sa.ForeignKey("barbeiros.id"), nullable=False),
        sa.Column("barbershop_id", sa.Integer(), sa.ForeignKey("barbershops.id"), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("barber_id", "barbershop_id", name="uq_membership_barber_barbershop"),
    )
    op.create_index(
        op.f("ix_barbershop_memberships_tenant_id"),
        "barbershop_memberships",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_barbershop_memberships_id"), "barbershop_memberships", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_barbershop_memberships_barber_id"),
        "barbershop_memberships",
        ["barber_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_barbershop_memberships_barbershop_id"),
        "barbershop_memberships",
        ["barbershop_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_barbershop_memberships_deleted"),
        "barbershop_memberships",
        ["deleted"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 3. Drop barbershop_memberships
    op.drop_index(op.f("ix_barbershop_memberships_tenant_id"), table_name="barbershop_memberships")
    op.drop_index(op.f("ix_barbershop_memberships_deleted"), table_name="barbershop_memberships")
    op.drop_index(
        op.f("ix_barbershop_memberships_barbershop_id"), table_name="barbershop_memberships"
    )
    op.drop_index(
        op.f("ix_barbershop_memberships_barber_id"), table_name="barbershop_memberships"
    )
    op.drop_index(op.f("ix_barbershop_memberships_id"), table_name="barbershop_memberships")
    op.drop_table("barbershop_memberships")

    # 2. Revert appointments.tenant_id to nullable
    op.alter_column("appointments", "tenant_id", existing_type=sa.INTEGER(), nullable=True)

    # 1. Drop deleted_at from 7 tables (reverse order)
    for table in (
        "barber_blocks",
        "barber_availabilities",
        "appointments",
        "barbershops",
        "servicos",
        "clientes",
        "barbeiros",
    ):
        op.drop_column(table, "deleted_at")
