"""add_user_tenant_email_unique_constraint

Revision ID: cd1826eb6e07
Revises: a8f2c3d4e5b6
Create Date: 2026-05-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cd1826eb6e07'
down_revision: Union[str, Sequence[str], None] = 'a8f2c3d4e5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('users_email_key', 'users', type_='unique')
    op.create_unique_constraint('uq_user_tenant_email', 'users', ['tenant_id', 'email'])


def downgrade() -> None:
    op.drop_constraint('uq_user_tenant_email', 'users', type_='unique')
    op.create_unique_constraint('users_email_key', 'users', ['email'])
