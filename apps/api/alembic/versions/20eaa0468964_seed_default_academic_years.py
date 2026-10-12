"""seed_default_academic_years

Revision ID: 20eaa0468964
Revises: acb2391cfee2
Create Date: 2026-10-12 08:21:12.540096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20eaa0468964'
down_revision: Union[str, Sequence[str], None] = 'acb2391cfee2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_ACADEMIC_YEARS = [
    {"name": "2024/2025", "semester": "Genap", "is_active": False},
    {"name": "2025/2026", "semester": "Ganjil", "is_active": True},
    {"name": "2025/2026", "semester": "Genap", "is_active": False},
    {"name": "2026/2027", "semester": "Ganjil", "is_active": False},
    {"name": "2026/2027", "semester": "Genap", "is_active": False},
]


def upgrade() -> None:
    conn = op.get_bind()
    
    # Check if there is already an active year
    has_active = conn.execute(
        sa.text("SELECT id FROM academic_years WHERE is_active = :act"),
        {"act": True}
    ).first()

    for item in DEFAULT_ACADEMIC_YEARS:
        # Check if already exists by name and semester
        row = conn.execute(
            sa.text("SELECT id FROM academic_years WHERE name = :name AND semester = :semester"),
            {"name": item["name"], "semester": item["semester"]}
        ).first()

        is_act = item["is_active"] if not has_active else False

        if not row:
            conn.execute(
                sa.text("INSERT INTO academic_years (name, semester, is_active) VALUES (:name, :semester, :is_active)"),
                {"name": item["name"], "semester": item["semester"], "is_active": is_act}
            )


def downgrade() -> None:
    pass
