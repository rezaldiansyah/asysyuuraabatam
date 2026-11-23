import os
import json
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import models

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "smpit_schedules.json")

def seed_smpit_data(db: Session, force: bool = False):
    """Seed SMPIT academic year, unit, classrooms, subjects, teachers, and schedules."""
    if not os.path.exists(DATA_PATH):
        print(f"[Seed SMPIT] Data file not found: {DATA_PATH}")
        return {"status": "error", "message": "Data file not found"}

    with open(DATA_PATH, "r") as f:
        schedules_data = json.load(f)

    # 1. Academic Year: 2026/2027 Ganjil
    ay = db.query(models.AcademicYear).filter(
        models.AcademicYear.name == "2026/2027",
        models.AcademicYear.semester == "Ganjil"
    ).first()
    if not ay:
        ay = models.AcademicYear(name="2026/2027", semester="Ganjil", is_active=True)
        db.add(ay)
        db.flush()
        print("[Seed SMPIT] Created Academic Year 2026/2027 Ganjil")
    else:
        # Activate it if not active
        if not ay.is_active:
            db.query(models.AcademicYear).update({"is_active": False})
            ay.is_active = True
            db.flush()
            print("[Seed SMPIT] Activated Academic Year 2026/2027 Ganjil")

    # 2. Unit SMPIT
    smpit_unit = db.query(models.Unit).filter(
        (models.Unit.code == "SMPIT") | (models.Unit.name.like("%SMPIT%"))
    ).first()
    if not smpit_unit:
        smpit_unit = models.Unit(name="SMPIT Asy-Syuuraa", code="SMPIT")
        db.add(smpit_unit)
        db.flush()
        print("[Seed SMPIT] Created Unit SMPIT Asy-Syuuraa")

    # 3. Classrooms
    classrooms_map = {}
    class_specs = [
        {"name": "VII", "level": 7, "homeroom_nik": "1220220155"},  # Astina Marru Kirama Baifar, S.Pd
        {"name": "VIII", "level": 8, "homeroom_nik": "1220250179"}, # Nurmatin Khanifah, S.H
        {"name": "IX-A", "level": 9, "homeroom_nik": "1220140051"}, # Lismanizar, S.Si
        {"name": "IX-B", "level": 9, "homeroom_nik": "1220240172"}, # Permadi, S.Sos
    ]
    for cs in class_specs:
        cr = db.query(models.Classroom).filter(
            models.Classroom.unit_id == smpit_unit.id,
            models.Classroom.name == cs["name"]
        ).first()

        hr_user = None
        if cs.get("homeroom_nik"):
            emp = db.query(models.Employee).filter(models.Employee.nik == cs["homeroom_nik"]).first()
            if emp:
                hr_user = db.query(models.User).filter(models.User.id == emp.user_id).first()
                if not hr_user:
                    hr_user = db.query(models.User).filter(models.User.email == emp.email).first()

        if not cr:
            cr = models.Classroom(
                name=cs["name"],
                level=cs["level"],
                unit_id=smpit_unit.id,
                academic_year_id=ay.id,
                homeroom_teacher_id=hr_user.id if hr_user else None
            )
            db.add(cr)
            db.flush()
            print(f"[Seed SMPIT] Created Classroom {cr.name}")
        else:
            updated = False
            if cr.academic_year_id != ay.id or cr.level != cs["level"]:
                cr.academic_year_id = ay.id
                cr.level = cs["level"]
                updated = True
            if hr_user and cr.homeroom_teacher_id != hr_user.id:
                cr.homeroom_teacher_id = hr_user.id
                updated = True
            if updated:
                db.flush()
        classrooms_map[cs["name"]] = cr

    # 4. Subjects
    subjects_map = {}
    for item in schedules_data:
        code = item["subject_code"]
        name = item["subject_name"]
        if code not in subjects_map:
            subj = db.query(models.Subject).filter(
                models.Subject.unit_id == smpit_unit.id,
                (models.Subject.code == code) | (models.Subject.name == name)
            ).first()
            if not subj:
                subj = models.Subject(
                    name=name,
                    code=code,
                    unit_id=smpit_unit.id
                )
                db.add(subj)
                db.flush()
                print(f"[Seed SMPIT] Created Subject {subj.name} ({subj.code})")
            subjects_map[code] = subj

    # 5. Teachers
    teachers_map = {}
    default_pw = bcrypt.hash("Bismillah123!")
    guru_role = db.query(models.Role).filter(models.Role.code == "guru").first()
    guru_role_id = guru_role.id if guru_role else 6

    for item in schedules_data:
        nik = item["teacher_nik"]
        name = item["teacher_name"]
        email = item["teacher_email"]
        if nik not in teachers_map:
            user = db.query(models.User).filter(
                (models.User.nik == nik) | (models.User.email == email)
            ).first()
            if not user:
                # Also try matching by name
                user = db.query(models.User).filter(
                    models.User.full_name.like(f"%{name.split(',')[0]}%")
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
                print(f"[Seed SMPIT] Created User Guru {user.full_name}")

            # Ensure Employee profile
            emp = db.query(models.Employee).filter(models.Employee.user_id == user.id).first()
            if not emp:
                emp = models.Employee(
                    user_id=user.id,
                    nama_lengkap=user.full_name,
                    nik_kepegawaian=user.nik,
                    nip=user.nik,
                    unit_id=smpit_unit.id,
                    employee_type="tetap",
                    position="Guru Bidang Studi"
                )
                db.add(emp)
                db.flush()
            teachers_map[nik] = user

    # 6. Schedules
    smp_cr_ids = [c.id for c in classrooms_map.values()]
    existing_count = db.query(models.Schedule).filter(
        models.Schedule.academic_year_id == ay.id,
        models.Schedule.classroom_id.in_(smp_cr_ids)
    ).count()

    if existing_count > 0 and not force:
        print(f"[Seed SMPIT] {existing_count} schedules already exist for SMPIT. Skipping seed.")
        db.commit()
        return {
            "status": "skipped",
            "message": f"{existing_count} schedules already exist.",
            "count": existing_count
        }

    if force:
        db.query(models.Schedule).filter(
            models.Schedule.academic_year_id == ay.id,
            models.Schedule.classroom_id.in_(smp_cr_ids)
        ).delete(synchronize_session=False)
        db.flush()

    inserted_count = 0
    for item in schedules_data:
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
            inserted_count += 1

    db.commit()
    print(f"[Seed SMPIT] Successfully seeded {inserted_count} schedules for SMPIT!")
    return {
        "status": "success",
        "message": f"Successfully seeded {inserted_count} schedules for SMPIT.",
        "count": inserted_count
    }
