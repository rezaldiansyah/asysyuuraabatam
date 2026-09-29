"""create_document_duplicate_resolutions_table

Revision ID: cafb34432dad
Revises: 8032751076b8
Create Date: 2026-09-29 08:13:16.847759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cafb34432dad'
down_revision: Union[str, Sequence[str], None] = '8032751076b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'document_duplicate_resolutions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doc_a_id', sa.Integer(), nullable=True),
        sa.Column('doc_b_id', sa.Integer(), nullable=True),
        sa.Column('resolution', sa.String(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['doc_a_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['doc_b_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_duplicate_resolutions_doc_a_id'), 'document_duplicate_resolutions', ['doc_a_id'], unique=False)
    op.create_index(op.f('ix_document_duplicate_resolutions_doc_b_id'), 'document_duplicate_resolutions', ['doc_b_id'], unique=False)
    op.create_index(op.f('ix_document_duplicate_resolutions_id'), 'document_duplicate_resolutions', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_document_duplicate_resolutions_id'), table_name='document_duplicate_resolutions')
    op.drop_index(op.f('ix_document_duplicate_resolutions_doc_b_id'), table_name='document_duplicate_resolutions')
    op.drop_index(op.f('ix_document_duplicate_resolutions_doc_a_id'), table_name='document_duplicate_resolutions')
    op.drop_table('document_duplicate_resolutions')

