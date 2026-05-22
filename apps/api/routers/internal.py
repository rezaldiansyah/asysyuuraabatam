from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models
from datetime import datetime
from typing import Optional
from deps import get_current_user

router = APIRouter(prefix="/internal", tags=["Internal Management"])

# ============================================================
# DOCUMENT CENTER (Pusat Unduhan)
# ============================================================

DOCUMENT_CATEGORIES = [
    {"value": "sk_yayasan", "label": "SK Yayasan"},
    {"value": "sop", "label": "SOP"},
    {"value": "kalender_akademik", "label": "Kalender Akademik"},
    {"value": "juknis", "label": "Juknis"},
    {"value": "surat_edaran", "label": "Surat Edaran"},
    {"value": "lainnya", "label": "Lainnya"},
]

@router.get("/documents/categories")
async def get_document_categories():
    """Get available document categories."""
    return DOCUMENT_CATEGORIES

@router.get("/documents")
async def get_documents(
    category: Optional[str] = None,
    visibility: Optional[str] = None,
    search: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents (authenticated users only)."""
    query = db.query(models.Document).filter(models.Document.is_active == True)
    
    if category:
        query = query.filter(models.Document.category == category)
    if visibility:
        query = query.filter(models.Document.visibility == visibility)
    if search:
        query = query.filter(models.Document.title.ilike(f"%{search}%"))
    
    docs = query.options(joinedload(models.Document.uploader)).order_by(models.Document.created_at.desc()).all()
    
    result = []
    for doc in docs:
        result.append({
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "category": doc.category,
            "file_url": doc.file_url,
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "visibility": doc.visibility,
            "uploaded_by": doc.uploaded_by,
            "uploader_name": doc.uploader.full_name if doc.uploader else None,
            "is_active": doc.is_active,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
        })
    
    return result

@router.post("/documents")
async def create_document(
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document entry."""
    doc = models.Document(
        title=data.get("title"),
        description=data.get("description"),
        category=data.get("category", "lainnya"),
        file_url=data.get("file_url"),
        file_name=data.get("file_name"),
        file_size=data.get("file_size"),
        visibility=data.get("visibility", "internal"),
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "message": "Document created successfully"}

@router.put("/documents/{doc_id}")
async def update_document(
    doc_id: int,
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a document entry."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    for field in ["title", "description", "category", "file_url", "file_name", "file_size", "visibility"]:
        if field in data:
            setattr(doc, field, data[field])
    
    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "message": "Document updated successfully"}

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft-delete a document."""
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc.is_active = False
    db.commit()
    return {"message": "Document deleted successfully"}


# ============================================================
# MUTABA'AH HARIAN & PEKANAN (SDM)
# ============================================================
import json
from datetime import timedelta, time

TU_ROLES = ["superadmin", "tu_yayasan", "tu_unit", "kabid_umum"]

def get_start_of_day(dt: datetime) -> datetime:
    return datetime.combine(dt.date(), time.min)

def get_monday_of_week(dt: datetime) -> datetime:
    monday = dt - timedelta(days=dt.weekday())
    return datetime.combine(monday.date(), time.min)

@router.get("/mutabaah/daily")
async def get_daily_mutabaah(
    user_id: Optional[int] = None,
    start_date: Optional[str] = None, # YYYY-MM-DD
    end_date: Optional[str] = None,   # YYYY-MM-DD
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve daily mutabaah records for a user within a date range."""
    target_user_id = user_id if user_id is not None else current_user.id
    
    # Permission check: If current user is accessing someone else's record, verify they are admin/TU/kepsek
    if target_user_id != current_user.id:
        current_role = current_user.role.code if current_user.role else ""
        if current_role not in TU_ROLES and current_role != "kepala_unit":
            raise HTTPException(status_code=403, detail="Unauthorized to view other users' mutabaah")
            
    query = db.query(models.DailyMutabaah).filter(models.DailyMutabaah.user_id == target_user_id)
    
    if start_date:
        s_date = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(models.DailyMutabaah.date >= get_start_of_day(s_date))
    if end_date:
        e_date = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(models.DailyMutabaah.date <= get_start_of_day(e_date))
        
    records = query.order_by(models.DailyMutabaah.date.asc()).all()
    
    result = []
    for rec in records:
        result.append({
            "id": rec.id,
            "user_id": rec.user_id,
            "date": rec.date.strftime("%Y-%m-%d"),
            "ibadah_data": json.loads(rec.ibadah_data) if rec.ibadah_data else {},
            "tilawah_pages": rec.tilawah_pages,
            "notes": rec.notes,
            "created_by": rec.created_by,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
        })
    return result

@router.post("/mutabaah/daily")
async def save_daily_mutabaah(
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save or update daily mutabaah record (upsert)."""
    target_user_id = data.get("user_id")
    if not target_user_id:
        raise HTTPException(status_code=420, detail="Missing user_id")
        
    req_date_str = data.get("date")
    if not req_date_str:
        raise HTTPException(status_code=420, detail="Missing date")
        
    req_date = datetime.strptime(req_date_str, "%Y-%m-%d")
    req_date_normalized = get_start_of_day(req_date)
    
    # Calculate limits based on local time
    today = get_start_of_day(datetime.now())
    days_difference = (today - req_date_normalized).days
    
    # Validate future date
    if days_difference < 0:
        raise HTTPException(status_code=400, detail="Tidak boleh mengisi mutabaah untuk hari esok")
        
    current_role = current_user.role.code if current_user.role else ""
    
    # Fetch target user's role to distinguish guru vs karyawan
    target_user = db.query(models.User).filter(models.User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    target_role = target_user.role.code if target_user.role else ""
    
    # Logic validations
    if target_user_id != current_user.id:
        # Filling on behalf of
        if current_role not in TU_ROLES:
            raise HTTPException(status_code=403, detail="Hanya TU / Admin yang boleh mengisi atas nama staf lain")
        if target_role == "guru":
            raise HTTPException(status_code=403, detail="TU tidak diperkenankan mengisi mutabaah untuk Guru")
        # Validate 20 days backdate for karyawan
        if days_difference > 20:
            raise HTTPException(status_code=400, detail="Batas pengisian untuk Karyawan adalah 20 hari ke belakang")
    else:
        # Filling own
        if current_role == "guru":
            if days_difference > 7:
                raise HTTPException(status_code=400, detail="Batas pengisian mandiri untuk Guru adalah 7 hari ke belakang")
        elif current_role == "karyawan":
            if days_difference > 20:
                raise HTTPException(status_code=400, detail="Batas pengisian mandiri untuk Karyawan adalah 20 hari ke belakang")
        else:
            # Other roles (admin, kepsek, etc.) default to 20 days backdate
            if days_difference > 20:
                raise HTTPException(status_code=400, detail="Batas pengisian adalah 20 hari ke belakang")

    # Perform Upsert
    record = db.query(models.DailyMutabaah).filter(
        models.DailyMutabaah.user_id == target_user_id,
        models.DailyMutabaah.date == req_date_normalized
    ).first()
    
    ibadah_json = json.dumps(data.get("ibadah_data", {}))
    tilawah_pages = int(data.get("tilawah_pages", 0))
    notes = data.get("notes")
    
    if record:
        record.ibadah_data = ibadah_json
        record.tilawah_pages = tilawah_pages
        record.notes = notes
        record.created_by = current_user.id
        record.updated_at = datetime.utcnow()
    else:
        record = models.DailyMutabaah(
            user_id=target_user_id,
            date=req_date_normalized,
            ibadah_data=ibadah_json,
            tilawah_pages=tilawah_pages,
            notes=notes,
            created_by=current_user.id
        )
        db.add(record)
        
    db.commit()
    db.refresh(record)
    return {"id": record.id, "message": "Mutabaah harian berhasil disimpan"}

@router.get("/mutabaah/weekly")
async def get_weekly_mutabaah(
    user_id: Optional[int] = None,
    start_date: Optional[str] = None, # YYYY-MM-DD (Monday of the week)
    end_date: Optional[str] = None,   # YYYY-MM-DD
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve weekly mutabaah records for a user."""
    target_user_id = user_id if user_id is not None else current_user.id
    
    if target_user_id != current_user.id:
        current_role = current_user.role.code if current_user.role else ""
        if current_role not in TU_ROLES and current_role != "kepala_unit":
            raise HTTPException(status_code=403, detail="Unauthorized to view other users' weekly mutabaah")
            
    query = db.query(models.WeeklyMutabaah).filter(models.WeeklyMutabaah.user_id == target_user_id)
    
    if start_date:
        s_date = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(models.WeeklyMutabaah.week_start_date >= get_monday_of_week(s_date))
    if end_date:
        e_date = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(models.WeeklyMutabaah.week_start_date <= get_monday_of_week(e_date))
        
    records = query.order_by(models.WeeklyMutabaah.week_start_date.asc()).all()
    
    result = []
    for rec in records:
        result.append({
            "id": rec.id,
            "user_id": rec.user_id,
            "week_start_date": rec.week_start_date.strftime("%Y-%m-%d"),
            "pekanan_data": json.loads(rec.pekanan_data) if rec.pekanan_data else {},
            "created_by": rec.created_by,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
            "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
        })
    return result

@router.post("/mutabaah/weekly")
async def save_weekly_mutabaah(
    data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save or update weekly mutabaah record (upsert)."""
    target_user_id = data.get("user_id")
    if not target_user_id:
        raise HTTPException(status_code=420, detail="Missing user_id")
        
    req_date_str = data.get("week_start_date")
    if not req_date_str:
        raise HTTPException(status_code=420, detail="Missing week_start_date")
        
    req_date = datetime.strptime(req_date_str, "%Y-%m-%d")
    req_date_normalized = get_monday_of_week(req_date)
    
    today = get_start_of_day(datetime.now())
    days_difference = (today - req_date_normalized).days
    
    if days_difference < -6: # Can fill current week, but not future weeks
        raise HTTPException(status_code=400, detail="Tidak boleh mengisi mutabaah untuk pekan depan")
        
    current_role = current_user.role.code if current_user.role else ""
    
    target_user = db.query(models.User).filter(models.User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    target_role = target_user.role.code if target_user.role else ""
    
    # Weekly backdating checks (Guru 14 days, Karyawan 28 days)
    if target_user_id != current_user.id:
        if current_role not in TU_ROLES:
            raise HTTPException(status_code=403, detail="Hanya TU / Admin yang boleh mengisi atas nama staf lain")
        if target_role == "guru":
            raise HTTPException(status_code=403, detail="TU tidak diperkenankan mengisi mutabaah untuk Guru")
        if days_difference > 28:
            raise HTTPException(status_code=400, detail="Batas pengisian pekanan untuk Karyawan adalah 28 hari ke belakang")
    else:
        if current_role == "guru":
            if days_difference > 14:
                raise HTTPException(status_code=400, detail="Batas pengisian pekanan mandiri untuk Guru adalah 14 hari ke belakang")
        elif current_role == "karyawan":
            if days_difference > 28:
                raise HTTPException(status_code=400, detail="Batas pengisian pekanan mandiri untuk Karyawan adalah 28 hari ke belakang")
        else:
            if days_difference > 28:
                raise HTTPException(status_code=400, detail="Batas pengisian pekanan adalah 28 hari ke belakang")

    # Perform Upsert
    record = db.query(models.WeeklyMutabaah).filter(
        models.WeeklyMutabaah.user_id == target_user_id,
        models.WeeklyMutabaah.week_start_date == req_date_normalized
    ).first()
    
    pekanan_json = json.dumps(data.get("pekanan_data", {}))
    
    if record:
        record.pekanan_data = pekanan_json
        record.created_by = current_user.id
        record.updated_at = datetime.utcnow()
    else:
        record = models.WeeklyMutabaah(
            user_id=target_user_id,
            week_start_date=req_date_normalized,
            pekanan_data=pekanan_json,
            created_by=current_user.id
        )
        db.add(record)
        
    db.commit()
    db.refresh(record)
    return {"id": record.id, "message": "Mutabaah pekanan berhasil disimpan"}


@router.get("/mutabaah/rekap")
async def get_mutabaah_rekap(
    start_date: str, # YYYY-MM-DD
    end_date: str,   # YYYY-MM-DD
    unit_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve summary report of daily & weekly mutabaah for all employees."""
    current_role = current_user.role.code if current_user.role else ""
    if current_role not in TU_ROLES and current_role != "kepala_unit":
        raise HTTPException(status_code=403, detail="Unauthorized to view mutabaah reports")
        
    s_date = get_start_of_day(datetime.strptime(start_date, "%Y-%m-%d"))
    e_date = get_start_of_day(datetime.strptime(end_date, "%Y-%m-%d"))
    
    # Calculate days in the range
    total_days = (e_date - s_date).days + 1
    if total_days <= 0:
        raise HTTPException(status_code=400, detail="Invalid date range")

    # Fetch employees
    emp_query = db.query(models.Employee).join(models.User).options(
        joinedload(models.Employee.user).joinedload(models.User.unit_assignments).joinedload(models.UserUnit.unit),
        joinedload(models.Employee.user).joinedload(models.User.role)
    )
    if unit_id:
        emp_query = emp_query.join(models.UserUnit, models.UserUnit.user_id == models.Employee.user_id).filter(models.UserUnit.unit_id == unit_id)
        
    employees = emp_query.all()
    
    rekap_results = []
    for emp in employees:
        if not emp.user:
            continue
            
        # Get Daily Records in range
        daily_recs = db.query(models.DailyMutabaah).filter(
            models.DailyMutabaah.user_id == emp.user_id,
            models.DailyMutabaah.date >= s_date,
            models.DailyMutabaah.date <= e_date
        ).all()
        
        days_filled = len(daily_recs)
        
        # Calculate Tilawah pages average
        total_tilawah = sum(r.tilawah_pages for r in daily_recs)
        avg_tilawah = round(total_tilawah / days_filled, 1) if days_filled > 0 else 0
        
        # Calculate Daily checklist completion percentage
        daily_checked = 0
        daily_fields = 0
        for rec in daily_recs:
            if rec.ibadah_data:
                try:
                    data = json.loads(rec.ibadah_data)
                    for k, v in data.items():
                        if k != "is_haid" and isinstance(v, bool):
                            daily_fields += 1
                            if v:
                                daily_checked += 1
                except Exception:
                    pass
        daily_pct = round((daily_checked / daily_fields * 100), 1) if daily_fields > 0 else 0
        
        # Get Weekly Records in range
        weekly_recs = db.query(models.WeeklyMutabaah).filter(
            models.WeeklyMutabaah.user_id == emp.user_id,
            models.WeeklyMutabaah.week_start_date >= s_date,
            models.WeeklyMutabaah.week_start_date <= e_date
        ).all()
        
        # Calculate Weekly checklist completion percentage
        weekly_checked = 0
        weekly_fields = 0
        for rec in weekly_recs:
            if rec.pekanan_data:
                try:
                    data = json.loads(rec.pekanan_data)
                    for k, v in data.items():
                        if isinstance(v, bool):
                            weekly_fields += 1
                            if v:
                                weekly_checked += 1
                except Exception:
                    pass
        weekly_pct = round((weekly_checked / weekly_fields * 100), 1) if weekly_fields > 0 else 0
        
        # Calculate overall score index (simply average daily & weekly % as a basic formula)
        # Note: In future, this can be customized with Tarbiyah grading rubrics
        overall_score = round((daily_pct + weekly_pct) / 2, 1)
        
        rekap_results.append({
            "employee_id": emp.id,
            "user_id": emp.user_id,
            "name": emp.user.full_name if emp.user else "Pegawai",
            "nip": emp.nip or (emp.user.nik if emp.user else "") or "-",
            "role_name": emp.user.role.name if emp.user and emp.user.role else "Pegawai",
            "unit_name": (
                emp.user.unit_assignments[0].unit.name
                if emp.user and emp.user.unit_assignments and emp.user.unit_assignments[0].unit
                else "-"
            ),
            "days_filled": days_filled,
            "total_days": total_days,
            "avg_tilawah": avg_tilawah,
            "daily_percentage": daily_pct,
            "weekly_percentage": weekly_pct,
            "overall_score": overall_score
        })
        
    return rekap_results


