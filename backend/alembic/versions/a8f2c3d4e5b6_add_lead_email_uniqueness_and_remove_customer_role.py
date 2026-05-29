"""add_lead_email_uniqueness_and_remove_customer_role

Revision ID: a8f2c3d4e5b6
Revises: 1e16f991424b
Create Date: 2026-05-27 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a8f2c3d4e5b6'
down_revision: Union[str, Sequence[str], None] = '1e16f991424b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_lead_tenant_email', 'leads', ['tenant_id', 'email'])
    op.execute("DELETE FROM userrole WHERE role = 'CUSTOMER'")


def downgrade() -> None:
    op.drop_constraint('uq_lead_tenant_email', 'leads', type_='unique')
