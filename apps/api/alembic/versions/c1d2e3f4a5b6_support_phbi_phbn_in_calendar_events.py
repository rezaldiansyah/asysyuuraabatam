"""support phbi phbn in calendar events

Revision ID: c1d2e3f4a5b6
Revises: e7b8c9d0e1f2
Create Date: 2026-10-20 07:47:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'e7b8c9d0e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Alter academic_calendar_events.type to VARCHAR(50) so any event type is allowed
    try:
        op.execute(sa.text("ALTER TABLE academic_calendar_events ALTER COLUMN type TYPE VARCHAR(50) USING type::text"))
    except Exception:
        pass

    # 2. Add PHBI, PHBN to native enums if they exist
    for enum_name in ['calendar_event_type_enum', 'calendareventtype']:
        for val in ['PHBI', 'PHBN']:
            try:
                op.execute(sa.text(f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS '{val}'"))
            except Exception:
                pass


def downgrade() -> None:
    pass
