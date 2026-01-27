
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import models, schemas, auth
import models, schemas, auth
from database import engine, get_db
import os
import shutil
import uuid

# Create Upload Directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Asy-Syuuraa Batam API",
    description="Backend API untuk Sistem Informasi Sekolah Asy-Syuuraa Batam",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Uploads Directory
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

from jose import JWTError, jwt

# ... (imports)

# Remove "from auth import get_current_user" - handled by replacing the block or just not adding it? 
# The ReplaceFileContent targets a block. I should target the top imports to remove the line, 
# and then target the body to add the function.
# I will do it in two steps or one large block if possible.
# Let's do imports first.

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
    user = db.query(models.User).filter(models.User.nik == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
async def root():
    return {
        "message": "Welcome to Asy-Syuuraa Batam API",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "database": "connected" # TODO: Implement DB check
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

@app.post("/auth/forgot-password")
async def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "If email exists, a reset link has been sent."}
    
    token = auth.create_password_reset_token(request.email)
    # Simulate sending email
    print(f"--- PASSWORD RESET LINK ---")
    print(f"To: {request.email}")
    print(f"Link: http://localhost:3000/reset-password?token={token}")
    print(f"---------------------------")
    
    return {"message": "If email exists, a reset link has been sent."}

@app.post("/auth/reset-password")
async def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    email = auth.verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = auth.get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password has been reset successfully"}

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
async def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Simple creation for now
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/academic/classrooms", response_model=List[schemas.Classroom])
async def get_classrooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    classrooms = db.query(models.Classroom).offset(skip).limit(limit).all()
    return classrooms

@app.post("/academic/classrooms", response_model=schemas.Classroom)
async def create_classroom(classroom: schemas.ClassroomCreate, db: Session = Depends(get_db)):
    db_classroom = models.Classroom(**classroom.dict())
    db.add(db_classroom)
    db.commit()
    db.refresh(db_classroom)
    return db_classroom

@app.get("/academic/years", response_model=List[schemas.AcademicYear])
async def get_academic_years(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    years = db.query(models.AcademicYear).offset(skip).limit(limit).all()
    return years

@app.post("/academic/years", response_model=schemas.AcademicYear)
async def create_academic_year(year: schemas.AcademicYearCreate, db: Session = Depends(get_db)):
    db_year = models.AcademicYear(**year.dict())
    db.add(db_year)
    db.commit()
    db.refresh(db_year)
    return db_year

@app.get("/academic/teachers", response_model=List[schemas.Teacher])
async def get_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    if not guru_role:
        return []
    
    teachers = db.query(models.User).filter(models.User.role_id == guru_role.id).offset(skip).limit(limit).all()
    return teachers

@app.post("/academic/teachers", response_model=schemas.Teacher)
async def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    # 1. Get Guru Role
    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    if not guru_role:
        raise HTTPException(status_code=400, detail="Role 'guru' not found in system")

    # 2. Create User
    hashed_pw = auth.get_password_hash(teacher.password)
    db_user = models.User(
        email=teacher.email,
        full_name=teacher.full_name,
        nik=teacher.nik,
        password_hash=hashed_pw,
        role_id=guru_role.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 3. Assign directly to Unit (Assuming unit exists)
    db_assignment = models.UserUnit(
        user_id=db_user.id,
        unit_id=teacher.unit_id,
        is_primary=True
    )
    db.add(db_assignment)
    db.commit()

    return db_user

# --- Subject Routes ---
@app.get("/academic/subjects", response_model=List[schemas.Subject])
async def get_subjects(unit_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Subject)
    if unit_id:
        query = query.filter(models.Subject.unit_id == unit_id)
    return query.all()

@app.post("/academic/subjects", response_model=schemas.Subject)
async def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    db_subject = models.Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

# --- Schedule Routes ---
@app.get("/academic/schedules", response_model=List[schemas.Schedule])
async def get_schedules(classroom_id: Optional[int] = None, teacher_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Schedule)
    if classroom_id:
        query = query.filter(models.Schedule.classroom_id == classroom_id)
    if teacher_id:
        query = query.filter(models.Schedule.teacher_id == teacher_id)
    
    # Order by day and start time
    # Note: Sorting by Day Enum might need custom logic if not ordered in DB, but let's assume UI handles it or simple sort
    return query.all()

@app.post("/academic/schedules", response_model=schemas.Schedule)
async def create_schedule(schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)):
    try:
        # 1. Check Room Conflict
        room_conflict = db.query(models.Schedule).filter(
            models.Schedule.day == schedule.day,
            models.Schedule.classroom_id == schedule.classroom_id,
            models.Schedule.start_time < schedule.end_time,
            models.Schedule.end_time > schedule.start_time
        ).first()
        
        if room_conflict:
            raise HTTPException(status_code=400, detail=f"Room Conflict: Classroom is already booked from {room_conflict.start_time} to {room_conflict.end_time}")

        # 2. Check Teacher Conflict
        teacher_conflict = db.query(models.Schedule).filter(
            models.Schedule.day == schedule.day,
            models.Schedule.teacher_id == schedule.teacher_id,
            models.Schedule.start_time < schedule.end_time,
            models.Schedule.end_time > schedule.start_time
        ).first()

        if teacher_conflict:
            raise HTTPException(status_code=400, detail=f"Teacher Conflict: Teacher is already teaching in another class from {teacher_conflict.start_time} to {teacher_conflict.end_time}")

        db_schedule = models.Schedule(**schedule.dict())
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

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
    if not db_content:
        # Create if not exists
        db_content = models.PageContent(**content.dict())
        db.add(db_content)
    else:
        # Update
        for key, value in content.dict().items():
            setattr(db_content, key, value)
    
    db.commit()
    db.refresh(db_content)
    return db_content

@app.post("/cms/upload")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    try:
        # Create safe filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return full URL
        # In production this should be based on env var or request.base_url
        return {"url": f"http://localhost:8000/uploads/{unique_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
