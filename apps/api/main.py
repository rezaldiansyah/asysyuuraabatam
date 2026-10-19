
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import models, schemas, auth
from database import engine, get_db
from jose import JWTError, jwt
import os
import shutil
import uuid
import json
from routers import ppdb
from routers import marketing

# Create Upload Directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Asy-Syuuraa Batam API",
    description="Backend API untuk Sistem Informasi Sekolah Asy-Syuuraa Batam",
    version="1.0.0"
)

# CORS Configuration
default_origins = [
    "https://asy-syuuraabatam.or.id",
    "https://www.asy-syuuraabatam.or.id",
    "http://asy-syuuraabatam.or.id",
    "http://www.asy-syuuraabatam.or.id",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env and allowed_origins_env != "*":
    env_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    origins = list(dict.fromkeys(default_origins + env_origins))
else:
    origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://([a-zA-Z0-9-]+\.)*asy-syuuraabatam\.or\.id(:\d+)?$|^https?://localhost(:\d+)?$|^https?://127\.0\.0\.1(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    origin = request.headers.get("origin") or "https://asy-syuuraabatam.or.id"
    return JSONResponse(
        status_code=500,
        content={"detail": f"Terjadi kesalahan di server: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Mount Uploads Directory
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(ppdb.router)
app.include_router(marketing.router)

from routers import internal, sdm, schedule_import, meeting, tasks
app.include_router(internal.router)
app.include_router(sdm.router)
app.include_router(schedule_import.router)
app.include_router(meeting.router)
app.include_router(tasks.router)

@app.on_event("startup")
def run_migrations_on_startup():
    # 1. Run direct DDL self-healing for new columns on existing tables
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS recipient_type VARCHAR DEFAULT 'individual'"))
            # Self-healing for PostgreSQL enum types if native enum was created
            try:
                conn.execute(text("ALTER TYPE calendareventtype ADD VALUE IF NOT EXISTS 'PHBI'"))
                conn.execute(text("ALTER TYPE calendareventtype ADD VALUE IF NOT EXISTS 'PHBN'"))
            except Exception:
                pass
            conn.commit()
            print("[Startup] Verified column documents.recipient_type and calendar enums exist.")
    except Exception as e:
        print(f"[Startup] DDL recipient_type note: {e}")

    # 2. Run Alembic auto-migration
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("[Startup] Alembic auto-migration executed to head.")
    except Exception as e:
        print(f"[Startup] Alembic auto-migration note: {e}")

    # 3. Create all missing tables
    try:
        models.Base.metadata.create_all(bind=engine)
        print("[Startup] Database tables verified/created via SQLAlchemy.")
    except Exception as e:
        print(f"[Startup] Metadata create_all note: {e}")

    # 4. Synchronize existing MeetingActionItem to Kanban Task
    try:
        from database import SessionLocal
        sync_db = SessionLocal()
        action_items = sync_db.query(models.MeetingActionItem).options(
            joinedload(models.MeetingActionItem.meeting)
        ).all()
        synced_count = 0
        for ai in action_items:
            existing = sync_db.query(models.Task).filter(models.Task.meeting_action_item_id == ai.id).first()
            if not existing:
                meeting = ai.meeting
                m_title = meeting.title if meeting else "Rapat Yayasan"
                m_nomor = meeting.nomor_notulen if meeting else "-"
                
                t_status = "antrian"
                if ai.status == "in_progress":
                    t_status = "in_progress"
                elif ai.status == "done":
                    t_status = "done"

                creator_id = meeting.notulis_id if (meeting and meeting.notulis_id) else (ai.pic_user_id or 1)
                new_task = models.Task(
                    title=ai.task_description,
                    description=f"Ditugaskan dari Notulen Rapat: {m_title} (#{m_nomor})\nCatatan: {ai.notes or '-'}",
                    status=t_status,
                    priority_level=2 if ai.deadline else 3,
                    creator_id=creator_id,
                    assignee_id=ai.pic_user_id,
                    unit_id=meeting.unit_id if meeting else None,
                    deadline=ai.deadline,
                    meeting_minute_id=ai.meeting_id,
                    meeting_action_item_id=ai.id,
                    is_active=True
                )
                sync_db.add(new_task)
                synced_count += 1
        if synced_count > 0:
            sync_db.commit()
            print(f"[Startup] Synchronized {synced_count} meeting action items to tasks.")
        sync_db.close()
    except Exception as e:
        print(f"[Startup] Sync meeting action items note: {e}")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.nik == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/")
async def root():
    return {
        "message": "Welcome to Asy-Syuuraa Batam API",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    from storage import is_r2_configured
    return {
        "status": "ok",
        "database": "connected",
        "r2_storage": "configured" if is_r2_configured() else "NOT configured - uploads will use local fallback"
    }

@app.post("/auth/login", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Check User by NIK or Email (Username field can contain either)
    user = db.query(models.User).filter(
        (models.User.email == form_data.username) | (models.User.nik == form_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Verify Password
    if not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create Token
    access_token = auth.create_access_token(
        data={"sub": user.nik} # Use NIK as subject identity
    )
    return {"access_token": access_token, "token_type": "bearer"}

from pydantic import BaseModel

class TestEmailRequest(BaseModel):
    to_email: str


@app.post("/auth/forgot-password")
async def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "If email exists, a reset link has been sent."}
    
    token = auth.create_password_reset_token(request.email)
    
    # Send email via ZeptoMail
    try:
        from email_service import send_password_reset_email
        send_password_reset_email(
            to_email=request.email,
            reset_token=token,
            user_name=user.full_name or ""
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to send password reset email to {request.email}: {e}")
    
    return {"message": "If email exists, a reset link has been sent."}


@app.post("/auth/test-email")
async def test_email(req: TestEmailRequest):
    """Endpoint untuk menguji koneksi & pengiriman email ZeptoMail."""
    from email_service import send_test_email
    try:
        res = send_test_email(to_email=req.to_email)
        return {
            "status": "success",
            "message": f"Email uji coba berhasil dikirim ke {req.to_email}",
            "details": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengirim email: {str(e)}")


@app.post("/auth/reset-password")
async def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    email = auth.verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = auth.get_password_hash(request.new_password)
    user.must_change_password = False
    db.commit()
    
    return {"message": "Password has been reset successfully"}

@app.get("/auth/me")
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Return user info with role permissions for sidebar filtering"""
    role_data = None
    if current_user.role:
        perms = []
        if current_user.role.permissions:
            try:
                perms = json.loads(current_user.role.permissions)
            except:
                perms = []
        role_data = {
            "id": current_user.role.id,
            "code": current_user.role.code,
            "name": current_user.role.name,
            "scope": current_user.role.scope,
            "permissions": perms
        }
    
    return {
        "id": current_user.id,
        "nik": current_user.nik,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "must_change_password": current_user.must_change_password,
        "role_id": current_user.role_id,
        "role": role_data
    }

# --- User & Role Routes ---

@app.get("/users", response_model=List[schemas.User])
async def get_users(
    skip: int = 0, 
    limit: int = 1000, 
    role_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.User).options(joinedload(models.User.role))
    if role_id is not None:
        query = query.filter(models.User.role_id == role_id)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.User.full_name.ilike(term),
                models.User.email.ilike(term),
                models.User.nik.ilike(term)
            )
        )
    users = query.order_by(models.User.id.desc()).offset(skip).limit(limit).all()
    return users

@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check email duplicate
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar. Silakan gunakan email lain.")
    
    # Check NIK duplicate if provided
    if user.nik and user.nik.strip():
        nik_user = db.query(models.User).filter(models.User.nik == user.nik.strip()).first()
        if nik_user:
            raise HTTPException(status_code=400, detail="NIK/Username sudah terdaftar. Silakan gunakan NIK/Username lain.")

    # Validate role
    role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role yang dipilih tidak valid.")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email.strip().lower(),
        full_name=user.full_name.strip(),
        nik=user.nik.strip() if user.nik else None,
        role_id=user.role_id,
        password_hash=hashed_password,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
    update_data = user_update.dict(exclude_unset=True)

    # Protect superadmin account from deactivation
    is_superadmin = db_user.role and db_user.role.code == "superadmin"
    if is_superadmin:
        if 'is_active' in update_data and not update_data['is_active']:
            raise HTTPException(status_code=400, detail="Akun Super Administrator dilindungi dan tidak dapat dinonaktifkan.")
        if 'role_id' in update_data and update_data['role_id'] != db_user.role_id:
            superadmin_role = db.query(models.Role).filter(models.Role.code == "superadmin").first()
            if not superadmin_role or update_data['role_id'] != superadmin_role.id:
                raise HTTPException(status_code=400, detail="Role Super Administrator utama tidak dapat diubah.")

    # Check email duplicate if updating email
    if 'email' in update_data and update_data['email']:
        new_email = update_data['email'].strip().lower()
        update_data['email'] = new_email
        if new_email != db_user.email:
            existing = db.query(models.User).filter(models.User.email == new_email, models.User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email sudah digunakan oleh akun lain.")

    # Check NIK duplicate if updating NIK
    if 'nik' in update_data:
        new_nik = update_data['nik'].strip() if update_data['nik'] else None
        update_data['nik'] = new_nik
        if new_nik and new_nik != db_user.nik:
            existing = db.query(models.User).filter(models.User.nik == new_nik, models.User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="NIK/Username sudah digunakan oleh akun lain.")

    # Safely handle password update
    password = update_data.pop('password', None)
    if password is not None and str(password).strip():
        update_data['password_hash'] = auth.get_password_hash(str(password).strip())
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
         raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    if current_user.id == db_user.id:
        raise HTTPException(status_code=400, detail="Tidak dapat menghapus akun Anda sendiri.")

    if db_user.role and db_user.role.code == "superadmin":
        raise HTTPException(status_code=403, detail="Akun Super Administrator dilindungi oleh sistem dan tidak dapat dihapus. Anda dapat mengubah data atau mereset password jika diperlukan.")
    
    # Unlink or remove linked employee record if present
    db_emp = db.query(models.Employee).filter(models.Employee.user_id == user_id).first()
    if db_emp:
        db.delete(db_emp)

    db.delete(db_user)
    db.commit()
    return {"message": "User berhasil dihapus"}
    
@app.get("/roles", response_model=List[schemas.Role])
async def get_roles(db: Session = Depends(get_db)):
    return db.query(models.Role).all()

@app.get("/roles/permissions")
async def get_all_role_permissions(db: Session = Depends(get_db)):
    """Get all roles with their permissions for the admin matrix"""
    roles = db.query(models.Role).order_by(models.Role.priority).all()
    result = []
    for role in roles:
        perms = []
        if role.permissions:
            try:
                perms = json.loads(role.permissions)
            except:
                perms = []
        result.append({
            "id": role.id,
            "code": role.code,
            "name": role.name,
            "scope": role.scope,
            "priority": role.priority,
            "permissions": perms
        })
    return result

@app.put("/roles/{role_id}/permissions")
async def update_role_permissions(role_id: int, data: dict, db: Session = Depends(get_db)):
    """Update the permissions (allowed menu keys) for a specific role"""
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    permissions = data.get("permissions", [])
    role.permissions = json.dumps(permissions)
    db.commit()
    db.refresh(role)
    return {"message": f"Permissions updated for {role.name}", "permissions": permissions}

# --- General Routes ---
@app.get("/units", response_model=List[schemas.Unit])
async def get_units(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    units = db.query(models.Unit).offset(skip).limit(limit).all()
    return units

# --- Academic Routes ---

from typing import List

@app.get("/academic/students", response_model=List[schemas.Student])
async def get_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(models.Student).offset(skip).limit(limit).all()
    return students

@app.post("/academic/students", response_model=schemas.Student)
async def create_student(
    student: schemas.StudentCreate, 
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from deps import check_user_perm
    if not check_user_perm(current_user, "akademik.siswa:create"):
        raise HTTPException(status_code=403, detail="Akses ditolak: Anda tidak memiliki izin untuk menambah data siswa.")

    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.put("/academic/students/{student_id}", response_model=schemas.Student)
async def update_student(
    student_id: int,
    student: schemas.StudentUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from deps import check_user_perm
    if not check_user_perm(current_user, "akademik.siswa:update"):
        raise HTTPException(status_code=403, detail="Akses ditolak: Anda tidak memiliki izin untuk mengedit data siswa.")

    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        
    for key, value in student.dict(exclude_unset=True).items():
        setattr(db_student, key, value)
        
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/academic/students/{student_id}")
async def delete_student(
    student_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    from deps import check_user_perm
    if not check_user_perm(current_user, "akademik.siswa:delete"):
        raise HTTPException(status_code=403, detail="Akses ditolak: Anda tidak memiliki izin untuk menghapus data siswa.")

    db_student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Siswa tidak ditemukan")
        
    db.delete(db_student)
    db.commit()
    return {"ok": True}

def _format_classroom_response(c: models.Classroom) -> dict:
    teacher_dict = None
    if c.homeroom_teacher:
        ht = c.homeroom_teacher
        emp = ht.employee
        teacher_dict = {
            "id": ht.id,
            "full_name": (emp.nama_lengkap if emp and emp.nama_lengkap else ht.full_name) or "",
            "nik": (emp.nik_kepegawaian if emp and emp.nik_kepegawaian else ht.nik) or "",
            "email": ht.email,
            "nuptk": emp.nuptk if emp else None,
            "nip": emp.nip if emp else None,
            "photo_url": emp.photo_url if emp else None,
        }
        
    student_count = len([s for s in (c.students or []) if s.status == "ACTIVE"])
    
    return {
        "id": c.id,
        "name": c.name,
        "level": c.level,
        "unit_id": c.unit_id,
        "academic_year_id": c.academic_year_id,
        "homeroom_teacher_id": c.homeroom_teacher_id,
        "unit": c.unit,
        "academic_year": c.academic_year,
        "homeroom_teacher": teacher_dict,
        "student_count": student_count
    }

@app.get("/academic/classrooms", response_model=List[schemas.Classroom])
async def get_classrooms(
    unit_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    level: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.Classroom).options(
        joinedload(models.Classroom.unit),
        joinedload(models.Classroom.academic_year),
        joinedload(models.Classroom.homeroom_teacher).joinedload(models.User.employee),
        joinedload(models.Classroom.students)
    )
    
    if unit_id:
        query = query.filter(models.Classroom.unit_id == unit_id)
        
    if academic_year_id:
        query = query.filter(models.Classroom.academic_year_id == academic_year_id)

    if level:
        query = query.filter(models.Classroom.level == level)
        
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(models.Classroom.name.ilike(s))

    classrooms = query.order_by(models.Classroom.level.asc(), models.Classroom.name.asc()).offset(skip).limit(limit).all()
    return [_format_classroom_response(c) for c in classrooms]

@app.get("/academic/classrooms/{classroom_id}")
async def get_classroom_detail(classroom_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Classroom).options(
        joinedload(models.Classroom.unit),
        joinedload(models.Classroom.academic_year),
        joinedload(models.Classroom.homeroom_teacher).joinedload(models.User.employee),
        joinedload(models.Classroom.students)
    ).filter(models.Classroom.id == classroom_id).first()
    
    if not c:
        raise HTTPException(status_code=404, detail="Rombel (Kelas) tidak ditemukan")

    resp = _format_classroom_response(c)
    resp["students"] = [
        {
            "id": s.id,
            "nis": s.nis,
            "nisn": s.nisn,
            "full_name": s.full_name,
            "gender": s.gender,
            "status": s.status
        }
        for s in (c.students or [])
    ]
    return resp

@app.post("/academic/classrooms", response_model=schemas.Classroom)
async def create_classroom(classroom: schemas.ClassroomCreate, db: Session = Depends(get_db)):
    # Auto-assign active academic year if not provided
    target_ay_id = classroom.academic_year_id
    if not target_ay_id:
        active_year = db.query(models.AcademicYear).filter(models.AcademicYear.is_active == True).first()
        if not active_year:
            active_year = db.query(models.AcademicYear).order_by(models.AcademicYear.id.desc()).first()
        if active_year:
            target_ay_id = active_year.id

    # Check duplication of name within same unit & academic year
    existing = db.query(models.Classroom).filter(
        models.Classroom.name == classroom.name,
        models.Classroom.unit_id == classroom.unit_id,
        models.Classroom.academic_year_id == target_ay_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Rombel dengan nama '{classroom.name}' sudah terdaftar pada tahun ajaran ini.")

    db_classroom = models.Classroom(
        name=classroom.name,
        level=classroom.level,
        unit_id=classroom.unit_id,
        academic_year_id=target_ay_id,
        homeroom_teacher_id=classroom.homeroom_teacher_id
    )
    db.add(db_classroom)
    db.commit()
    db.refresh(db_classroom)
    
    c = db.query(models.Classroom).options(
        joinedload(models.Classroom.unit),
        joinedload(models.Classroom.academic_year),
        joinedload(models.Classroom.homeroom_teacher).joinedload(models.User.employee),
        joinedload(models.Classroom.students)
    ).filter(models.Classroom.id == db_classroom.id).first()
    return _format_classroom_response(c)

@app.put("/academic/classrooms/{classroom_id}", response_model=schemas.Classroom)
async def update_classroom(classroom_id: int, payload: schemas.ClassroomUpdate, db: Session = Depends(get_db)):
    c = db.query(models.Classroom).filter(models.Classroom.id == classroom_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Rombel (Kelas) tidak ditemukan")

    data = payload.dict(exclude_unset=True)
    for field, val in data.items():
        setattr(c, field, val)

    db.commit()
    db.refresh(c)
    
    reloaded = db.query(models.Classroom).options(
        joinedload(models.Classroom.unit),
        joinedload(models.Classroom.academic_year),
        joinedload(models.Classroom.homeroom_teacher).joinedload(models.User.employee),
        joinedload(models.Classroom.students)
    ).filter(models.Classroom.id == c.id).first()
    return _format_classroom_response(reloaded)

@app.delete("/academic/classrooms/{classroom_id}")
async def delete_classroom(classroom_id: int, db: Session = Depends(get_db)):
    c = db.query(models.Classroom).options(
        joinedload(models.Classroom.students)
    ).filter(models.Classroom.id == classroom_id).first()
    
    if not c:
        raise HTTPException(status_code=404, detail="Rombel (Kelas) tidak ditemukan")

    active_students = [s for s in (c.students or []) if s.status == "ACTIVE"]
    if active_students:
        raise HTTPException(
            status_code=400,
            detail=f"Tidak dapat menghapus: Masih ada {len(active_students)} siswa aktif di kelas '{c.name}'. Pindahkan penempatan siswa terlebih dahulu."
        )

    schedule_count = db.query(models.Schedule).filter(models.Schedule.classroom_id == classroom_id).count()
    if schedule_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Tidak dapat menghapus: Masih terdapat {schedule_count} jadwal pelajaran yang menggunakan kelas '{c.name}'."
        )

    db.delete(c)
    db.commit()
    return {"message": f"Rombel '{c.name}' berhasil dihapus."}

def _get_expected_academic_period(dt: datetime = None):
    from datetime import timedelta
    now_wib = dt or (datetime.utcnow() + timedelta(hours=7))
    if now_wib.month >= 7:
        return f"{now_wib.year}/{now_wib.year + 1}", "Ganjil"
    else:
        return f"{now_wib.year - 1}/{now_wib.year}", "Genap"


def _sync_active_academic_year(db: Session):
    """
    Ensure the current calendar-based AcademicYear & Semester exists (Jul-Dec = Ganjil, Jan-Jun = Genap),
    automatically set it as active (unless manual override is enabled), and re-link calendar events
    whose dates belong to the current period but were saved under an older default AcademicYear.
    """
    expected_name, expected_semester = _get_expected_academic_period()
    start_yr = int(expected_name.split("/")[0])

    # Ensure both Ganjil & Genap rows exist for the current academic year
    changed = False
    for sem, s_date, e_date in [
        ("Ganjil", datetime(start_yr, 7, 1), datetime(start_yr, 12, 31, 23, 59, 59)),
        ("Genap", datetime(start_yr + 1, 1, 1), datetime(start_yr + 1, 6, 30, 23, 59, 59)),
    ]:
        row = db.query(models.AcademicYear).filter(
            models.AcademicYear.name == expected_name,
            models.AcademicYear.semester == sem
        ).first()
        if not row:
            row = models.AcademicYear(
                name=expected_name,
                semester=sem,
                is_active=(sem == expected_semester),
                start_date=s_date,
                end_date=e_date
            )
            db.add(row)
            changed = True

    if changed:
        db.commit()

    # Check if manual mode override is set
    mode_setting = db.query(models.PageContent).filter(
        models.PageContent.section_key == "settings_academic_year_mode"
    ).first()
    is_manual = False
    if mode_setting and isinstance(mode_setting.content, dict):
        is_manual = mode_setting.content.get("mode") == "manual"

    all_years = db.query(models.AcademicYear).all()
    year_map = {(y.name, y.semester): y for y in all_years}
    target_active = year_map.get((expected_name, expected_semester))

    if not is_manual and target_active:
        for y in all_years:
            should_be_active = (y.id == target_active.id)
            if y.is_active != should_be_active:
                y.is_active = should_be_active
                changed = True
        if changed:
            db.commit()

    # Re-link any AcademicCalendarEvent whose event date clearly belongs to an existing AcademicYear
    # (e.g. Nov 2026 event accidentally saved under 2025/2026 Ganjil when 2025/2026 was hardcoded)
    events = db.query(models.AcademicCalendarEvent).all()
    relinked = False
    for ev in events:
        if not ev.date:
            continue
        ev_name, ev_sem = _get_expected_academic_period(ev.date)
        correct_ay = year_map.get((ev_name, ev_sem))
        if correct_ay and ev.academic_year_id != correct_ay.id:
            ev.academic_year_id = correct_ay.id
            relinked = True
    if relinked:
        db.commit()


@app.get("/academic/years", response_model=List[schemas.AcademicYear])
async def get_academic_years(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    _sync_active_academic_year(db)
    years = db.query(models.AcademicYear).order_by(
        models.AcademicYear.name.desc(),
        models.AcademicYear.semester.asc()
    ).offset(skip).limit(limit).all()
    return years

@app.post("/academic/years", response_model=schemas.AcademicYear)
async def create_academic_year(year: schemas.AcademicYearCreate, db: Session = Depends(get_db)):
    existing = db.query(models.AcademicYear).filter(
        models.AcademicYear.name == year.name,
        models.AcademicYear.semester == year.semester
    ).first()
    if existing:
        if year.is_active:
            for y in db.query(models.AcademicYear).all():
                y.is_active = (y.id == existing.id)
            db.commit()
            db.refresh(existing)
        return existing

    if year.is_active:
        for y in db.query(models.AcademicYear).all():
            y.is_active = False
    db_year = models.AcademicYear(**year.dict())
    db.add(db_year)
    db.commit()
    db.refresh(db_year)
    return db_year

@app.put("/academic/years/{year_id}/activate", response_model=schemas.AcademicYear)
async def activate_academic_year(
    year_id: int,
    mode: str = "manual",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    target = db.query(models.AcademicYear).filter(models.AcademicYear.id == year_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Tahun ajaran tidak ditemukan")

    mode_setting = db.query(models.PageContent).filter(
        models.PageContent.section_key == "settings_academic_year_mode"
    ).first()
    if not mode_setting:
        mode_setting = models.PageContent(
            section_key="settings_academic_year_mode",
            title="Mode Tahun Ajaran",
            content={"mode": mode}
        )
        db.add(mode_setting)
    else:
        mode_setting.content = {"mode": mode}

    if mode == "auto":
        db.commit()
        _sync_active_academic_year(db)
        active = db.query(models.AcademicYear).filter(models.AcademicYear.is_active == True).first()
        return active or target

    for y in db.query(models.AcademicYear).all():
        y.is_active = (y.id == target.id)
    db.commit()
    db.refresh(target)
    return target

def _format_teacher_response(u: models.User, emp: Optional[models.Employee] = None) -> dict:
    unit_id = None
    unit_name = None
    if emp and emp.unit:
        unit_id = emp.unit_id
        unit_name = emp.unit.name
    elif u.unit_assignments:
        primary_ua = next((ua for ua in u.unit_assignments if ua.is_primary), u.unit_assignments[0])
        unit_id = primary_ua.unit_id
        unit_name = primary_ua.unit.name if primary_ua.unit else None
        
    return {
        "id": u.id,
        "email": u.email,
        "full_name": (emp.nama_lengkap if emp and emp.nama_lengkap else u.full_name) or "",
        "nik": (emp.nik_kepegawaian if emp and emp.nik_kepegawaian else u.nik) or "",
        "is_active": emp.is_active if (emp and emp.is_active is not None) else u.is_active,
        "role_id": u.role_id,
        "role": u.role,
        "employee_id": emp.id if emp else None,
        "nuptk": emp.nuptk if emp else None,
        "nip": emp.nip if emp else None,
        "position": (emp.position if emp and emp.position else "Guru") or "Guru",
        "employee_type": (emp.employee_type if emp and emp.employee_type else "tetap") or "tetap",
        "unit_id": unit_id,
        "unit_name": unit_name,
        "photo_url": emp.photo_url if emp else None,
        "no_hp": emp.no_hp if emp else None,
        "gender": emp.jenis_kelamin if emp else None,
    }

@app.get("/academic/teachers", response_model=List[schemas.Teacher])
async def get_teachers(
    unit_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    
    # 1. Query Employees who are teachers (role is guru OR position has guru/pengajar/ustadz/tahfidz/nuptk)
    emp_query = db.query(models.Employee).options(
        joinedload(models.Employee.user).joinedload(models.User.role),
        joinedload(models.Employee.unit)
    )
    
    if unit_id:
        emp_query = emp_query.filter(models.Employee.unit_id == unit_id)
        
    all_emps = emp_query.all()
    
    teacher_emps = []
    for emp in all_emps:
        is_guru_role = emp.user and emp.user.role and emp.user.role.code == "guru"
        pos_lower = (emp.position or "").lower()
        has_guru_pos = any(k in pos_lower for k in ["guru", "pengajar", "ustadz", "ustadzah", "tahfidz", "wali kelas"])
        has_nuptk = bool(emp.nuptk and emp.nuptk.strip())
        
        if is_guru_role or has_guru_pos or has_nuptk:
            teacher_emps.append(emp)

    results = []
    seen_user_ids = set()

    for emp in teacher_emps:
        # Ensure user account exists
        u = emp.user
        if not u:
            # Auto-link or auto-create User account for employee if missing
            u = db.query(models.User).filter(models.User.nik == emp.nik_kepegawaian).first()
            if not u:
                pw_plain = emp.tanggal_lahir.strftime("%d%m%Y") if emp.tanggal_lahir else "password123"
                u = models.User(
                    nik=emp.nik_kepegawaian,
                    full_name=emp.nama_lengkap,
                    password_hash=auth.get_password_hash(pw_plain),
                    role_id=guru_role.id if guru_role else None,
                    is_active=emp.is_active if emp.is_active is not None else True,
                    must_change_password=True
                )
                db.add(u)
                db.flush()
            emp.user_id = u.id
            db.commit()
            db.refresh(emp)

        seen_user_ids.add(u.id)
        results.append(_format_teacher_response(u, emp))

    # 2. Also query Users with role 'guru' who might not have an Employee record yet
    if guru_role:
        u_query = db.query(models.User).options(
            joinedload(models.User.role),
            joinedload(models.User.unit_assignments).joinedload(models.UserUnit.unit)
        ).filter(models.User.role_id == guru_role.id)
        
        if seen_user_ids:
            u_query = u_query.filter(~models.User.id.in_(seen_user_ids))
            
        orphan_gurus = u_query.all()
        for u in orphan_gurus:
            # Check unit filter if requested
            if unit_id:
                has_unit = any(ua.unit_id == unit_id for ua in u.unit_assignments)
                if not has_unit:
                    continue
            results.append(_format_teacher_response(u, None))

    # Optional search filtering in memory
    if search:
        s = search.lower().strip()
        results = [
            t for t in results
            if s in (t["full_name"] or "").lower()
            or s in (t["nik"] or "").lower()
            or s in (t["nuptk"] or "").lower()
            or s in (t["position"] or "").lower()
        ]

    # Sort alphabetically by name
    results.sort(key=lambda x: (x["full_name"] or "").lower())
    return results

@app.get("/academic/teachers/candidates")
async def get_teacher_candidates(db: Session = Depends(get_db)):
    """Returns employees from SDM who are not yet assigned as Guru."""
    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    
    # Get all active employees
    emps = db.query(models.Employee).options(
        joinedload(models.Employee.user).joinedload(models.User.role),
        joinedload(models.Employee.unit)
    ).filter(or_(models.Employee.is_active == True, models.Employee.is_active.is_(None))).order_by(models.Employee.nama_lengkap.asc()).all()
    
    candidates = []
    for emp in emps:
        is_guru_role = emp.user and emp.user.role and emp.user.role.code == "guru"
        pos_lower = (emp.position or "").lower()
        has_guru_pos = any(k in pos_lower for k in ["guru", "pengajar", "ustadz", "ustadzah", "tahfidz", "wali kelas"])
        
        # Candidate is someone who isn't already recognized as guru
        if not (is_guru_role or has_guru_pos):
            candidates.append({
                "id": emp.id,
                "nama_lengkap": emp.nama_lengkap,
                "nik_kepegawaian": emp.nik_kepegawaian,
                "position": emp.position or "Staf",
                "unit_id": emp.unit_id,
                "unit_name": emp.unit.name if emp.unit else "-",
                "user_id": emp.user_id
            })
            
    return candidates

@app.post("/academic/teachers", response_model=schemas.Teacher)
async def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    if not guru_role:
        raise HTTPException(status_code=400, detail="Role 'guru' belum tersedia di sistem")

    # CASE A: Linking an existing Employee from SDM
    if teacher.employee_id:
        emp = db.query(models.Employee).options(joinedload(models.Employee.unit)).filter(models.Employee.id == teacher.employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Data pegawai tidak ditemukan")
            
        u = emp.user
        if not u:
            u = db.query(models.User).filter(models.User.nik == emp.nik_kepegawaian).first()
            if not u:
                pw_plain = teacher.password or (emp.tanggal_lahir.strftime("%d%m%Y") if emp.tanggal_lahir else "password123")
                u = models.User(
                    nik=emp.nik_kepegawaian,
                    full_name=emp.nama_lengkap,
                    email=teacher.email or (emp.user.email if hasattr(emp, 'user') and emp.user else None),
                    password_hash=auth.get_password_hash(pw_plain),
                    role_id=guru_role.id,
                    is_active=True,
                    must_change_password=True
                )
                db.add(u)
                db.flush()
            emp.user_id = u.id
            
        u.role_id = guru_role.id
        if teacher.email:
            u.email = teacher.email
            
        # Update position if provided or currently not guru
        if teacher.position:
            emp.position = teacher.position
        elif not emp.position or "guru" not in emp.position.lower():
            emp.position = "Guru"
            
        if teacher.unit_id:
            emp.unit_id = teacher.unit_id
            
        # Update / add user unit
        target_unit_id = teacher.unit_id or emp.unit_id
        if target_unit_id:
            existing_ua = db.query(models.UserUnit).filter(models.UserUnit.user_id == u.id, models.UserUnit.unit_id == target_unit_id).first()
            if not existing_ua:
                db.add(models.UserUnit(user_id=u.id, unit_id=target_unit_id, is_primary=True))
                
        db.commit()
        db.refresh(u)
        db.refresh(emp)
        return _format_teacher_response(u, emp)

    # CASE B: Creating fresh new teacher (creates both User and Employee)
    if teacher.nik:
        existing_u = db.query(models.User).filter(models.User.nik == teacher.nik).first()
        if existing_u:
            raise HTTPException(status_code=400, detail=f"NIK {teacher.nik} sudah terdaftar pada pengguna lain")
        existing_emp = db.query(models.Employee).filter(models.Employee.nik_kepegawaian == teacher.nik).first()
        if existing_emp:
            raise HTTPException(status_code=400, detail=f"NIK {teacher.nik} sudah terdaftar di data pegawai SDM")

    pw_plain = teacher.password or "password123"
    hashed_pw = auth.get_password_hash(pw_plain)
    
    db_user = models.User(
        email=teacher.email,
        full_name=teacher.full_name,
        nik=teacher.nik,
        password_hash=hashed_pw,
        role_id=guru_role.id,
        is_active=True,
        must_change_password=True
    )
    db.add(db_user)
    db.flush()

    # Create matching Employee profile
    db_emp = models.Employee(
        user_id=db_user.id,
        nama_lengkap=teacher.full_name,
        nik_kepegawaian=teacher.nik,
        nuptk=teacher.nuptk,
        nip=teacher.nip,
        position=teacher.position or "Guru",
        employee_type=teacher.employee_type or "tetap",
        unit_id=teacher.unit_id,
        no_hp=teacher.no_hp,
        is_active=True
    )
    db.add(db_emp)

    if teacher.unit_id:
        db.add(models.UserUnit(user_id=db_user.id, unit_id=teacher.unit_id, is_primary=True))

    db.commit()
    db.refresh(db_user)
    db.refresh(db_emp)
    return _format_teacher_response(db_user, db_emp)

@app.put("/academic/teachers/{teacher_id}", response_model=schemas.Teacher)
async def update_teacher(teacher_id: int, payload: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    u = db.query(models.User).options(
        joinedload(models.User.role),
        joinedload(models.User.employee),
        joinedload(models.User.unit_assignments)
    ).filter(models.User.id == teacher_id).first()
    
    if not u:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    if payload.full_name:
        u.full_name = payload.full_name
    if payload.email is not None:
        u.email = payload.email or None
    if payload.nik:
        u.nik = payload.nik
    if payload.is_active is not None:
        u.is_active = payload.is_active
    if payload.password and payload.password.strip():
        u.password_hash = auth.get_password_hash(payload.password.strip())

    emp = u.employee
    if not emp:
        emp = models.Employee(
            user_id=u.id,
            nama_lengkap=u.full_name,
            nik_kepegawaian=u.nik,
            position=payload.position or "Guru",
            unit_id=payload.unit_id,
            is_active=u.is_active
        )
        db.add(emp)
        db.flush()

    if payload.full_name:
        emp.nama_lengkap = payload.full_name
    if payload.nik:
        emp.nik_kepegawaian = payload.nik
    if payload.position:
        emp.position = payload.position
    if payload.unit_id is not None:
        emp.unit_id = payload.unit_id
    if payload.nuptk is not None:
        emp.nuptk = payload.nuptk.strip() or None
    if payload.nip is not None:
        emp.nip = payload.nip.strip() or None
    if payload.no_hp is not None:
        emp.no_hp = payload.no_hp
    if payload.employee_type:
        emp.employee_type = payload.employee_type
    if payload.is_active is not None:
        emp.is_active = payload.is_active

    target_unit_id = payload.unit_id or emp.unit_id
    if target_unit_id:
        ua = db.query(models.UserUnit).filter(models.UserUnit.user_id == u.id).first()
        if ua:
            ua.unit_id = target_unit_id
        else:
            db.add(models.UserUnit(user_id=u.id, unit_id=target_unit_id, is_primary=True))

    db.commit()
    db.refresh(u)
    db.refresh(emp)
    return _format_teacher_response(u, emp)

@app.delete("/academic/teachers/{teacher_id}")
async def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.id == teacher_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Guru tidak ditemukan")

    active_classroom = db.query(models.Classroom).filter(models.Classroom.homeroom_teacher_id == teacher_id).first()
    if active_classroom:
        raise HTTPException(
            status_code=400,
            detail=f"Tidak dapat menghapus: Guru ini masih tercatat sebagai Wali Kelas di '{active_classroom.name}'. Silakan ganti wali kelas terlebih dahulu atau nonaktifkan status aktifnya."
        )

    active_schedule = db.query(models.Schedule).filter(models.Schedule.teacher_id == teacher_id).first()
    if active_schedule:
        raise HTTPException(
            status_code=400,
            detail=f"Tidak dapat menghapus: Guru ini masih memiliki Jadwal Pelajaran aktif. Silakan hapus/pindahkan jadwal mengajarnya terlebih dahulu atau nonaktifkan status aktifnya."
        )

    emp = db.query(models.Employee).filter(models.Employee.user_id == teacher_id).first()
    karyawan_role = db.query(models.Role).filter(models.Role.code == "karyawan").first()

    if emp:
        if karyawan_role:
            u.role_id = karyawan_role.id
        if emp.position and "guru" in emp.position.lower():
            emp.position = "Karyawan"
        db.commit()
        return {"message": "Status penugasan guru berhasil dicabut. Akun dan data pegawai tetap tersimpan sebagai staf/karyawan."}
    else:
        db.query(models.UserUnit).filter(models.UserUnit.user_id == teacher_id).delete()
        db.delete(u)
        db.commit()
        return {"message": "Data guru berhasil dihapus dari sistem."}

# --- Subject Routes ---
@app.get("/academic/subjects", response_model=List[schemas.Subject])
async def get_subjects(unit_id: Optional[int] = None, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Subject).options(joinedload(models.Subject.unit))
    if unit_id:
        query = query.filter(models.Subject.unit_id == unit_id)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(models.Subject.name.ilike(s), models.Subject.code.ilike(s)))
    return query.order_by(models.Subject.name.asc()).all()

@app.post("/academic/subjects", response_model=schemas.Subject)
async def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Subject).filter(
        models.Subject.name == subject.name,
        models.Subject.unit_id == subject.unit_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mata pelajaran '{subject.name}' sudah ada di unit ini.")

    db_subject = models.Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db.query(models.Subject).options(joinedload(models.Subject.unit)).filter(models.Subject.id == db_subject.id).first()

@app.put("/academic/subjects/{subject_id}", response_model=schemas.Subject)
async def update_subject(subject_id: int, payload: schemas.SubjectUpdate, db: Session = Depends(get_db)):
    sb = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not sb:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")
    
    data = payload.dict(exclude_unset=True)
    for field, val in data.items():
        setattr(sb, field, val)
    db.commit()
    db.refresh(sb)
    return db.query(models.Subject).options(joinedload(models.Subject.unit)).filter(models.Subject.id == sb.id).first()

@app.delete("/academic/subjects/{subject_id}")
async def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    sb = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not sb:
        raise HTTPException(status_code=404, detail="Mata pelajaran tidak ditemukan")

    count = db.query(models.Schedule).filter(models.Schedule.subject_id == subject_id).count()
    if count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Tidak dapat menghapus: Mata pelajaran '{sb.name}' masih digunakan dalam {count} jadwal pelajaran."
        )

    db.delete(sb)
    db.commit()
    return {"message": f"Mata pelajaran '{sb.name}' berhasil dihapus."}

# --- Schedule Routes ---
def _format_schedule_response(sc: models.Schedule) -> dict:
    teacher_dict = None
    if sc.teacher:
        u = sc.teacher
        emp = u.employee
        teacher_dict = {
            "id": u.id,
            "full_name": (emp.nama_lengkap if emp and emp.nama_lengkap else u.full_name) or "",
            "nik": (emp.nik_kepegawaian if emp and emp.nik_kepegawaian else u.nik) or "",
            "email": u.email,
            "nuptk": emp.nuptk if emp else None,
            "nip": emp.nip if emp else None,
            "position": emp.position if emp else "Guru",
            "photo_url": emp.photo_url if emp else None,
            "no_hp": emp.no_hp if emp else None,
            "unit_id": emp.unit_id if emp else None,
            "unit_name": emp.unit.name if emp and emp.unit else None
        }

    return {
        "id": sc.id,
        "academic_year_id": sc.academic_year_id,
        "classroom_id": sc.classroom_id,
        "subject_id": sc.subject_id,
        "teacher_id": sc.teacher_id,
        "day": sc.day,
        "start_time": sc.start_time,
        "end_time": sc.end_time,
        "classroom": sc.classroom,
        "subject": sc.subject,
        "teacher": teacher_dict,
        "academic_year": sc.academic_year
    }

DAY_ORDER = {
    "SENIN": 1,
    "SELASA": 2,
    "RABU": 3,
    "KAMIS": 4,
    "JUMAT": 5,
    "SABTU": 6,
    "AHAD": 7
}

@app.get("/academic/schedules", response_model=List[schemas.Schedule])
async def get_schedules(
    classroom_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    day: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Schedule).options(
        joinedload(models.Schedule.classroom).joinedload(models.Classroom.unit),
        joinedload(models.Schedule.subject).joinedload(models.Subject.unit),
        joinedload(models.Schedule.teacher).joinedload(models.User.employee).joinedload(models.Employee.unit),
        joinedload(models.Schedule.academic_year)
    )

    if classroom_id:
        query = query.filter(models.Schedule.classroom_id == classroom_id)
    if teacher_id:
        query = query.filter(models.Schedule.teacher_id == teacher_id)
    if academic_year_id:
        query = query.filter(models.Schedule.academic_year_id == academic_year_id)
    if day:
        query = query.filter(models.Schedule.day == day.upper())
    if unit_id:
        query = query.join(models.Classroom).filter(models.Classroom.unit_id == unit_id)

    schedules = query.all()
    schedules.sort(key=lambda s: (DAY_ORDER.get(str(s.day).upper(), 99), s.start_time or ""))
    return [_format_schedule_response(s) for s in schedules]

@app.post("/academic/schedules", response_model=schemas.Schedule)
async def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    target_ay_id = schedule.academic_year_id
    if not target_ay_id:
        active_year = db.query(models.AcademicYear).filter(models.AcademicYear.is_active == True).first()
        if not active_year:
            active_year = db.query(models.AcademicYear).order_by(models.AcademicYear.id.desc()).first()
        if active_year:
            target_ay_id = active_year.id

    day_val = schedule.day.upper()
    start_t = schedule.start_time.strip()
    end_t = schedule.end_time.strip()

    if start_t >= end_t:
        raise HTTPException(status_code=400, detail="Jam mulai harus lebih awal dari jam selesai.")

    # 1. Check Room Conflict
    room_conflict = db.query(models.Schedule).options(
        joinedload(models.Schedule.classroom),
        joinedload(models.Schedule.subject)
    ).filter(
        models.Schedule.day == day_val,
        models.Schedule.classroom_id == schedule.classroom_id,
        models.Schedule.academic_year_id == target_ay_id,
        models.Schedule.start_time < end_t,
        models.Schedule.end_time > start_t
    ).first()
    
    if room_conflict:
        cr_name = room_conflict.classroom.name if room_conflict.classroom else f"ID {schedule.classroom_id}"
        mapel_name = room_conflict.subject.name if room_conflict.subject else "Mapel lain"
        raise HTTPException(
            status_code=400,
            detail=f"Bentrok Ruangan: Kelas '{cr_name}' sudah memiliki jadwal mapel '{mapel_name}' pada hari {day_val} jam {room_conflict.start_time} - {room_conflict.end_time}."
        )

    # 2. Check Teacher Conflict
    teacher_conflict = db.query(models.Schedule).options(
        joinedload(models.Schedule.classroom),
        joinedload(models.Schedule.teacher).joinedload(models.User.employee)
    ).filter(
        models.Schedule.day == day_val,
        models.Schedule.teacher_id == schedule.teacher_id,
        models.Schedule.academic_year_id == target_ay_id,
        models.Schedule.start_time < end_t,
        models.Schedule.end_time > start_t
    ).first()

    if teacher_conflict:
        t_name = teacher_conflict.teacher.full_name if teacher_conflict.teacher else f"Guru ID {schedule.teacher_id}"
        cr_conflict = teacher_conflict.classroom.name if teacher_conflict.classroom else "kelas lain"
        raise HTTPException(
            status_code=400,
            detail=f"Bentrok Jadwal Guru: {t_name} sudah mengajar di {cr_conflict} pada hari {day_val} jam {teacher_conflict.start_time} - {teacher_conflict.end_time}."
        )

    db_schedule = models.Schedule(
        academic_year_id=target_ay_id,
        classroom_id=schedule.classroom_id,
        subject_id=schedule.subject_id,
        teacher_id=schedule.teacher_id,
        day=day_val,
        start_time=start_t,
        end_time=end_t
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    reloaded = db.query(models.Schedule).options(
        joinedload(models.Schedule.classroom).joinedload(models.Classroom.unit),
        joinedload(models.Schedule.subject).joinedload(models.Subject.unit),
        joinedload(models.Schedule.teacher).joinedload(models.User.employee).joinedload(models.Employee.unit),
        joinedload(models.Schedule.academic_year)
    ).filter(models.Schedule.id == db_schedule.id).first()
    return _format_schedule_response(reloaded)

@app.put("/academic/schedules/{schedule_id}", response_model=schemas.Schedule)
async def update_schedule(schedule_id: int, payload: schemas.ScheduleUpdate, db: Session = Depends(get_db)):
    sc = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Jadwal pelajaran tidak ditemukan")

    target_ay_id = payload.academic_year_id or sc.academic_year_id
    classroom_id = payload.classroom_id or sc.classroom_id
    teacher_id = payload.teacher_id or sc.teacher_id
    day_val = (payload.day or sc.day).upper()
    start_t = (payload.start_time or sc.start_time).strip()
    end_t = (payload.end_time or sc.end_time).strip()

    if start_t >= end_t:
        raise HTTPException(status_code=400, detail="Jam mulai harus lebih awal dari jam selesai.")

    # 1. Check Room Conflict (exclude self)
    room_conflict = db.query(models.Schedule).filter(
        models.Schedule.id != schedule_id,
        models.Schedule.day == day_val,
        models.Schedule.classroom_id == classroom_id,
        models.Schedule.academic_year_id == target_ay_id,
        models.Schedule.start_time < end_t,
        models.Schedule.end_time > start_t
    ).first()
    if room_conflict:
        raise HTTPException(status_code=400, detail=f"Bentrok Ruangan: Kelas sudah terpakai pada {day_val} jam {room_conflict.start_time} - {room_conflict.end_time}.")

    # 2. Check Teacher Conflict (exclude self)
    teacher_conflict = db.query(models.Schedule).filter(
        models.Schedule.id != schedule_id,
        models.Schedule.day == day_val,
        models.Schedule.teacher_id == teacher_id,
        models.Schedule.academic_year_id == target_ay_id,
        models.Schedule.start_time < end_t,
        models.Schedule.end_time > start_t
    ).first()
    if teacher_conflict:
        raise HTTPException(status_code=400, detail=f"Bentrok Guru: Guru sudah mengajar pada {day_val} jam {teacher_conflict.start_time} - {teacher_conflict.end_time}.")

    data = payload.dict(exclude_unset=True)
    for field, val in data.items():
        if field == "day" and val:
            setattr(sc, field, val.upper())
        else:
            setattr(sc, field, val)

    db.commit()
    db.refresh(sc)

    reloaded = db.query(models.Schedule).options(
        joinedload(models.Schedule.classroom).joinedload(models.Classroom.unit),
        joinedload(models.Schedule.subject).joinedload(models.Subject.unit),
        joinedload(models.Schedule.teacher).joinedload(models.User.employee).joinedload(models.Employee.unit),
        joinedload(models.Schedule.academic_year)
    ).filter(models.Schedule.id == sc.id).first()
    return _format_schedule_response(reloaded)

@app.delete("/academic/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    sc = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    if not sc:
        raise HTTPException(status_code=404, detail="Jadwal pelajaran tidak ditemukan")
    db.delete(sc)
    db.commit()
    return {"message": "Jadwal pelajaran berhasil dihapus."}

# --- Finance Routes ---

@app.get("/finance/categories", response_model=List[schemas.PaymentCategory])
async def get_payment_categories(db: Session = Depends(get_db)):
    return db.query(models.PaymentCategory).all()

@app.post("/finance/categories", response_model=schemas.PaymentCategory)
async def create_payment_category(category: schemas.PaymentCategoryCreate, db: Session = Depends(get_db)):
    db_cat = models.PaymentCategory(**category.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.post("/finance/bills/generate")
async def generate_bill(
    request: schemas.StudentBillCreate, # Basic create for now, bulk logic can be added
    db: Session = Depends(get_db)
):
    # Check if bill already exists is good practice, but for MVP just create
    db_bill = models.StudentBill(**request.dict())
    db_bill.created_at = datetime.utcnow()
    db.add(db_bill)
    db.commit()
    return {"message": "Bill created", "bill_id": db_bill.id}

@app.get("/finance/bills", response_model=List[schemas.StudentBill])
async def get_bills(student_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.StudentBill)
    if student_id:
        query = query.filter(models.StudentBill.student_id == student_id)
    if status:
        query = query.filter(models.StudentBill.status == status)
    
    # Eager load relationships
    # query = query.options(joinedload(models.StudentBill.category), joinedload(models.StudentBill.student))
    
    return query.order_by(models.StudentBill.created_at.desc()).all()

# --- Scholarship Endpoints ---
@app.get("/finance/scholarships", response_model=List[schemas.Scholarship])
async def get_scholarships(db: Session = Depends(get_db)):
    return db.query(models.Scholarship).filter(models.Scholarship.is_active == True).all()

@app.post("/finance/scholarships", response_model=schemas.Scholarship)
async def create_scholarship(scholarship: schemas.ScholarshipCreate, db: Session = Depends(get_db)):
    db_obj = models.Scholarship(**scholarship.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- Bulk Billing Endpoints ---

@app.post("/finance/bills/bulk-preview", response_model=List[schemas.BulkBillPreviewResponse])
async def preview_bulk_bills(
    request: schemas.BulkBillPreviewRequest,
    db: Session = Depends(get_db)
):
    # 1. Get Classroom Students
    students = db.query(models.Student).filter(
        models.Student.current_classroom_id == request.classroom_id,
        models.Student.status == "ACTIVE"
    ).all()
    
    if not students:
        return []

    # 2. Get Payment Category
    category = db.query(models.PaymentCategory).filter(models.PaymentCategory.id == request.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    timestamp_title = datetime.utcnow().strftime("%B %Y") # e.g. January 2026 (simplified, user provided title is preferred or auto-appended)
    # Actually user provides title in request.

    response_items = []
    
    for student in students:
        original_amount = category.amount
        discount = 0
        scholarship_name = None
        
        # Calculate Scholarship if Category is eligible
        if category.is_scholarship_eligible and student.scholarship_id:
            scholarship = db.query(models.Scholarship).filter(models.Scholarship.id == student.scholarship_id).first()
            if scholarship and scholarship.is_active:
                scholarship_name = scholarship.name
                if scholarship.type == models.ScholarshipType.FIXED:
                    discount = scholarship.value
                elif scholarship.type == models.ScholarshipType.PERCENTAGE:
                    discount = int(original_amount * (scholarship.value / 100))
        
        final_amount = max(0, original_amount - discount)
        
        response_items.append(schemas.BulkBillPreviewResponse(
            student_id=student.id,
            student_name=student.full_name,
            original_amount=original_amount,
            scholarship_name=scholarship_name,
            discount_amount=discount,
            final_amount=final_amount
        ))
        
    return response_items

@app.post("/finance/bills/bulk")
async def create_bulk_bills(
    request: schemas.BulkBillCreateRequest,
    db: Session = Depends(get_db)
):
    count = 0
    for item in request.items:
        db_bill = models.StudentBill(
            student_id=item.student_id,
            category_id=request.category_id,
            title=item.title,
            amount=item.amount,
            status="UNPAID",
            due_date=request.due_date,
            created_at=datetime.utcnow()
        )
        db.add(db_bill)
        count += 1
    
    db.commit()
    return {"message": f"Successfully created {count} bills"}


@app.post("/finance/payments", response_model=schemas.PaymentTransaction)
async def create_payment(payment: schemas.PaymentTransactionCreate, db: Session = Depends(get_db)):
    # 1. Record Transaction
    db_tx = models.PaymentTransaction(**payment.dict())
    db.add(db_tx)
    
    # 2. Update Bill Status
    bill = db.query(models.StudentBill).filter(models.StudentBill.id == payment.bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    # Calculate total paid
    total_paid = sum(t.amount_paid for t in bill.transactions) + payment.amount_paid
    
    if total_paid >= bill.amount:
        bill.status = "PAID"
    elif total_paid > 0:
        bill.status = "PARTIAL"
    
    # 3. Create Journal Entry (Accounting Integration)
    # Check if category has income account
    if bill.category and bill.category.income_account_id:
        revenue_account_id = bill.category.income_account_id
        
        # Find Cash Account (Debit) - Simplified: Find first ASSET account with 'Kas' or create simplified rule
        # For now, let's try to find account code '1-1001' or similar, or just pick first ASSET
        cash_account = db.query(models.Account).filter(models.Account.type == "ASSET").first()
        
        if cash_account:
            journal = models.JournalEntry(
                date=datetime.utcnow(),
                description=f"Payment for {bill.title} - {bill.student.full_name if bill.student else ''}",
                reference_id=f"PAY-{db_tx.id}", # Note: db_tx.id might not be available yet if not flushed
                total_amount=payment.amount_paid
            )
            db.add(journal)
            db.flush() # To get ID

            # Debit Cash
            db.add(models.JournalItem(
                journal_id=journal.id,
                account_id=cash_account.id,
                debit=payment.amount_paid,
                credit=0
            ))
            
            # Credit Revenue
            db.add(models.JournalItem(
                journal_id=journal.id,
                account_id=revenue_account_id,
                debit=0,
                credit=payment.amount_paid
            ))
        
    db.commit()
    db.refresh(db_tx)
    return db_tx

# --- Accounting Routes ---

@app.get("/finance/accounts", response_model=List[schemas.Account])
async def get_accounts(type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Account)
    if type:
        query = query.filter(models.Account.type == type)
    return query.order_by(models.Account.code).all()

@app.post("/finance/accounts", response_model=schemas.Account)
async def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_acc = models.Account(**account.dict())
    db.add(db_acc)
    db.commit()
    db.refresh(db_acc)
    return db_acc

@app.get("/finance/journals", response_model=List[schemas.JournalEntry])
async def get_journals(db: Session = Depends(get_db)):
    # Eager load items and accounts
    return db.query(models.JournalEntry).options(
        joinedload(models.JournalEntry.items).joinedload(models.JournalItem.account)
    ).order_by(models.JournalEntry.date.desc()).all()

# --- CMS Endpoints ---

# Public Routes
@app.get("/public/posts", response_model=List[schemas.Post])
async def get_public_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).filter(models.Post.is_published == True).order_by(models.Post.created_at.desc()).all()

@app.get("/public/content/{section_key}", response_model=schemas.PageContent)
async def get_page_content(section_key: str, db: Session = Depends(get_db)):
    content = db.query(models.PageContent).filter(models.PageContent.section_key == section_key).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

# Admin Routes
@app.post("/cms/posts", response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Auto generate slug from title if not provided (simplified)
    # In real app, handle duplicates. Here relying on unique constraint triggering error if dup.
    if not post.slug:
        post.slug = post.title.lower().replace(" ", "-")
        
    db_post = models.Post(**post.dict(), author_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/cms/posts", response_model=List[schemas.Post])
async def get_admin_posts(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).all()

@app.put("/cms/posts/{post_id}", response_model=schemas.Post)
async def update_post(post_id: int, post: schemas.PostCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    for key, value in post.dict().items():
        setattr(db_post, key, value)
        
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/cms/posts/{post_id}")
async def delete_post(post_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted"}

@app.put("/cms/content/{section_key}", response_model=schemas.PageContent)
async def update_page_content(section_key: str, content: schemas.PageContentCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_content = db.query(models.PageContent).filter(models.PageContent.section_key == section_key).first()
    
    # Get content data, always override section_key with URL path value
    content_data = content.dict()
    content_data["section_key"] = section_key
    
    if not db_content:
        # Create if not exists
        db_content = models.PageContent(**content_data)
        db.add(db_content)
    else:
        # Update, skip section_key to avoid PK issues  
        for key, value in content_data.items():
            if key != "section_key":
                setattr(db_content, key, value)
    
    db.commit()
    db.refresh(db_content)
    return db_content

@app.post("/cms/upload")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    try:
        from storage import upload_to_r2, is_r2_configured
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate file size (max 10MB)
        file_bytes = await file.read()
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_bytes) > max_size:
            raise HTTPException(status_code=413, detail="File terlalu besar. Maksimal 10MB.")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nama file tidak valid")
        
        r2_configured = is_r2_configured()
        logger.info(f"Upload request: filename={file.filename}, size={len(file_bytes)}, r2_configured={r2_configured}")
        
        if r2_configured:
            # Upload to Cloudflare R2 (with auto image compression)
            url = upload_to_r2(file_bytes, file.filename, folder="uploads")
            logger.info(f"Upload to R2 successful: {url}")
            return {"url": url}
        else:
            # Fallback: save locally
            logger.warning("R2 not configured, falling back to local storage. Images may be lost on container restart!")
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            with open(file_path, "wb") as buffer:
                buffer.write(file_bytes)
                
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
            return {"url": f"{base_url.rstrip('/')}/uploads/{unique_filename}"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/cms/upload/batch")
async def upload_files_batch(files: List[UploadFile] = File(...), current_user: models.User = Depends(get_current_user)):
    try:
        from storage import upload_to_r2, is_r2_configured
        import logging
        logger = logging.getLogger(__name__)
        
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maksimal 10 file dalam satu request.")

        urls = []
        r2_configured = is_r2_configured()
        max_size = 10 * 1024 * 1024  # 10MB
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

        for file in files:
            file_bytes = await file.read()
            if len(file_bytes) > max_size:
                raise HTTPException(status_code=413, detail=f"File {file.filename} terlalu besar. Maksimal 10MB.")
            
            if not file.filename:
                raise HTTPException(status_code=400, detail="Nama file tidak valid")
            
            logger.info(f"Batch upload request: filename={file.filename}, size={len(file_bytes)}, r2_configured={r2_configured}")
            
            if r2_configured:
                # Upload to Cloudflare R2
                url = upload_to_r2(file_bytes, file.filename, folder="uploads")
                logger.info(f"Batch upload to R2 successful: {url}")
                urls.append(url)
            else:
                # Fallback: save locally
                logger.warning("R2 not configured, falling back to local storage.")
                file_extension = os.path.splitext(file.filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = os.path.join(UPLOAD_DIR, unique_filename)
                
                with open(file_path, "wb") as buffer:
                    buffer.write(file_bytes)
                    
                urls.append(f"{base_url.rstrip('/')}/uploads/{unique_filename}")
                
        return {"urls": urls}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")

# --- Academic Calendar Routes ---

@app.get("/academic-calendar", response_model=List[schemas.CalendarEvent])
def get_calendar_events(academic_year_id: Optional[int] = None, skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    query = db.query(models.AcademicCalendarEvent)
    if academic_year_id:
        query = query.filter(models.AcademicCalendarEvent.academic_year_id == academic_year_id)
    return query.order_by(models.AcademicCalendarEvent.date.asc()).offset(skip).limit(limit).all()

@app.post("/academic-calendar", response_model=schemas.CalendarEvent)
def create_calendar_event(event: schemas.CalendarEventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    from deps import check_user_perm
    if not check_user_perm(current_user, "akademik.kalender:create"):
        raise HTTPException(status_code=403, detail="Akses ditolak: Anda tidak memiliki izin untuk menambah agenda kalender akademik.")

    # 1. Resolve academic year
    _sync_active_academic_year(db)
    ay = None
    if event.academic_year_id:
        ay = db.query(models.AcademicYear).filter(models.AcademicYear.id == event.academic_year_id).first()
    
    if not ay and event.date:
        ev_name, ev_sem = _get_expected_academic_period(event.date)
        ay = db.query(models.AcademicYear).filter(
            models.AcademicYear.name == ev_name,
            models.AcademicYear.semester == ev_sem
        ).first()

    if not ay:
        # Fallback to active academic year
        ay = db.query(models.AcademicYear).filter(models.AcademicYear.is_active == True).first()
    
    if not ay:
        # Fallback to first existing academic year
        ay = db.query(models.AcademicYear).first()

    event_dict = event.dict()
    event_dict["academic_year_id"] = ay.id
    
    db_event = models.AcademicCalendarEvent(**event_dict)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.put("/academic-calendar/{event_id}", response_model=schemas.CalendarEvent)
def update_calendar_event(event_id: int, event: schemas.CalendarEventUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    from deps import check_user_perm
    if not check_user_perm(current_user, "akademik.kalender:update"):
        raise HTTPException(status_code=403, detail="Akses ditolak: Anda tidak memiliki izin untuk mengedit agenda kalender akademik.")

    db_event = db.query(models.AcademicCalendarEvent).filter(models.AcademicCalendarEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    
    event_data = event.dict(exclude_unset=True)
    
    # If academic_year_id is provided, validate it exists
    if "academic_year_id" in event_data and event_data["academic_year_id"]:
        ay_exists = db.query(models.AcademicYear).filter(models.AcademicYear.id == event_data["academic_year_id"]).first()
        if not ay_exists:
            event_data.pop("academic_year_id", None)
            
    for key, value in event_data.items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/academic-calendar/{event_id}")
def delete_calendar_event(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    from deps import check_user_perm
    if not check_user_perm(current_user, "akademik.kalender:delete"):
        raise HTTPException(status_code=403, detail="Akses ditolak: Anda tidak memiliki izin untuk menghapus agenda kalender akademik.")

    db_event = db.query(models.AcademicCalendarEvent).filter(models.AcademicCalendarEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    
    db.delete(db_event)
    db.commit()
    return {"ok": True}

# --- Attendance Routes ---

@app.get("/attendance/students", response_model=List[schemas.StudentAttendance])
async def get_student_attendances(
    classroom_id: Optional[int] = None,
    date: Optional[str] = None,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db)
):
    query = db.query(models.StudentAttendance).options(joinedload(models.StudentAttendance.student))
    
    if classroom_id:
        # Join with student to filter by classroom
        query = query.join(models.Student).filter(models.Student.current_classroom_id == classroom_id)
    
    if date:
        from datetime import datetime as dt
        target_date = dt.strptime(date, "%Y-%m-%d").date()
        query = query.filter(models.StudentAttendance.date == target_date)
    
    return query.order_by(models.StudentAttendance.date.desc()).all()

@app.post("/attendance/students", response_model=schemas.StudentAttendance)
async def create_student_attendance(attendance: schemas.StudentAttendanceCreate, db: Session = Depends(get_db)):
    # Check for duplicate
    existing = db.query(models.StudentAttendance).filter(
        models.StudentAttendance.student_id == attendance.student_id,
        models.StudentAttendance.date == attendance.date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded for this student on this date")
    
    db_att = models.StudentAttendance(**attendance.dict())
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return db_att

@app.post("/attendance/students/bulk")
async def create_bulk_student_attendance(request: schemas.BulkStudentAttendanceCreate, db: Session = Depends(get_db)):
    count = 0
    skipped = 0
    
    for item in request.items:
        # Check for existing
        existing = db.query(models.StudentAttendance).filter(
            models.StudentAttendance.student_id == item.student_id,
            models.StudentAttendance.date == request.date
        ).first()
        
        if existing:
            skipped += 1
            continue
        
        db_att = models.StudentAttendance(
            student_id=item.student_id,
            date=request.date,
            status=item.status.value,
            notes=item.notes
        )
        db.add(db_att)
        count += 1
    
    db.commit()
    return {"message": f"Created {count} attendance records, skipped {skipped} duplicates"}



# --- Grade Routes ---

@app.get("/academic/grades", response_model=List[schemas.Grade])
async def get_grades(
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Grade).options(
        joinedload(models.Grade.student),
        joinedload(models.Grade.subject)
    )
    
    if student_id:
        query = query.filter(models.Grade.student_id == student_id)
    if subject_id:
        query = query.filter(models.Grade.subject_id == subject_id)
    if academic_year_id:
        query = query.filter(models.Grade.academic_year_id == academic_year_id)
    if type:
        query = query.filter(models.Grade.type == type)
    
    return query.order_by(models.Grade.created_at.desc()).all()

@app.post("/academic/grades", response_model=schemas.Grade)
async def create_grade(grade: schemas.GradeCreate, db: Session = Depends(get_db)):
    db_grade = models.Grade(**grade.dict())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

@app.post("/academic/grades/bulk")
async def create_bulk_grades(request: schemas.BulkGradeCreate, db: Session = Depends(get_db)):
    count = 0
    
    for item in request.items:
        db_grade = models.Grade(
            student_id=item.student_id,
            subject_id=request.subject_id,
            academic_year_id=request.academic_year_id,
            type=request.type.value,
            score=item.score,
            notes=item.notes
        )
        db.add(db_grade)
        count += 1
    
    db.commit()
    return {"message": f"Created {count} grade records"}

@app.get("/academic/grades/report/{student_id}")
async def get_student_grade_report(
    student_id: int,
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Get student
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get grades
    query = db.query(models.Grade).filter(models.Grade.student_id == student_id)
    if academic_year_id:
        query = query.filter(models.Grade.academic_year_id == academic_year_id)
    
    grades = query.options(joinedload(models.Grade.subject)).all()
    
    # Group by subject and calculate averages
    from collections import defaultdict
    subject_grades = defaultdict(list)
    
    for grade in grades:
        subject_grades[grade.subject_id].append({
            "type": grade.type.value if hasattr(grade.type, 'value') else grade.type,
            "score": grade.score
        })
    
    # Calculate average per subject
    report = []
    for subject_id, grade_list in subject_grades.items():
        subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
        avg_score = sum(g["score"] for g in grade_list) / len(grade_list) if grade_list else 0
        
        report.append({
            "subject_id": subject_id,
            "subject_name": subject.name if subject else "Unknown",
            "grades": grade_list,
            "average": round(avg_score, 2)
        })
    
    # Get attitude grade
    attitude = db.query(models.AttitudeGrade).filter(
        models.AttitudeGrade.student_id == student_id
    )
    if academic_year_id:
        attitude = attitude.filter(models.AttitudeGrade.academic_year_id == academic_year_id)
    attitude = attitude.first()
    
    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "subjects": report,
        "attitude": {
            "spiritual": attitude.spiritual if attitude else None,
            "social": attitude.social if attitude else None
        } if attitude else None
    }

# Attitude Grade endpoints
@app.get("/academic/attitude-grades", response_model=List[schemas.AttitudeGrade])
async def get_attitude_grades(
    classroom_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.AttitudeGrade).options(joinedload(models.AttitudeGrade.student))
    
    if classroom_id:
        query = query.join(models.Student).filter(models.Student.current_classroom_id == classroom_id)
    if academic_year_id:
        query = query.filter(models.AttitudeGrade.academic_year_id == academic_year_id)
    
    return query.all()

@app.post("/academic/attitude-grades", response_model=schemas.AttitudeGrade)
async def create_attitude_grade(attitude: schemas.AttitudeGradeCreate, db: Session = Depends(get_db)):
    # Check existing
    existing = db.query(models.AttitudeGrade).filter(
        models.AttitudeGrade.student_id == attitude.student_id,
        models.AttitudeGrade.academic_year_id == attitude.academic_year_id
    ).first()
    
    if existing:
        # Update existing
        for key, value in attitude.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    
    db_att = models.AttitudeGrade(**attitude.dict())
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return db_att

# --- Tahfidz Routes ---

@app.get("/tahfidz/progress", response_model=List[schemas.TahfidzProgress])
async def get_tahfidz_progress(
    student_id: Optional[int] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.TahfidzProgress).options(joinedload(models.TahfidzProgress.student))
    
    if student_id:
        query = query.filter(models.TahfidzProgress.student_id == student_id)
    if type:
        query = query.filter(models.TahfidzProgress.type == type)
    
    return query.order_by(models.TahfidzProgress.date.desc()).all()

@app.post("/tahfidz/progress", response_model=schemas.TahfidzProgress)
async def create_tahfidz_progress(progress: schemas.TahfidzProgressCreate, db: Session = Depends(get_db)):
    db_progress = models.TahfidzProgress(**progress.dict())
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress

@app.get("/tahfidz/progress/{student_id}/summary")
async def get_tahfidz_summary(student_id: int, db: Session = Depends(get_db)):
    # Get student
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get all progress records
    progress_list = db.query(models.TahfidzProgress).filter(
        models.TahfidzProgress.student_id == student_id
    ).all()
    
    # Group by type
    quran_count = sum(1 for p in progress_list if p.type.value == "QURAN" or p.type == "QURAN")
    mutun_count = sum(1 for p in progress_list if p.type.value == "MUTUN" or p.type == "MUTUN")
    
    # Get unique surah/kitab names
    quran_surah = set()
    mutun_kitab = set()
    
    for p in progress_list:
        ptype = p.type.value if hasattr(p.type, 'value') else p.type
        if ptype == "QURAN":
            quran_surah.add(p.new_memorization)
        else:
            if p.kitab_name:
                mutun_kitab.add(p.kitab_name)
    
    # Calculate average score
    scores = [p.score for p in progress_list if p.score]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "total_sessions": len(progress_list),
        "quran": {
            "sessions": quran_count,
            "surah_learned": list(quran_surah)
        },
        "mutun": {
            "sessions": mutun_count,
            "kitab_learned": list(mutun_kitab)
        },
        "average_score": round(avg_score, 2)
    }

# Tahfidz Exam endpoints
@app.get("/tahfidz/exams", response_model=List[schemas.TahfidzExam])
async def get_tahfidz_exams(
    student_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.TahfidzExam).options(joinedload(models.TahfidzExam.student))
    
    if student_id:
        query = query.filter(models.TahfidzExam.student_id == student_id)
    if academic_year_id:
        query = query.filter(models.TahfidzExam.academic_year_id == academic_year_id)
    
    return query.order_by(models.TahfidzExam.created_at.desc()).all()

@app.post("/tahfidz/exams", response_model=schemas.TahfidzExam)
async def create_tahfidz_exam(exam: schemas.TahfidzExamCreate, db: Session = Depends(get_db)):
    db_exam = models.TahfidzExam(**exam.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

@app.post("/auth/change-password")
async def change_password(request: schemas.ChangePasswordRequest, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not auth.verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Password lama salah")
        
    current_user.password_hash = auth.get_password_hash(request.new_password)
    current_user.must_change_password = False
    db.commit()
    return {"message": "Password berhasil diubah"}
