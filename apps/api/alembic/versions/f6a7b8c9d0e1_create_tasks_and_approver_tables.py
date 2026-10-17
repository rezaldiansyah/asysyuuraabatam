"""create_tasks_and_approver_tables

Revision ID: f6a7b8c9d0e1
Revises: e5f1b2c3d4a5
Create Date: 2026-10-17 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f1b2c3d4a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='antrian'),
        sa.Column('priority_level', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('creator_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assignee_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('unit_id', sa.Integer(), sa.ForeignKey('units.id'), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('meeting_minute_id', sa.Integer(), sa.ForeignKey('meeting_minutes.id'), nullable=True),
        sa.Column('meeting_action_item_id', sa.Integer(), sa.ForeignKey('meeting_action_items.id'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_title'), 'tasks', ['title'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    op.create_index(op.f('ix_tasks_priority_level'), 'tasks', ['priority_level'], unique=False)
    op.create_index(op.f('ix_tasks_creator_id'), 'tasks', ['creator_id'], unique=False)
    op.create_index(op.f('ix_tasks_assignee_id'), 'tasks', ['assignee_id'], unique=False)
    op.create_index(op.f('ix_tasks_unit_id'), 'tasks', ['unit_id'], unique=False)
    op.create_index(op.f('ix_tasks_deadline'), 'tasks', ['deadline'], unique=False)

    # 2. Create task_approver_links table
    op.create_table(
        'task_approver_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_approver_links_id'), 'task_approver_links', ['id'], unique=False)
    op.create_index(op.f('ix_task_approver_links_task_id'), 'task_approver_links', ['task_id'], unique=False)
    op.create_index(op.f('ix_task_approver_links_user_id'), 'task_approver_links', ['user_id'], unique=False)

    # 3. Create task_histories table
    op.create_table(
        'task_histories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('from_status', sa.String(), nullable=True),
        sa.Column('to_status', sa.String(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('changed_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_histories_id'), 'task_histories', ['id'], unique=False)
    op.create_index(op.f('ix_task_histories_task_id'), 'task_histories', ['task_id'], unique=False)


def downgrade() -> None:
    op.drop_table('task_histories')
    op.drop_table('task_approver_links')
    op.drop_table('tasks')
