"""add barbershop billing fields

Revision ID: c4d8e2f1a9b7
Revises: f2b4d6e8a1c3
Create Date: 2026-03-19 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

revision = "c4d8e2f1a9b7"
down_revision = "f2b4d6e8a1c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "barbershops",
        sa.Column("billing_plan", sa.String(), nullable=False, server_default="free"),
    )
    op.add_column(
        "barbershops",
        sa.Column("subscription_status", sa.String(), nullable=False, server_default="inactive"),
    )
    op.add_column(
        "barbershops",
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
    )
    op.add_column(
        "barbershops",
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
    )
    op.create_index("ix_barbershops_billing_plan", "barbershops", ["billing_plan"])
    op.create_index("ix_barbershops_subscription_status", "barbershops", ["subscription_status"])
    op.create_index("ix_barbershops_stripe_customer_id", "barbershops", ["stripe_customer_id"], unique=True)
    op.create_index("ix_barbershops_stripe_subscription_id", "barbershops", ["stripe_subscription_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_barbershops_stripe_subscription_id", table_name="barbershops")
    op.drop_index("ix_barbershops_stripe_customer_id", table_name="barbershops")
    op.drop_index("ix_barbershops_subscription_status", table_name="barbershops")
    op.drop_index("ix_barbershops_billing_plan", table_name="barbershops")
    op.drop_column("barbershops", "stripe_subscription_id")
    op.drop_column("barbershops", "stripe_customer_id")
    op.drop_column("barbershops", "subscription_status")
    op.drop_column("barbershops", "billing_plan")
