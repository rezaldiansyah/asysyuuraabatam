"""add_document_team_members_and_recipient_type

Revision ID: e7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-10-17 19:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b8c9d0e1f2'
down_revision: Union[str, Sequence[str], None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add recipient_type column to documents
    try:
        op.add_column('documents', sa.Column('recipient_type', sa.String(), nullable=True, server_default='individual'))
    except Exception:
        pass

    # 2. Create document_team_members table
    try:
        op.create_table(
            'document_team_members',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('document_id', sa.Integer(), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('employee_name', sa.String(), nullable=False),
            sa.Column('role_in_team', sa.String(), nullable=True),
            sa.Column('unit_id', sa.Integer(), sa.ForeignKey('units.id'), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_document_team_members_id'), 'document_team_members', ['id'], unique=False)
        op.create_index(op.f('ix_document_team_members_document_id'), 'document_team_members', ['document_id'], unique=False)
        op.create_index(op.f('ix_document_team_members_user_id'), 'document_team_members', ['user_id'], unique=False)
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_table('document_team_members')
    except Exception:
        pass
    try:
        op.drop_column('documents', 'recipient_type')
    except Exception:
        pass
