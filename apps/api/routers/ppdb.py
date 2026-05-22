from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from deps import get_current_user
import models
import auth
import json
import re
import uuid
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/ppdb", tags=["PPDB"])

# --- Validation Helpers ---
def validate_nik(nik: str, field_name: str = "NIK"):
    """Validate that NIK is exactly 16 digits."""
    if not nik or not re.match(r'^\d{16}$', nik.replace(" ", "")):
        raise HTTPException(status_code=422, detail=f"{field_name} harus tepat 16 digit angka")

def validate_nisn(nisn: str):
    """Validate that NISN is exactly 10 digits (if provided)."""
    if nisn and not re.match(r'^\d{10}$', nisn.replace(" ", "")):
        raise HTTPException(status_code=422, detail="NISN harus tepat 10 digit angka")

def validate_phone(phone: str, field_name: str = "No. HP"):
    """Validate phone number format."""
    if not phone:
        raise HTTPException(status_code=422, detail=f"{field_name} wajib diisi")
    cleaned = phone.replace(" ", "").replace("-", "")
    if not re.match(r'^(0|62)\d{9,13}$', cleaned):
        raise HTTPException(status_code=422, detail=f"{field_name} harus berformat angka (08xx atau 628xx)")

def validate_required(value, field_name: str):
    """Validate required string field."""
    if not value or (isinstance(value, str) and len(value.strip()) < 1):
        raise HTTPException(status_code=422, detail=f"{field_name} wajib diisi")


def _serialize_registration(reg):
    """Convert a PPDBRegistration object to a JSON-safe dictionary."""
    return {
        "id": reg.id,
        "registration_number": reg.registration_number,
        "unit": reg.unit,
        "student_name": reg.student_name,
        "nisn": reg.nisn,
        "gender": reg.gender,
        "phone": reg.phone,
        "email": reg.email,
        "status": reg.status,
        "last_completed_step": reg.last_completed_step or 0,
        "created_at": reg.created_at,
        "updated_at": reg.updated_at,
        "student_data": json.loads(reg.student_data) if reg.student_data else {},
        "father_data": json.loads(reg.father_data) if reg.father_data else {},
        "mother_data": json.loads(reg.mother_data) if reg.mother_data else {},
        "guardian_data": json.loads(reg.guardian_data) if reg.guardian_data else {},
        "periodic_data": json.loads(reg.periodic_data) if reg.periodic_data else {},
        "achievements_data": json.loads(reg.achievements_data) if reg.achievements_data else [],
        "other_data": json.loads(reg.other_data) if reg.other_data else {},
        "file_kk_url": reg.file_kk_url,
        "file_akta_url": reg.file_akta_url,
        "file_foto_url": reg.file_foto_url,
    }


# --- Endpoint 1: Save Draft (Step 1-3, public) ---
@router.post("/register/draft")
async def register_draft(data: dict, db: Session = Depends(get_db)):
    """Save Step 1-3 data as draft. Creates parent user account automatically."""
    
    student_data = data.get("student_data", {})
    father_data = data.get("father_data", {})
    unit = data.get("unit", "")
    
    # Validate required fields
    validate_required(unit, "Unit Pendidikan")
    validate_required(student_data.get("full_name"), "Nama Lengkap Siswa")
    validate_nik(student_data.get("nik", ""), "NIK Siswa")
    validate_nik(student_data.get("no_kk", ""), "No. KK")
    validate_required(student_data.get("tempat_lahir"), "Tempat Lahir")
    validate_required(student_data.get("tanggal_lahir"), "Tanggal Lahir")
    
    if student_data.get("nisn"):
        validate_nisn(student_data.get("nisn", ""))
    
    validate_required(father_data.get("name"), "Nama Ayah")
    validate_nik(father_data.get("nik", ""), "NIK Ayah")
    validate_required(father_data.get("phone"), "No. HP Ayah")
    
    father_nik = father_data.get("nik", "").replace(" ", "")
    father_phone = father_data.get("phone", "")
    father_email = father_data.get("email", "")
    
    # --- Create or find parent user ---
    parent_user_id = None
    user = None
    
    if father_nik:
        user = db.query(models.User).filter(models.User.nik == father_nik).first()
        
        if not user and father_email:
            user = db.query(models.User).filter(models.User.email == father_email).first()
    
    if not user and father_nik:
        # Find orangtua role
        role = db.query(models.Role).filter(models.Role.code == "orangtua").first()
        if not role:
            role = db.query(models.Role).filter(models.Role.name.ilike("%wali%")).first()
        if not role:
            role = db.query(models.Role).filter(models.Role.name.ilike("%orang%")).first()
        
        raw_password = father_phone if father_phone else "AsySyuuraa2026"
        hashed_password = auth.get_password_hash(raw_password)
        
        user = models.User(
            email=father_email or None,
            nik=father_nik,
            password_hash=hashed_password,
            full_name=father_data.get("name", "Orang Tua / Wali"),
            role_id=role.id if role else None,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if user:
        parent_user_id = user.id
    
    # --- Check for existing draft by this parent ---
    existing = None
    if parent_user_id:
        existing = db.query(models.PPDBRegistration).filter(
            models.PPDBRegistration.parent_user_id == parent_user_id,
            models.PPDBRegistration.status == "DRAFT"
        ).first()
    
    student_name = student_data.get("full_name", "")
    nisn = student_data.get("nisn", "")
    gender = student_data.get("gender", "L")
    
    if existing:
        # Update existing draft
        existing.unit = unit
        existing.student_name = student_name
        existing.nisn = nisn
        existing.gender = gender
        existing.phone = father_phone
        existing.email = father_email
        existing.student_data = json.dumps(student_data)
        existing.father_data = json.dumps(father_data)
        existing.last_completed_step = 3
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        
        return {
            "message": "Draft berhasil diperbarui",
            "registration_number": existing.registration_number,
            "registration_id": existing.id,
            "login_info": {
                "username": father_nik,
                "password": father_phone
            }
        }
    
    # --- Create new registration ---
    reg_number = f"PPDB-{datetime.utcnow().year}-{str(uuid.uuid4())[:6].upper()}"
    
    new_registration = models.PPDBRegistration(
        registration_number=reg_number,
        unit=unit,
        student_name=student_name,
        nisn=nisn,
        gender=gender,
        phone=father_phone,
        email=father_email,
        student_data=json.dumps(student_data),
        father_data=json.dumps(father_data),
        mother_data=None,
        guardian_data=None,
        periodic_data=None,
        achievements_data=None,
        other_data=None,
        status="DRAFT",
        last_completed_step=3,
        parent_user_id=parent_user_id,
    )
    
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    
    return {
        "message": "Draft berhasil disimpan",
        "registration_number": reg_number,
        "registration_id": new_registration.id,
        "login_info": {
            "username": father_nik,
            "password": father_phone
        }
    }


# --- Endpoint 2: Update Registration (Step 4-8, requires auth) ---
@router.put("/register/{reg_id}")
async def update_registration(
    reg_id: int,
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update registration with data from subsequent steps (4-8)."""
    reg = db.query(models.PPDBRegistration).filter(
        models.PPDBRegistration.id == reg_id
    ).first()
    
    if not reg:
        raise HTTPException(status_code=404, detail="Pendaftaran tidak ditemukan")
    
    # Only the parent owner or admin can update
    current_role = current_user.role.code if current_user.role else ""
    if reg.parent_user_id != current_user.id and current_role not in ("superadmin", "admin"):
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses untuk mengubah pendaftaran ini")
    
    step = data.get("step", 0)
    
    if step == 4:
        mother_data = data.get("mother_data", {})
        validate_required(mother_data.get("name"), "Nama Ibu")
        validate_nik(mother_data.get("nik", ""), "NIK Ibu")
        reg.mother_data = json.dumps(mother_data)
        reg.last_completed_step = max(reg.last_completed_step or 0, 4)
        
    elif step == 5:
        guardian_data = data.get("guardian_data", {})
        reg.guardian_data = json.dumps(guardian_data)
        reg.last_completed_step = max(reg.last_completed_step or 0, 5)
        
    elif step == 6:
        periodic_data = data.get("periodic_data", {})
        reg.periodic_data = json.dumps(periodic_data)
        reg.last_completed_step = max(reg.last_completed_step or 0, 6)
        
    elif step == 7:
        achievements_data = data.get("achievements_data", [])
        other_data = data.get("other_data", {})
        reg.achievements_data = json.dumps(achievements_data)
        reg.other_data = json.dumps(other_data)
        reg.last_completed_step = max(reg.last_completed_step or 0, 7)
        
    elif step == 8:
        # Final submit — update files and change status
        if data.get("file_kk_url"):
            reg.file_kk_url = data["file_kk_url"]
        if data.get("file_akta_url"):
            reg.file_akta_url = data["file_akta_url"]
        if data.get("file_foto_url"):
            reg.file_foto_url = data["file_foto_url"]
        
        reg.last_completed_step = 8
        reg.status = "PENDING"
        
    else:
        raise HTTPException(status_code=400, detail=f"Step {step} tidak valid. Gunakan step 4-8.")
    
    reg.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(reg)
    
    return {
        "message": "Data berhasil diperbarui",
        "status": reg.status,
        "last_completed_step": reg.last_completed_step
    }


# --- Endpoint 3: Get My Registrations (requires auth) ---
@router.get("/register/my")
async def get_my_registrations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's PPDB registration(s)."""
    registrations = db.query(models.PPDBRegistration).filter(
        models.PPDBRegistration.parent_user_id == current_user.id
    ).order_by(models.PPDBRegistration.created_at.desc()).all()
    
    return [_serialize_registration(reg) for reg in registrations]


# --- Endpoint 4: Admin — Get All Registrations ---
@router.get("/registrations")
async def get_all_registrations(db: Session = Depends(get_db)):
    """Admin endpoint to get all registrations."""
    registrations = db.query(models.PPDBRegistration).order_by(
        models.PPDBRegistration.created_at.desc()
    ).all()
    
    return [_serialize_registration(reg) for reg in registrations]


# --- Endpoint 5: Admin — Delete Registration ---
@router.delete("/registrations/{id}")
async def delete_registration(id: int, db: Session = Depends(get_db)):
    """Admin endpoint to delete a registration."""
    reg = db.query(models.PPDBRegistration).filter(models.PPDBRegistration.id == id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    db.delete(reg)
    db.commit()
    return {"message": "Deleted successfully"}


# --- Legacy Endpoint: Full Registration (backward compat) ---
@router.post("/register")
async def register_ppdb(data: dict, db: Session = Depends(get_db)):
    """Public endpoint to submit full PPDB Registration form (legacy / complete in one shot)."""
    reg_number = f"PPDB-{datetime.utcnow().year}-{str(uuid.uuid4())[:6].upper()}"
    
    student_data = data.get("student_data", {})
    student_name = student_data.get("full_name", "") or data.get("child_name", "")
    nisn = student_data.get("nisn", "")
    gender = student_data.get("gender", "L")
    
    father_data = data.get("father_data", {})
    father_phone = father_data.get("phone", "")
    father_nik = father_data.get("nik", "")
    father_email = father_data.get("email", data.get("email", ""))
    
    unit = data.get("unit", "SDIT")
    
    parent_user_id = None
    if father_nik or father_email:
        user = db.query(models.User).filter(
            (models.User.nik == father_nik) | 
            (models.User.email == father_email)
        ).first()
        
        if not user and father_nik:
            role = db.query(models.Role).filter(models.Role.code == "orangtua").first()
            if not role:
                role = db.query(models.Role).filter(models.Role.name.ilike("%wali%")).first()
            if not role:
                role = db.query(models.Role).first()
                
            raw_password = father_phone if father_phone else "AsySyuuraa2026"
            hashed_password = auth.get_password_hash(raw_password)
            
            user = models.User(
                email=father_email,
                nik=father_nik,
                password_hash=hashed_password,
                full_name=father_data.get("name", "Orang Tua / Wali"),
                role_id=role.id if role else None,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        if user:
            parent_user_id = user.id
    
    new_registration = models.PPDBRegistration(
        registration_number=reg_number,
        unit=unit,
        student_name=student_name,
        nisn=nisn,
        gender=gender,
        phone=father_phone,
        email=father_email,
        student_data=json.dumps(data.get("student_data", {})),
        father_data=json.dumps(data.get("father_data", {})),
        mother_data=json.dumps(data.get("mother_data", {})),
        guardian_data=json.dumps(data.get("guardian_data", {})),
        periodic_data=json.dumps(data.get("periodic_data", {})),
        achievements_data=json.dumps(data.get("achievements_data", [])),
        other_data=json.dumps(data.get("other_data", {})),
        status="PENDING",
        last_completed_step=8,
        parent_user_id=parent_user_id,
        file_kk_url=data.get("file_kk_url"),
        file_akta_url=data.get("file_akta_url"),
        file_foto_url=data.get("file_foto_url"),
    )
    
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    
    return {"message": "Registration successful", "registration_number": reg_number}
