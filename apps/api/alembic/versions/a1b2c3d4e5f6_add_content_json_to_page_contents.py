"""add_content_json_to_page_contents

Revision ID: a1b2c3d4e5f6
Revises: 75f3d73b2a37
Create Date: 2026-02-11 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '75f3d73b2a37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing content_json column to page_contents table."""
    op.add_column('page_contents', sa.Column('content_json', sa.String(), nullable=True))


def downgrade() -> None:
    """Remove content_json column from page_contents table."""
    op.drop_column('page_contents', 'content_json')
