import os
import json
import pdfplumber
from datetime import datetime

PDF_PATH = "/Users/rezaaldi/Downloads/file asy syuuraa/DATA PESERTA DIDIK, KELAS & MAPEL SDIT ASY SYUURAA.pdf"
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdit_data.json")

TEACHERS = {
    'Reni': {'nik': '1020140060', 'name': 'Yulia Reni, S.Pd., Gr.', 'email': 'yulia.reni@asy-syuuraabatam.or.id'},
    'Anjar': {'nik': '1120090019', 'name': 'Anjar Puji Astutik, S.Pd.AUD., Gr.', 'email': 'anjar.puji@asy-syuuraabatam.or.id'},
    'Elna': {'nik': '1120160082', 'name': 'Elnawati, S.E.I., Gr.', 'email': 'elnawati@asy-syuuraabatam.or.id'},
    'Nadia': {'nik': '1120220144', 'name': 'Nadia Nefianti, S.Pd., Gr.', 'email': 'nadia.nefianti@asy-syuuraabatam.or.id'},
    'Ade': {'nik': '1120170092', 'name': 'Ade Mulyana, S.Pd., Gr.', 'email': 'ade.mulyana@asy-syuuraabatam.or.id'},
    'Seri': {'nik': '1120090017', 'name': 'Seri Rahmadhani, S.Pd., Gr.', 'email': 'seri.rahmadani@asy-syuuraabatam.or.id'},
    'Nory': {'nik': '1120150067', 'name': 'Nory Fadhillah, S.Pd.I., Gr.', 'email': 'nory.fadhillah@asy-syuuraabatam.or.id'},
    'Lastri': {'nik': '1120160087', 'name': 'Sulastri, S.E., Gr.', 'email': 'sulastri@asy-syuuraabatam.or.id'},
    'Hafsah': {'nik': '1120230168', 'name': 'Hafsah Fauziyyah Yusra, S.Pd., Gr.', 'email': 'hafsah.fauziyyah@asy-syuuraabatam.or.id'},
    'Yellya': {'nik': '1120090020', 'name': 'Yellya Asri, S.Pd., Gr.', 'email': 'yellya.asri@asy-syuuraabatam.or.id'},
    'Aji': {'nik': '1120240171', 'name': 'Aji Pramana, S.Pd', 'email': 'ajipramana250617@gmail.com'},
    'Deby': {'nik': '1120220152', 'name': 'Debby Liyany Ra\'ad, S.Pd., Gr.', 'email': 'debby.liyani@asy-syuuraabatam.or.id'},
    'Ayu': {'nik': '1120220146', 'name': 'Ayu Zahara Salsabila', 'email': 'ayu.zahara@asy-syuuraabatam.or.id'},
    'Fifah': {'nik': '1120240176', 'name': 'Khafifah Mulya Ikhwani, S.Ag', 'email': 'khafifah.mulya@asy-syuuraabatam.or.id'},
    'Tholib': {'nik': '1220240177', 'name': 'Muhammad Tholibin Azhari, QH. M.Pd', 'email': 'm.tholibin@asy-syuuraabatam.or.id'},
    'Febri': {'nik': '1120130048', 'name': 'Febriani, S.Si', 'email': 'febriani@asy-syuuraabatam.or.id'},
    'Baiq': {'nik': '1120190116', 'name': 'Baiq Dwi Alfiani.H, S.Pd.I', 'email': 'baiq.dwi@asy-syuuraabatam.or.id'},
    'Is': {'nik': '1120230157', 'name': 'Iswandi, SH', 'email': 'iswandi@asy-syuuraabatam.or.id'},
    'Agus': {'nik': '1120220154', 'name': 'Agus Kurniawan, S.Ag', 'email': 'agus.kurniawan@asy-syuuraabatam.or.id'},
    'Yeni': {'nik': '1120080014', 'name': 'Siti Yeni Nur Hidayat, S.T', 'email': 'siti.yeni@asy-syuuraabatam.or.id'},
}

SUBJECT_NAMES = {
    'MTK': 'Matematika',
    'BI': 'Bahasa Indonesia',
    'IPAS': 'Ilmu Pengetahuan Alam dan Sosial',
    'BING': 'Bahasa Inggris',
    'TIK': 'Teknologi Informasi dan Komunikasi',
    'AA': 'Aqidah Akhlak',
    'PJOK': 'Pendidikan Jasmani, Olahraga, dan Kesehatan',
    'TTQ': 'Tahsin / Tahfidz Al-Qur\'an',
    'SR': 'Seni Rupa',
    'PP': 'Pendidikan Pancasila',
    'SBM': 'Seni Budaya & Musik',
    'BA': 'Bahasa Arab',
    'SKI': 'Sejarah Kebudayaan Islam',
    'FIK': 'Fiqih',
    'QH': 'Al-Qur\'an Hadits',
    'KKA': 'Koding & Kecerdasan Artifisial',
}

CLASSROOM_SPECS = [
    {'name': '1', 'level': 1, 'wali_key': 'Reni'},
    {'name': '2', 'level': 2, 'wali_key': 'Anjar'},
    {'name': '3A', 'level': 3, 'wali_key': 'Elna'},
    {'name': '3B', 'level': 3, 'wali_key': 'Nadia'},
    {'name': '4A', 'level': 4, 'wali_key': 'Ade'},
    {'name': '4B', 'level': 4, 'wali_key': 'Seri'},
    {'name': '5A', 'level': 5, 'wali_key': 'Nory'},
    {'name': '5B', 'level': 5, 'wali_key': 'Lastri'},
    {'name': '6A', 'level': 6, 'wali_key': 'Hafsah'},
    {'name': '6B', 'level': 6, 'wali_key': 'Yellya'},
]

COLOR_TEACHER_MAP = {
    (0.855, 0.588, 0.58): 'Reni',
    (0.98, 0.749, 0.561): 'Anjar',
    (0.463, 0.89, 1.0): 'Elna',
    (0.824, 0.941, 0.384): 'Nadia',
    (0.847, 0.086, 0.847): 'Ade',
    (0.133, 0.478, 0.796): 'Seri',
    (0.0, 0.0, 0.8): 'Nory',
    (0.408, 0.196, 0.784): 'Lastri',
    (0.0, 1.0, 0.0): 'Hafsah',
    (0.58, 0.541, 0.329): 'Yellya',
    (0.886, 0.42, 0.039): 'Aji',
    (0.675, 0.31, 0.235): 'Deby',
    0.502: 'Is',
    (0.933, 0.925, 0.882): 'Agus',
    0.949: 'Agus',
    (0.855, 0.933, 0.953): 'Fifah',
    (0.2, 0.6, 0.4): 'Yeni',
    (1.0, 0.0, 0.0): 'Tholib',
    (0.0, 0.69, 0.314): 'Febri',
    (1.0, 0.2, 0.6): 'Baiq',       # TTQ 1
    (0.573, 0.816, 0.314): 'Tholib', # TTQ 3
    (0.965, 0.765, 1.0): 'Ayu',      # TTQ 4
    (1.0, 1.0, 0.0): 'Baiq',         # TTQ 5 & 6
}

def parse_all():
    with pdfplumber.open(PDF_PATH) as pdf:
        # 1. Parse Students
        print("Parsing students from pages 1-8...")
        students = []
        for p_idx in range(8):
            p = pdf.pages[p_idx]
            for t in p.extract_tables():
                for row in t:
                    vals = [c for c in row if c is not None and str(c).strip() != '']
                    if not vals or not vals[0].isdigit():
                        continue
                    no = int(vals[0])
                    nama = vals[1]
                    nis = vals[2]
                    gender = vals[3]
                    if len(vals) == 8:
                        nisn, pob, dob, rombel = vals[4], vals[5], vals[6], vals[7]
                    elif len(vals) == 7:
                        if '-' in vals[5]:
                            nisn, pob, dob, rombel = None, vals[4], vals[5], vals[6]
                        else:
                            nisn, pob, dob, rombel = vals[4], vals[5], None, vals[6]
                    else:
                        continue
                    
                    rombel_clean = rombel.replace('Kelas ', '').replace('kelas ', '').strip().upper()
                    students.append({
                        'no': no,
                        'name': nama,
                        'nis': nis,
                        'gender': gender,
                        'nisn': nisn,
                        'birth_place': pob,
                        'birth_date': dob,
                        'classroom': rombel_clean
                    })
        print(f"Total students parsed: {len(students)}")

        # 2. Parse Schedules from page 22
        print("Parsing schedules from page 22...")
        p22 = pdf.pages[21]
        t = p22.extract_tables()[0]
        
        # Build color lookup from rects
        # Group rects by day and time slot
        rects = [r for r in p22.rects if r['top'] < 450 and r.get('non_stroking_color') not in [None, 0.0, 1.0, 0.831]]

        def get_cell_color(x, y):
            for r in rects:
                if r['x0'] - 2 <= x <= r['x1'] + 2 and r['top'] - 2 <= y <= r['bottom'] + 2:
                    c = r['non_stroking_color']
                    return round(c, 3) if isinstance(c, float) else tuple(round(v, 3) for v in c)
            return None

        # Sections definition
        # (day_name, row_indices_and_times, time_col_idx, class_cols)
        class_cols_left = [
            ('1', 1), ('2', 2), ('3A', 3), ('3B', 4), ('4A', 5),
            ('4B', 6), ('5A', 7), ('5B', 8), ('6A', 9), ('6B', 10)
        ]
        class_cols_right = [
            ('1', 13), ('2', 14), ('3A', 15), ('3B', 16), ('4A', 17),
            ('4B', 18), ('5A', 19), ('5B', 20), ('6A', 21), ('6B', 22)
        ]

        weekday_rows = [
            (3, '07:30', '08:05'),
            (4, '08:05', '08:40'),
            (5, '08:40', '09:15'),
            # 6 is istirahat
            (7, '09:35', '10:10'),
            (8, '10:10', '10:45'),
            (9, '10:45', '11:20'),
            (10, '11:20', '11:55'),
            # 11 is ishoma
            (12, '12:55', '13:30'),
            (13, '13:30', '14:05'),
            (14, '14:05', '14:40'),
        ]

        jumat_rows = [
            (35, '07:30', '08:05'),
            (36, '08:05', '08:40'),
            (37, '08:40', '09:15'),
            # 38 is istirahat
            (39, '09:35', '10:10'),
            (40, '10:10', '10:45'),
        ]

        days_plan = [
            ('Senin', weekday_rows, class_cols_left),
            ('Selasa', weekday_rows, class_cols_right),
            ('Rabu', [(r + 16, st, et) for r, st, et in weekday_rows], class_cols_left),
            ('Kamis', [(r + 16, st, et) for r, st, et in weekday_rows], class_cols_right),
            ('Jumat', jumat_rows, class_cols_left),
        ]

        schedules = []
        for day, rows_cfg, cols_cfg in days_plan:
            for r_idx, start_t, end_t in rows_cfg:
                row_data = t[r_idx]
                for cr_name, c_idx in cols_cfg:
                    val = row_data[c_idx]
                    if not val or val.strip() == '' or val.strip().lower() in ['istirahat', 'sholat', 'upacara', 'senam']:
                        continue
                    
                    val_clean = val.strip()
                    
                    # Handle merged or special text
                    subject_code = val_clean
                    teacher_key = None
                    
                    if 'SR/YENI' in val_clean:
                        subject_code = 'SR'
                        teacher_key = 'Yeni'
                    elif 'QH/AGUS' in val_clean:
                        subject_code = 'QH'
                        teacher_key = 'Agus'
                    elif 'nad, khaf' in val_clean:
                        subject_code = 'TTQ'
                        teacher_key = 'Nadia'
                    elif 'Baiq, ayu' in val_clean:
                        subject_code = 'TTQ'
                        teacher_key = 'Baiq'
                    elif 'HIL, KHAF, FEB' in val_clean:
                        subject_code = 'TTQ'
                        teacher_key = 'Tholib'
                    elif 'ay.haf,khaf,hil' in val_clean:
                        subject_code = 'TTQ'
                        teacher_key = 'Ayu'
                    elif 'Ba, Ay, hil, is,YEL' in val_clean or 'Ba, Ay, hil, is,no' in val_clean:
                        subject_code = 'TTQ'
                        teacher_key = 'Baiq'
                    elif subject_code == 'TTQ':
                        teacher_key = 'Baiq'

                    # Extract primary subject code if multi-line or prefixed
                    subject_code = subject_code.split('\n')[0].split('/')[0].strip()
                    if subject_code not in SUBJECT_NAMES:
                        # Try finding subject keyword
                        for code in SUBJECT_NAMES.keys():
                            if code in subject_code:
                                subject_code = code
                                break

                    # If teacher_key not determined by text, determine by classroom wali or subject
                    if not teacher_key:
                        # Check homeroom assignments for standard subjects:
                        # Kelas 1: Reni
                        # Kelas 2: Anjar
                        # Kelas 3A: Elna
                        # Kelas 3B: Nadia
                        # Kelas 4A: Ade
                        # Kelas 4B: Seri
                        # Kelas 5A: Nory
                        # Kelas 5B: Lastri
                        # Kelas 6A: Hafsah
                        # Kelas 6B: Yellya
                        
                        # Subject-specific specialists:
                        if subject_code == 'PJOK':
                            teacher_key = 'Aji'
                        elif subject_code == 'BING':
                            if cr_name == '2':
                                teacher_key = 'Reni'
                            else:
                                teacher_key = 'Deby'
                        elif subject_code == 'SBM' and cr_name in ['5B', '6A', '6B']:
                            teacher_key = 'Aji'
                        elif subject_code == 'SR' and cr_name in ['5B', '6A', '6B']:
                            teacher_key = 'Yeni'
                        elif subject_code == 'BI' and cr_name in ['6A', '6B']:
                            teacher_key = 'Fifah'
                        elif subject_code in ['AA', 'FIK'] and cr_name in ['4A', '4B']:
                            teacher_key = 'Is'
                        elif subject_code == 'QH' and cr_name in ['3B', '4B']:
                            teacher_key = 'Is'
                        elif subject_code in ['FIK', 'BA'] and cr_name in ['6A', '6B', '5A', '5B']:
                            teacher_key = 'Agus'
                        elif subject_code == 'QH' and cr_name in ['3A', '6A', '6B']:
                            teacher_key = 'Agus'
                        elif subject_code == 'FIK' and cr_name in ['3A', '3B']:
                            teacher_key = 'Febri'
                        elif subject_code in ['QH', 'FIK'] and cr_name in ['5A', '5B']:
                            teacher_key = 'Tholib'
                        elif subject_code == 'SKI' and cr_name in ['3A', '3B']:
                            teacher_key = 'Reni'
                        else:
                            # Default to homeroom teacher
                            wali_map = {cs['name']: cs['wali_key'] for cs in CLASSROOM_SPECS}
                            teacher_key = wali_map.get(cr_name, 'Reni')

                    teacher_info = TEACHERS.get(teacher_key, TEACHERS['Reni'])
                    subject_name = SUBJECT_NAMES.get(subject_code, subject_code)

                    schedules.append({
                        'day': day,
                        'start_time': start_t,
                        'end_time': end_t,
                        'classroom_name': cr_name,
                        'subject_code': subject_code,
                        'subject_name': subject_name,
                        'teacher_nik': teacher_info['nik'],
                        'teacher_name': teacher_info['name'],
                        'teacher_email': teacher_info['email'],
                    })

        print(f"Total schedules parsed: {len(schedules)}")
        
        final_data = {
            'unit': {'name': 'SDIT Asy-Syuuraa', 'code': 'SDIT'},
            'classrooms': CLASSROOM_SPECS,
            'subjects': [{'code': k, 'name': v} for k, v in SUBJECT_NAMES.items()],
            'teachers': list(TEACHERS.values()),
            'students': students,
            'schedules': schedules
        }

        with open(OUTPUT_PATH, 'w') as out_f:
            json.dump(final_data, out_f, indent=2)
        print(f"Saved complete SDIT dataset to {OUTPUT_PATH}!")

if __name__ == '__main__':
    parse_all()
