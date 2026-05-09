"""add end_date to academic_calendar_events

Revision ID: f1a2b3c4d5e6
Revises: 8043e121b888
Create Date: 2026-05-09 08:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '8043e121b888'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('academic_calendar_events', sa.Column('end_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('academic_calendar_events', 'end_date')
