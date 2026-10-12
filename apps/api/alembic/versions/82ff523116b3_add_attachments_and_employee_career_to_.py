"""add_attachments_and_employee_career_to_documents

Revision ID: 82ff523116b3
Revises: 20eaa0468964
Create Date: 2026-10-12 08:38:50.922517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82ff523116b3'
down_revision: Union[str, Sequence[str], None] = '20eaa0468964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add attachments and employee career columns to documents
    with op.batch_alter_table('documents') as batch_op:
        batch_op.add_column(sa.Column('attachments', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('employee_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('employee_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('sk_type', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('position_title', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('term_start_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('term_end_date', sa.DateTime(), nullable=True))
        batch_op.create_foreign_key('fk_documents_employee_id', 'users', ['employee_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('documents') as batch_op:
        batch_op.drop_constraint('fk_documents_employee_id', type_='foreignkey')
        batch_op.drop_column('term_end_date')
        batch_op.drop_column('term_start_date')
        batch_op.drop_column('position_title')
        batch_op.drop_column('sk_type')
        batch_op.drop_column('employee_name')
        batch_op.drop_column('employee_id')
        batch_op.drop_column('attachments')
