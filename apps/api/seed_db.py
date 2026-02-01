from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def seed_data():
    db = SessionLocal()
    
    try:
        # 1. Seed Units
        units_data = [
            {"code": "YYS", "name": "Yayasan Asy-Syuuraa"},
            {"code": "RA", "name": "RA Asy-Syuuraa"},
            {"code": "SDIT", "name": "SDIT Asy-Syuuraa"},
            {"code": "SMPIT", "name": "SMPIT Asy-Syuuraa"},
        ]
        
        for unit in units_data:
            exists = db.query(models.Unit).filter(models.Unit.code == unit["code"]).first()
            if not exists:
                db_unit = models.Unit(**unit)
                db.add(db_unit)
                print(f"Added Unit: {unit['name']}")
        
        # 2. Seed Roles
        roles_data = [
            {"code": "superadmin", "name": "Superadmin", "scope": "sistem", "priority": 1},
            {"code": "kabid_umum", "name": "Kepala Bidang Umum", "scope": "yayasan", "priority": 2},
            {"code": "kabid_keuangan", "name": "Kepala Bidang Keuangan", "scope": "yayasan", "priority": 2},
            {"code": "tu_yayasan", "name": "Tata Usaha Yayasan", "scope": "yayasan", "priority": 3},
            {"code": "staf_keuangan", "name": "Staf Keuangan", "scope": "yayasan", "priority": 3},
            {"code": "kepala_unit", "name": "Kepala Unit", "scope": "unit", "priority": 4},
            {"code": "wakil_kepala", "name": "Wakil Kepala Unit", "scope": "unit", "priority": 5},
            {"code": "tu_unit", "name": "Tata Usaha Unit", "scope": "unit", "priority": 6},
            {"code": "guru", "name": "Guru", "scope": "unit", "priority": 7},
            {"code": "karyawan", "name": "Karyawan", "scope": "unit", "priority": 8},
            {"code": "orangtua", "name": "Orangtua", "scope": "portal", "priority": 9},
        ]
        
        for role in roles_data:
            exists = db.query(models.Role).filter(models.Role.code == role["code"]).first()
            if not exists:
                db_role = models.Role(**role)
                db.add(db_role)
                print(f"Added Role: {role['name']}")
        
        db.commit() # Commit roles first to get IDs

        # 3. Seed Superadmin User
        import auth
        superadmin_role = db.query(models.Role).filter(models.Role.code == "superadmin").first()
        
        if superadmin_role:
            exists_user = db.query(models.User).filter(models.User.email == "admin@asysyuura.sch.id").first()
            if not exists_user:
                hashed_password = auth.get_password_hash("admin123") # Default Password
                superadmin = models.User(
                    nik="999999",
                    email="admin@asysyuura.sch.id",
                    full_name="Super Administrator",
                    password_hash=hashed_password,
                    role_id=superadmin_role.id
                )
                db.add(superadmin)
                print("Added Superadmin User: admin@asysyuura.sch.id / admin123")

        db.commit()
        print("Seeding Complete!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
