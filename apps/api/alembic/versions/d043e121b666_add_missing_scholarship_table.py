"""Add missing scholarship table

Revision ID: d043e121b666
Revises: cabba5b647e7
Create Date: 2026-02-01 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd043e121b666'
down_revision: Union[str, Sequence[str], None] = 'cabba5b647e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('scholarships',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('type', sa.Enum('FIXED', 'PERCENTAGE', name='scholarshiptype'), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scholarships_id'), 'scholarships', ['id'], unique=False)
    
    # Add dependency column
    op.add_column('students', sa.Column('scholarship_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_index(op.f('ix_scholarships_id'), table_name='scholarships')
    op.drop_table('scholarships')
    sa.Enum(name='scholarshiptype').drop(op.get_bind(), checkfirst=False)
