"""initial schema

Revision ID: ddfd6b03d05e
Revises:
Create Date: 2026-03-15 22:30:59.328626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddfd6b03d05e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # appointments — add tenant_id index
    op.create_index(op.f('ix_appointments_tenant_id'), 'appointments', ['tenant_id'], unique=False)

    # barbeiros — assign NULL tenant_id rows to tenant 1 before enforcing NOT NULL
    op.execute(sa.text(
        "UPDATE barbeiros SET tenant_id = (SELECT id FROM tenants ORDER BY id LIMIT 1) "
        "WHERE tenant_id IS NULL"
    ))
    op.alter_column('barbeiros', 'tenant_id', existing_type=sa.INTEGER(), nullable=False)
    op.create_index(op.f('ix_barbeiros_deleted'), 'barbeiros', ['deleted'], unique=False)
    op.create_index(op.f('ix_barbeiros_tenant_id'), 'barbeiros', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_barbeiros_user_id'), 'barbeiros', ['user_id'], unique=False)

    # barber_availabilities — add deleted column (use server_default for existing rows)
    op.add_column('barber_availabilities', sa.Column(
        'deleted', sa.Boolean(), nullable=False, server_default='false'
    ))
    op.alter_column('barber_availabilities', 'deleted', server_default=None)
    op.create_index(op.f('ix_barber_availabilities_deleted'), 'barber_availabilities', ['deleted'], unique=False)

    # barber_blocks — same pattern
    op.add_column('barber_blocks', sa.Column(
        'deleted', sa.Boolean(), nullable=False, server_default='false'
    ))
    op.alter_column('barber_blocks', 'deleted', server_default=None)
    op.create_index(op.f('ix_barber_blocks_deleted'), 'barber_blocks', ['deleted'], unique=False)

    # barbershops — fix index uniqueness and add deleted index
    op.drop_index(op.f('ix_barbershops_owner_user_id'), table_name='barbershops')
    op.create_index(op.f('ix_barbershops_owner_user_id'), 'barbershops', ['owner_user_id'], unique=False)
    op.create_index(op.f('ix_barbershops_deleted'), 'barbershops', ['deleted'], unique=False)

    # clientes — add tenant_id (nullable first, fill, then NOT NULL), user_id, deleted
    op.add_column('clientes', sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.execute(sa.text(
        "UPDATE clientes SET tenant_id = (SELECT id FROM tenants ORDER BY id LIMIT 1) "
        "WHERE tenant_id IS NULL"
    ))
    op.alter_column('clientes', 'tenant_id', existing_type=sa.INTEGER(), nullable=False)
    op.add_column('clientes', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('clientes', sa.Column(
        'deleted', sa.Boolean(), nullable=False, server_default='false'
    ))
    op.alter_column('clientes', 'deleted', server_default=None)
    op.create_index(op.f('ix_clientes_deleted'), 'clientes', ['deleted'], unique=False)
    op.create_index(op.f('ix_clientes_tenant_id'), 'clientes', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_clientes_user_id'), 'clientes', ['user_id'], unique=False)
    op.create_foreign_key(None, 'clientes', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'clientes', 'tenants', ['tenant_id'], ['id'])

    # servicos — enforce NOT NULL on tenant_id (0 rows, safe) and add indexes
    op.alter_column('servicos', 'tenant_id', existing_type=sa.INTEGER(), nullable=False)
    op.create_index(op.f('ix_servicos_deleted'), 'servicos', ['deleted'], unique=False)
    op.create_index(op.f('ix_servicos_tenant_id'), 'servicos', ['tenant_id'], unique=False)

    # users — remove legacy tenant_id column (not in User model)
    op.drop_index(op.f('ix_users_tenant_id'), table_name='users')
    op.drop_constraint(op.f('users_tenant_id_fkey'), 'users', type_='foreignkey')
    op.drop_column('users', 'tenant_id')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('users', sa.Column('tenant_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('users_tenant_id_fkey'), 'users', 'tenants', ['tenant_id'], ['id'])
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)
    op.drop_index(op.f('ix_servicos_tenant_id'), table_name='servicos')
    op.drop_index(op.f('ix_servicos_deleted'), table_name='servicos')
    op.alter_column('servicos', 'tenant_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_constraint(None, 'clientes', type_='foreignkey')
    op.drop_constraint(None, 'clientes', type_='foreignkey')
    op.drop_index(op.f('ix_clientes_user_id'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_tenant_id'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_deleted'), table_name='clientes')
    op.drop_column('clientes', 'deleted')
    op.drop_column('clientes', 'user_id')
    op.drop_column('clientes', 'tenant_id')
    op.drop_index(op.f('ix_barbershops_deleted'), table_name='barbershops')
    op.drop_index(op.f('ix_barbershops_owner_user_id'), table_name='barbershops')
    op.create_index(op.f('ix_barbershops_owner_user_id'), 'barbershops', ['owner_user_id'], unique=True)
    op.drop_index(op.f('ix_barber_blocks_deleted'), table_name='barber_blocks')
    op.drop_column('barber_blocks', 'deleted')
    op.drop_index(op.f('ix_barber_availabilities_deleted'), table_name='barber_availabilities')
    op.drop_column('barber_availabilities', 'deleted')
    op.drop_index(op.f('ix_barbeiros_user_id'), table_name='barbeiros')
    op.drop_index(op.f('ix_barbeiros_tenant_id'), table_name='barbeiros')
    op.drop_index(op.f('ix_barbeiros_deleted'), table_name='barbeiros')
    op.alter_column('barbeiros', 'tenant_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_index(op.f('ix_appointments_tenant_id'), table_name='appointments')
