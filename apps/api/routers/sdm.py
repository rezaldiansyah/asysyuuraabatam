from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
import passlib.hash

import models, schemas
from database import get_db

router = APIRouter(prefix="/sdm", tags=["sdm"])

# Computed fields schema
class EmployeeComputed(BaseModel):
    tahun_pensiun: Optional[date]
    masa_kerja: str
    lama_kerja_pensiun: str

@router.get("/employees", response_model=List[schemas.Employee])
async def get_employees(
    unit_id: Optional[int] = None,
    employee_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Employee).options(
        joinedload(models.Employee.user),
        joinedload(models.Employee.unit),
        joinedload(models.Employee.education_history),
        joinedload(models.Employee.position_history)
    )
    
    if unit_id:
        query = query.filter(models.Employee.unit_id == unit_id)
    if employee_type:
        query = query.filter(models.Employee.employee_type == employee_type)
    if is_active is not None:
        query = query.filter(models.Employee.is_active == is_active)
    if search:
        query = query.filter(
            or_(
                models.Employee.nama_lengkap.ilike(f"%{search}%"),
                models.Employee.nik_kepegawaian.ilike(f"%{search}%")
            )
        )
        
    return query.all()

@router.get("/employees/{employee_id}", response_model=schemas.Employee)
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).options(
        joinedload(models.Employee.user),
        joinedload(models.Employee.unit),
        joinedload(models.Employee.education_history),
        joinedload(models.Employee.position_history)
    ).filter(models.Employee.id == employee_id).first()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.post("/employees")
async def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Check NIK KTP
    if employee.no_ktp:
        existing_ktp = db.query(models.Employee).filter(models.Employee.no_ktp == employee.no_ktp).first()
        if existing_ktp:
            raise HTTPException(status_code=400, detail="KTP already exists")
    
    # Check NIK Kepegawaian
    if employee.nik_kepegawaian:
        existing_nik = db.query(models.Employee).filter(models.Employee.nik_kepegawaian == employee.nik_kepegawaian).first()
        if existing_nik:
            raise HTTPException(status_code=400, detail="NIK Kepegawaian already exists")
            
    # Step 1: Handle User Account
    user = db.query(models.User).filter(models.User.nik == employee.nik_kepegawaian).first()
    
    generated_password = None
    if not user:
        if employee.tanggal_lahir:
            # Format password DDMMYYYY
            generated_password = employee.tanggal_lahir.strftime("%d%m%Y")
        else:
            generated_password = "password123" # Fallback
            
        hashed_password = passlib.hash.bcrypt.hash(generated_password)
        
        # Determine Role
        role_id = 3 # Default to Karyawan (assuming ID 3)
        if employee.position and "guru" in employee.position.lower():
            role_id = 2 # Guru (assuming ID 2)
            
        user = models.User(
            nik=employee.nik_kepegawaian,
            full_name=employee.nama_lengkap,
            password_hash=hashed_password,
            must_change_password=True,
            role_id=role_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Step 2: Create Employee
    employee_dict = employee.dict()
    db_emp = models.Employee(**employee_dict, user_id=user.id)
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    
    response = {
        "employee": db_emp,
        "message": "Employee created successfully"
    }
    
    if generated_password:
        response["login_info"] = {
            "username": user.nik,
            "password": generated_password
        }
        
    return response

@router.put("/employees/{employee_id}", response_model=schemas.Employee)
async def update_employee(employee_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    for key, value in employee.dict(exclude_unset=True).items():
        setattr(db_emp, key, value)
    
    db.commit()
    db.refresh(db_emp)
    return db_emp

@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db_emp.is_active = False
    db.commit()
    return {"message": "Employee deactivated"}

@router.get("/employees/{employee_id}/computed", response_model=EmployeeComputed)
async def get_employee_computed(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).options(joinedload(models.Employee.position_history)).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    today = date.today()
    
    # Tahun pensiun
    pensiun = None
    if emp.tanggal_lahir:
        pensiun = emp.tanggal_lahir.date() + relativedelta(years=55)
        
    # Masa kerja
    masa_kerja = "-"
    lama_pensiun = "-"
    
    first_tmt = None
    if emp.join_date:
        first_tmt = emp.join_date.date()
    elif emp.position_history:
        # Get earliest tmt_mulai
        earliest_pos = min(emp.position_history, key=lambda p: p.tmt_mulai)
        first_tmt = earliest_pos.tmt_mulai.date()
        
    if first_tmt:
        delta = relativedelta(today, first_tmt)
        masa_kerja = f"{delta.years} tahun {delta.months} bulan {delta.days} hari"
        
        if pensiun:
            delta_pensiun = relativedelta(pensiun, first_tmt)
            lama_pensiun = f"{delta_pensiun.years} tahun {delta_pensiun.months} bulan"
            
    return {
        "tahun_pensiun": pensiun,
        "masa_kerja": masa_kerja,
        "lama_kerja_pensiun": lama_pensiun
    }

# --- Education & Position History Routes ---
@router.post("/employees/{employee_id}/education", response_model=schemas.EducationHistory)
async def add_education(employee_id: int, edu: schemas.EducationHistoryCreate, db: Session = Depends(get_db)):
    db_edu = models.EducationHistory(**edu.dict(), employee_id=employee_id)
    db.add(db_edu)
    db.commit()
    db.refresh(db_edu)
    return db_edu

@router.delete("/education/{id}")
async def delete_education(id: int, db: Session = Depends(get_db)):
    db_edu = db.query(models.EducationHistory).filter(models.EducationHistory.id == id).first()
    if not db_edu:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_edu)
    db.commit()
    return {"ok": True}

@router.post("/employees/{employee_id}/positions", response_model=schemas.PositionHistory)
async def add_position(employee_id: int, pos: schemas.PositionHistoryCreate, db: Session = Depends(get_db)):
    db_pos = models.PositionHistory(**pos.dict(), employee_id=employee_id)
    db.add(db_pos)
    db.commit()
    db.refresh(db_pos)
    return db_pos

@router.delete("/positions/{id}")
async def delete_position(id: int, db: Session = Depends(get_db)):
    db_pos = db.query(models.PositionHistory).filter(models.PositionHistory.id == id).first()
    if not db_pos:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_pos)
    db.commit()
    return {"ok": True}

# --- Employee Attendance Routes ---

@router.get("/attendance", response_model=List[schemas.EmployeeAttendance])
async def get_employee_attendances(
    date: Optional[str] = None,
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.EmployeeAttendance).options(joinedload(models.EmployeeAttendance.employee))
    
    if date:
        from datetime import datetime as dt
        target_date = dt.strptime(date, "%Y-%m-%d").date()
        query = query.filter(models.EmployeeAttendance.date == target_date)
        
    if unit_id:
        query = query.join(models.Employee).filter(models.Employee.unit_id == unit_id)
    
    return query.order_by(models.EmployeeAttendance.date.desc()).all()

@router.post("/attendance", response_model=schemas.EmployeeAttendance)
async def create_employee_attendance(attendance: schemas.EmployeeAttendanceCreate, db: Session = Depends(get_db)):
    existing = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.employee_id == attendance.employee_id,
        models.EmployeeAttendance.date == attendance.date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded for this employee on this date")
    
    db_att = models.EmployeeAttendance(**attendance.dict())
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return db_att

@router.post("/attendance/bulk")
async def create_bulk_employee_attendance(request: schemas.BulkEmployeeAttendanceCreate, db: Session = Depends(get_db)):
    count = 0
    updated = 0
    
    for item in request.items:
        existing = db.query(models.EmployeeAttendance).filter(
            models.EmployeeAttendance.employee_id == item.employee_id,
            models.EmployeeAttendance.date == request.date
        ).first()
        
        if existing:
            # Update existing
            existing.status = item.status.value
            existing.check_in = item.check_in
            existing.check_out = item.check_out
            existing.notes = item.notes
            updated += 1
        else:
            # Create new
            db_att = models.EmployeeAttendance(
                employee_id=item.employee_id,
                date=request.date,
                status=item.status.value,
                check_in=item.check_in,
                check_out=item.check_out,
                notes=item.notes
            )
            db.add(db_att)
            count += 1
            
    db.commit()
    return {"message": f"Created {count} new attendance records, updated {updated} existing ones"}

@router.get("/attendance/recap")
async def get_employee_attendance_recap(
    month: str, # Format YYYY-MM
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from datetime import datetime as dt
    import calendar
    from sqlalchemy import func
    
    try:
        target_month = dt.strptime(month, "%Y-%m")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid month format, use YYYY-MM")
        
    start_date = target_month.date()
    _, last_day = calendar.monthrange(start_date.year, start_date.month)
    end_date = start_date.replace(day=last_day)
    
    # Get all employees
    emp_query = db.query(models.Employee).filter(models.Employee.is_active == True)
    if unit_id:
        emp_query = emp_query.filter(models.Employee.unit_id == unit_id)
        
    employees = emp_query.all()
    
    # Get all attendance records for the month
    att_query = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.date >= start_date,
        models.EmployeeAttendance.date <= end_date
    )
    if unit_id:
        att_query = att_query.join(models.Employee).filter(models.Employee.unit_id == unit_id)
        
    attendances = att_query.all()
    
    # Group by employee
    results = []
    for emp in employees:
        emp_att = [a for a in attendances if a.employee_id == emp.id]
        
        h = sum(1 for a in emp_att if a.status == 'PRESENT')
        s = sum(1 for a in emp_att if a.status == 'SICK')
        i = sum(1 for a in emp_att if a.status == 'PERMIT')
        a = sum(1 for a in emp_att if a.status == 'ABSENT')
        total = h + s + i + a
        
        results.append({
            "employee_id": emp.id,
            "nama_lengkap": emp.nama_lengkap,
            "nip": emp.nip,
            "hadir": h,
            "sakit": s,
            "izin": i,
            "alpa": a,
            "total": total,
            "persentase": f"{(h/total*100):.1f}%" if total > 0 else "0.0%"
        })
        
    return results
