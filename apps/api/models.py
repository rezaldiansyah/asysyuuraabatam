from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

# Enums
class RoleScope(str, enum.Enum):
    SISTEM = "sistem"
    YAYASAN = "yayasan"
    UNIT = "unit"
    PORTAL = "portal"

class UnitCode(str, enum.Enum):
    YYS = "YYS"
    RA = "RA"
    SDIT = "SDIT"
    SMPIT = "SMPIT"

class ScholarshipType(str, enum.Enum):
    FIXED = "FIXED" # Potongan Nominal (e.g. Rp 500.000)
    PERCENTAGE = "PERCENTAGE" # Potongan Persen (e.g. 50%)


# Models
class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)  # YYS, RA, SDIT, SMPIT
    name = Column(String)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_assignments = relationship("UserUnit", back_populates="unit")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # superadmin, guru, etc
    name = Column(String)
    scope = Column(String) # Stored as string to keep it simple, validated by Pydantic
    priority = Column(Integer, default=99)
    
    # Relationships
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String, unique=True, index=True, nullable=True) # Important for Legacy migration
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    role_id = Column(Integer, ForeignKey("roles.id"))
    
    # Relationships
    role = relationship("Role", back_populates="users")
    unit_assignments = relationship("UserUnit", back_populates="user")

class UserUnit(Base):
    __tablename__ = "user_units"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    # Relationships
    unit = relationship("Unit", back_populates="user_assignments")
    user = relationship("User", back_populates="unit_assignments")

class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # e.g., "2025/2026"
    semester = Column(String) # "Ganjil" or "Genap"
    is_active = Column(Boolean, default=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Relationships
    classrooms = relationship("Classroom", back_populates="academic_year")

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g., "1 Abu Bakar"
    level = Column(Integer) # 1, 2, 3...
    unit_id = Column(Integer, ForeignKey("units.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    homeroom_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    unit = relationship("Unit")
    academic_year = relationship("AcademicYear", back_populates="classrooms")
    homeroom_teacher = relationship("User")
    students = relationship("Student", back_populates="classroom")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nis = Column(String, unique=True, index=True, nullable=True) # Nomor Induk Sekolah
    nisn = Column(String, unique=True, index=True, nullable=True) # Nasional
    full_name = Column(String)
    gender = Column(Enum("L", "P", name="gender_enum"), default="L")
    birth_place = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    address = Column(String, nullable=True)
    
    # Status
    status = Column(Enum("ACTIVE", "GRADUATED", "MOVED", "DROPPED", name="student_status_enum"), default="ACTIVE")
    
    # Current placement
    current_classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("units.id")) # To know which unit they belong to inherently
    scholarship_id = Column(Integer, ForeignKey("scholarships.id"), nullable=True)
    
    # Relationships
    classroom = relationship("Classroom", back_populates="students")
    unit = relationship("Unit")
    scholarship = relationship("Scholarship")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # Matematika, IPA
    code = Column(String, nullable=True) # MTK, IPA
    unit_id = Column(Integer, ForeignKey("units.id"))
    
    # Relationships
    unit = relationship("Unit")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    day = Column(Enum("SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", name="day_enum"))
    start_time = Column(String) # "07:30"
    end_time = Column(String) # "09:00"
    
    # Relationships
    academic_year = relationship("AcademicYear")
    classroom = relationship("Classroom")
    subject = relationship("Subject")
    teacher = relationship("User")

# --- Finance Models ---

class Scholarship(Base):
    __tablename__ = "scholarships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # "Beasiswa Yatim", "Anak Guru"
    type = Column(Enum(ScholarshipType), default=ScholarshipType.PERCENTAGE)
    value = Column(Integer) # 50 (for 50%) or 500000 (for Rp 500k)
    is_active = Column(Boolean, default=True)
    
    students = relationship("Student", back_populates="scholarship")

class PaymentCategory(Base):
    __tablename__ = "payment_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # SPP, Uang Gedung, Seragam
    amount = Column(Integer, default=0) # Default nominal
    type = Column(Enum("MONTHLY", "ONE_TIME", name="payment_type_enum"), default="MONTHLY")
    is_scholarship_eligible = Column(Boolean, default=True) # Whether scholarship applies to this category

    
    # Accounting Link
    income_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    
    # Relationships
    bills = relationship("StudentBill", back_populates="category")
    income_account = relationship("Account", back_populates="payment_categories")

class StudentBill(Base):
    __tablename__ = "student_bills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    category_id = Column(Integer, ForeignKey("payment_categories.id"))
    
    title = Column(String) # "SPP Januari 2026"
    amount = Column(Integer) # Total tagihan
    status = Column(Enum("UNPAID", "PARTIAL", "PAID", name="bill_status_enum"), default="UNPAID")
    due_date = Column(DateTime, nullable=True) # Jatuh tempo
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")
    category = relationship("PaymentCategory", back_populates="bills")
    transactions = relationship("PaymentTransaction", back_populates="bill")

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("student_bills.id"))
    
    amount_paid = Column(Integer)
    payment_date = Column(DateTime, default=datetime.utcnow)
    method = Column(String, default="CASH") # CASH, TRANSFER
    notes = Column(String, nullable=True)
    
    bill = relationship("StudentBill", back_populates="transactions")

# --- Accounting Models ---

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # 1-1000
    name = Column(String) # Kas di Tangan
    type = Column(Enum("ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE", name="account_type_enum"))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    payment_categories = relationship("PaymentCategory", back_populates="income_account")
    journal_items = relationship("JournalItem", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
    reference_id = Column(String, nullable=True) # PaymentTransaction ID or similar
    total_amount = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship("JournalItem", back_populates="journal")

class JournalItem(Base):
    __tablename__ = "journal_items"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    
    debit = Column(Integer, default=0)
    credit = Column(Integer, default=0)
    
    # Relationships
    journal = relationship("JournalEntry", back_populates="items")
    account = relationship("Account", back_populates="journal_items")

# --- CMS Models ---

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    slug = Column(String, unique=True, index=True)
    content = Column(String) # Text/HTML
    image_url = Column(String, nullable=True)
    is_published = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User")

class PageContent(Base):
    __tablename__ = "page_contents"
    
    section_key = Column(String, primary_key=True, index=True) # e.g. "home_hero"
    title = Column(String, nullable=True)
    subtitle = Column(String, nullable=True)
    body = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    cta_text = Column(String, nullable=True)
    cta_link = Column(String, nullable=True)
    content_json = Column(String, nullable=True) # JSON String for arrays (Features, Testimonials)


# Update PaymentCategory to link to Account
# Note: Since PaymentCategory is already defined above, we normally would put Account above it or use string reference.
# But PaymentCategory is already defined in previous edits. I need to UPDATE PaymentCategory definition.
# Since I cannot easily "move" code with replace_file_content, I will rely on Python's behavior or re-define if needed.
# However, `PaymentCategory` was defined in lines 156-165. I should probably edit THAT block instead of appending.
# Wait, I can't look back at the file content in this turn easily without another tool call if I wasn't careful.
# But I know I just added it.
# Let's Modify the PaymentCategory definition first, then add the others.
# Actually, I will just ADD the new models at the end, and then modify PaymentCategory separately or use string forward ref.
# String forward ref `income_account = relationship("Account")` works even if Account is defined later.
# But I need to add the Column `income_account_id`.

# --- SDM/Employee Models ---

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"   # Hadir
    SICK = "SICK"         # Sakit
    PERMIT = "PERMIT"     # Izin
    ABSENT = "ABSENT"     # Alpa

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Employee specific fields
    nip = Column(String, unique=True, index=True, nullable=True)  # Nomor Induk Pegawai
    nuptk = Column(String, unique=True, index=True, nullable=True)  # NUPTK for teachers
    position = Column(String, nullable=True)  # Jabatan: Guru, Staff, etc.
    join_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")
    attendances = relationship("EmployeeAttendance", back_populates="employee")

class StudentAttendance(Base):
    __tablename__ = "student_attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(DateTime, index=True)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")

class EmployeeAttendance(Base):
    __tablename__ = "employee_attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(DateTime, index=True)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendances")

# --- Academic Grade Models ---

class GradeType(str, enum.Enum):
    QUIZ = "QUIZ"           # Ulangan Harian
    MIDTERM = "MIDTERM"     # UTS
    FINAL = "FINAL"         # UAS
    ASSIGNMENT = "ASSIGNMENT"  # Tugas
    PRACTICE = "PRACTICE"   # Praktik

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    
    type = Column(Enum(GradeType), default=GradeType.QUIZ)
    score = Column(Integer, default=0)  # 0-100
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")
    subject = relationship("Subject")
    academic_year = relationship("AcademicYear")

class AttitudeGrade(Base):
    __tablename__ = "attitude_grades"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    
    spiritual = Column(String, default="B")  # A, B, C
    social = Column(String, default="B")     # A, B, C
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")
    academic_year = relationship("AcademicYear")

# --- Tahfidz Models ---

class MemorizationType(str, enum.Enum):
    QURAN = "QURAN"     # Al-Quran tahfidz
    MUTUN = "MUTUN"     # Kitab/Nazham (Urjuzah Mi'iyah, etc.)

class TahfidzProgress(Base):
    __tablename__ = "tahfidz_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(DateTime, index=True)
    
    type = Column(Enum(MemorizationType), default=MemorizationType.QURAN)
    new_memorization = Column(String)  # Hafalan baru (surah name / bab kitab)
    review = Column(String, nullable=True)  # Murojaah
    kitab_name = Column(String, nullable=True)  # For MUTUN type: Urjuzah Mi'iyah, etc.
    score = Column(Integer, default=0)  # 0-100
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")

class TahfidzExam(Base):
    __tablename__ = "tahfidz_exams"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"))
    
    type = Column(Enum(MemorizationType), default=MemorizationType.QURAN)
    surah_from = Column(String, nullable=True)  # Start range
    surah_to = Column(String, nullable=True)    # End range
    kitab_name = Column(String, nullable=True)  # For MUTUN
    score = Column(Integer, default=0)
    notes = Column(String, nullable=True)
    exam_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("Student")
    academic_year = relationship("AcademicYear")
