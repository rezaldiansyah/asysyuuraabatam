from database import SessionLocal
from models import PaymentCategory, Classroom, Student, Scholarship, ScholarshipType, Unit, AcademicYear
from datetime import datetime

db = SessionLocal()

# 0. Create Academic Year
academic_year = AcademicYear(name="2025/2026", semester="Ganjil", is_active=True)
db.add(academic_year)
db.commit()
db.refresh(academic_year)
print(f"Created AcademicYear: {academic_year.id}")

# 1. Create Scholarship
scholarship = Scholarship(name="Test Scholarship", type=ScholarshipType.PERCENTAGE, value=50, is_active=True)
db.add(scholarship)
db.commit()
db.refresh(scholarship)
print(f"Created Scholarship: {scholarship.id}")

# 2. Create Category
category = PaymentCategory(name="SPP Test", amount=100000, type="MONTHLY", is_scholarship_eligible=True)
db.add(category)
db.commit()
db.refresh(category)
print(f"Created Category: {category.id}")

# 3. Create Classroom
classroom = Classroom(name="1A Test", level=1, unit_id=3, academic_year_id=academic_year.id) # SDIT
db.add(classroom)
db.commit()
db.refresh(classroom)
print(f"Created Classroom: {classroom.id}")

# 4. Create Student with Scholarship
student1 = Student(
    full_name="Student With Scholarship", 
    unit_id=3, 
    current_classroom_id=classroom.id, 
    scholarship_id=scholarship.id,
    status="ACTIVE",
    nis="1001",
    gender="L"
)
db.add(student1)
db.commit()
db.refresh(student1)
print(f"Created Student1: {student1.id}")

# 5. Create Student without Scholarship
student2 = Student(
    full_name="Student No Scholarship", 
    unit_id=3, 
    current_classroom_id=classroom.id, 
    status="ACTIVE",
    nis="1002",
    gender="P"
)
db.add(student2)
db.commit()
db.refresh(student2)
print(f"Created Student2: {student2.id}")
