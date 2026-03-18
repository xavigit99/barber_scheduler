"""f28-f30-f31: service packs, loyalty, birthday fields

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-03-18 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # F28 — Service Packs
    op.create_table(
        "service_packs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("n_sessoes", sa.Integer(), nullable=False),
        sa.Column("preco", sa.Float(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["servicos.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_packs_id", "service_packs", ["id"])
    op.create_index("ix_service_packs_tenant_id", "service_packs", ["tenant_id"])
    op.create_index("ix_service_packs_service_id", "service_packs", ["service_id"])
    op.create_index("ix_service_packs_deleted", "service_packs", ["deleted"])

    op.create_table(
        "client_packs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("service_pack_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sessoes_restantes", sa.Integer(), nullable=False),
        sa.Column("comprado_em", sa.DateTime(), nullable=False),
        sa.Column("expira_em", sa.Date(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["service_pack_id"], ["service_packs.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_client_packs_id", "client_packs", ["id"])
    op.create_index("ix_client_packs_client_id", "client_packs", ["client_id"])
    op.create_index("ix_client_packs_tenant_id", "client_packs", ["tenant_id"])
    op.create_index("ix_client_packs_deleted", "client_packs", ["deleted"])

    # F30 — Loyalty
    op.create_table(
        "loyalty_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("pontos_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontos_disponiveis", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_loyalty_accounts_id", "loyalty_accounts", ["id"])
    op.create_index("ix_loyalty_accounts_client_id", "loyalty_accounts", ["client_id"])
    op.create_index("ix_loyalty_accounts_tenant_id", "loyalty_accounts", ["tenant_id"])

    op.create_table(
        "loyalty_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("loyalty_account_id", sa.Integer(), nullable=False),
        sa.Column("appointment_id", sa.Integer(), nullable=True),
        sa.Column("pontos", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("descricao", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["loyalty_account_id"], ["loyalty_accounts.id"]),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_loyalty_transactions_id", "loyalty_transactions", ["id"])
    op.create_index(
        "ix_loyalty_transactions_loyalty_account_id",
        "loyalty_transactions",
        ["loyalty_account_id"],
    )
    op.create_index(
        "ix_loyalty_transactions_appointment_id",
        "loyalty_transactions",
        ["appointment_id"],
    )

    # F31 — Birthday fields on clients
    op.add_column("clientes", sa.Column("data_nascimento", sa.Date(), nullable=True))
    op.add_column("clientes", sa.Column("birthday_msg_year", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("clientes", "birthday_msg_year")
    op.drop_column("clientes", "data_nascimento")

    op.drop_index("ix_loyalty_transactions_appointment_id", table_name="loyalty_transactions")
    op.drop_index(
        "ix_loyalty_transactions_loyalty_account_id", table_name="loyalty_transactions"
    )
    op.drop_index("ix_loyalty_transactions_id", table_name="loyalty_transactions")
    op.drop_table("loyalty_transactions")

    op.drop_index("ix_loyalty_accounts_tenant_id", table_name="loyalty_accounts")
    op.drop_index("ix_loyalty_accounts_client_id", table_name="loyalty_accounts")
    op.drop_index("ix_loyalty_accounts_id", table_name="loyalty_accounts")
    op.drop_table("loyalty_accounts")

    op.drop_index("ix_client_packs_deleted", table_name="client_packs")
    op.drop_index("ix_client_packs_tenant_id", table_name="client_packs")
    op.drop_index("ix_client_packs_client_id", table_name="client_packs")
    op.drop_index("ix_client_packs_id", table_name="client_packs")
    op.drop_table("client_packs")

    op.drop_index("ix_service_packs_deleted", table_name="service_packs")
    op.drop_index("ix_service_packs_service_id", table_name="service_packs")
    op.drop_index("ix_service_packs_tenant_id", table_name="service_packs")
    op.drop_index("ix_service_packs_id", table_name="service_packs")
    op.drop_table("service_packs")
