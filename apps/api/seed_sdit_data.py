import os
import json
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import models

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sdit_data.json")

def seed_sdit_data(db: Session, force: bool = False):
    """Seed SDIT academic year, unit, classrooms, subjects, teachers, students, and schedules."""
    if not os.path.exists(DATA_PATH):
        print(f"[Seed SDIT] Data file not found: {DATA_PATH}")
        return {"status": "error", "message": "Data file not found"}

    with open(DATA_PATH, "r") as f:
        payload = json.load(f)

    unit_spec = payload.get("unit", {"name": "SDIT Asy-Syuuraa", "code": "SDIT"})
    classrooms_spec = payload.get("classrooms", [])
    subjects_spec = payload.get("subjects", [])
    teachers_spec = payload.get("teachers", [])
    students_spec = payload.get("students", [])
    schedules_spec = payload.get("schedules", [])

    # 1. Academic Year: 2026/2027 Ganjil
    ay = db.query(models.AcademicYear).filter(
        models.AcademicYear.name == "2026/2027",
        models.AcademicYear.semester == "Ganjil"
    ).first()
    if not ay:
        ay = models.AcademicYear(name="2026/2027", semester="Ganjil", is_active=True)
        db.add(ay)
        db.flush()
        print("[Seed SDIT] Created Academic Year 2026/2027 Ganjil")
    else:
        if not ay.is_active:
            db.query(models.AcademicYear).update({"is_active": False})
            ay.is_active = True
            db.flush()

    # 2. Unit SDIT
    sdit_unit = db.query(models.Unit).filter(
        (models.Unit.code == "SDIT") | (models.Unit.name.like("%SDIT%"))
    ).first()
    if not sdit_unit:
        sdit_unit = models.Unit(name=unit_spec["name"], code=unit_spec["code"])
        db.add(sdit_unit)
        db.flush()
        print(f"[Seed SDIT] Created Unit {sdit_unit.name}")

    # 3. Teachers & Employees
    teachers_map = {} # nik -> User
    teachers_by_key = {} # wali_key (e.g. 'Reni') -> User
    
    # Generate default password hash safely with bcrypt
    import bcrypt as _bc
    default_pw = _bc.hashpw(b"Bismillah123!", _bc.gensalt()).decode("utf-8")

    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    guru_role_id = guru_role.id if guru_role else 6

    for item in teachers_spec:
        nik = item["nik"]
        name = item["name"]
        email = item["email"]

        user = db.query(models.User).filter(
            (models.User.nik == nik) | (models.User.email == email)
        ).first()
        if not user:
            first_word = name.split()[0].replace(',', '')
            user = db.query(models.User).filter(
                models.User.full_name.ilike(f"%{first_word}%")
            ).first()

        if not user:
            user = models.User(
                nik=nik,
                email=email,
                full_name=name,
                password_hash=default_pw,
                is_active=True,
                role_id=guru_role_id
            )
            db.add(user)
            db.flush()
            print(f"[Seed SDIT] Created Teacher User {user.full_name} ({user.nik})")
        else:
            if not user.nik:
                user.nik = nik
                db.flush()

        # Employee profile
        emp = db.query(models.Employee).filter(models.Employee.user_id == user.id).first()
        if not emp:
            emp = models.Employee(
                user_id=user.id,
                nama_lengkap=user.full_name,
                nik_kepegawaian=user.nik or nik,
                nip=user.nik or nik,
                unit_id=sdit_unit.id,
                employee_type="tetap",
                position="Guru SDIT"
            )
            db.add(emp)
            db.flush()

        teachers_map[nik] = user

    # 4. Classrooms
    classrooms_map = {} # name -> Classroom
    for cs in classrooms_spec:
        wali_key = cs.get("wali_key")
        # Find wali user by partial match on name or known key
        wali_user = None
        for u in teachers_map.values():
            if wali_key and wali_key.lower() in u.full_name.lower():
                wali_user = u
                break

        cr = db.query(models.Classroom).filter(
            models.Classroom.unit_id == sdit_unit.id,
            models.Classroom.name == cs["name"]
        ).first()

        if not cr:
            cr = models.Classroom(
                name=cs["name"],
                level=cs["level"],
                unit_id=sdit_unit.id,
                academic_year_id=ay.id,
                homeroom_teacher_id=wali_user.id if wali_user else None
            )
            db.add(cr)
            db.flush()
            print(f"[Seed SDIT] Created Classroom {cr.name} (Level {cr.level})")
        else:
            cr.level = cs["level"]
            cr.academic_year_id = ay.id
            if wali_user and not cr.homeroom_teacher_id:
                cr.homeroom_teacher_id = wali_user.id
            db.flush()

        classrooms_map[cs["name"]] = cr

    # 5. Subjects
    subjects_map = {} # code -> Subject
    for item in subjects_spec:
        code = item["code"]
        name = item["name"]
        subj = db.query(models.Subject).filter(
            models.Subject.unit_id == sdit_unit.id,
            (models.Subject.code == code) | (models.Subject.name == name)
        ).first()
        if not subj:
            subj = models.Subject(
                name=name,
                code=code,
                unit_id=sdit_unit.id
            )
            db.add(subj)
            db.flush()
            print(f"[Seed SDIT] Created Subject {subj.name} ({subj.code})")
        subjects_map[code] = subj

    # 6. Students (252 pupils)
    student_count = 0
    seen_nis = set()

    for st in students_spec:
        nis = st.get("nis")
        nisn = st.get("nisn")
        nama = st.get("name")
        gender = st.get("gender", "L")
        pob = st.get("birth_place")
        dob_str = st.get("birth_date")
        cr_name = st.get("classroom")

        if nis:
            if nis in seen_nis:
                # Disambiguate duplicate NIS from document typo
                nis = f"{nis}-B"
            seen_nis.add(nis)

        cr = classrooms_map.get(cr_name)

        dob = None
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d")
            except Exception:
                dob = None

        student = None
        if nis:
            student = db.query(models.Student).filter(models.Student.nis == nis).first()
        if not student and nisn:
            student = db.query(models.Student).filter(models.Student.nisn == nisn).first()
        if not student and nama:
            student = db.query(models.Student).filter(
                models.Student.unit_id == sdit_unit.id,
                models.Student.full_name == nama
            ).first()

        if not student:
            student = models.Student(
                nis=nis,
                nisn=nisn,
                full_name=nama,
                gender=gender,
                birth_place=pob,
                birth_date=dob,
                status="ACTIVE",
                current_classroom_id=cr.id if cr else None,
                unit_id=sdit_unit.id
            )
            db.add(student)
            student_count += 1
        else:
            if cr and student.current_classroom_id != cr.id:
                student.current_classroom_id = cr.id
            if not student.unit_id:
                student.unit_id = sdit_unit.id
            db.flush()

    db.flush()
    print(f"[Seed SDIT] Seeded {student_count} new students (Total dataset: {len(students_spec)})")

    # 7. Schedules
    sdit_cr_ids = [c.id for c in classrooms_map.values()]
    existing_scheds = db.query(models.Schedule).filter(
        models.Schedule.academic_year_id == ay.id,
        models.Schedule.classroom_id.in_(sdit_cr_ids)
    ).count()

    if existing_scheds > 0 and not force:
        print(f"[Seed SDIT] {existing_scheds} schedules already exist for SDIT. Skipping schedule injection.")
        db.commit()
        return {
            "status": "partial_success",
            "message": f"Classrooms, subjects, and students seeded. Schedules already existed ({existing_scheds} items).",
            "students_count": len(students_spec),
            "schedules_count": existing_scheds
        }

    if force:
        db.query(models.Schedule).filter(
            models.Schedule.academic_year_id == ay.id,
            models.Schedule.classroom_id.in_(sdit_cr_ids)
        ).delete(synchronize_session=False)
        db.flush()

    inserted_sched_count = 0
    for item in schedules_spec:
        cr = classrooms_map.get(item["classroom_name"])
        subj = subjects_map.get(item["subject_code"])
        teacher = teachers_map.get(item["teacher_nik"])

        if cr and subj and teacher:
            sched = models.Schedule(
                academic_year_id=ay.id,
                classroom_id=cr.id,
                subject_id=subj.id,
                teacher_id=teacher.id,
                day=item["day"],
                start_time=item["start_time"],
                end_time=item["end_time"]
            )
            db.add(sched)
            inserted_sched_count += 1

    db.commit()
    print(f"[Seed SDIT] Successfully seeded {inserted_sched_count} schedules for SDIT!")
    return {
        "status": "success",
        "message": f"Successfully seeded {len(students_spec)} students and {inserted_sched_count} schedules for SDIT.",
        "students_count": len(students_spec),
        "schedules_count": inserted_sched_count
    }
