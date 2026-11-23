import os
import sys
import re
from datetime import datetime

# Set up paths
API_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, API_DIR)
os.chdir(API_DIR)
from database import SessionLocal, engine
import models

EXCEL_PATH = "/Users/rezaaldi/Downloads/file asy syuuraa/RENCANA KEBUTUHAN - PEMETAAN - JADWAL PELAJARAN subsidi silang sdit.xlsx"

def clean_time(time_str: str):
    """Convert '07.15 - 07.55' into ('07:15', '07:55')"""
    if not time_str or '-' not in time_str:
        return None, None
    parts = time_str.split('-')
    start = parts[0].strip().replace('.', ':')
    end = parts[1].strip().replace('.', ':')
    # Pad to HH:MM if needed
    if len(start) == 4 and start[1] == ':':
        start = '0' + start
    if len(end) == 4 and end[1] == ':':
        end = '0' + end
    return start, end

def run_injection():
    import openpyxl
    
    db = SessionLocal()
    print("=== STARTING SMPIT SCHEDULE INJECTION ===")
    
    # 1. Academic Year: 2026/2027 Ganjil
    ay = db.query(models.AcademicYear).filter(
        models.AcademicYear.name == "2026/2027",
        models.AcademicYear.semester == "Ganjil"
    ).first()
    if not ay:
        ay = models.AcademicYear(name="2026/2027", semester="Ganjil", is_active=True)
        db.add(ay)
        db.flush()
        print("Created Academic Year: 2026/2027 Ganjil")
    else:
        # Deactivate all others, activate this one
        db.query(models.AcademicYear).update({"is_active": False})
        ay.is_active = True
        db.flush()
        print(f"Activated Academic Year: 2026/2027 Ganjil (ID: {ay.id})")

    # 2. Unit SMPIT
    smpit_unit = db.query(models.Unit).filter(
        (models.Unit.code == "SMPIT") | (models.Unit.name.like("%SMPIT%"))
    ).first()
    if not smpit_unit:
        smpit_unit = models.Unit(name="SMPIT Asy-Syuuraa", code="SMPIT")
        db.add(smpit_unit)
        db.flush()
        print("Created Unit: SMPIT Asy-Syuuraa")
    else:
        print(f"Found Unit: {smpit_unit.name} (ID: {smpit_unit.id})")

    # 3. Classrooms: VII, VIII, IX-A, IX-B
    class_specs = [
        {"name": "VII", "level": 7, "homeroom_nik": "1220220155"},  # Astina Marru Kirama Baifar, S.Pd
        {"name": "VIII", "level": 8, "homeroom_nik": "1220250179"}, # Nurmatin Khanifah, S.H
        {"name": "IX-A", "level": 9, "homeroom_nik": "1220140051"}, # Lismanizar, S.Si
        {"name": "IX-B", "level": 9, "homeroom_nik": "1220240172"}, # Permadi, S.Sos
    ]
    classrooms = {}
    for cs in class_specs:
        hr_user = None
        if cs.get("homeroom_nik"):
            emp = db.query(models.Employee).filter(models.Employee.nik == cs["homeroom_nik"]).first()
            if emp:
                hr_user = db.query(models.User).filter(models.User.id == emp.user_id).first()
                if not hr_user:
                    hr_user = db.query(models.User).filter(models.User.email == emp.email).first()

        cr = db.query(models.Classroom).filter(
            models.Classroom.unit_id == smpit_unit.id,
            models.Classroom.academic_year_id == ay.id,
            models.Classroom.name == cs["name"]
        ).first()
        if not cr:
            # Check without academic_year_id
            cr = db.query(models.Classroom).filter(
                models.Classroom.unit_id == smpit_unit.id,
                models.Classroom.name == cs["name"]
            ).first()
            if cr:
                cr.academic_year_id = ay.id
                cr.level = cs["level"]
                if hr_user:
                    cr.homeroom_teacher_id = hr_user.id
            else:
                cr = models.Classroom(
                    name=cs["name"],
                    level=cs["level"],
                    unit_id=smpit_unit.id,
                    academic_year_id=ay.id,
                    homeroom_teacher_id=hr_user.id if hr_user else None
                )
                db.add(cr)
                db.flush()
                print(f"Created Classroom: {cr.name} (Level: {cr.level}, ID: {cr.id})")
        else:
            if hr_user and cr.homeroom_teacher_id != hr_user.id:
                cr.homeroom_teacher_id = hr_user.id
                db.flush()
        classrooms[cs["name"]] = cr
    db.commit()

    # 4. Teachers
    teacher_specs = [
        {"name": "Nuridawati, S.Pd", "nik": "1120050006", "email": "nuridawati@asysyuura.sch.id"},
        {"name": "Yunida Sari, S.Pd, Gr", "nik": "1220160086", "email": "yunida@asysyuura.sch.id"},
        {"name": "Normansyah, S.Pd, Gr", "nik": "1120180112", "email": "normansyah@asysyuura.sch.id"},
        {"name": "Nurmatin Khanifah, S.H", "nik": "1220180117", "email": "nurmatin@asysyuura.sch.id"},
        {"name": "Lismanizar, S.Si, Gr", "nik": "1220170094", "email": "lismanizar@asysyuura.sch.id"},
        {"name": "Muhammad Tholibin Azhari, QH. M.Pd", "nik": "1120190124", "email": "tholibin@asysyuura.sch.id"},
        {"name": "Astina Marru Kirama Baifar, S.Pd", "nik": "1220200135", "email": "astina@asysyuura.sch.id"},
        {"name": "Zurriatus Solihah, S.Pd", "nik": "1220210142", "email": "zurriatus@asysyuura.sch.id"},
        {"name": "Ahmad Sa'adi, S.Pd.I, M.M", "nik": "1120150077", "email": "ahmad.saadi@asysyuura.sch.id"},
        {"name": "Permadi, S.Sos", "nik": "1120220155", "email": "permadi@asysyuura.sch.id"},
        {"name": "Debby Liyany Ra'ad, S.Pd, Gr", "nik": "1220220158", "email": "debby@asysyuura.sch.id"},
        {"name": "Parlindungan, S.Pd.I", "nik": "1120100033", "email": "parlindungan@asysyuura.sch.id"},
    ]
    
    teachers_map = {}
    from passlib.hash import bcrypt
    default_pw = bcrypt.hash("Bismillah123!")

    for ts in teacher_specs:
        user = db.query(models.User).filter(
            (models.User.full_name.like(f"%{ts['name'].split(',')[0]}%")) |
            (models.User.email == ts["email"]) |
            (models.User.nik == ts["nik"])
        ).first()
        if not user:
            user = models.User(
                nik=ts["nik"],
                email=ts["email"],
                full_name=ts["name"],
                password_hash=default_pw,
                is_active=True,
                role_id=6 # Guru role
            )
            db.add(user)
            db.flush()
            print(f"Created User Guru: {user.full_name} (ID: {user.id})")
        
        # Ensure employee profile exists
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
        
        # Map various lookup keys
        key_short = ts["name"].split(",")[0].strip()
        teachers_map[key_short.lower()] = user
        teachers_map[ts["name"].lower()] = user
    db.commit()

    # 5. Subjects
    subject_specs = [
        {"name": "Pendidikan Kewarganegaraan (PKn)", "code": "PKN"},
        {"name": "Matematika", "code": "MTK"},
        {"name": "Ilmu Pengetahuan Alam (IPA)", "code": "IPA"},
        {"name": "Ilmu Pengetahuan Sosial (IPS)", "code": "IPS"},
        {"name": "Bahasa Indonesia", "code": "BINDO"},
        {"name": "Bahasa Inggris", "code": "BING"},
        {"name": "Bahasa Arab", "code": "BARAB"},
        {"name": "Pendidikan Jasmani & Olahraga (PJOK)", "code": "PJOK"},
        {"name": "Seni Budaya Melayu", "code": "SBM"},
        {"name": "Informatika", "code": "INFO"},
        {"name": "Prakarya & Seni Rupa", "code": "PRAK"},
        {"name": "Fiqih", "code": "FIQIH"},
        {"name": "Aqidah Akhlak", "code": "AQIDAH"},
        {"name": "Hadits", "code": "HADITS"},
        {"name": "Tahsin & Tahfidz Al-Qur'an (TTQ)", "code": "TTQ"},
    ]
    subjects_map = {}
    for ss in subject_specs:
        subj = db.query(models.Subject).filter(
            models.Subject.unit_id == smpit_unit.id,
            (models.Subject.code == ss["code"]) | (models.Subject.name == ss["name"])
        ).first()
        if not subj:
            subj = models.Subject(
                name=ss["name"],
                code=ss["code"],
                unit_id=smpit_unit.id
            )
            db.add(subj)
            db.flush()
            print(f"Created Subject: {subj.name} ({subj.code})")
        subjects_map[ss["code"]] = subj
        subjects_map[ss["name"].lower()] = subj
    db.commit()

    # Helper mapping subject name in Excel to (Subject, default Teacher) per class
    # Helper to resolve teacher by keywords
    def get_teacher(query_str):
        q = query_str.lower()
        for k, u in teachers_map.items():
            if k in q or q in k:
                return u
        return None

    def resolve_subject_and_teacher(cell_val: str, class_name: str):
        if not cell_val:
            return None, None
        v = cell_val.strip().upper()
        
        # Skip ceremonial or break slots
        if any(ign in v for ign in ["ISTIRAHAT", "ISHOMA", "MUROJA", "GORO", "SHOLAT", "EKSTAKURIKULER"]):
            return None, None

        if "PKN" in v:
            return subjects_map["PKN"], get_teacher("Nuridawati")
        if "MATEMATIKA" in v or "MTK" in v:
            return subjects_map["MTK"], get_teacher("Lismanizar")
        if "IPA" in v:
            return subjects_map["IPA"], get_teacher("Astina")
        if "IPS" in v:
            return subjects_map["IPS"], get_teacher("Zurriatus")
        if "BAHASA INDONESIA" in v or "BINDO" in v:
            if class_name == "VII":
                return subjects_map["BINDO"], get_teacher("Lismanizar")
            return subjects_map["BINDO"], get_teacher("Astina")
        if "BAHASA INGGRIS" in v or "B INGGRIS" in v:
            if class_name in ["IX-A", "IX-B"]:
                return subjects_map["BING"], get_teacher("Debby")
            return subjects_map["BING"], get_teacher("Nurmatin")
        if "BAHASA ARAB" in v or "B ARAB" in v:
            return subjects_map["BARAB"], get_teacher("Nurmatin")
        if "PJOK" in v:
            return subjects_map["PJOK"], get_teacher("Normansyah")
        if "SENI BUDAYA MELAYU" in v or "SBM" in v:
            return subjects_map["SBM"], get_teacher("Normansyah")
        if "INFORMATIKA" in v:
            return subjects_map["INFO"], get_teacher("Yunida")
        if "PRAKARYA" in v or "SENI RUPA" in v:
            return subjects_map["PRAK"], get_teacher("Permadi")
        if "FIQIH" in v or "FIQH" in v:
            return subjects_map["FIQIH"], get_teacher("Tholibin")
        if "AQIDAH" in v:
            return subjects_map["AQIDAH"], get_teacher("Ahmad Sa'adi")
        if "HADITS" in v:
            return subjects_map["HADITS"], get_teacher("Permadi")
        if "TTQ" in v:
            # TTQ lead teacher per class
            if class_name == "VII":
                return subjects_map["TTQ"], get_teacher("Yunida")
            elif class_name == "VIII":
                return subjects_map["TTQ"], get_teacher("Lismanizar")
            elif class_name == "IX-A":
                return subjects_map["TTQ"], get_teacher("Tholibin")
            elif class_name == "IX-B":
                return subjects_map["TTQ"], get_teacher("Parlindungan")
        
        return None, None

    # 6. Parse Excel JADWAL MAPEL
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb["JADWAL MAPEL"]
    
    current_day = None
    inserted_count = 0
    skipped_count = 0

    # Clear existing schedules for this academic year & SMPIT classrooms
    smp_cr_ids = [c.id for c in classrooms.values()]
    db.query(models.Schedule).filter(
        models.Schedule.academic_year_id == ay.id,
        models.Schedule.classroom_id.in_(smp_cr_ids)
    ).delete(synchronize_session=False)
    db.commit()

    for r in range(7, ws.max_row + 1):
        c_hari = ws.cell(r, 2).value
        c_jp = ws.cell(r, 4).value
        c_jam = ws.cell(r, 5).value
        
        if c_hari and str(c_hari).strip() in ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT"]:
            current_day = str(c_hari).strip()
            
        if not c_jam or '-' not in str(c_jam) or c_jp is None or not str(c_jp).strip().isdigit():
            continue
            
        start_time, end_time = clean_time(str(c_jam))
        if not start_time or not end_time:
            continue
            
        # Classes: Col 6 (VII), Col 7 (VIII), Col 8 (IX-A), Col 9 (IX-B)
        class_col_map = [
            ("VII", ws.cell(r, 6).value),
            ("VIII", ws.cell(r, 7).value),
            ("IX-A", ws.cell(r, 8).value),
            ("IX-B", ws.cell(r, 9).value),
        ]

        for c_name, cell_val in class_col_map:
            if not cell_val:
                continue
            subj, teacher = resolve_subject_and_teacher(str(cell_val), c_name)
            if subj and teacher:
                cr = classrooms[c_name]
                sched = models.Schedule(
                    academic_year_id=ay.id,
                    classroom_id=cr.id,
                    subject_id=subj.id,
                    teacher_id=teacher.id,
                    day=current_day,
                    start_time=start_time,
                    end_time=end_time
                )
                db.add(sched)
                inserted_count += 1
            else:
                skipped_count += 1

    db.commit()
    print(f"\n=== INJECTION COMPLETE ===")
    print(f"Total Jadwal Pelajaran Berhasil Ditambahkan: {inserted_count}")
    print(f"Slot Non-KBM Dilewati (Istirahat/Ishoma/Dzikir/dll): {skipped_count}")

    # Verification summary per classroom
    for c_name, cr in classrooms.items():
        count = db.query(models.Schedule).filter(
            models.Schedule.academic_year_id == ay.id,
            models.Schedule.classroom_id == cr.id
        ).count()
        print(f"  * Kelas {c_name}: {count} slot jadwal KBM")

    db.close()

if __name__ == "__main__":
    run_injection()
