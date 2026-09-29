"""add_expired_date_to_documents

Revision ID: 8032751076b8
Revises: c87b60e9d36a
Create Date: 2026-09-29 07:35:56.355988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8032751076b8'
down_revision: Union[str, Sequence[str], None] = 'c87b60e9d36a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('documents', sa.Column('expired_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'expired_date')

