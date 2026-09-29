"""seed_missing_roles_and_default_permissions

Revision ID: acb2391cfee2
Revises: cafb34432dad
Create Date: 2026-09-29 08:57:11.356868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acb2391cfee2'
down_revision: Union[str, Sequence[str], None] = 'cafb34432dad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import json

ROLES_DATA = [
    {"code": "superadmin", "name": "Superadmin", "scope": "sistem", "priority": 1, "permissions": ["dashboard", "akademik", "tahfidz", "kesiswaan", "keuangan", "kepegawaian", "internal", "ppdb", "cms", "pengaturan"]},
    {"code": "ketua_yayasan", "name": "Ketua Yayasan", "scope": "yayasan", "priority": 2, "permissions": ["dashboard", "akademik", "tahfidz", "kesiswaan", "keuangan", "kepegawaian", "internal", "ppdb", "cms", "pengaturan"]},
    {"code": "wakil_ketua_yayasan", "name": "Wakil Ketua Yayasan", "scope": "yayasan", "priority": 3, "permissions": ["dashboard", "akademik", "tahfidz", "kesiswaan", "keuangan", "kepegawaian", "internal", "ppdb", "cms"]},
    {"code": "kabid_umum", "name": "Kepala Bidang Umum", "scope": "yayasan", "priority": 4, "permissions": ["dashboard", "akademik", "kesiswaan", "kepegawaian", "internal", "ppdb", "cms"]},
    {"code": "kabid_keuangan", "name": "Kepala Bidang Keuangan", "scope": "yayasan", "priority": 4, "permissions": ["dashboard", "keuangan", "internal"]},
    {"code": "tu_yayasan", "name": "Tata Usaha Yayasan", "scope": "yayasan", "priority": 5, "permissions": ["dashboard", "kepegawaian", "internal", "cms", "ppdb"]},
    {"code": "staf_keuangan", "name": "Staf Keuangan", "scope": "yayasan", "priority": 5, "permissions": ["dashboard", "keuangan"]},
    {"code": "kepala_unit", "name": "Kepala Unit", "scope": "unit", "priority": 4, "permissions": ["dashboard", "akademik", "tahfidz", "kesiswaan", "kepegawaian", "internal", "ppdb"]},
    {"code": "wakil_kepala", "name": "Wakil Kepala Unit", "scope": "unit", "priority": 5, "permissions": ["dashboard", "akademik", "tahfidz", "kesiswaan", "kepegawaian", "internal"]},
    {"code": "tu_unit", "name": "Tata Usaha Unit", "scope": "unit", "priority": 6, "permissions": ["dashboard", "akademik", "tahfidz", "kesiswaan", "kepegawaian", "internal", "ppdb"]},
    {"code": "guru", "name": "Guru", "scope": "unit", "priority": 7, "permissions": ["dashboard", "akademik", "tahfidz", "kesiswaan", "internal"]},
    {"code": "karyawan", "name": "Karyawan", "scope": "unit", "priority": 8, "permissions": ["dashboard", "internal"]},
    {"code": "orangtua", "name": "Orangtua", "scope": "portal", "priority": 9, "permissions": ["dashboard"]},
]


def upgrade() -> None:
    conn = op.get_bind()
    for r in ROLES_DATA:
        res = conn.execute(sa.text("SELECT id, permissions FROM roles WHERE code = :code"), {"code": r["code"]}).first()
        perm_json = json.dumps(r["permissions"])
        if not res:
            conn.execute(
                sa.text("INSERT INTO roles (code, name, scope, priority, permissions) VALUES (:code, :name, :scope, :priority, :permissions)"),
                {
                    "code": r["code"],
                    "name": r["name"],
                    "scope": r["scope"],
                    "priority": r["priority"],
                    "permissions": perm_json
                }
            )
        else:
            if not res[1] or res[1] == "[]" or res[1] == "null":
                conn.execute(
                    sa.text("UPDATE roles SET permissions = :permissions WHERE id = :id"),
                    {"permissions": perm_json, "id": res[0]}
                )


def downgrade() -> None:
    pass
