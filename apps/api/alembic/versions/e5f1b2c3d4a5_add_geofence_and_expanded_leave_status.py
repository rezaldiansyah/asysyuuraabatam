"""add_geofence_and_expanded_leave_status

Revision ID: e5f1b2c3d4a5
Revises: 82ff523116b3
Create Date: 2026-10-14 12:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f1b2c3d4a5'
down_revision: Union[str, Sequence[str], None] = '82ff523116b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "postgresql":
        new_statuses = [
            'LATE',
            'DISPENSATION',
            'LEAVE_ANNUAL',
            'LEAVE_MATERNITY',
            'LEAVE_MARRIAGE',
            'LEAVE_BEREAVEMENT',
            'LEAVE_PILGRIMAGE',
            'LEAVE_UNPAID'
        ]
        for val in new_statuses:
            try:
                conn.execute(sa.text(f"ALTER TYPE attendancestatus ADD VALUE IF NOT EXISTS '{val}'"))
            except Exception as e:
                print(f"Notice adding enum value {val}: {e}")

    with op.batch_alter_table('employee_attendances') as batch_op:
        batch_op.add_column(sa.Column('check_in_lat', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('check_in_lng', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('check_in_distance', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('check_out_lat', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('check_out_lng', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('check_out_distance', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('device_info', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('employee_attendances') as batch_op:
        batch_op.drop_column('device_info')
        batch_op.drop_column('check_out_distance')
        batch_op.drop_column('check_out_lng')
        batch_op.drop_column('check_out_lat')
        batch_op.drop_column('check_in_distance')
        batch_op.drop_column('check_in_lng')
        batch_op.drop_column('check_in_lat')
