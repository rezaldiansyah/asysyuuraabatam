import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
import models

logger = logging.getLogger(__name__)

def merge_employee_and_user_pair(
    db: Session,
    target_label: str,
    canonical_name: str,
    canonical_nik: str,
    name_keywords: list,
    nik_list: list
):
    """Safely merge duplicate employee and user records into one canonical profile."""
    # 1. Find all matching users
    user_query = db.query(models.User)
    user_conditions = [models.User.nik.in_(nik_list)]
    for kw in name_keywords:
        user_conditions.append(models.User.full_name.ilike(f"%{kw}%"))
    from sqlalchemy import or_
    matching_users = db.query(models.User).filter(or_(*user_conditions)).all()

    # 2. Find all matching employees
    emp_conditions = [models.Employee.nik_kepegawaian.in_(nik_list)]
    for kw in name_keywords:
        emp_conditions.append(models.Employee.nama_lengkap.ilike(f"%{kw}%"))
    matching_employees = db.query(models.Employee).filter(or_(*emp_conditions)).all()

    print(f"[{target_label}] Found {len(matching_users)} users and {len(matching_employees)} employees.")

    if not matching_employees and not matching_users:
        print(f"[{target_label}] No records found to merge.")
        return

    # Determine primary employee: prefer one with attendance records or with canonical NIK
    primary_emp = None
    if matching_employees:
        # Sort by attendance count descending, then canonical NIK, then lowest ID
        def emp_priority(e):
            att_count = len(e.attendances) if hasattr(e, "attendances") and e.attendances else 0
            is_canonical = 1 if (e.nik_kepegawaian == canonical_nik or e.nip == canonical_nik) else 0
            return (att_count, is_canonical, -e.id)

        sorted_emps = sorted(matching_employees, key=emp_priority, reverse=True)
        primary_emp = sorted_emps[0]
        secondary_emps = sorted_emps[1:]
    else:
        secondary_emps = []

    # Determine primary user
    primary_user = None
    if primary_emp and primary_emp.user_id:
        primary_user = db.query(models.User).filter(models.User.id == primary_emp.user_id).first()
    
    if not primary_user and matching_users:
        # Sort users by canonical NIK, then lowest ID
        sorted_users = sorted(
            matching_users,
            key=lambda u: (1 if u.nik == canonical_nik else 0, -u.id),
            reverse=True
        )
        primary_user = sorted_users[0]

    secondary_users = [u for u in matching_users if not primary_user or u.id != primary_user.id]

    print(f"[{target_label}] Primary Employee: ID={primary_emp.id if primary_emp else None}, Name={primary_emp.nama_lengkap if primary_emp else None}")
    print(f"[{target_label}] Primary User: ID={primary_user.id if primary_user else None}, Name={primary_user.full_name if primary_user else None}")

    # Reassign attendances and foreign keys for secondary employees
    if primary_emp:
        primary_dates = set()
        for a in primary_emp.attendances:
            if a.date:
                d_val = a.date.date() if hasattr(a.date, "date") and callable(a.date.date) else a.date
                primary_dates.add(str(d_val)[:10])

        for sec_emp in secondary_emps:
            print(f"[{target_label}] Merging secondary employee ID={sec_emp.id} ({sec_emp.nama_lengkap})...")
            # Attendances
            sec_atts = db.query(models.EmployeeAttendance).filter(models.EmployeeAttendance.employee_id == sec_emp.id).all()
            for sa in sec_atts:
                sa_d = str(sa.date.date() if hasattr(sa.date, "date") and callable(sa.date.date) else sa.date)[:10]
                if sa_d in primary_dates:
                    # Date already exists on primary employee: update primary if primary is missing check_in
                    pa = db.query(models.EmployeeAttendance).filter(
                        models.EmployeeAttendance.employee_id == primary_emp.id,
                        models.EmployeeAttendance.date == sa.date
                    ).first()
                    if pa and not pa.check_in and sa.check_in:
                        pa.check_in = sa.check_in
                        pa.check_out = sa.check_out or pa.check_out
                        pa.status = sa.status
                        pa.notes = sa.notes or pa.notes
                    db.delete(sa)
                else:
                    sa.employee_id = primary_emp.id
                    primary_dates.add(sa_d)
            db.flush()

            # Education history
            db.query(models.EducationHistory).filter(models.EducationHistory.employee_id == sec_emp.id).update(
                {"employee_id": primary_emp.id}, synchronize_session=False
            )
            # Position history
            db.query(models.PositionHistory).filter(models.PositionHistory.employee_id == sec_emp.id).update(
                {"employee_id": primary_emp.id}, synchronize_session=False
            )
            db.flush()

            # Delete secondary employee
            db.delete(sec_emp)
            db.flush()

    # Reassign schedules and user foreign keys
    if primary_user:
        for sec_user in secondary_users:
            print(f"[{target_label}] Merging secondary user ID={sec_user.id} ({sec_user.full_name})...")
            
            # Schedules
            sched_updated = db.query(models.Schedule).filter(models.Schedule.teacher_id == sec_user.id).update(
                {"teacher_id": primary_user.id}, synchronize_session=False
            )
            print(f"[{target_label}] Reassigned {sched_updated} schedules to user ID {primary_user.id}.")

            # Classroom homeroom
            cr_updated = db.query(models.Classroom).filter(models.Classroom.homeroom_teacher_id == sec_user.id).update(
                {"homeroom_teacher_id": primary_user.id}, synchronize_session=False
            )
            if cr_updated:
                print(f"[{target_label}] Reassigned {cr_updated} classrooms to user ID {primary_user.id}.")

            # Generic raw table updates for safe merge
            for tbl_col in [
                ("leave_requests", "user_id"),
                ("overtime_requests", "user_id"),
                ("meeting_notes", "notulis_id"),
                ("sdm_tasks", "creator_id"),
                ("sdm_tasks", "assignee_id"),
                ("violations", "pic_user_id"),
            ]:
                try:
                    db.execute(text(f"UPDATE {tbl_col[0]} SET {tbl_col[1]}=:prim WHERE {tbl_col[1]}=:sec"),
                               {"prim": primary_user.id, "sec": sec_user.id})
                except Exception:
                    pass

            db.flush()
            # Delete secondary user
            db.delete(sec_user)
            db.flush()

    # Finally, standardize canonical names and NIK on primary
    if primary_emp:
        primary_emp.nama_lengkap = canonical_name
        primary_emp.nik_kepegawaian = canonical_nik
        primary_emp.nip = canonical_nik
        if primary_user:
            primary_emp.user_id = primary_user.id
        db.flush()

    if primary_user:
        primary_user.full_name = canonical_name
        primary_user.nik = canonical_nik
        db.flush()

    print(f"[{target_label}] Successfully merged into: {canonical_name} (NIK: {canonical_nik})")

def merge_all_duplicates(db: Session):
    """Run all duplicate employee/teacher merges."""
    try:
        # 1. Dr. M. Tholibin Azhari
        merge_employee_and_user_pair(
            db=db,
            target_label="Tholibin",
            canonical_name="Dr. M. Tholibin Azhari, QH, S.Pd. M.Pd",
            canonical_nik="1220240177",
            name_keywords=["Tholib", "Tholibin"],
            nik_list=["1120190124", "1220240177"]
        )

        # 2. Debby Liyani Ra'ad
        merge_employee_and_user_pair(
            db=db,
            target_label="Debby",
            canonical_name="Debby Liyani Ra'ad, S.Pd., Gr.",
            canonical_nik="1120220152",
            name_keywords=["Debby", "Deby", "Liyani", "Liyany"],
            nik_list=["1120220152", "1220220158"]
        )

        db.commit()
        return {"status": "success", "message": "Successfully merged duplicate teachers."}
    except Exception as e:
        db.rollback()
        print(f"[Merge Duplicates Error]: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import sys, os
    API_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, API_DIR)
    from database import SessionLocal
    test_db = SessionLocal()
    try:
        res = merge_all_duplicates(test_db)
        print("Result:", res)
    finally:
        test_db.close()
