from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import date, datetime

class UserLogin(BaseModel):
    username: str # NIK/Email/Username
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- User/Teacher Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: str
    nik: Optional[str] = None

class TeacherCreate(UserBase):
    unit_id: int
    password: str # Initial password

class User(UserBase):
    id: int
    is_active: bool
    role_id: int
    
    class Config:
        from_attributes = True

class Teacher(User):
    # For response, might want to include unit info later
    pass

# --- Academic/Schedule Schemas ---
class SubjectBase(BaseModel):
    name: str # Matematika
    code: Optional[str] = None # MTK
    unit_id: int

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int

    class Config:
        from_attributes = True

class ScheduleBase(BaseModel):
    academic_year_id: int
    classroom_id: int
    subject_id: int
    teacher_id: int
    day: str # SENIN, SELASA...
    start_time: str # 07:30
    end_time: str # 09:00

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    academic_year_id: int # Relationships
    
    # We might want nested objects for the list view
    subject: Optional[Subject] = None
    teacher: Optional[Teacher] = None
    
    teacher: Optional[Teacher] = None
    
    class Config:
        from_attributes = True

# --- Finance Schemas ---
# Accounting Schemas
class AccountBase(BaseModel):
    code: str
    name: str
    type: str # ASSET, REVENUE, etc
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    class Config:
        from_attributes = True

class JournalItemBase(BaseModel):
    account_id: int
    debit: int = 0
    credit: int = 0

class JournalEntryBase(BaseModel):
    date: datetime
    description: str
    reference_id: Optional[str] = None
    total_amount: int

class JournalEntry(JournalEntryBase):
    id: int
    items: List["JournalItem"] = []
    class Config:
        from_attributes = True

class JournalItem(JournalItemBase):
    id: int
    account: Optional[Account] = None
    class Config:
        from_attributes = True

# --- Scholarship Schemas ---
class ScholarshipBase(BaseModel):
    name: str
    type: str # FIXED, PERCENTAGE
    value: int
    is_active: bool = True

class ScholarshipCreate(ScholarshipBase):
    pass

class Scholarship(ScholarshipBase):
    id: int
    class Config:
        from_attributes = True


# --- CMS Schemas ---
class PostBase(BaseModel):
    title: str
    slug: str
    content: str
    image_url: Optional[str] = None
    is_published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    # author: User (Circular import issue, can skip for now or use minimalist User)
    
    class Config:
        from_attributes = True

class PageContentBase(BaseModel):
    section_key: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[str] = None
    cta_text: Optional[str] = None
    cta_link: Optional[str] = None
    content_json: Optional[str] = None

class PageContentCreate(PageContentBase):
    pass

class PageContent(PageContentBase):
    class Config:
        from_attributes = True

JournalEntry.model_rebuild()

class PaymentCategoryBase(BaseModel):
    name: str
    amount: int
    type: str # MONTHLY, ONE_TIME
    is_scholarship_eligible: bool = True
    income_account_id: Optional[int] = None # Link to Account


class PaymentCategoryCreate(PaymentCategoryBase):
    pass

class PaymentCategory(PaymentCategoryBase):
    id: int
    income_account: Optional[Account] = None

    class Config:
        from_attributes = True

class StudentBillBase(BaseModel):
    student_id: int
    category_id: int
    title: str
    amount: int
    status: str = "UNPAID"
    due_date: Optional[datetime] = None

class StudentBillCreate(StudentBillBase):
    pass

class StudentBill(StudentBillBase):
    id: int
    created_at: datetime
    
    category: Optional[PaymentCategory] = None
    student: Optional["Student"] = None
    
    class Config:
        from_attributes = True

# --- Bulk Billing Schemas ---
class BulkBillPreviewRequest(BaseModel):
    classroom_id: int
    category_id: int
    title: str
    due_date: Optional[datetime] = None

class BulkBillItem(BaseModel):
    student_id: int
    amount: int
    title: str

class BulkBillPreviewResponse(BaseModel):
    student_id: int
    student_name: str
    original_amount: int
    scholarship_name: Optional[str] = None
    discount_amount: int
    final_amount: int

class BulkBillCreateRequest(BaseModel):
    category_id: int
    items: List[BulkBillItem]
    due_date: Optional[datetime] = None

class PaymentTransactionBase(BaseModel):
    bill_id: int
    amount_paid: int
    method: str = "CASH"
    notes: Optional[str] = None

class PaymentTransactionCreate(PaymentTransactionBase):
    pass

class PaymentTransaction(PaymentTransactionBase):
    id: int
    payment_date: datetime
    
    class Config:
        from_attributes = True

# --- General Schemas ---
class UnitBase(BaseModel):
    code: str
    name: str

class Unit(UnitBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# Enums (Mirroring models.py)
class GenderEnum(str, Enum):
    L = "L"
    P = "P"

class StudentStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    GRADUATED = "GRADUATED"
    MOVED = "MOVED"
    DROPPED = "DROPPED"

# --- Academic Schemas ---

# Student
class StudentBase(BaseModel):
    nis: Optional[str] = None
    nisn: Optional[str] = None
    full_name: str
    gender: GenderEnum = GenderEnum.L
    birth_place: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    unit_id: int
    unit_id: int
    current_classroom_id: Optional[int] = None
    scholarship_id: Optional[int] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    full_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    unit_id: Optional[int] = None

class Student(StudentBase):
    id: int
    status: StudentStatusEnum
    scholarship: Optional[Scholarship] = None
    created_at: Optional[datetime] = None # If we had it, but we didn't add it in model.

    
    class Config:
        from_attributes = True

# Classroom
class ClassroomBase(BaseModel):
    name: str
    level: int
    unit_id: int
    academic_year_id: int
    homeroom_teacher_id: Optional[int] = None

class ClassroomCreate(ClassroomBase):
    pass

class Classroom(ClassroomBase):
    id: int
    
    class Config:
        from_attributes = True

# Academic Year
class AcademicYearBase(BaseModel):
    name: str
    semester: str
    is_active: bool = False
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class AcademicYearCreate(AcademicYearBase):
    pass

class AcademicYear(AcademicYearBase):
    id: int
    
    class Config:
        from_attributes = True
StudentBill.model_rebuild()

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
