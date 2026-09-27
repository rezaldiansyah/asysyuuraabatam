import io
import re
from datetime import datetime, time
from typing import Optional, List, Dict, Any

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from database import get_db
import models
from deps import get_current_user

router = APIRouter(prefix="/academic/schedules", tags=["Academic Schedules"])

VALID_DAYS = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]


def _format_time_str(val: Any) -> Optional[str]:
    """Convert Excel cell time or string to HH:MM format."""
    if val is None:
        return None
    if isinstance(val, time):
        return val.strftime("%H:%M")
    if isinstance(val, datetime):
        return val.strftime("%H:%M")
    s = str(val).strip()
    # Check if HH:MM:SS or HH:MM
    match = re.match(r"^(\d{1,2})[:.](\d{2})(?::\d{2})?$", s)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"
    return None


def _is_time_overlap(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
    """Return True if interval A overlaps with interval B."""
    return start_a < end_b and end_a > start_b


@router.get("/template")
async def download_schedule_template(
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate and download Excel template for schedule import with reference data."""
    wb = openpyxl.Workbook()
    
    # Sheet 1: Form Jadwal
    ws_jadwal = wb.active
    ws_jadwal.title = "Jadwal"
    
    # Header styles
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    sample_font = Font(name="Calibri", size=10, italic=True, color="475569")
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    
    headers = [
        "Hari (Wajib)",
        "Jam Mulai (Wajib)",
        "Jam Selesai (Wajib)",
        "Nama Kelas (Wajib)",
        "Kode / Nama Mapel (Wajib)",
        "NIK Guru (Wajib)",
        "Nama Guru (Opsional / Info)",
        "Keterangan (Opsional)"
    ]
    
    ws_jadwal.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws_jadwal.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center
        cell.border = thin_border
    
    # Sample rows
    samples = [
        ["SENIN", "07:30", "09:00", "1 Abu Bakar", "MTK", "999999", "Contoh Guru Matematika", "Jam pertama"],
        ["SENIN", "09:15", "10:45", "1 Abu Bakar", "IPA", "999999", "Contoh Guru IPA", "Jam kedua"],
        ["SELASA", "07:30", "09:00", "1 Abu Bakar", "B.IND", "999999", "Contoh Guru B.Indo", ""],
    ]
    for r_idx, row_data in enumerate(samples, start=2):
        ws_jadwal.append(row_data)
        for c_idx in range(1, len(row_data) + 1):
            cell = ws_jadwal.cell(row=r_idx, column=c_idx)
            cell.font = sample_font
            cell.alignment = align_center if c_idx in [1, 2, 3, 6] else align_left
            cell.border = thin_border
            
    # Auto adjust column width
    for col in ws_jadwal.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_jadwal.column_dimensions[col_letter].width = max(max_len + 4, 16)
        
    # Sheet 2: Data Referensi
    ws_ref = wb.create_sheet(title="Data Referensi")
    ref_header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    ref_sub_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    
    # 1. Hari Sah
    ws_ref.cell(row=1, column=1, value="DAFTAR HARI VALID").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=1).fill = ref_header_fill
    for i, day in enumerate(VALID_DAYS, start=2):
        c = ws_ref.cell(row=i, column=1, value=day)
        c.border = thin_border
        
    # 2. Kelas
    ws_ref.cell(row=1, column=3, value="NAMA KELAS").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=3).fill = ref_header_fill
    ws_ref.cell(row=1, column=4, value="UNIT").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=4).fill = ref_header_fill
    
    classroom_query = db.query(models.Classroom).options(joinedload(models.Classroom.unit))
    if academic_year_id:
        classroom_query = classroom_query.filter(models.Classroom.academic_year_id == academic_year_id)
    classrooms = classroom_query.order_by(models.Classroom.name).all()
    for i, cl in enumerate(classrooms, start=2):
        ws_ref.cell(row=i, column=3, value=cl.name).border = thin_border
        ws_ref.cell(row=i, column=4, value=cl.unit.name if cl.unit else "-").border = thin_border
        
    # 3. Mata Pelajaran
    ws_ref.cell(row=1, column=6, value="KODE MAPEL").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=6).fill = ref_header_fill
    ws_ref.cell(row=1, column=7, value="NAMA MAPEL").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=7).fill = ref_header_fill
    ws_ref.cell(row=1, column=8, value="UNIT").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=8).fill = ref_header_fill
    
    subjects = db.query(models.Subject).options(joinedload(models.Subject.unit)).order_by(models.Subject.name).all()
    for i, sb in enumerate(subjects, start=2):
        ws_ref.cell(row=i, column=6, value=sb.code or "-").border = thin_border
        ws_ref.cell(row=i, column=7, value=sb.name).border = thin_border
        ws_ref.cell(row=i, column=8, value=sb.unit.name if sb.unit else "-").border = thin_border

    # 4. Guru (Users with role guru or employees)
    ws_ref.cell(row=1, column=10, value="NIK GURU").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=10).fill = ref_header_fill
    ws_ref.cell(row=1, column=11, value="NAMA GURU").font = Font(name="Calibri", bold=True, color="FFFFFF")
    ws_ref.cell(row=1, column=11).fill = ref_header_fill
    
    teachers = db.query(models.User).filter(models.User.is_active == True).order_by(models.User.full_name).all()
    for i, tc in enumerate(teachers, start=2):
        ws_ref.cell(row=i, column=10, value=tc.nik or "-").border = thin_border
        ws_ref.cell(row=i, column=11, value=tc.full_name or tc.name).border = thin_border

    for col in ws_ref.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_ref.column_dimensions[col_letter].width = max(max_len + 3, 14)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = "template_jadwal_mengajar.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/upload-preview")
async def preview_schedule_upload(
    file: UploadFile = File(...),
    academic_year_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Validate uploaded Excel schedule file, detect conflicts, and return structured preview."""
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Format file harus .xlsx atau .xls")
    
    file_bytes = await file.read()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal membaca file Excel: {str(e)}")

    sheet_name = "Jadwal" if "Jadwal" in wb.sheetnames else wb.sheetnames[0]
    ws = wb[sheet_name]
    
    # Preload master reference caches for fast lookup
    classrooms_db = db.query(models.Classroom).all()
    classroom_map: Dict[str, models.Classroom] = {}
    for c in classrooms_db:
        classroom_map[c.name.strip().lower()] = c

    subjects_db = db.query(models.Subject).all()
    subject_map: Dict[str, models.Subject] = {}
    for s in subjects_db:
        if s.code:
            subject_map[s.code.strip().lower()] = s
        subject_map[s.name.strip().lower()] = s

    users_db = db.query(models.User).filter(models.User.is_active == True).all()
    teacher_by_nik: Dict[str, models.User] = {}
    teacher_by_name: Dict[str, models.User] = {}
    for u in users_db:
        if u.nik:
            teacher_by_nik[str(u.nik).strip()] = u
        if u.full_name:
            teacher_by_name[u.full_name.strip().lower()] = u
        name_attr = getattr(u, 'name', None)
        if name_attr:
            teacher_by_name[name_attr.strip().lower()] = u

    # Existing DB schedules for this academic year
    existing_schedules = db.query(models.Schedule).filter(
        models.Schedule.academic_year_id == academic_year_id
    ).all()

    parsed_rows: List[Dict[str, Any]] = []
    total_rows = 0
    valid_count = 0
    error_count = 0
    conflict_count = 0

    # Iterasi data mulai dari baris ke-2 (skip header)
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        # Abaikan baris kosong total
        if not any(row):
            continue
        
        total_rows += 1
        day_raw = row[0]
        start_raw = row[1]
        end_raw = row[2]
        class_raw = row[3]
        subject_raw = row[4]
        nik_raw = row[5]
        teacher_raw = row[6] if len(row) > 6 else None
        notes_raw = row[7] if len(row) > 7 else None

        errors: List[str] = []
        conflicts: List[str] = []

        # 1. Validasi Hari
        day_str = str(day_raw or "").strip().upper()
        if not day_str:
            errors.append("Hari harus diisi")
        elif day_str not in VALID_DAYS:
            errors.append(f"Hari '{day_str}' tidak valid (Gunakan: {', '.join(VALID_DAYS)})")

        # 2. Validasi Jam Mulai & Selesai
        start_time = _format_time_str(start_raw)
        end_time = _format_time_str(end_raw)
        if not start_time:
            errors.append("Jam mulai tidak valid (format HH:MM, contoh: 07:30)")
        if not end_time:
            errors.append("Jam selesai tidak valid (format HH:MM, contoh: 09:00)")
        if start_time and end_time and start_time >= end_time:
            errors.append(f"Jam mulai ({start_time}) harus lebih awal dari jam selesai ({end_time})")

        # 3. Validasi Kelas
        classroom_id = None
        classroom_name = str(class_raw or "").strip()
        if not classroom_name:
            errors.append("Nama kelas harus diisi")
        else:
            cl_obj = classroom_map.get(classroom_name.lower())
            if cl_obj:
                classroom_id = cl_obj.id
                classroom_name = cl_obj.name
            else:
                errors.append(f"Kelas '{classroom_name}' tidak ditemukan di sistem")

        # 4. Validasi Mata Pelajaran
        subject_id = None
        subject_name = str(subject_raw or "").strip()
        if not subject_name:
            errors.append("Mata pelajaran harus diisi")
        else:
            sb_obj = subject_map.get(subject_name.lower())
            if sb_obj:
                subject_id = sb_obj.id
                subject_name = sb_obj.name
            else:
                errors.append(f"Mapel '{subject_name}' tidak ditemukan di sistem")

        # 5. Validasi Guru
        teacher_id = None
        teacher_nik = str(nik_raw or "").strip() if nik_raw is not None else ""
        teacher_name = str(teacher_raw or "").strip()
        
        tc_obj = None
        if teacher_nik and teacher_nik != "-":
            tc_obj = teacher_by_nik.get(teacher_nik)
        if not tc_obj and teacher_name:
            tc_obj = teacher_by_name.get(teacher_name.lower())

        if tc_obj:
            teacher_id = tc_obj.id
            teacher_name = tc_obj.full_name or getattr(tc_obj, 'name', '')
            teacher_nik = tc_obj.nik or teacher_nik
        else:
            identifier = teacher_nik if teacher_nik else teacher_name
            errors.append(f"Guru '{identifier or 'tidak diisi'}' tidak ditemukan di database")

        # 6. Deteksi Konflik (Hanya jika data entitas & waktu sudah valid)
        if not errors and start_time and end_time:
            # A. Konflik intra-file (antar baris dalam file Excel yang sama)
            for prev in parsed_rows:
                if prev["status"] == "ERROR":
                    continue
                if prev["day"] == day_str and _is_time_overlap(start_time, end_time, prev["start_time"], prev["end_time"]):
                    # Konflik guru
                    if prev["teacher_id"] == teacher_id:
                        conflicts.append(
                            f"Bentrok dengan Baris {prev['row_index']} di file: Guru {teacher_name} sudah mengajar di kelas {prev['classroom_name']} ({prev['start_time']}-{prev['end_time']})"
                        )
                    # Konflik kelas
                    if prev["classroom_id"] == classroom_id:
                        conflicts.append(
                            f"Bentrok dengan Baris {prev['row_index']} di file: Kelas {classroom_name} sudah terisi mapel {prev['subject_name']} ({prev['start_time']}-{prev['end_time']})"
                        )

            # B. Konflik dengan jadwal yang sudah ada di database
            for ex in existing_schedules:
                if ex.day == day_str and _is_time_overlap(start_time, end_time, ex.start_time, ex.end_time):
                    if ex.teacher_id == teacher_id:
                        cl_name = ex.classroom.name if ex.classroom else f"Kelas ID {ex.classroom_id}"
                        conflicts.append(
                            f"Bentrok Database: Guru {teacher_name} sudah ada jadwal di {cl_name} ({ex.start_time}-{ex.end_time})"
                        )
                    if ex.classroom_id == classroom_id:
                        sb_name = ex.subject.name if ex.subject else f"Mapel ID {ex.subject_id}"
                        conflicts.append(
                            f"Bentrok Database: Kelas {classroom_name} sudah ada jadwal mapel {sb_name} ({ex.start_time}-{ex.end_time})"
                        )

        # Tentukan status akhir baris
        if errors:
            status_row = "ERROR"
            error_count += 1
        elif conflicts:
            status_row = "CONFLICT"
            conflict_count += 1
        else:
            status_row = "VALID"
            valid_count += 1

        parsed_rows.append({
            "row_index": row_idx,
            "day": day_str,
            "start_time": start_time or str(start_raw or ""),
            "end_time": end_time or str(end_raw or ""),
            "classroom_name": classroom_name,
            "classroom_id": classroom_id,
            "subject_name": subject_name,
            "subject_id": subject_id,
            "teacher_name": teacher_name,
            "teacher_nik": teacher_nik,
            "teacher_id": teacher_id,
            "notes": str(notes_raw or "").strip() if notes_raw else "",
            "status": status_row,
            "errors": errors,
            "conflicts": conflicts
        })

    return {
        "total_rows": total_rows,
        "valid_count": valid_count,
        "error_count": error_count,
        "conflict_count": conflict_count,
        "rows": parsed_rows
    }


@router.post("/upload-confirm")
async def confirm_schedule_upload(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Commit validated schedule rows into the database."""
    academic_year_id = payload.get("academic_year_id")
    mode = payload.get("mode", "append")  # "replace" or "append"
    items = payload.get("items", [])

    if not academic_year_id:
        raise HTTPException(status_code=400, detail="academic_year_id harus disertakan")

    if not items:
        raise HTTPException(status_code=400, detail="Tidak ada baris jadwal yang valid untuk diimpor")

    # Mode Replace: Hapus jadwal semester ini sebelum import
    if mode == "replace":
        db.query(models.Schedule).filter(models.Schedule.academic_year_id == academic_year_id).delete(synchronize_session=False)

    inserted_count = 0
    for itm in items:
        # Cek validitas item
        if not all([itm.get("classroom_id"), itm.get("subject_id"), itm.get("teacher_id"), itm.get("day"), itm.get("start_time"), itm.get("end_time")]):
            continue

        new_schedule = models.Schedule(
            academic_year_id=academic_year_id,
            classroom_id=itm["classroom_id"],
            subject_id=itm["subject_id"],
            teacher_id=itm["teacher_id"],
            day=itm["day"],
            start_time=itm["start_time"],
            end_time=itm["end_time"],
        )
        db.add(new_schedule)
        inserted_count += 1

    db.commit()

    return {
        "message": f"Berhasil mengimpor {inserted_count} jadwal pelajaran.",
        "count": inserted_count,
        "mode": mode
    }
