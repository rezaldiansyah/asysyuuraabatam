import logging
from sqlalchemy.orm import Session
import models

logger = logging.getLogger(__name__)

def deduplicate_academic_data(db: Session):
    """
    Find and merge any duplicate classrooms and subjects across all units.
    Ensures that for any given unit, academic year, and classroom name, only 1 record exists.
    Ensures that for any given unit and subject code/name, only 1 record exists.
    Reassigns all foreign key references (schedules, students, grades) to the primary record before deleting duplicates.
    """
    print("[Deduplicate] Starting academic data deduplication...")

    # 1. Deduplicate Classrooms
    # Order by ID asc so the earliest inserted record is kept as primary
    all_classrooms = db.query(models.Classroom).order_by(models.Classroom.id.asc()).all()
    seen_cr = {} # (unit_id, name.strip().upper(), academic_year_id) -> primary_classroom
    deleted_cr_count = 0

    for cr in all_classrooms:
        key = (cr.unit_id, (cr.name or "").strip().upper(), cr.academic_year_id)
        if key not in seen_cr:
            seen_cr[key] = cr
        else:
            primary_cr = seen_cr[key]
            # Duplicate found!
            # Reassign schedules pointing to duplicate classroom
            s_up = db.query(models.Schedule).filter(models.Schedule.classroom_id == cr.id).update(
                {"classroom_id": primary_cr.id}, synchronize_session=False
            )
            # Reassign students pointing to duplicate classroom
            st_up = db.query(models.Student).filter(models.Student.current_classroom_id == cr.id).update(
                {"current_classroom_id": primary_cr.id}, synchronize_session=False
            )
            db.flush()

            # Safely delete duplicate classroom
            try:
                with db.begin_nested():
                    db.delete(cr)
                    db.flush()
                deleted_cr_count += 1
                print(f"[Deduplicate] Merged classroom '{cr.name}' (ID={cr.id}) into ID={primary_cr.id} (reassigned {s_up} schedules, {st_up} students)")
            except Exception as e:
                print(f"[Deduplicate] Warning: could not delete duplicate classroom ID={cr.id}: {e}")

    # 2. Deduplicate Subjects
    # Order by ID asc so earliest is primary
    all_subjects = db.query(models.Subject).order_by(models.Subject.id.asc()).all()
    seen_subj_code = {} # (unit_id, code.strip().upper()) -> primary_subject
    seen_subj_name = {} # (unit_id, name.strip().upper()) -> primary_subject
    deleted_subj_count = 0

    for sb in all_subjects:
        c_key = (sb.unit_id, (sb.code or "").strip().upper())
        n_key = (sb.unit_id, (sb.name or "").strip().upper())

        primary_sb = seen_subj_code.get(c_key) or seen_subj_name.get(n_key)

        if not primary_sb:
            seen_subj_code[c_key] = sb
            seen_subj_name[n_key] = sb
        else:
            # Duplicate found!
            # Reassign schedules
            s_up = db.query(models.Schedule).filter(models.Schedule.subject_id == sb.id).update(
                {"subject_id": primary_sb.id}, synchronize_session=False
            )
            # Reassign grades if any
            g_up = db.query(models.Grade).filter(models.Grade.subject_id == sb.id).update(
                {"subject_id": primary_sb.id}, synchronize_session=False
            )
            db.flush()

            # Safely delete duplicate subject
            try:
                with db.begin_nested():
                    db.delete(sb)
                    db.flush()
                deleted_subj_count += 1
                print(f"[Deduplicate] Merged subject '{sb.name}' ({sb.code}) (ID={sb.id}) into ID={primary_sb.id} (reassigned {s_up} schedules, {g_up} grades)")
            except Exception as e:
                print(f"[Deduplicate] Warning: could not delete duplicate subject ID={sb.id}: {e}")

    db.commit()
    print(f"[Deduplicate] Summary: {deleted_cr_count} duplicate classrooms and {deleted_subj_count} duplicate subjects removed.")
    return {
        "status": "success",
        "deleted_classrooms": deleted_cr_count,
        "deleted_subjects": deleted_subj_count
    }

if __name__ == "__main__":
    import sys, os
    API_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, API_DIR)
    from database import SessionLocal
    db = SessionLocal()
    try:
        res = deduplicate_academic_data(db)
        print("Result:", res)
    finally:
        db.close()
