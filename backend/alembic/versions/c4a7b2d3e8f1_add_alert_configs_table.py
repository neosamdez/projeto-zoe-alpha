"""add_alert_configs_table

Revision ID: c4a7b2d3e8f1
Revises: b3f7a1c2d4e5
Create Date: 2026-05-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision: str = 'c4a7b2d3e8f1'
down_revision: Union[str, Sequence[str], None] = 'b3f7a1c2d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'alert_configs',
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('min_stock_threshold', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'name', name='uq_alert_config_tenant_name'),
    )
    op.create_index(op.f('ix_alert_configs_id'), 'alert_configs', ['id'], unique=False)
    op.create_index(op.f('ix_alert_configs_tenant_id'), 'alert_configs', ['tenant_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_alert_configs_tenant_id'), table_name='alert_configs')
    op.drop_index(op.f('ix_alert_configs_id'), table_name='alert_configs')
    op.drop_table('alert_configs')
