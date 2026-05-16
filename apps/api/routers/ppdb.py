from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
import json
import uuid
from datetime import datetime

router = APIRouter(prefix="/ppdb", tags=["PPDB"])

@router.post("/register")
async def register_ppdb(data: dict, db: Session = Depends(get_db)):
    """Public endpoint to submit PPDB Registration form"""
    # Generate a unique registration number
    # Format: PPDB-2026-XXXX
    reg_number = f"PPDB-{datetime.utcnow().year}-{str(uuid.uuid4())[:6].upper()}"
    
    # Extract indexable fields from the raw payload
    student_name = data.get("student_data", {}).get("full_name", "")
    if not student_name:
        # fallback
        student_name = data.get("child_name", "")
        
    nisn = data.get("student_data", {}).get("nisn", "")
    gender = data.get("student_data", {}).get("gender", "L")
    
    father_data = data.get("father_data", {})
    father_phone = father_data.get("phone", "")
    father_nik = father_data.get("nik", "")
    father_email = father_data.get("email", data.get("email", ""))
    
    unit = data.get("unit", "SDIT")
    
    parent_user_id = None
    if father_nik or father_email:
        # Check by NIK first, then Email
        user = db.query(models.User).filter(
            (models.User.nik == father_nik) | 
            (models.User.email == father_email)
        ).first()
        
        if not user and father_nik:
            role = db.query(models.Role).filter(models.Role.name.ilike("%wali%")).first()
            if not role:
                role = db.query(models.Role).first() # Fallback
                
            raw_password = father_phone if father_phone else "AsySyuuraa2026"
            hashed_password = auth.get_password_hash(raw_password)
            
            user = models.User(
                email=father_email,
                nik=father_nik, # NIK Ayah as primary identifier
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
        parent_user_id=parent_user_id
    )
    
    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    
    return {"message": "Registration successful", "registration_number": reg_number}

@router.get("/registrations")
async def get_all_registrations(db: Session = Depends(get_db)):
    """Admin endpoint to get all registrations"""
    
    registrations = db.query(models.PPDBRegistration).order_by(models.PPDBRegistration.created_at.desc()).all()
    
    # Return parsed json data for the admin table
    result = []
    for reg in registrations:
        result.append({
            "id": reg.id,
            "registration_number": reg.registration_number,
            "unit": reg.unit,
            "student_name": reg.student_name,
            "nisn": reg.nisn,
            "gender": reg.gender,
            "phone": reg.phone,
            "email": reg.email,
            "status": reg.status,
            "created_at": reg.created_at,
            "student_data": json.loads(reg.student_data) if reg.student_data else {},
            "father_data": json.loads(reg.father_data) if reg.father_data else {},
            "mother_data": json.loads(reg.mother_data) if reg.mother_data else {},
            "periodic_data": json.loads(reg.periodic_data) if reg.periodic_data else {},
            "achievements_data": json.loads(reg.achievements_data) if reg.achievements_data else [],
        })
        
    return result

@router.delete("/registrations/{id}")
async def delete_registration(id: int, db: Session = Depends(get_db)):
    """Admin endpoint to delete a registration"""
    reg = db.query(models.PPDBRegistration).filter(models.PPDBRegistration.id == id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    db.delete(reg)
    db.commit()
    return {"message": "Deleted successfully"}
