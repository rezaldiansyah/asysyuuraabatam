from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
import csv
import io
import re
import math
import json
import openpyxl
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List, Optional
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel
import passlib.hash

import models, schemas
from database import get_db
from deps import get_current_user, check_user_perm

router = APIRouter(prefix="/sdm", tags=["sdm"])

# Computed fields schema
class EmployeeComputed(BaseModel):
    tahun_pensiun: Optional[date]
    masa_kerja: str
    lama_kerja_pensiun: str

@router.get("/employees", response_model=List[schemas.Employee])
async def get_employees(
    unit_id: Optional[int] = None,
    employee_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Employee).options(
        joinedload(models.Employee.user),
        joinedload(models.Employee.unit),
        joinedload(models.Employee.education_history),
        joinedload(models.Employee.position_history)
    )
    
    if unit_id:
        query = query.filter(models.Employee.unit_id == unit_id)
    if employee_type:
        query = query.filter(models.Employee.employee_type == employee_type)
    if is_active is not None:
        if is_active:
            query = query.filter(or_(models.Employee.is_active == True, models.Employee.is_active.is_(None)))
        else:
            query = query.filter(models.Employee.is_active == False)
    if search:
        query = query.filter(
            or_(
                models.Employee.nama_lengkap.ilike(f"%{search}%"),
                models.Employee.nik_kepegawaian.ilike(f"%{search}%")
            )
        )
        
    return query.all()

@router.get("/employees/template")
async def get_employee_template():
    # Return a CSV template for bulk importing
    csv_header = "Nama Lengkap,NIK KTP,NIK Kepegawaian,Tanggal Lahir (YYYY-MM-DD),No HP,Tempat Lahir,Jenis Kelamin (Laki-laki/Perempuan),Status Pernikahan (Kawin/Belum Kawin),Alamat,Jabatan,Jenis Pegawai (tetap/kontrak/honorer),Unit ID,NIP,NUPTK\n"
    sample_row = "Fulan Bin Fulan,1234567890123456,YYS-100,1990-01-01,08123456789,Batam,Laki-laki,Kawin,Jl. Merdeka No 1,Guru Tetap,tetap,1,199001012020121001,1234567890123456\n"
    csv_content = csv_header + sample_row
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=template_pegawai.csv"}
    )

INDONESIAN_MONTHS = {
    'januari': 1, 'jan': 1,
    'februari': 2, 'feb': 2,
    'maret': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'mei': 5,
    'juni': 6, 'jun': 6,
    'juli': 7, 'jul': 7,
    'agustus': 8, 'agu': 8, 'agt': 8,
    'september': 9, 'sep': 9,
    'oktober': 10, 'okt': 10,
    'november': 11, 'nopember': 11, 'nov': 11,
    'desember': 12, 'des': 12
}

def _clean_str(val) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return "" if s in ["-", "None", "nan", "null"] else s

def _clean_phone_number(val) -> Optional[str]:
    s = _clean_str(val)
    if not s:
        return None
    s = s.split(".")[0].strip()
    s = re.sub(r'[^0-9+]', '', s)
    if s.startswith("8"):
        s = "0" + s
    return s if s else None

def _parse_birth_date(val) -> Optional[datetime]:
    if not val:
        return None
    if isinstance(val, (datetime, date)):
        return val if isinstance(val, datetime) else datetime.combine(val, datetime.min.time())
    s = str(val).strip()
    if len(s) >= 10 and s[4] == '-' and s[7] == '-':
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d")
        except Exception:
            pass
    m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', s)
    if m:
        d = int(m.group(1))
        m_name = m.group(2).lower()
        y = int(m.group(3))
        month_num = INDONESIAN_MONTHS.get(m_name)
        if month_num:
            try:
                return datetime(y, month_num, d)
            except Exception:
                pass
    return None

def _parse_ttl_field(ttl_str) -> tuple[Optional[str], Optional[datetime]]:
    if not ttl_str:
        return None, None
    s = str(ttl_str).strip()
    m = re.search(r'^(.*?)[,\s]+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*$', s)
    if m:
        place = m.group(1).strip()
        d = int(m.group(2))
        m_name = m.group(3).lower()
        y = int(m.group(4))
        month_num = INDONESIAN_MONTHS.get(m_name)
        if month_num:
            try:
                return place, datetime(y, month_num, d)
            except Exception:
                pass
    return s, None

def _parse_gender_val(val) -> Optional[str]:
    if not val:
        return None
    s = str(val).strip().lower()
    if s in ["l", "lk", "laki", "laki-laki", "pria", "male"]:
        return "Laki-laki"
    if s in ["p", "pr", "perempuan", "wanita", "female"]:
        return "Perempuan"
    return None

@router.post("/employees/import")
async def import_employees(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = (file.filename or "").lower()
    contents = await file.read()
    
    rows_data = [] # List of dicts with normalized keys
    
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        try:
            wb = openpyxl.load_workbook(io.BytesIO(contents), data_only=True)
            sheet = wb.active
            
            # Auto-detect header row
            header_row_idx = 1
            for r in range(1, min(11, sheet.max_row + 1)):
                txts = [re.sub(r'[^a-z0-9]', '', str(cell.value or '').lower()) for cell in sheet[r]]
                if any(t in ['namalengkap', 'nama', 'nik', 'ttl'] for t in txts):
                    header_row_idx = r
                    break
            
            col_map = {}
            for c in range(1, sheet.max_column + 1):
                raw_h = sheet.cell(row=header_row_idx, column=c).value
                if raw_h:
                    norm_k = re.sub(r'[^a-z0-9]', '', str(raw_h).lower())
                    col_map[c] = norm_k
                    
            for r in range(header_row_idx + 1, sheet.max_row + 1):
                row_dict = {}
                for c, norm_k in col_map.items():
                    row_dict[norm_k] = sheet.cell(row=r, column=c).value
                if any(row_dict.values()):
                    rows_data.append(row_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Gagal membaca file Excel (.xlsx): {str(e)}")
            
    elif filename.endswith(".csv"):
        try:
            decoded = contents.decode('utf-8-sig', errors='replace')
            csv_reader = csv.reader(io.StringIO(decoded))
            raw_rows = list(csv_reader)
            if not raw_rows:
                raise HTTPException(status_code=400, detail="File CSV kosong")
                
            header_row_idx = 0
            for idx, r in enumerate(raw_rows[:10]):
                txts = [re.sub(r'[^a-z0-9]', '', str(cell or '').lower()) for cell in r]
                if any(t in ['namalengkap', 'nama', 'nik', 'ttl'] for t in txts):
                    header_row_idx = idx
                    break
                    
            header_keys = [re.sub(r'[^a-z0-9]', '', str(c or '').lower()) for c in raw_rows[header_row_idx]]
            for r in raw_rows[header_row_idx + 1:]:
                row_dict = {}
                for idx, k in enumerate(header_keys):
                    if idx < len(r) and k:
                        row_dict[k] = r[idx]
                if any(row_dict.values()):
                    rows_data.append(row_dict)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Gagal membaca file CSV: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Format file harus berupa .xlsx atau .csv")

    if not rows_data:
        raise HTTPException(status_code=400, detail="Tidak ada baris data yang ditemukan dalam file")

    success_count = 0
    errors = []
    
    karyawan_role = db.query(models.Role).filter(models.Role.code == "karyawan").first()
    role_id = karyawan_role.id if karyawan_role else None
    
    # Pre-cache units
    units = db.query(models.Unit).all()
    unit_code_map = {u.code.upper(): u.id for u in units}

    # Pre-clean any invalid empty string emails in users table so unique constraint isn't violated
    try:
        db.query(models.User).filter(models.User.email == "").update({models.User.email: None})
        db.commit()
    except Exception:
        db.rollback()

    for row_idx, row in enumerate(rows_data, start=1):
        nama_lengkap = _clean_str(row.get("namalengkap") or row.get("nama"))
        if not nama_lengkap:
            continue # Skip blank rows
            
        nik_kepegawaian = _clean_str(row.get("nikkepegawaian") or row.get("nik") or row.get("username"))
        if not nik_kepegawaian:
            errors.append(f"Baris {row_idx} ({nama_lengkap}): NIK Kepegawaian tidak boleh kosong")
            continue

        savepoint = db.begin_nested()
        try:
            nik_ktp = _clean_str(row.get("noktp") or row.get("ktp") or row.get("nikktp") or row.get("niknegara"))
            raw_email = _clean_str(row.get("email"))
            email = raw_email if (raw_email and "@" in raw_email and "." in raw_email) else None
                
            # Check duplication for KTP against other employees
            if nik_ktp:
                existing_ktp = db.query(models.Employee).filter(
                    models.Employee.no_ktp == nik_ktp,
                    models.Employee.nik_kepegawaian != nik_kepegawaian
                ).first()
                if existing_ktp:
                    errors.append(f"Baris {row_idx} ({nama_lengkap}): NIK KTP {nik_ktp} sudah terdaftar pada {existing_ktp.nama_lengkap}. No KTP dikosongkan sementara.")
                    nik_ktp = None

            # TTL & Date parsing
            tempat_lahir = _clean_str(row.get("tempatlahir"))
            tanggal_lahir = _parse_birth_date(row.get("tanggallahir") or row.get("tgllahir"))
            
            raw_ttl = row.get("ttl") or row.get("tempattanggallahir")
            if raw_ttl:
                parsed_place, parsed_date = _parse_ttl_field(raw_ttl)
                if not tempat_lahir and parsed_place:
                    tempat_lahir = parsed_place
                if not tanggal_lahir and parsed_date:
                    tanggal_lahir = parsed_date

            # Gender parsing
            jk_val = _parse_gender_val(row.get("jk") or row.get("jeniskelamin"))
            
            # Phone & Admin
            no_hp = _clean_phone_number(row.get("nohp") or row.get("hp") or row.get("telepon") or row.get("wa") or row.get("whatsapp"))
            nuptk = _clean_str(row.get("nuptk")) or None
            nip = _clean_str(row.get("nip")) or None
            npwp = _clean_str(row.get("nonpwp") or row.get("npwp")) or None
            bpjs_tk = _clean_str(row.get("nobpjsketenagakerjaan") or row.get("bpjsketenagakerjaan") or row.get("bpjstk") or row.get("nobpjstk")) or None
            bpjs_kes = _clean_str(row.get("nobpjskesehatan") or row.get("bpjskesehatan") or row.get("bpjskes") or row.get("nobpjskes")) or None
            tmt_date = _parse_birth_date(row.get("tmt") or row.get("tmtmulaikerja") or row.get("tanggalmulaitugas"))
            
            # Check duplication for NUPTK against other employees
            if nuptk:
                existing_nuptk = db.query(models.Employee).filter(
                    models.Employee.nuptk == nuptk,
                    models.Employee.nik_kepegawaian != nik_kepegawaian
                ).first()
                if existing_nuptk:
                    errors.append(f"Baris {row_idx} ({nama_lengkap}): NUPTK '{nuptk}' kembar/sudah terdaftar pada {existing_nuptk.nama_lengkap}. NUPTK dikosongkan sementara agar data tetap tersimpan.")
                    nuptk = None

            # Check duplication for NIP against other employees
            if nip:
                existing_nip = db.query(models.Employee).filter(
                    models.Employee.nip == nip,
                    models.Employee.nik_kepegawaian != nik_kepegawaian
                ).first()
                if existing_nip:
                    errors.append(f"Baris {row_idx} ({nama_lengkap}): NIP '{nip}' sudah terdaftar pada {existing_nip.nama_lengkap}. NIP dikosongkan sementara.")
                    nip = None

            position = _clean_str(row.get("jabatan") or row.get("posisi")) or None
            
            # Employee type
            raw_type = _clean_str(row.get("statuspegawai") or row.get("jenispegawai")).lower()
            if "honorer" in raw_type:
                employee_type = "honorer"
            elif "kontrak" in raw_type:
                employee_type = "kontrak"
            else:
                employee_type = "tetap" # GTY, Tetap, etc
                
            # Unit ID auto-detection
            unit_id = None
            raw_unit = _clean_str(row.get("unitid") or row.get("unit"))
            if raw_unit:
                if raw_unit.isdigit():
                    unit_id = int(raw_unit)
                elif raw_unit.upper() in unit_code_map:
                    unit_id = unit_code_map[raw_unit.upper()]
                    
            if not unit_id and position:
                pos_lower = position.lower()
                if "ra" in pos_lower or "paud" in pos_lower:
                    unit_id = unit_code_map.get("RA")
                elif "sdit" in pos_lower or "sd" in pos_lower:
                    unit_id = unit_code_map.get("SDIT")
                elif "smpit" in pos_lower or "smp" in pos_lower:
                    unit_id = unit_code_map.get("SMPIT")
                elif any(k in pos_lower for k in ["yayasan", "kabid", "yys", "keuangan", "umum"]):
                    unit_id = unit_code_map.get("YYS")

            status_nikah = _clean_str(row.get("status") or row.get("statuspernikahan")) or None
            raw_anak = _clean_str(row.get("jumlahanak"))
            jml_anak = int(raw_anak) if raw_anak and raw_anak.isdigit() else 0
            alamat = _clean_str(row.get("alamat")) or None

            # Password generation (DDMMYYYY)
            generated_password = "password123"
            if tanggal_lahir:
                generated_password = tanggal_lahir.strftime("%d%m%Y")
            hashed_password = passlib.hash.bcrypt.hash(generated_password)

            # Check existing User
            existing_user = db.query(models.User).filter(models.User.nik == nik_kepegawaian).first()
            if existing_user:
                user = existing_user
                if email and not user.email:
                    existing_email = db.query(models.User).filter(models.User.email == email).first()
                    if not existing_email:
                        user.email = email
            else:
                user_email = email
                if user_email:
                    existing_email = db.query(models.User).filter(models.User.email == user_email).first()
                    if existing_email:
                        user_email = None # Don't conflict, fallback without email
                        
                user = models.User(
                    nik=nik_kepegawaian,
                    full_name=nama_lengkap,
                    email=user_email if user_email else None,
                    password_hash=hashed_password,
                    must_change_password=True,
                    role_id=role_id
                )
                db.add(user)
                db.flush()

            # Upsert Employee
            existing_emp = db.query(models.Employee).filter(models.Employee.nik_kepegawaian == nik_kepegawaian).first()
            if existing_emp:
                emp = existing_emp
                emp.nama_lengkap = nama_lengkap
                emp.is_active = True
                if nik_ktp: emp.no_ktp = nik_ktp
                if tempat_lahir: emp.tempat_lahir = tempat_lahir
                if tanggal_lahir: emp.tanggal_lahir = tanggal_lahir
                if jk_val: emp.jenis_kelamin = jk_val
                if status_nikah: emp.status_pernikahan = status_nikah
                emp.jumlah_anak = jml_anak
                if alamat: emp.alamat = alamat
                if no_hp: emp.no_hp = no_hp
                if npwp: emp.npwp = npwp
                if bpjs_tk: emp.no_bpjs_tk = bpjs_tk
                if bpjs_kes: emp.no_bpjs_kes = bpjs_kes
                if position: emp.position = position
                if employee_type: emp.employee_type = employee_type
                if unit_id: emp.unit_id = unit_id
                if tmt_date: emp.join_date = tmt_date
                if nip: emp.nip = nip
                if nuptk: emp.nuptk = nuptk
            else:
                emp = models.Employee(
                    user_id=user.id,
                    nama_lengkap=nama_lengkap,
                    no_ktp=nik_ktp if nik_ktp else None,
                    nik_kepegawaian=nik_kepegawaian,
                    tempat_lahir=tempat_lahir if tempat_lahir else None,
                    tanggal_lahir=tanggal_lahir,
                    jenis_kelamin=jk_val,
                    status_pernikahan=status_nikah,
                    jumlah_anak=jml_anak,
                    alamat=alamat,
                    no_hp=no_hp,
                    npwp=npwp,
                    no_bpjs_tk=bpjs_tk,
                    no_bpjs_kes=bpjs_kes,
                    position=position,
                    employee_type=employee_type,
                    unit_id=unit_id,
                    join_date=tmt_date,
                    nip=nip,
                    nuptk=nuptk,
                    is_active=True
                )
                db.add(emp)
                db.flush()

            # Education History if available
            pendidikan = _clean_str(row.get("pendidikan") or row.get("tingkatpendidikan"))
            jurusan = _clean_str(row.get("jurusan") or row.get("jurusanprodi") or row.get("prodi"))
            thn_lulus = _clean_str(row.get("tahunlulus") or row.get("thnlulus"))
            if pendidikan or jurusan or thn_lulus:
                # Check if already added
                existing_edu = db.query(models.EducationHistory).filter(models.EducationHistory.employee_id == emp.id).first()
                if not existing_edu:
                    edu = models.EducationHistory(
                        employee_id=emp.id,
                        tingkat=pendidikan if pendidikan else "S1",
                        jurusan=jurusan if jurusan else None,
                        institusi=None,
                        tahun_lulus=int(thn_lulus) if thn_lulus and thn_lulus.isdigit() else None
                    )
                    db.add(edu)

            savepoint.commit()
            success_count += 1
        except Exception as e:
            savepoint.rollback()
            errors.append(f"Baris {row_idx} ({nama_lengkap}): {str(e)}")
            continue

    if success_count > 0:
        db.commit()
    else:
        db.rollback()

    return {
        "success_count": success_count,
        "errors": errors,
        "message": f"Berhasil mengimpor {success_count} data pegawai." + (f" Terdapat {len(errors)} kendala." if errors else "")
    }

@router.get("/employees/{employee_id}", response_model=schemas.Employee)
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).options(
        joinedload(models.Employee.user),
        joinedload(models.Employee.unit),
        joinedload(models.Employee.education_history),
        joinedload(models.Employee.position_history)
    ).filter(models.Employee.id == employee_id).first()
    
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@router.post("/employees")
async def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # Check NIK KTP
    if employee.no_ktp:
        existing_ktp = db.query(models.Employee).filter(models.Employee.no_ktp == employee.no_ktp).first()
        if existing_ktp:
            raise HTTPException(status_code=400, detail="KTP already exists")
    
    # Check NIK Kepegawaian
    if employee.nik_kepegawaian:
        existing_nik = db.query(models.Employee).filter(models.Employee.nik_kepegawaian == employee.nik_kepegawaian).first()
        if existing_nik:
            raise HTTPException(status_code=400, detail="NIK Kepegawaian already exists")
            
    # Step 1: Handle User Account
    user = db.query(models.User).filter(models.User.nik == employee.nik_kepegawaian).first()
    
    generated_password = None
    if not user:
        if employee.tanggal_lahir:
            # Format password DDMMYYYY
            generated_password = employee.tanggal_lahir.strftime("%d%m%Y")
        else:
            generated_password = "password123" # Fallback
            
        hashed_password = passlib.hash.bcrypt.hash(generated_password)
        
        # Determine Role: default to 'karyawan' (Opsi B)
        karyawan_role = db.query(models.Role).filter(models.Role.code == "karyawan").first()
        role_id = karyawan_role.id if karyawan_role else None
            
        user = models.User(
            nik=employee.nik_kepegawaian,
            full_name=employee.nama_lengkap,
            password_hash=hashed_password,
            must_change_password=True,
            role_id=role_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Step 2: Create Employee
    employee_dict = employee.dict()
    db_emp = models.Employee(**employee_dict, user_id=user.id)
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    
    response = {
        "employee": db_emp,
        "message": "Employee created successfully"
    }
    
    if generated_password:
        response["login_info"] = {
            "username": user.nik,
            "password": generated_password
        }
        
    return response

@router.put("/employees/{employee_id}", response_model=schemas.Employee)
async def update_employee(employee_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    data = employee.dict(exclude_unset=True)
    email = data.pop("email", None)
    email_provided = "email" in employee.dict(exclude_unset=True)

    # Normalisasi string kosong -> None (hindari bentrok unique constraint)
    for key in ("nik_kepegawaian", "nip", "nuptk", "no_ktp"):
        if key in data and isinstance(data[key], str):
            data[key] = data[key].strip() or None

    # Cek keunikan identitas
    for key, label in (("nik_kepegawaian", "NIK Kepegawaian"), ("nip", "NIP"), ("nuptk", "NUPTK"), ("no_ktp", "No. KTP")):
        val = data.get(key)
        if val:
            dup = db.query(models.Employee).filter(getattr(models.Employee, key) == val, models.Employee.id != employee_id).first()
            if dup:
                raise HTTPException(status_code=400, detail=f"{label} {val} sudah dipakai pegawai lain ({dup.nama_lengkap})")

    user = db_emp.user
    if email_provided and user:
        new_email = (email or "").strip() or None
        if new_email:
            dup_user = db.query(models.User).filter(models.User.email == new_email, models.User.id != user.id).first()
            if dup_user:
                raise HTTPException(status_code=400, detail=f"Email {new_email} sudah dipakai akun lain")
        user.email = new_email

    for key, value in data.items():
        setattr(db_emp, key, value)

    # Sinkronkan akun login
    if user:
        if data.get("nik_kepegawaian"):
            user.nik = data["nik_kepegawaian"]
        if data.get("nama_lengkap"):
            user.full_name = data["nama_lengkap"]

    db.commit()
    db.refresh(db_emp)
    return db_emp

@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db_emp.is_active = False
    db.commit()
    return {"message": "Employee deactivated"}

@router.get("/employees/{employee_id}/computed", response_model=EmployeeComputed)
async def get_employee_computed(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).options(joinedload(models.Employee.position_history)).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
        
    today = date.today()
    
    # Tahun pensiun
    pensiun = None
    if emp.tanggal_lahir:
        pensiun = emp.tanggal_lahir.date() + relativedelta(years=55)
        
    # Masa kerja
    masa_kerja = "-"
    lama_pensiun = "-"
    
    first_tmt = None
    if emp.join_date:
        first_tmt = emp.join_date.date()
    elif emp.position_history:
        # Get earliest tmt_mulai
        earliest_pos = min(emp.position_history, key=lambda p: p.tmt_mulai)
        first_tmt = earliest_pos.tmt_mulai.date()
        
    if first_tmt:
        delta = relativedelta(today, first_tmt)
        masa_kerja = f"{delta.years} tahun {delta.months} bulan {delta.days} hari"
        
        if pensiun:
            delta_pensiun = relativedelta(pensiun, first_tmt)
            lama_pensiun = f"{delta_pensiun.years} tahun {delta_pensiun.months} bulan"
            
    return {
        "tahun_pensiun": pensiun,
        "masa_kerja": masa_kerja,
        "lama_kerja_pensiun": lama_pensiun
    }

def _to_date_val(val) -> Optional[date]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return datetime.strptime(val[:10], "%Y-%m-%d").date()
        except Exception:
            return None
    return None

_DEGREE_RE = re.compile(r"\b(s\.?\s?pd(\.?\s?i)?|m\.?\s?pd(\.?\s?i)?|s\.?\s?e(\.?i)?|s\.?\s?si|s\.?\s?kom|s\.?\s?ag|m\.?\s?ag|s\.?\s?sos|m\.?\s?si|m\.?\s?m|lc|s\.?\s?h|s\.?\s?psi|s\.?\s?hum|s\.?\s?t|s\.?\s?s|s\.?\s?p|s\.?\s?pt|s\.?\s?ked|s\.?\s?farm|a\.?\s?md|gr|aud|dr|drs|hj|h|ust|ustadz|ustadzah)\b\.?", re.I)

def _norm_person_name(name: Optional[str]) -> str:
    if not name:
        return ""
    s = name.lower()
    # Strip apostrophes / glottal stops (e.g. Sa'adi -> Saadi, Syafi'i -> Syafii) without splitting the word
    s = re.sub(r"['’`‘ʼʻ]", "", s)
    # Replace separators like commas, hyphens, slashes with spaces before degree stripping
    s = re.sub(r"[,_/\-]", " ", s)
    s = re.sub(r"[^a-z\s\.]", " ", s)
    s = _DEGREE_RE.sub(" ", s)
    s = re.sub(r"[^a-z\s]", " ", s)
    # Standardize common Indonesian name abbreviations
    parts = s.split()
    standardized = []
    for p in parts:
        if p in ("m", "moh", "moch"):
            standardized.append("muhammad")
        else:
            standardized.append(p)
    return " ".join(standardized)

def _phonetic_person_key(name: Optional[str]) -> str:
    """Collapse spaces, common Indonesian phonetic variants, and repeated letters."""
    norm = _norm_person_name(name)
    if not norm:
        return ""
    collapsed = norm.replace(" ", "")
    # Normalize common phonetics (dh -> d, sh -> s, th -> t, kh -> k)
    collapsed = collapsed.replace("dh", "d").replace("sh", "s").replace("th", "t").replace("kh", "k")
    collapsed = re.sub(r"(.)\1+", r"\1", collapsed)
    return collapsed

@router.get("/employees/{employee_id}/documents")
async def get_employee_documents(employee_id: int, db: Session = Depends(get_db)):
    """Daftar SK/dokumen yang terkait dengan pegawai (via akun user, nama pegawai, atau judul dokumen)."""
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    target = _norm_person_name(emp.nama_lengkap)
    docs = db.query(models.Document).filter(models.Document.is_active == True).order_by(models.Document.effective_date.desc().nullslast(), models.Document.created_at.desc()).all()

    results = []
    relinked = False
    for d in docs:
        match = None
        if emp.user_id and d.employee_id == emp.user_id:
            match = "terhubung"
        elif target and len(target) >= 4:
            dn = _norm_person_name(d.employee_name)
            if dn and dn == target:
                match = "nama"
            elif not d.employee_name and not d.employee_id and d.category == "sk_yayasan" and target in _norm_person_name(d.title):
                match = "judul"
        if not match:
            continue
        # Simpan tautan permanen ke akun pegawai agar tidak perlu dicocokkan ulang
        if match != "terhubung" and emp.user_id and not d.employee_id:
            d.employee_id = emp.user_id
            if not d.employee_name:
                d.employee_name = emp.nama_lengkap
            relinked = True
        results.append({
            "id": d.id,
            "title": d.title,
            "document_number": d.document_number,
            "category": d.category,
            "sk_type": d.sk_type,
            "position_title": d.position_title,
            "effective_date": d.effective_date.isoformat() if d.effective_date else None,
            "expired_date": d.expired_date.isoformat() if d.expired_date else None,
            "term_start_date": d.term_start_date.isoformat() if d.term_start_date else None,
            "term_end_date": d.term_end_date.isoformat() if d.term_end_date else None,
            "file_url": d.file_url,
            "file_name": d.file_name,
            "match": match,
        })
    if relinked:
        db.commit()
    return results

# --- Education & Position History Routes ---
EDUCATION_LEVELS = ["SD", "SMP", "SMA/SMK", "D1", "D2", "D3", "D4", "S1", "S2", "S3"]

def _normalize_education_level(raw: str) -> str:
    level = (raw or "").strip().upper().replace(" ", "")
    if level in ("SMA", "SMK", "SMA/SMK", "MA"):
        level = "SMA/SMK"
    if level not in EDUCATION_LEVELS:
        raise HTTPException(status_code=400, detail=f"Jenjang pendidikan tidak valid. Pilihan: {', '.join(EDUCATION_LEVELS)}")
    return level

def _assert_education_unique(db, employee_id: int, level: str, exclude_id: Optional[int] = None):
    q = db.query(models.EducationHistory).filter(
        models.EducationHistory.employee_id == employee_id,
        models.EducationHistory.tingkat == level
    )
    if exclude_id:
        q = q.filter(models.EducationHistory.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=400, detail=f"Pendidikan jenjang {level} sudah ada. Edit data yang ada, bukan menambah baru.")

@router.post("/employees/{employee_id}/education", response_model=schemas.EducationHistory)
async def add_education(employee_id: int, edu: schemas.EducationHistoryCreate, db: Session = Depends(get_db)):
    if not db.query(models.Employee).filter(models.Employee.id == employee_id).first():
        raise HTTPException(status_code=404, detail="Employee not found")
    data = edu.dict()
    data["tingkat"] = _normalize_education_level(data["tingkat"])
    _assert_education_unique(db, employee_id, data["tingkat"])
    db_edu = models.EducationHistory(**data, employee_id=employee_id)
    db.add(db_edu)
    db.commit()
    db.refresh(db_edu)
    return db_edu

@router.put("/education/{id}", response_model=schemas.EducationHistory)
async def update_education(id: int, edu: schemas.EducationHistoryCreate, db: Session = Depends(get_db)):
    db_edu = db.query(models.EducationHistory).filter(models.EducationHistory.id == id).first()
    if not db_edu:
        raise HTTPException(status_code=404, detail="Not found")
    data = edu.dict()
    data["tingkat"] = _normalize_education_level(data["tingkat"])
    _assert_education_unique(db, db_edu.employee_id, data["tingkat"], exclude_id=id)
    for k, v in data.items():
        setattr(db_edu, k, v)
    db.commit()
    db.refresh(db_edu)
    return db_edu

@router.put("/positions/{id}", response_model=schemas.PositionHistory)
async def update_position(id: int, pos: schemas.PositionHistoryCreate, db: Session = Depends(get_db)):
    db_pos = db.query(models.PositionHistory).filter(models.PositionHistory.id == id).first()
    if not db_pos:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in pos.dict().items():
        setattr(db_pos, k, v)
    db.commit()
    db.refresh(db_pos)
    return db_pos

@router.delete("/education/{id}")
async def delete_education(id: int, db: Session = Depends(get_db)):
    db_edu = db.query(models.EducationHistory).filter(models.EducationHistory.id == id).first()
    if not db_edu:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_edu)
    db.commit()
    return {"ok": True}

@router.post("/employees/{employee_id}/positions", response_model=schemas.PositionHistory)
async def add_position(employee_id: int, pos: schemas.PositionHistoryCreate, db: Session = Depends(get_db)):
    db_pos = models.PositionHistory(**pos.dict(), employee_id=employee_id)
    db.add(db_pos)
    db.commit()
    db.refresh(db_pos)
    return db_pos

@router.delete("/positions/{id}")
async def delete_position(id: int, db: Session = Depends(get_db)):
    db_pos = db.query(models.PositionHistory).filter(models.PositionHistory.id == id).first()
    if not db_pos:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_pos)
    db.commit()
    return {"ok": True}

# --- Employee Attendance & Geofencing Routes ---

DEFAULT_GEOFENCE = {
    "is_enabled": True,
    "latitude": 1.123456,
    "longitude": 104.012345,
    "radius_meters": 30.0,
    "location_name": "Komplek Sekolah Asy-Syuuraa Batam",
    "work_start_time": "06:45",
    "work_end_time": "15:30",
    "late_tolerance_minutes": 5,
    "schedule_ra_mon_thu": "14:00",
    "schedule_sdit_mon_thu": "15:00",
    "schedule_smpit_mon_thu": "15:30",
    "schedule_friday": "11:30",
    "schedule_saturday": "12:00",
    "schedule_default_mon_thu": "15:30"
}

def get_expected_checkout_time(target_date: date, unit_name: Optional[str] = None, geofence: Optional[dict] = None) -> str:
    cfg = geofence or DEFAULT_GEOFENCE
    weekday = target_date.weekday()
    if weekday == 4: # Jumat
        return cfg.get("schedule_friday", "11:30")
    elif weekday == 5: # Sabtu
        return cfg.get("schedule_saturday", "12:00")
    elif weekday == 6: # Ahad
        return "Libur"
    else: # Senin - Kamis
        u_name = (unit_name or "").upper()
        ra_time = cfg.get("schedule_ra_mon_thu") or "14:00"
        sdit_time = cfg.get("schedule_sdit_mon_thu") or "15:00"
        smpit_time = cfg.get("schedule_smpit_mon_thu") or "15:30"

        # Unit yang paling terakhir pulang di antara unit-unit sekolah
        defined_times = [t for t in [ra_time, sdit_time, smpit_time] if t]
        latest_unit_time = max(defined_times) if defined_times else "15:30"

        if "RA" in u_name:
            return ra_time
        elif "SDIT" in u_name or "SD" in u_name:
            return sdit_time
        elif "SMPIT" in u_name or "SMP" in u_name:
            return smpit_time

        # Unit lainnya / Yayasan / Non-unit jika tidak didefinisikan mengikuti unit yang paling terakhir pulang
        default_val = cfg.get("schedule_default_mon_thu")
        return default_val if default_val else latest_unit_time

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns distance in meters between two lat/lon coordinates."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def get_geofence_config(db: Session) -> dict:
    row = db.query(models.PageContent).filter(models.PageContent.section_key == "settings_geofence").first()
    if row and row.content_json:
        try:
            data = json.loads(row.content_json)
            merged = {**DEFAULT_GEOFENCE, **data}
            return merged
        except Exception:
            pass
    return DEFAULT_GEOFENCE.copy()

@router.get("/settings/geofence")
async def get_geofence_settings(db: Session = Depends(get_db)):
    """Retrieve geofencing & work hours configuration."""
    return get_geofence_config(db)

@router.put("/settings/geofence")
async def update_geofence_settings(
    settings: schemas.GeofenceSettingsSchema,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update geofencing & work hours configuration (Superadmin or Admin)."""
    if current_user.role and current_user.role.code != "superadmin":
        if not check_user_perm(current_user, "pengaturan.sekolah:update"):
            raise HTTPException(status_code=403, detail="Tidak memiliki hak akses mengubah pengaturan lokasi presensi.")
            
    row = db.query(models.PageContent).filter(models.PageContent.section_key == "settings_geofence").first()
    content_data = settings.dict()
    if not row:
        row = models.PageContent(
            section_key="settings_geofence",
            title="Pengaturan Geofence Presensi",
            content_json=json.dumps(content_data)
        )
        db.add(row)
    else:
        row.content_json = json.dumps(content_data)
        
    db.commit()
    return content_data

@router.get("/attendance/today")
async def get_today_employee_attendance(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's attendance record & geofence settings for the logged-in employee."""
    employee = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not employee:
        employee = db.query(models.Employee).filter(
            (models.Employee.nik_kepegawaian == current_user.nik) |
            (models.Employee.nip == current_user.nik)
        ).first()

    today_date = date.today()
    geofence = get_geofence_config(db)
    
    attendance = None
    if employee:
        attendance = db.query(models.EmployeeAttendance).filter(
            models.EmployeeAttendance.employee_id == employee.id,
            models.EmployeeAttendance.date == today_date
        ).first()
        
    return {
        "today": today_date.isoformat(),
        "has_employee_profile": employee is not None,
        "employee": {
            "id": employee.id,
            "nama_lengkap": employee.nama_lengkap,
            "nip": employee.nip,
            "position": employee.position,
            "unit_id": employee.unit_id
        } if employee else None,
        "attendance": {
            "id": attendance.id,
            "status": attendance.status.value if hasattr(attendance.status, "value") else str(attendance.status),
            "check_in": attendance.check_in.isoformat() if attendance.check_in else None,
            "check_out": attendance.check_out.isoformat() if attendance.check_out else None,
            "notes": attendance.notes,
            "check_in_distance": attendance.check_in_distance,
            "check_out_distance": attendance.check_out_distance,
        } if attendance else None,
        "geofence": geofence
    }

@router.post("/attendance/check-in")
async def employee_check_in(
    req: schemas.EmployeeCheckInRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Employee self check-in with GPS Geofencing validation."""
    employee = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not employee:
        employee = db.query(models.Employee).filter(
            (models.Employee.nik_kepegawaian == current_user.nik) |
            (models.Employee.nip == current_user.nik)
        ).first()
    if not employee:
        raise HTTPException(status_code=400, detail="Data pegawai tidak ditemukan untuk akun ini. Silakan hubungi bagian Tata Usaha.")

    today_date = date.today()
    now_dt = datetime.now()
    
    existing = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.employee_id == employee.id,
        models.EmployeeAttendance.date == today_date
    ).first()
    
    if existing and existing.check_in:
        raise HTTPException(status_code=400, detail=f"Anda sudah melakukan Check-in hari ini pada pukul {existing.check_in.strftime('%H:%M:%S')}.")
        
    is_duty = bool(req.is_duty_outside)
    if is_duty:
        if not (req.duty_reason or "").strip():
            raise HTTPException(status_code=400, detail="Keterangan tugas luar/dinas wajib diisi jika presensi di luar sekolah.")

    geofence = get_geofence_config(db)
    dist_meters = 0.0
    if geofence.get("is_enabled", True):
        school_lat = float(geofence.get("latitude", 1.123456))
        school_lng = float(geofence.get("longitude", 104.012345))
        allowed_radius = float(geofence.get("radius_meters", 30.0))
        dist_meters = round(calculate_haversine_distance(req.latitude, req.longitude, school_lat, school_lng), 1)
        
        if not is_duty and dist_meters > allowed_radius:
            raise HTTPException(
                status_code=400,
                detail=f"Presensi ditolak. Anda berada di luar radius sekolah ({dist_meters:.1f}m dari sekolah). Jika sedang agenda dinas/lomba di luar, centang opsi 'Tugas Luar / Dinas' dan sertakan keterangannya."
            )

    # Determine status (DISPENSATION for duty outside, or PRESENT / LATE for regular check-in)
    if is_duty:
        status_val = models.AttendanceStatus.DISPENSATION
    else:
        status_val = models.AttendanceStatus.PRESENT
        work_start = geofence.get("work_start_time", "07:30")
        tol_mins = int(geofence.get("late_tolerance_minutes", 0) or 0)
        try:
            sh, sm = map(int, work_start.split(":"))
            cutoff_minutes = (sh * 60) + sm + tol_mins
            now_minutes = (now_dt.hour * 60) + now_dt.minute
            if now_minutes > cutoff_minutes:
                status_val = models.AttendanceStatus.LATE
        except Exception:
            pass

    if is_duty:
        loc_str = f"Lat: {req.latitude:.5f}, Lng: {req.longitude:.5f} ({dist_meters}m dari sekolah)"
        gps_note_prefix = f"Presensi Mandiri GPS [Tugas Luar / Dinas] ({loc_str}) — Keperluan: {req.duty_reason.strip()}"
        combined_gps_note = f"{gps_note_prefix} | Catatan: {req.notes.strip()}" if req.notes else gps_note_prefix
    else:
        gps_note_prefix = f"Presensi Mandiri GPS (Jarak {dist_meters}m)"
        combined_gps_note = f"{gps_note_prefix} - {req.notes}" if req.notes else gps_note_prefix

    if existing:
        existing.status = status_val
        existing.check_in = now_dt
        existing.check_in_lat = req.latitude
        existing.check_in_lng = req.longitude
        existing.check_in_distance = dist_meters
        existing.device_info = req.device_info
        existing.notes = combined_gps_note
        db_att = existing
    else:
        db_att = models.EmployeeAttendance(
            employee_id=employee.id,
            date=today_date,
            status=status_val,
            check_in=now_dt,
            check_in_lat=req.latitude,
            check_in_lng=req.longitude,
            check_in_distance=dist_meters,
            device_info=req.device_info,
            notes=combined_gps_note
        )
        db.add(db_att)
        
    db.commit()
    db.refresh(db_att)
    status_text = "Tugas Luar/Dinas" if is_duty else ("Tepat Waktu" if status_val == models.AttendanceStatus.PRESENT else "Terlambat")
    return {
        "message": f"Berhasil Check-in pada {now_dt.strftime('%H:%M:%S')} ({status_text}). Lokasi GPS berhasil dicatat.",
        "distance_meters": dist_meters,
        "status": status_val.value,
        "check_in": now_dt.isoformat()
    }

@router.post("/attendance/check-out")
async def employee_check_out(
    req: schemas.EmployeeCheckOutRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Employee self check-out with GPS Geofencing validation."""
    employee = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not employee:
        employee = db.query(models.Employee).filter(
            (models.Employee.nik_kepegawaian == current_user.nik) |
            (models.Employee.nip == current_user.nik)
        ).first()
    if not employee:
        raise HTTPException(status_code=400, detail="Data pegawai tidak ditemukan untuk akun ini.")

    today_date = date.today()
    now_dt = datetime.now()
    
    existing = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.employee_id == employee.id,
        models.EmployeeAttendance.date == today_date
    ).first()
    
    if not existing or not existing.check_in:
        raise HTTPException(status_code=400, detail="Anda belum melakukan Check-in masuk hari ini.")
        
    if existing.check_out:
        raise HTTPException(status_code=400, detail=f"Anda sudah melakukan Check-out pada pukul {existing.check_out.strftime('%H:%M:%S')}.")
        
    is_duty = bool(req.is_duty_outside) or ("Tugas Luar" in (existing.notes or ""))
    geofence = get_geofence_config(db)
    dist_meters = 0.0
    if geofence.get("is_enabled", True):
        school_lat = float(geofence.get("latitude", 1.123456))
        school_lng = float(geofence.get("longitude", 104.012345))
        allowed_radius = float(geofence.get("radius_meters", 30.0))
        dist_meters = round(calculate_haversine_distance(req.latitude, req.longitude, school_lat, school_lng), 1)
        
        if not is_duty and dist_meters > allowed_radius:
            raise HTTPException(
                status_code=400,
                detail=f"Presensi ditolak. Anda berada di luar radius sekolah saat Check-out ({dist_meters:.1f}m). Jika sedang dinas luar, centang opsi Tugas Luar."
            )

    existing.check_out = now_dt
    existing.check_out_lat = req.latitude
    existing.check_out_lng = req.longitude
    existing.check_out_distance = dist_meters
    if req.notes:
        existing.notes = (existing.notes or "") + " " + req.notes
        
    db.commit()
    db.refresh(existing)
    return {
        "message": f"Berhasil Check-out pada {now_dt.strftime('%H:%M:%S')}. Selamat beristirahat!",
        "distance_meters": dist_meters,
        "check_out": now_dt.isoformat()
    }

@router.get("/attendance", response_model=List[schemas.EmployeeAttendance])
async def get_employee_attendances(
    date: Optional[str] = None,
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.EmployeeAttendance).options(joinedload(models.EmployeeAttendance.employee))
    
    if date:
        from datetime import datetime as dt
        target_date = dt.strptime(date, "%Y-%m-%d").date()
        query = query.filter(models.EmployeeAttendance.date == target_date)
        
    if unit_id:
        query = query.join(models.Employee).filter(models.Employee.unit_id == unit_id)
    
    return query.order_by(models.EmployeeAttendance.date.desc()).all()

@router.post("/attendance", response_model=schemas.EmployeeAttendance)
async def create_employee_attendance(attendance: schemas.EmployeeAttendanceCreate, db: Session = Depends(get_db)):
    existing = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.employee_id == attendance.employee_id,
        models.EmployeeAttendance.date == attendance.date
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already recorded for this employee on this date")
    
    db_att = models.EmployeeAttendance(**attendance.dict())
    db.add(db_att)
    db.commit()
    db.refresh(db_att)
    return db_att

@router.post("/attendance/bulk")
async def create_bulk_employee_attendance(request: schemas.BulkEmployeeAttendanceCreate, db: Session = Depends(get_db)):
    count = 0
    updated = 0
    skipped_locked = 0
    
    for item in request.items:
        existing = db.query(models.EmployeeAttendance).filter(
            models.EmployeeAttendance.employee_id == item.employee_id,
            models.EmployeeAttendance.date == request.date
        ).first()
        
        status_val = item.status.value if hasattr(item.status, "value") else str(item.status)
        
        if existing:
            existing_note = existing.notes or ""
            is_locked = (
                existing.check_in_distance is not None
                or "Sinkronisasi Fingerprint" in existing_note
                or "Presensi Mandiri GPS" in existing_note
            )
            if is_locked:
                # Locked records from Fingerprint / GPS Mandiri cannot be modified manually
                skipped_locked += 1
                continue

            existing.status = status_val
            if item.check_in is not None:
                existing.check_in = item.check_in
            if item.check_out is not None:
                existing.check_out = item.check_out
            if item.notes is not None:
                existing.notes = item.notes
            updated += 1
        else:
            # Create new manual record for employee without fingerprint/GPS data
            note_val = item.notes or "Tidak ada data di Fingerprint"
            db_att = models.EmployeeAttendance(
                employee_id=item.employee_id,
                date=request.date,
                status=status_val,
                check_in=item.check_in,
                check_out=item.check_out,
                notes=note_val
            )
            db.add(db_att)
            count += 1
            
    db.commit()
    return {
        "message": f"Created {count} new attendance records, updated {updated} existing ones, protected {skipped_locked} locked Fingerprint/GPS records"
    }

@router.get("/attendance/recap")
async def get_employee_attendance_recap(
    month: Optional[str] = None, # Format YYYY-MM
    start_date: Optional[str] = None, # Format YYYY-MM-DD
    end_date: Optional[str] = None, # Format YYYY-MM-DD
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from datetime import datetime as dt
    import calendar

    # Determine date range
    if start_date and end_date:
        try:
            s_date = dt.strptime(start_date, "%Y-%m-%d").date()
            e_date = dt.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Format start_date/end_date tidak valid. Gunakan YYYY-MM-DD.")
    elif month:
        try:
            target_month = dt.strptime(month, "%Y-%m")
            s_date = target_month.date()
            _, last_day = calendar.monthrange(s_date.year, s_date.month)
            e_date = s_date.replace(day=last_day)
        except ValueError:
            raise HTTPException(status_code=400, detail="Format month tidak valid. Gunakan YYYY-MM.")
    else:
        # Default to current month
        today = dt.today().date()
        s_date = today.replace(day=1)
        _, last_day = calendar.monthrange(today.year, today.month)
        e_date = today.replace(day=last_day)

    # Get all employees
    emp_query = db.query(models.Employee).options(joinedload(models.Employee.unit)).filter(models.Employee.is_active == True)
    if unit_id:
        emp_query = emp_query.filter(models.Employee.unit_id == unit_id)
    employees = emp_query.all()

    # Get all attendance records in date range
    att_query = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.date >= s_date,
        models.EmployeeAttendance.date <= e_date
    )
    if unit_id:
        att_query = att_query.join(models.Employee).filter(models.Employee.unit_id == unit_id)
    attendances = att_query.all()

    def status_str(att):
        return att.status.value if hasattr(att.status, "value") else str(att.status)

    def extract_activity_category(text: str) -> str:
        if not text:
            return "Lainnya / Umum"
        lower = text.lower()
        if "[lomba]" in lower or "lomba" in lower or "olimpiade" in lower or "tahfidz" in lower or "futsal" in lower:
            return "Pendampingan Lomba"
        if "[mabit]" in lower or "mabit" in lower or "keagamaan" in lower or "pesantren" in lower or "halaqah" in lower or "tarbiyah" in lower:
            return "Kegiatan Keagamaan / Mabit"
        if "[rapat]" in lower or "rapat" in lower or "dinas" in lower or "yayasan" in lower or "musyawarah" in lower:
            return "Rapat Dinas / Yayasan"
        if "[akreditasi]" in lower or "akreditasi" in lower or "rapor" in lower or "asesmen" in lower or "anbk" in lower or "ujian" in lower:
            return "Akreditasi / Asesmen"
        if "[piket]" in lower or "piket" in lower or "spmb" in lower or "open house" in lower:
            return "Piket Sekolah / SPMB"
        return "Lainnya / Umum"

    day_names_id = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]

    # Group by employee
    results = []
    has_cleanup = False
    for emp in employees:
        j_date = _to_date_val(emp.join_date)
        r_date = _to_date_val(emp.resign_date)

        # Clean up any phantom automated 'Tidak ada data di Fingerprint' absences that were recorded before the employee joined
        if j_date:
            try:
                j_dt = datetime.combine(j_date, datetime.min.time())
                deleted = db.query(models.EmployeeAttendance).filter(
                    models.EmployeeAttendance.employee_id == emp.id,
                    models.EmployeeAttendance.date < j_dt,
                    models.EmployeeAttendance.notes == "Tidak ada data di Fingerprint"
                ).delete(synchronize_session=False)
                if deleted > 0:
                    has_cleanup = True
            except Exception:
                pass

        # Filter emp_att to only dates where the employee was legitimately employed
        emp_att = []
        for a in attendances:
            if a.employee_id != emp.id:
                continue
            a_d = _to_date_val(a.date)
            if j_date and a_d and a_d < j_date:
                continue
            if r_date and a_d and a_d > r_date:
                continue
            emp_att.append(a)

        h = sum(1 for a in emp_att if status_str(a) in ['PRESENT', 'LATE'])
        terlambat = sum(1 for a in emp_att if status_str(a) == 'LATE')
        s = sum(1 for a in emp_att if status_str(a) == 'SICK')
        i = sum(1 for a in emp_att if status_str(a) in ['PERMIT', 'DISPENSATION'])
        cuti = sum(1 for a in emp_att if status_str(a).startswith('LEAVE_'))
        a = sum(1 for a in emp_att if status_str(a) == 'ABSENT')
        total = h + s + i + cuti + a

        # Monthly breakdown for trend analysis & Overtime/Sunday logs
        monthly_trend = {}
        overtime_records = []
        total_lembur = 0
        total_ahad = 0

        for att in emp_att:
            try:
                if not att.date:
                    continue
                m_key = att.date.strftime("%Y-%m") if hasattr(att.date, "strftime") else str(att.date)[:7]
                if m_key not in monthly_trend:
                    monthly_trend[m_key] = {
                        "hadir": 0, "terlambat": 0, "sakit": 0, "izin": 0, 
                        "cuti": 0, "alpa": 0, "total": 0, "lembur": 0, "ahad": 0
                    }
                st = status_str(att)
                if st in ['PRESENT', 'LATE']:
                    monthly_trend[m_key]["hadir"] += 1
                if st == 'LATE':
                    monthly_trend[m_key]["terlambat"] += 1
                elif st == 'SICK':
                    monthly_trend[m_key]["sakit"] += 1
                elif st in ['PERMIT', 'DISPENSATION']:
                    monthly_trend[m_key]["izin"] += 1
                elif st.startswith('LEAVE_'):
                    monthly_trend[m_key]["cuti"] += 1
                elif st == 'ABSENT':
                    monthly_trend[m_key]["alpa"] += 1
                monthly_trend[m_key]["total"] += 1

                # Check Overtime (Checkout >= 18:00) and Sunday (weekday == 6)
                is_sunday = att.date.weekday() == 6 if hasattr(att.date, "weekday") else False
                is_late_checkout = False
                if att.check_out and hasattr(att.check_out, "time"):
                    is_late_checkout = bool(att.check_out.time() >= dt.strptime("18:00", "%H:%M").time())
                is_active_present = st in ['PRESENT', 'LATE', 'DISPENSATION'] or att.check_in is not None

                if is_sunday and is_active_present:
                    total_ahad += 1
                    monthly_trend[m_key]["ahad"] += 1

                if is_late_checkout:
                    total_lembur += 1
                    monthly_trend[m_key]["lembur"] += 1

                if (is_sunday and is_active_present) or is_late_checkout:
                    notes_text = att.notes or ""
                    cat = extract_activity_category(notes_text)
                    is_duty = "[tugas luar" in notes_text.lower() or "dinas" in notes_text.lower()
                    date_str = att.date.strftime("%Y-%m-%d") if hasattr(att.date, "strftime") else str(att.date)[:10]
                    day_idx = att.date.weekday() if hasattr(att.date, "weekday") else 0
                    day_name = day_names_id[day_idx] if 0 <= day_idx < len(day_names_id) else "-"

                    overtime_records.append({
                        "attendance_id": att.id,
                        "date": date_str,
                        "day_name": day_name,
                        "is_sunday": is_sunday,
                        "is_overtime": is_late_checkout,
                        "check_in": att.check_in.strftime("%H:%M") if (att.check_in and hasattr(att.check_in, "strftime")) else "-",
                        "check_out": att.check_out.strftime("%H:%M") if (att.check_out and hasattr(att.check_out, "strftime")) else "-",
                        "category": cat,
                        "notes": notes_text,
                        "is_duty_outside": is_duty,
                        "status": st
                    })
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Error processing attendance record {getattr(att, 'id', None)}: {e}")

        # Sort overtime records descending by date
        overtime_records.sort(key=lambda x: x["date"], reverse=True)

        results.append({
            "employee_id": emp.id,
            "nama_lengkap": emp.nama_lengkap,
            "nip": emp.nip,
            "unit_id": emp.unit_id,
            "unit_name": emp.unit.name if emp.unit else "Tanpa Unit",
            "position": emp.position or "Staf / Guru",
            "join_date": j_date.strftime("%Y-%m-%d") if j_date else None,
            "resign_date": r_date.strftime("%Y-%m-%d") if r_date else None,
            "hadir": h,
            "terlambat": terlambat,
            "sakit": s,
            "izin": i,
            "cuti": cuti,
            "alpa": a,
            "total": total,
            "persentase": f"{(h/total*100):.1f}%" if total > 0 else "0.0%",
            "monthly_trend": monthly_trend,
            "total_lembur": total_lembur,
            "total_ahad": total_ahad,
            "overtime_records": overtime_records
        })

    if has_cleanup:
        try:
            db.commit()
        except Exception:
            db.rollback()

    return results


class FingerprintSyncRequest(BaseModel):
    date: Optional[str] = None        # Format YYYY-MM-DD (default: hari ini WIB)
    mode: Optional[str] = "all"       # "fetch_raw" | "process_one" | "all"
    source: Optional[str] = "manual"  # "manual" | "cron"
    employee_id: Optional[int] = None
    raw_logs: Optional[List[dict]] = None


class FingerprintLogRecordRequest(BaseModel):
    date: str
    source: str = "manual"
    status: str  # "success" | "partial" | "failed" | "empty"
    raw_count: int = 0
    synced_employees: int = 0
    failed_employees: int = 0
    unmatched_logs: List[str] = []
    message: str = ""
    error_detail: Optional[str] = None


def _append_fingerprint_sync_log(db: Session, entry: dict):
    """Append a sync log entry to PageContent('fingerprint_sync_logs'), keeping the latest 100 entries."""
    try:
        row = db.query(models.PageContent).filter(
            models.PageContent.section_key == "fingerprint_sync_logs"
        ).first()
        logs = []
        if row and row.content_json:
            try:
                logs = json.loads(row.content_json)
                if not isinstance(logs, list):
                    logs = []
            except Exception:
                logs = []

        logs.insert(0, entry)
        logs = logs[:100]  # Keep last 100 logs

        if not row:
            row = models.PageContent(
                section_key="fingerprint_sync_logs",
                title="Riwayat Log Sinkronisasi Mesin Presensi",
                content_json=json.dumps(logs)
            )
            db.add(row)
        else:
            row.content_json = json.dumps(logs)
        db.commit()
    except Exception:
        db.rollback()


@router.get("/attendance/sync-logs")
async def get_fingerprint_sync_logs(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve history of fingerprint attendance synchronization (manual & cron, success & failures)."""
    row = db.query(models.PageContent).filter(
        models.PageContent.section_key == "fingerprint_sync_logs"
    ).first()
    if row and row.content_json:
        try:
            logs = json.loads(row.content_json)
            if isinstance(logs, list):
                return logs[:limit]
        except Exception:
            pass
    return []


def _mark_missing_fingerprint_employees(db: Session, target_date: date) -> int:
    """
    Ensure any active employee who had NO tap in the fingerprint machine on target_date
    has a note stating 'Tidak ada data di Fingerprint' so Admin must fill their status & reason manually.
    """
    active_emps = db.query(models.Employee).filter(
        or_(models.Employee.is_active == True, models.Employee.is_active.is_(None))
    ).all()
    existing_rows = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.date == target_date
    ).all()
    by_emp_id = {r.employee_id: r for r in existing_rows}

    t_date = _to_date_val(target_date)
    marked_count = 0
    for emp in active_emps:
        # Skip if target_date is before employee joined (e.g. joined 3 months ago)
        j_date = _to_date_val(emp.join_date)
        if j_date and t_date and t_date < j_date:
            continue

        # Skip if employee already resigned prior to target_date
        r_date = _to_date_val(emp.resign_date)
        if r_date and t_date and t_date > r_date:
            continue

        row = by_emp_id.get(emp.id)
        if not row:
            db.add(models.EmployeeAttendance(
                employee_id=emp.id,
                date=target_date,
                status=models.AttendanceStatus.ABSENT,
                check_in=None,
                check_out=None,
                notes="Tidak ada data di Fingerprint"
            ))
            marked_count += 1
        else:
            curr_note = (row.notes or "").strip()
            is_auto = (
                row.check_in_distance is not None
                or "Sinkronisasi Fingerprint" in curr_note
                or "Presensi Mandiri GPS" in curr_note
            )
            if not is_auto and not curr_note:
                row.notes = "Tidak ada data di Fingerprint"
                marked_count += 1

    if marked_count > 0:
        db.commit()
    return marked_count


@router.post("/attendance/sync-logs")
async def record_fingerprint_sync_log(
    req: FingerprintLogRecordRequest,
    db: Session = Depends(get_db)
):
    """Record a completed or failed step-by-step sync session from frontend."""
    from datetime import timezone, timedelta
    wib_now = datetime.now(timezone(timedelta(hours=7)))
    if req.status in ("success", "partial") and req.date:
        try:
            t_date = datetime.strptime(req.date, "%Y-%m-%d").date()
            _mark_missing_fingerprint_employees(db, t_date)
        except Exception:
            db.rollback()
    entry = {
        "id": f"sync-{int(wib_now.timestamp() * 1000)}",
        "timestamp": wib_now.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "date_target": req.date,
        "source": req.source,
        "status": req.status,
        "raw_count": req.raw_count,
        "synced_employees": req.synced_employees,
        "failed_employees": req.failed_employees,
        "unmatched_logs": req.unmatched_logs,
        "message": req.message,
        "error_detail": req.error_detail
    }
    _append_fingerprint_sync_log(db, entry)
    return entry


def _fetch_sdit_fingerprint_logs(date_str: str, timeout_sec: int = 12) -> list[dict]:
    """Fetch raw attendance logs from sdit.asysyuuraa.my.id with strict timeout so Gunicorn never hangs."""
    import os
    import ssl
    import urllib.request
    import urllib.parse

    api_url = os.getenv(
        "FINGERPRINT_API_URL",
        "https://sdit.asysyuuraa.my.id/api/api_absensi_karyawan.php"
    )
    api_key = os.getenv(
        "FINGERPRINT_API_KEY",
        "CBT_ASY_8xK9mP2qV5nB7cJ4hF1zR6tY3wL0dG"
    )

    params = urllib.parse.urlencode({"tanggal": date_str, "api_key": api_key})
    full_url = f"{api_url}?{params}"

    ssl_ctx = ssl._create_unverified_context()
    http_req = urllib.request.Request(
        full_url,
        headers={
            "x-api-key": api_key,
            "User-Agent": "AsySyuuraa-ERP-Sync/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(http_req, timeout=timeout_sec, context=ssl_ctx) as resp:
        raw_body = resp.read().decode("utf-8", errors="replace")
        payload = json.loads(raw_body)

    if payload.get("status") != "success":
        raise RuntimeError(payload.get("message") or "API mesin presensi mengembalikan status error.")

    return payload.get("data") or []


def _get_fingerprint_nik_map(db: Session) -> dict:
    """Return mapping of fingerprint PIN/NIK -> {"employee_id": int, "fp_name": str}."""
    row = db.query(models.PageContent).filter(
        models.PageContent.section_key == "fingerprint_nik_map"
    ).first()
    if row and row.content_json:
        try:
            data = json.loads(row.content_json)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def _save_fingerprint_nik_map(db: Session, mapping: dict):
    try:
        row = db.query(models.PageContent).filter(
            models.PageContent.section_key == "fingerprint_nik_map"
        ).first()
        if not row:
            row = models.PageContent(
                section_key="fingerprint_nik_map",
                title="Mapping PIN Mesin Fingerprint ke Pegawai SDM",
                content_json=json.dumps(mapping)
            )
            db.add(row)
        else:
            row.content_json = json.dumps(mapping)
        db.commit()
    except Exception:
        db.rollback()


class FingerprintPinMappingRequest(BaseModel):
    fp_nik: str
    fp_name: Optional[str] = ""
    employee_id: int


@router.get("/attendance/fingerprint-mappings")
async def get_fingerprint_mappings(db: Session = Depends(get_db)):
    mapping = _get_fingerprint_nik_map(db)
    employees = db.query(models.Employee).all()
    emp_by_id = {e.id: e for e in employees}
    result = []
    for fp_nik, info in mapping.items():
        emp_id = info.get("employee_id") if isinstance(info, dict) else info
        emp = emp_by_id.get(emp_id)
        if emp:
            result.append({
                "fp_nik": fp_nik,
                "fp_name": info.get("fp_name", "") if isinstance(info, dict) else "",
                "employee_id": emp.id,
                "employee_name": emp.nama_lengkap,
                "nik_kepegawaian": emp.nik_kepegawaian,
            })
    return result


@router.post("/attendance/fingerprint-mappings")
async def save_fingerprint_mapping(req: FingerprintPinMappingRequest, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == req.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")
    mapping = _get_fingerprint_nik_map(db)
    mapping[str(req.fp_nik).strip()] = {
        "employee_id": emp.id,
        "fp_name": (req.fp_name or "").strip(),
    }
    _save_fingerprint_nik_map(db, mapping)
    return {"status": "success", "fp_nik": req.fp_nik, "employee_id": emp.id, "employee_name": emp.nama_lengkap}


@router.delete("/attendance/fingerprint-mappings/{fp_nik}")
async def delete_fingerprint_mapping(fp_nik: str, db: Session = Depends(get_db)):
    mapping = _get_fingerprint_nik_map(db)
    if fp_nik in mapping:
        del mapping[fp_nik]
        _save_fingerprint_nik_map(db, mapping)
    return {"status": "success"}


def _match_and_group_punches(db: Session, raw_logs: list[dict], target_date: date):
    """Match raw fingerprint logs to active employees and return (emp_punches, emp_map, unmatched_list)."""
    employees = db.query(models.Employee).filter(
        or_(models.Employee.is_active == True, models.Employee.is_active.is_(None))
    ).all()

    emp_by_id = {emp.id: emp for emp in employees}
    custom_fp_map = _get_fingerprint_nik_map(db)
    custom_map_updated = False

    by_nik = {}
    by_norm_name = {}
    by_phonetic = {}
    for emp in employees:
        if emp.nik_kepegawaian:
            by_nik[emp.nik_kepegawaian.strip()] = emp
        if emp.nip:
            by_nik[emp.nip.strip()] = emp
        norm = _norm_person_name(emp.nama_lengkap)
        if norm:
            by_norm_name[norm] = emp
        phon = _phonetic_person_key(emp.nama_lengkap)
        if phon:
            by_phonetic[phon] = emp

    # Overlay custom PIN/NIK mappings
    for fp_nik, info in custom_fp_map.items():
        emp_id = info.get("employee_id") if isinstance(info, dict) else info
        if emp_id in emp_by_id:
            by_nik[str(fp_nik).strip()] = emp_by_id[emp_id]

    emp_punches: dict[int, list[datetime]] = {}
    emp_map: dict[int, models.Employee] = {}
    unmatched_names = set()

    for log in raw_logs:
        raw_nik = str(log.get("nik") or log.get("Nik") or "").strip()
        raw_name = str(log.get("nama") or log.get("namee") or "").strip()
        raw_dt_str = str(log.get("tanggal") or "").strip()
        raw_time_str = str(log.get("waktu") or log.get("timee") or "").strip()

        emp = by_nik.get(raw_nik)
        if not emp and raw_name:
            norm_n = _norm_person_name(raw_name)
            phon_n = _phonetic_person_key(raw_name)
            emp = by_norm_name.get(norm_n) or by_phonetic.get(phon_n)
            if not emp and norm_n:
                for k_norm, candidate in by_norm_name.items():
                    if len(norm_n) >= 5 and (norm_n in k_norm or k_norm in norm_n):
                        emp = candidate
                        break
            if not emp and phon_n:
                for k_phon, candidate in by_phonetic.items():
                    if len(phon_n) >= 5 and (phon_n in k_phon or k_phon in phon_n):
                        emp = candidate
                        break

            # Auto-learn fingerprint PIN -> employee_id when matched by name
            if emp and raw_nik and raw_nik not in custom_fp_map:
                custom_fp_map[raw_nik] = {"employee_id": emp.id, "fp_name": raw_name}
                by_nik[raw_nik] = emp
                custom_map_updated = True

        if not emp:
            unmatched_names.add(f"{raw_name} ({raw_nik})")
            continue

        punch_dt = None
        if raw_dt_str:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                try:
                    punch_dt = datetime.strptime(raw_dt_str, fmt)
                    break
                except ValueError:
                    pass
        if not punch_dt and raw_time_str:
            for fmt in ("%I:%M:%S %p", "%H:%M:%S", "%H:%M"):
                try:
                    t_parsed = datetime.strptime(raw_time_str, fmt).time()
                    punch_dt = datetime.combine(target_date, t_parsed)
                    break
                except ValueError:
                    pass

        if punch_dt:
            emp_map[emp.id] = emp
            emp_punches.setdefault(emp.id, []).append(punch_dt)

    if custom_map_updated:
        _save_fingerprint_nik_map(db, custom_fp_map)

    return emp_punches, emp_map, sorted(list(unmatched_names))


def _save_single_employee_punches(
    db: Session,
    emp_id: int,
    punches: list[datetime],
    target_date: date,
    sh: int,
    sm: int,
    tol_mins: int = 0,
    auto_commit: bool = True
) -> tuple[str, str, Optional[str], Optional[str]]:
    """Save a single employee's grouped punches to DB and return (action, status_str, check_in_str, check_out_str)."""
    punches.sort()
    first_punch = punches[0]
    last_punch = punches[-1]

    check_in_dt = None
    check_out_dt = None

    if len(punches) == 1:
        if first_punch.hour >= 13:
            check_out_dt = first_punch
            check_in_dt = first_punch
        else:
            check_in_dt = first_punch
    else:
        check_in_dt = first_punch
        if (last_punch - first_punch).total_seconds() >= 600:
            check_out_dt = last_punch

    status_val = models.AttendanceStatus.PRESENT
    if check_in_dt:
        cutoff_minutes = (sh * 60) + sm + max(0, tol_mins)
        checkin_minutes = (check_in_dt.hour * 60) + check_in_dt.minute
        if checkin_minutes > cutoff_minutes:
            status_val = models.AttendanceStatus.LATE

    existing = db.query(models.EmployeeAttendance).filter(
        models.EmployeeAttendance.employee_id == emp_id,
        models.EmployeeAttendance.date == target_date
    ).first()

    note_tag = f"Sinkronisasi Fingerprint ({len(punches)}x tap)"

    if existing:
        curr_status = existing.status.value if hasattr(existing.status, "value") else str(existing.status)
        if curr_status in ("ABSENT", "PRESENT", "LATE"):
            existing.status = status_val
        if check_in_dt and (not existing.check_in or check_in_dt < existing.check_in):
            existing.check_in = check_in_dt
        if check_out_dt and (not existing.check_out or check_out_dt > existing.check_out):
            existing.check_out = check_out_dt
        if not existing.notes or "Sinkronisasi Fingerprint" in existing.notes or "Tidak ada data di Fingerprint" in existing.notes:
            existing.notes = note_tag
        action = "updated"
    else:
        db_att = models.EmployeeAttendance(
            employee_id=emp_id,
            date=target_date,
            status=status_val,
            check_in=check_in_dt,
            check_out=check_out_dt,
            notes=note_tag
        )
        db.add(db_att)
        action = "created"

    if auto_commit:
        db.commit()
    else:
        db.flush()

    return (
        action,
        status_val.value,
        check_in_dt.strftime("%H:%M:%S") if check_in_dt else None,
        check_out_dt.strftime("%H:%M:%S") if check_out_dt else None
    )


@router.get("/attendance/sync-fingerprint")
@router.post("/attendance/sync-fingerprint")
async def sync_fingerprint_attendance(
    req: Optional[FingerprintSyncRequest] = None,
    date_param: Optional[str] = Query(default=None, alias="date"),
    mode_param: Optional[str] = Query(default=None, alias="mode"),
    source_param: Optional[str] = Query(default=None, alias="source"),
    db: Session = Depends(get_db)
):
    """
    Sync employee attendance from external fingerprint API (sdit.asysyuuraa.my.id).
    Supports 3 modes:
    - mode="fetch_raw": Only fetches raw logs & matches employee queue so frontend can process 1-by-1 with progress bar.
    - mode="process_one": Processes a single employee's punches (step-by-step from frontend).
    - mode="all" (default / cron): Processes employee by employee sequentially with a small delay and logs the result.
    """
    import time
    from datetime import timezone, timedelta

    wib_now = datetime.now(timezone(timedelta(hours=7)))
    date_str = (req.date if req and req.date else None) or date_param or wib_now.strftime("%Y-%m-%d")
    mode = (req.mode if req and req.mode else None) or mode_param or "all"
    source = (req.source if req and req.source else None) or source_param or ("cron" if req is None else "manual")

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format tanggal tidak valid. Gunakan YYYY-MM-DD.")

    geofence = get_geofence_config(db)
    work_start = geofence.get("work_start_time", "07:30")
    tol_mins = int(geofence.get("late_tolerance_minutes", 0) or 0)
    sh, sm = 7, 30
    try:
        sh, sm = map(int, work_start.split(":"))
    except Exception:
        pass

    # MODE 1: Process a single employee step-by-step (called from frontend progress loop)
    if mode == "process_one":
        if not req or not req.employee_id or not req.raw_logs:
            raise HTTPException(status_code=400, detail="employee_id dan raw_logs wajib diisi untuk mode process_one.")
        punches = []
        for p_str in req.raw_logs:
            ts = p_str.get("timestamp") if isinstance(p_str, dict) else str(p_str)
            try:
                punches.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                pass
        if not punches:
            raise HTTPException(status_code=400, detail="Format waktu tap tidak valid.")
        action, st_val, c_in, c_out = _save_single_employee_punches(db, req.employee_id, punches, target_date, sh, sm, tol_mins)
        return {
            "status": "success",
            "employee_id": req.employee_id,
            "action": action,
            "attendance_status": st_val,
            "check_in": c_in,
            "check_out": c_out
        }

    # Fetch raw logs from sdit.asysyuuraa.my.id (12s strict timeout to prevent Gunicorn 30s worker kill)
    try:
        raw_logs = _fetch_sdit_fingerprint_logs(date_str, timeout_sec=12)
    except Exception as e:
        err_msg = f"Gagal menghubungi server mesin presensi (sdit.asysyuuraa.my.id / 192.168.188.222): {str(e)}"
        _append_fingerprint_sync_log(db, {
            "id": f"sync-{int(wib_now.timestamp() * 1000)}",
            "timestamp": wib_now.strftime("%Y-%m-%d %H:%M:%S WIB"),
            "date_target": date_str,
            "source": source,
            "status": "failed",
            "raw_count": 0,
            "synced_employees": 0,
            "failed_employees": 0,
            "unmatched_logs": [],
            "message": "Gagal menarik data dari mesin presensi (Koneksi ke 192.168.188.222 timeout/terputus).",
            "error_detail": str(e)
        })
        raise HTTPException(status_code=502, detail=err_msg)

    if not raw_logs:
        empty_msg = f"Tidak ditemukan data tap fingerprint pada tanggal {date_str}."
        _append_fingerprint_sync_log(db, {
            "id": f"sync-{int(wib_now.timestamp() * 1000)}",
            "timestamp": wib_now.strftime("%Y-%m-%d %H:%M:%S WIB"),
            "date_target": date_str,
            "source": source,
            "status": "empty",
            "raw_count": 0,
            "synced_employees": 0,
            "failed_employees": 0,
            "unmatched_logs": [],
            "message": empty_msg,
            "error_detail": None
        })
        return {
            "status": "empty",
            "date": date_str,
            "raw_count": 0,
            "synced_employees": 0,
            "queue": [],
            "unmatched_logs": [],
            "message": empty_msg
        }

    emp_punches, emp_map, unmatched_list = _match_and_group_punches(db, raw_logs, target_date)

    # MODE 2: Return matched queue to frontend so UI can process one by one with live progress bar
    if mode == "fetch_raw":
        queue = []
        for emp_id, punches in emp_punches.items():
            emp = emp_map[emp_id]
            queue.append({
                "employee_id": emp_id,
                "nama_lengkap": emp.nama_lengkap,
                "nik_kepegawaian": emp.nik_kepegawaian,
                "punches": [{"timestamp": p.strftime("%Y-%m-%d %H:%M:%S")} for p in sorted(punches)]
            })
        return {
            "status": "success",
            "date": date_str,
            "raw_count": len(raw_logs),
            "synced_employees": len(queue),
            "queue": queue,
            "unmatched_logs": unmatched_list,
            "message": f"Ditemukan {len(raw_logs)} log untuk {len(queue)} pegawai. Memulai pemrosesan satu per satu..."
        }

    # MODE 3: Sequential one-by-one processing (for Cron Job or direct call)
    created_count = 0
    updated_count = 0
    failed_count = 0
    errors_detail = []

    for emp_id, punches in emp_punches.items():
        try:
            action, _, _, _ = _save_single_employee_punches(db, emp_id, punches, target_date, sh, sm, tol_mins, auto_commit=False)
            if action == "created":
                created_count += 1
            else:
                updated_count += 1
        except Exception as ex:
            db.rollback()
            failed_count += 1
            emp_name = emp_map[emp_id].nama_lengkap if emp_id in emp_map else f"ID {emp_id}"
            errors_detail.append(f"{emp_name}: {str(ex)}")

    try:
        db.commit()
    except Exception:
        db.rollback()

    # Mark remaining active employees who had NO fingerprint data on target_date
    try:
        _mark_missing_fingerprint_employees(db, target_date)
    except Exception:
        db.rollback()

    final_status = "success" if failed_count == 0 else ("partial" if (created_count + updated_count) > 0 else "failed")
    summary_msg = f"Berhasil menyinkronkan {created_count + updated_count} pegawai dari {len(raw_logs)} log mesin fingerprint pada tanggal {date_str}."
    if failed_count > 0:
        summary_msg += f" ({failed_count} gagal diproses)"

    _append_fingerprint_sync_log(db, {
        "id": f"sync-{int(wib_now.timestamp() * 1000)}",
        "timestamp": wib_now.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "date_target": date_str,
        "source": source,
        "status": final_status,
        "raw_count": len(raw_logs),
        "synced_employees": created_count + updated_count,
        "failed_employees": failed_count,
        "unmatched_logs": unmatched_list,
        "message": summary_msg,
        "error_detail": "; ".join(errors_detail) if errors_detail else None
    })

    return {
        "status": final_status,
        "date": date_str,
        "raw_count": len(raw_logs),
        "synced_employees": created_count + updated_count,
        "created": created_count,
        "updated": updated_count,
        "failed": failed_count,
        "unmatched_logs": unmatched_list,
        "message": summary_msg
    }


class FingerprintRangeSyncRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD


@router.post("/attendance/sync-fingerprint-range")
async def sync_fingerprint_attendance_range(
    req: FingerprintRangeSyncRequest,
    db: Session = Depends(get_db)
):
    """
    Sync attendance for a date range (e.g. 2026-10-01 to today).
    Iterates day by day with pacing so external machine & database are not overloaded.
    """
    from datetime import timedelta
    try:
        s_date = datetime.strptime(req.start_date, "%Y-%m-%d").date()
        e_date = datetime.strptime(req.end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format tanggal tidak valid. Gunakan YYYY-MM-DD.")

    if s_date > e_date:
        raise HTTPException(status_code=400, detail="Tanggal mulai tidak boleh lebih besar dari tanggal selesai.")

    if (e_date - s_date).days > 365:
        raise HTTPException(status_code=400, detail="Rentang tanggal maksimal 365 hari (1 tahun).")

    results = []
    curr = s_date
    while curr <= e_date:
        d_str = curr.strftime("%Y-%m-%d")
        try:
            res = await sync_fingerprint_attendance(
                req=FingerprintSyncRequest(date=d_str, mode="all", source="manual"),
                db=db
            )
            results.append({"date": d_str, "status": res.get("status"), "message": res.get("message")})
        except Exception as e:
            results.append({"date": d_str, "status": "failed", "message": str(e)})
        curr += timedelta(days=1)

    return {"status": "completed", "results": results}


