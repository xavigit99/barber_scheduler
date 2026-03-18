"""f8 multi-tenant hardening

Revision ID: a8f4c2e9b3d7
Revises: ddfd6b03d05e
Create Date: 2026-03-16 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8f4c2e9b3d7"
down_revision: str | Sequence[str] | None = "ddfd6b03d05e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema — idempotent via IF NOT EXISTS guards."""
    conn = op.get_bind()

    # 1. Add deleted_at to 7 existing tables (IF NOT EXISTS)
    for table in (
        "barbeiros",
        "clientes",
        "servicos",
        "barbershops",
        "appointments",
        "barber_availabilities",
        "barber_blocks",
    ):
        conn.execute(sa.text(
            f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP"
        ))

    # 2. Fix appointments.tenant_id — fill NULLs then enforce NOT NULL
    conn.execute(sa.text(
        "UPDATE appointments SET tenant_id = (SELECT id FROM tenants ORDER BY id LIMIT 1) "
        "WHERE tenant_id IS NULL AND (SELECT COUNT(*) FROM tenants) > 0"
    ))
    op.alter_column("appointments", "tenant_id", existing_type=sa.INTEGER(), nullable=False)

    # 3. Create barbershop_memberships table (IF NOT EXISTS)
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS barbershop_memberships (
            id SERIAL NOT NULL,
            barber_id INTEGER NOT NULL REFERENCES barbeiros(id),
            barbershop_id INTEGER NOT NULL REFERENCES barbershops(id),
            role VARCHAR NOT NULL,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            deleted BOOLEAN NOT NULL DEFAULT false,
            deleted_at TIMESTAMP,
            PRIMARY KEY (id),
            CONSTRAINT uq_membership_barber_barbershop UNIQUE (barber_id, barbershop_id)
        )
    """))

    # 3b. Indexes (IF NOT EXISTS)
    for idx, col in (
        ("ix_barbershop_memberships_id", "id"),
        ("ix_barbershop_memberships_barber_id", "barber_id"),
        ("ix_barbershop_memberships_barbershop_id", "barbershop_id"),
        ("ix_barbershop_memberships_tenant_id", "tenant_id"),
        ("ix_barbershop_memberships_deleted", "deleted"),
    ):
        conn.execute(sa.text(
            f"CREATE INDEX IF NOT EXISTS {idx} ON barbershop_memberships ({col})"
        ))


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
