"""f36-f41: stocks, rooms/resources, qr, widget, clinical records

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-03-18 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # F37 — Products (stock management)
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("descricao", sa.String(), nullable=True),
        sa.Column("stock_atual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stock_minimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("preco_unitario", sa.Float(), nullable=False, server_default="0"),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_id", "products", ["id"])
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"])
    op.create_index("ix_products_deleted", "products", ["deleted"])

    # F37 — Service-Product links
    op.create_table(
        "service_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["service_id"], ["servicos.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_service_products_id", "service_products", ["id"])
    op.create_index("ix_service_products_service_id", "service_products", ["service_id"])
    op.create_index("ix_service_products_product_id", "service_products", ["product_id"])
    op.create_index("ix_service_products_tenant_id", "service_products", ["tenant_id"])
    op.create_index("ix_service_products_deleted", "service_products", ["deleted"])

    # F38 — Resources (rooms, chairs, equipment)
    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_resources_id", "resources", ["id"])
    op.create_index("ix_resources_tenant_id", "resources", ["tenant_id"])
    op.create_index("ix_resources_deleted", "resources", ["deleted"])

    # F38 — Add resource_id to appointments
    op.add_column(
        "appointments",
        sa.Column("resource_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_appointments_resource_id",
        "appointments",
        "resources",
        ["resource_id"],
        ["id"],
    )
    op.create_index("ix_appointments_resource_id", "appointments", ["resource_id"])

    # F41 — Clinical records
    op.create_table(
        "clinical_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("alergias", sa.Text(), nullable=True),
        sa.Column("notas_saude", sa.Text(), nullable=True),
        sa.Column(
            "consentimento_assinado",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("consentimento_data", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clinical_records_id", "clinical_records", ["id"])
    op.create_index("ix_clinical_records_client_id", "clinical_records", ["client_id"])
    op.create_index("ix_clinical_records_tenant_id", "clinical_records", ["tenant_id"])
    op.create_index("ix_clinical_records_deleted", "clinical_records", ["deleted"])

    # F41 — Clinical notes
    op.create_table(
        "clinical_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("clinical_record_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("nota", sa.Text(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("barber_id", sa.Integer(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["clinical_record_id"], ["clinical_records.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["barber_id"], ["barbeiros.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clinical_notes_id", "clinical_notes", ["id"])
    op.create_index(
        "ix_clinical_notes_clinical_record_id",
        "clinical_notes",
        ["clinical_record_id"],
    )
    op.create_index("ix_clinical_notes_tenant_id", "clinical_notes", ["tenant_id"])
    op.create_index("ix_clinical_notes_deleted", "clinical_notes", ["deleted"])


def downgrade() -> None:
    op.drop_index("ix_clinical_notes_deleted", table_name="clinical_notes")
    op.drop_index("ix_clinical_notes_tenant_id", table_name="clinical_notes")
    op.drop_index(
        "ix_clinical_notes_clinical_record_id", table_name="clinical_notes"
    )
    op.drop_index("ix_clinical_notes_id", table_name="clinical_notes")
    op.drop_table("clinical_notes")

    op.drop_index("ix_clinical_records_deleted", table_name="clinical_records")
    op.drop_index("ix_clinical_records_tenant_id", table_name="clinical_records")
    op.drop_index("ix_clinical_records_client_id", table_name="clinical_records")
    op.drop_index("ix_clinical_records_id", table_name="clinical_records")
    op.drop_table("clinical_records")

    op.drop_index("ix_appointments_resource_id", table_name="appointments")
    op.drop_constraint("fk_appointments_resource_id", "appointments", type_="foreignkey")
    op.drop_column("appointments", "resource_id")

    op.drop_index("ix_resources_deleted", table_name="resources")
    op.drop_index("ix_resources_tenant_id", table_name="resources")
    op.drop_index("ix_resources_id", table_name="resources")
    op.drop_table("resources")

    op.drop_index("ix_service_products_deleted", table_name="service_products")
    op.drop_index("ix_service_products_tenant_id", table_name="service_products")
    op.drop_index("ix_service_products_product_id", table_name="service_products")
    op.drop_index("ix_service_products_service_id", table_name="service_products")
    op.drop_index("ix_service_products_id", table_name="service_products")
    op.drop_table("service_products")

    op.drop_index("ix_products_deleted", table_name="products")
    op.drop_index("ix_products_tenant_id", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")
