"""add permissions to roles

Revision ID: 0a5e1c6cc05d
Revises: e0d9bd201a9b
Create Date: 2026-05-17 11:19:40.677795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a5e1c6cc05d'
down_revision: Union[str, Sequence[str], None] = 'e0d9bd201a9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('roles', sa.Column('permissions', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('roles', 'permissions')
