# Software Requirements Specification (SRS)
# Sistem Informasi Sekolah Asy-Syuuraa Batam

> **Version:** 1.0  
> **Tanggal:** 22 Januari 2026  
> **Standard:** IEEE 830-1998 (Modified)  
> **Status:** Draft untuk Review

---

## 1. Pendahuluan

### 1.1 Tujuan Dokumen
Dokumen SRS ini menjelaskan secara detail **spesifikasi kebutuhan software** untuk pengembangan Sistem Informasi Sekolah Asy-Syuuraa Batam. Dokumen ini menjadi acuan bagi:
- Tim pengembangan dalam membangun sistem
- Tim QA dalam testing dan validasi
- Stakeholder dalam review dan approval

### 1.2 Lingkup Produk
Produk yang dikembangkan adalah **aplikasi web berbasis cloud** yang terdiri dari:
1. **Landing Page** - Website publik untuk promosi sekolah
2. **Admin Dashboard** - Sistem internal untuk pengelolaan sekolah
3. **Portal Orangtua** - Dashboard orangtua untuk monitoring anak

### 1.3 Definisi dan Akronim

| Term | Definisi |
|------|----------|
| RA | Raudhatul Athfal (TK/PAUD Islam) |
| SDIT | Sekolah Dasar Islam Terpadu |
| SMPIT | Sekolah Menengah Pertama Islam Terpadu |
| NIS | Nomor Induk Siswa |
| NIK | Nomor Induk Pegawai |
| NISN | Nomor Induk Siswa Nasional |
| SPP | Sumbangan Pembinaan Pendidikan |
| Marhalah | Tingkatan/jenjang pendidikan |
| Tahfidz | Hafalan Al-Quran |
| Kesantrian | Aspek kepribadian/karakter santri |
| Halaqoh | Kelompok belajar Al-Quran |
| ACL | Access Control List |
| JWT | JSON Web Token |
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| VPS | Virtual Private Server |

### 1.4 Referensi
- Dokumen SQL database existing: `asyuraa.sql`
- IEEE 830-1998 Software Requirements Specification Standard
- PRD Sistem Informasi Sekolah Asy-Syuuraa Batam v1.0

---

## 2. Deskripsi Umum Produk

### 2.1 Perspektif Produk
Sistem ini merupakan **pengembangan baru** yang menggantikan sistem lama berbasis PHP native. Sistem baru dibangun dengan:
- **Arsitektur modern**: Frontend-Backend terpisah (decoupled)
- **API-first design**: RESTful API untuk fleksibilitas
- **Cloud-native**: Containerized dengan Docker
- **Responsive design**: Mobile-first approach

### 2.2 Fungsi Utama Produk

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEM INFORMASI SEKOLAH                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ LANDING PAGE  │  │ ADMIN PANEL   │  │PORTAL ORANGTUA│   │
│  │  (Publik)     │  │  (Internal)   │  │  (Wali Murid) │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│                   ┌────────┴────────┐                       │
│                   │   BACKEND API   │                       │
│                   │    (Python)     │                       │
│                   └────────┬────────┘                       │
│                            │                                │
│                   ┌────────┴────────┐                       │
│                   │   PostgreSQL    │                       │
│                   │    Database     │                       │
│                   └─────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Karakteristik Pengguna

| User Class | Karakteristik | Level Teknis |
|------------|---------------|--------------|
| Superadmin | IT staff, manajemen sistem | Tinggi |
| Tata Usaha | Staff administrasi, familiar komputer | Menengah |
| Kepala Bidang | Manajemen, decision maker | Menengah |
| Staf Keuangan | Operator keuangan | Menengah |
| Guru | Pendidik, input nilai & absensi | Dasar-Menengah |
| Orangtua | Berbagai latar belakang | Dasar |
| Pengunjung Web | Masyarakat umum | Bervariasi |

### 2.4 Batasan Umum
- Sistem membutuhkan **koneksi internet**
- Browser yang didukung: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Minimum screen resolution: 320px (mobile)
- Database harus **PostgreSQL 14+**
- Server hosting di **BiznetGio VPS** dengan Docker

### 2.5 Asumsi dan Dependensi
- Data siswa dan keuangan akan dimigrasi dari database existing
- Domain dan SSL sudah tersedia
- VPS BiznetGio sudah aktif dengan EasyPanel/CyberPanel
- Cloudflare R2 atau Cloudinary tersedia untuk file storage

---

## 3. Kebutuhan Spesifik

### 3.1 Kebutuhan Fungsional

---

#### 3.1.1 Modul Autentikasi dan Manajemen User

##### REQ-AUTH-001: Login Sistem
| Atribut | Detail |
|---------|--------|
| ID | REQ-AUTH-001 |
| Nama | Login Sistem Multi-role |
| Deskripsi | Sistem harus memungkinkan user login dengan username/email dan password sesuai rolenya |
| Prioritas | **Mandatory** |
| Aktor | Semua user terotentikasi |

**Input:**
- Username atau email
- Password

**Proses:**
- Validasi kredensial terhadap database
- Generate JWT token jika valid
- Load permission/menu sesuai role

**Output:**
- JWT access token (expire 24 jam)
- Refresh token (expire 7 hari)
- User profile dengan role dan permissions
- Redirect ke dashboard sesuai role

**Validasi:**
- Username/email tidak boleh kosong
- Password minimal 8 karakter
- Maksimal 5 kali gagal login = lock 30 menit

---

##### REQ-AUTH-002: Logout
| Atribut | Detail |
|---------|--------|
| ID | REQ-AUTH-002 |
| Nama | Logout User |
| Prioritas | **Mandatory** |

**Proses:**
- Invalidate token di server
- Clear session/localStorage
- Redirect ke halaman login

---

##### REQ-AUTH-003: Reset Password
| Atribut | Detail |
|---------|--------|
| ID | REQ-AUTH-003 |
| Nama | Self-service Password Reset |
| Prioritas | High |

**Flow:**
1. User request reset via email
2. Sistem generate reset token (expire 1 jam)
3. Kirim email dengan link reset
4. User set password baru
5. Invalidate semua session existing

---

##### REQ-AUTH-004: Manajemen User (Admin)
| Atribut | Detail |
|---------|--------|
| ID | REQ-AUTH-004 |
| Nama | CRUD User Account |
| Prioritas | **Mandatory** |
| Aktor | Superadmin |

**Fungsionalitas:**
- Create: Buat akun user baru dengan role
- Read: List dan detail user
- Update: Edit profil dan role user
- Delete: Soft delete user (deactivate)

**Data User (acl_users):**
```
- id: INT PRIMARY KEY
- nik: VARCHAR(20) - Nomor Induk
- username: VARCHAR(50)
- email: VARCHAR(100)
- password_hash: VARCHAR(255)
- role_id: INT FK to roles
- is_active: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- last_login: TIMESTAMP
```

---

##### REQ-AUTH-005: Role-Based Access Control (RBAC)
| Atribut | Detail |
|---------|--------|
| ID | REQ-AUTH-005 |
| Nama | Sistem Kontrol Akses |
| Prioritas | **Mandatory** |

**Definisi Unit (units):**
```
- id: INT PRIMARY KEY
- code: VARCHAR(10) UNIQUE - 'YYS', 'RA', 'SDIT', 'SMPIT'
- name: VARCHAR(100)
- description: TEXT
- is_active: BOOLEAN
- created_at: TIMESTAMP
```

| Kode | Nama Unit | Level | Keterangan |
|------|-----------|-------|------------|
| `YYS` | Yayasan Asy-Syuuraa | 0 | Level tertinggi, mengawasi semua unit |
| `RA` | RA Asy-Syuuraa | 1 | Raudhatul Athfal (TK/PAUD) |
| `SDIT` | SDIT Asy-Syuuraa | 1 | Sekolah Dasar Islam Terpadu |
| `SMPIT` | SMPIT Asy-Syuuraa | 1 | Sekolah Menengah Pertama Islam Terpadu |

**Hierarki Role dengan Level Akses:**

| Role | Kode | Scope | Unit Default | Prioritas | Deskripsi |
|------|------|-------|--------------|-----------|-----------|
| Superadmin | `superadmin` | Sistem | ALL | 1 | Full access, konfigurasi sistem |
| Kabid Umum | `kabid_umum` | Yayasan | ALL | 2 | Data umum semua unit |
| Kabid Keuangan | `kabid_keuangan` | Yayasan | ALL | 2 | Data keuangan semua unit |
| TU Yayasan | `tu_yayasan` | Yayasan | ALL | 3 | Administrasi semua unit |
| Staf Keuangan | `staf_keuangan` | Yayasan | ALL | 3 | Pembayaran & tagihan |
| Kepala Unit | `kepala_unit` | Unit | Assigned | 4 | Full access data unit |
| Wakil Kepala Unit | `wakil_kepala` | Unit | Assigned | 5 | Akses unit (non-keuangan) |
| TU Unit | `tu_unit` | Unit | Assigned | 6 | Administrasi unit |
| Guru | `guru` | Unit | Assigned | 7 | Nilai, absensi |
| Karyawan | `karyawan` | Unit | Assigned | 8 | Akses minimal |
| Orangtua | `orangtua` | Portal | - | 9 | Data anak sendiri |

**Data Role (roles):**
```
- id: INT PRIMARY KEY
- code: VARCHAR(50) UNIQUE
- name: VARCHAR(100)
- scope: ENUM('sistem', 'yayasan', 'unit', 'portal')
- priority: INT - untuk hierarki
- description: TEXT
- is_active: BOOLEAN
```

**Data User dengan Unit Assignment (users):**
```
- id: INT PRIMARY KEY
- nik: VARCHAR(20)
- username: VARCHAR(50) UNIQUE
- email: VARCHAR(100) UNIQUE
- password_hash: VARCHAR(255)
- role_id: INT FK roles
- is_active: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- last_login: TIMESTAMP
```

**Mapping User ke Unit (user_units):**
```
- id: INT PRIMARY KEY
- user_id: INT FK users
- unit_code: VARCHAR(10) FK units
- is_primary: BOOLEAN - unit utama jika multi-unit
- created_at: TIMESTAMP
```

> **Catatan:** User dengan scope `unit` bisa di-assign ke satu atau lebih unit. Contoh: Guru yang mengajar di SDIT dan SMPIT memiliki 2 record di user_units.

**Aturan Filtering Data berdasarkan Scope:**

| Scope | Query Filter | Contoh |
|-------|-------------|--------|
| `sistem` | Tidak ada filter | Superadmin lihat semua |
| `yayasan` | Tidak ada filter | Kabid lihat semua unit |
| `unit` | `WHERE unit_code IN (user_units)` | Kepala SDIT hanya lihat SDIT |
| `portal` | `WHERE siswa.nis IN (orangtua.anak)` | Ortu lihat anak sendiri |

**Menu Access (acl_menus):**
```
- id: INT PRIMARY KEY
- route: VARCHAR(255)
- name: VARCHAR(100)
- icon: VARCHAR(50)
- parent_id: INT - hierarki menu
- sort_order: INT
- is_active: BOOLEAN
```

**Permission per Role (role_permissions):**
```
- id: INT PRIMARY KEY
- role_id: INT FK roles
- menu_id: INT FK acl_menus
- can_view: BOOLEAN
- can_create: BOOLEAN
- can_update: BOOLEAN
- can_delete: BOOLEAN
```

**Contoh Login Flow:**
1. User login dengan username/password
2. Sistem load role dan scope
3. Jika scope = 'unit', load unit assignment dari user_units
4. Filter semua query dengan unit yang di-assign
5. Tampilkan menu sesuai role_permissions

---

#### 3.1.2 Modul Data Siswa

##### REQ-SISWA-001: List Data Siswa
| Atribut | Detail |
|---------|--------|
| ID | REQ-SISWA-001 |
| Nama | Daftar Siswa dengan Filter |
| Prioritas | **Mandatory** |
| Aktor | Tata Usaha, Guru, Kabid |

**Filter Options:**
- Marhalah (RA/SDIT/SMPIT)
- Kelas
- Status (aktif/alumni/keluar)
- Nama (search)
- NIS

**Output:**
- Tabel dengan pagination (20 per page)
- Export Excel, PDF
- Quick view detail

---

##### REQ-SISWA-002: Detail Data Siswa
| Atribut | Detail |
|---------|--------|
| ID | REQ-SISWA-002 |
| Nama | View Detail Siswa Lengkap |
| Prioritas | **Mandatory** |

**Data yang ditampilkan:**

**Tab 1: Data Pribadi**
```
- NIS (Primary Key)
- NISN
- NIK
- Nama siswa
- Kota lahir
- Tanggal lahir
- Jenis kelamin
- Golongan darah
- Anak ke / dari bersaudara
- Foto
- Status kewarganegaraan
```

**Tab 2: Data Orangtua**
```
Ayah:
- Nama
- NIK
- Tempat/tanggal lahir
- Pekerjaan
- Pendidikan
- Penghasilan
- No HP

Ibu:
- Nama
- NIK
- Tempat/tanggal lahir
- Pekerjaan
- Pendidikan
- Penghasilan

Alamat:
- Alamat lengkap
- Kelurahan
- Kecamatan
- Kota
- Provinsi
- Telepon
```

**Tab 3: Data Akademik**
```
- Marhalah
- Kelas saat ini
- Wali kelas
- Asal sekolah
- Alamat sekolah asal
- Tanggal masuk
- No. Induk sekolah
- Ijazah
- Akte
- SKHUN
```

**Tab 4: Data Asrama (jika ada)**
```
- Nama asrama
- Nama kamar
- Wali asrama
- Murobbi
- Limit laundry bulanan
- Kuota izin
- Status cekal izin
```

**Tab 5: Data Keuangan**
```
- Nominal SPP
- Uang pangkal
- Daftar ulang
- Piutang
- Catatan piutang
- Status blokir rapor
- Virtual Account (SPP, uang saku, daftar ulang)
```

---

##### REQ-SISWA-003: Tambah Siswa Baru
| Atribut | Detail |
|---------|--------|
| ID | REQ-SISWA-003 |
| Nama | Input Data Siswa Baru |
| Prioritas | **Mandatory** |
| Aktor | Tata Usaha |

**Validasi:**
- NIS unik dan wajib diisi
- Nama wajib diisi
- Format tanggal lahir valid
- No HP valid (format Indonesia)
- File foto max 2MB, format JPG/PNG

**Flow:**
1. Form multi-step (wizard)
2. Step 1: Data pribadi
3. Step 2: Data orangtua
4. Step 3: Data akademik
5. Step 4: Upload dokumen
6. Preview & submit

---

##### REQ-SISWA-004: Edit Data Siswa
| Atribut | Detail |
|---------|--------|
| ID | REQ-SISWA-004 |
| Nama | Update Data Siswa |
| Prioritas | **Mandatory** |

- Semua field dapat diupdate kecuali NIS
- Simpan history perubahan (audit trail)

---

##### REQ-SISWA-005: Kenaikan Kelas
| Atribut | Detail |
|---------|--------|
| ID | REQ-SISWA-005 |
| Nama | Proses Kenaikan Kelas Bulk |
| Prioritas | High |

**Flow:**
1. Pilih tahun ajaran baru
2. Pilih kelas asal
3. Mapping ke kelas tujuan
4. Pilih siswa yang naik/tidak naik
5. Proses batch update

---

##### REQ-SISWA-006: Kelulusan Siswa
| Atribut | Detail |
|---------|--------|
| ID | REQ-SISWA-006 |
| Nama | Proses Kelulusan |
| Prioritas | High |

- Update status siswa menjadi "lulus"
- Arsip data siswa
- Tetap dapat diakses untuk alumni

---

#### 3.1.3 Modul Data Pegawai

##### REQ-PEGAWAI-001: CRUD Data Pegawai
| Atribut | Detail |
|---------|--------|
| ID | REQ-PEGAWAI-001 |
| Nama | Manajemen Data Guru/Karyawan |
| Prioritas | **Mandatory** |

**Data Pegawai (pegawai):**
```
Data Pribadi:
- NIK (Primary Key)
- Nama lengkap
- Nama panggilan
- Jenis kelamin
- TTL
- Alamat lengkap
- No HP
- No KTP
- Status nikah
- No BPJS
- NPWP
- Golongan darah

Data Keluarga:
- Nama ayah/ibu
- Jumlah istri (pria)
- Jumlah anak

Data Kepegawaian:
- NIY (No Induk Yayasan)
- Tanggal mulai bekerja
- Masa kerja (auto calculate)
- Golongan
- Jabatan
- Jabatan struktural
- Divisi
- Unit (RA/SDIT/SMPIT/Yayasan)
- Status aktif/keluar

Riwayat Pendidikan:
- SD, SMP, SMA
- Universitas
- Gelar
- Fakultas
- Jurusan
- Tahun lulus

Data Pengajaran (untuk guru):
- Mapel diampu
- Jam mengajar
- Status pendidik
- Jenis tenaga

Pelatihan:
- Nama pelatihan
- Jenis
- Penyelenggara
- Tanggal
```

---

#### 3.1.4 Modul Kelas dan Akademik

##### REQ-KELAS-001: Manajemen Kelas
| Atribut | Detail |
|---------|--------|
| ID | REQ-KELAS-001 |
| Nama | CRUD Data Kelas |
| Prioritas | **Mandatory** |

**Data Kelas:**
```
- nourut: INT PRIMARY KEY
- namakelas: VARCHAR(10) - e.g., "1A", "7B", "TK A"
- marhalah: VARCHAR(50) - "TK/PAUD", "SLTA"
- walikelas: VARCHAR(100) - NIK wali kelas (FK pegawai)
- putraputri: VARCHAR(10) - untuk pemisahan gender jika ada
```

**Validasi:**
- Nama kelas unik
- Wali kelas harus pegawai aktif

---

##### REQ-KELAS-002: Setting Mata Pelajaran
| Atribut | Detail |
|---------|--------|
| ID | REQ-KELAS-002 |
| Nama | Manajemen Mapel per Kelas |
| Prioritas | **Mandatory** |

**Data yang dikelola:**
- Daftar mapel per marhalah
- Penugasan guru per mapel per kelas
- Bobot nilai (harian, UTS, UAS)
- KKM per mapel

---

##### REQ-ABSEN-001: Absensi Siswa
| Atribut | Detail |
|---------|--------|
| ID | REQ-ABSEN-001 |
| Nama | Input dan Rekap Absensi Siswa |
| Prioritas | **Mandatory** |
| Aktor | Guru, Tata Usaha |

**Data Absensi (absen):**
```
- nourut: PRIMARY KEY
- nis: VARCHAR - FK siswa
- tanggal: DATE
- tanggalakhir: DATE
- sakit: INT - jumlah hari sakit
- ijin: INT - jumlah hari izin  
- alpa: INT - jumlah hari tanpa keterangan
- catatan: VARCHAR(250)
- pengguna: VARCHAR(100) - user yang input
```

**Fitur:**
- Input per tanggal (daily)
- Input bulk per kelas
- Rekap bulanan
- Laporan per siswa
- Export data

---

##### REQ-NILAI-001: Input Nilai Siswa
| Atribut | Detail |
|---------|--------|
| ID | REQ-NILAI-001 |
| Nama | Sistem Penilaian |
| Prioritas | **Mandatory** |
| Aktor | Guru |

**Data Nilai (nilai2):**
```
- id: PRIMARY KEY
- nis: DOUBLE (should be VARCHAR)
- settingmapel_id: INT - FK ke setting mapel
- h1, h2, h3: INT - Nilai harian
- u1, u2, u3: INT - Nilai ulangan
- uts: INT - Nilai UTS
- uas: INT - Nilai UAS
- nilai: INT - Nilai akhir pengetahuan
- nilaiinternal: INT
- ph1, ph2, ph3: INT - Nilai praktik harian
- pu1, pu2, pu3: INT
- puts: INT - Nilai praktik UTS
- puas: INT - Nilai praktik UAS
- pnilai: INT - Nilai akhir keterampilan
- pnilaiinternal: INT
```

**Konversi Nilai (nilaikonversi):**
| Range | Predikat | Deskripsi |
|-------|----------|-----------|
| 91-100 | A | Istimewa |
| 81-90 | B | Sangat Baik |
| 71-80 | C | Baik |
| 61-70 | D | Kurang |
| 0-60 | E | Buruk |

---

##### REQ-NILAI-002: Nilai Sikap
| Atribut | Detail |
|---------|--------|
| ID | REQ-NILAI-002 |
| Nama | Penilaian Sikap Spiritual dan Sosial |
| Prioritas | High |

**Data Nilai Sikap (nilaisikap):**
```
- nis: PRIMARY KEY
- spiritual: TEXT - predikat sikap spiritual
- sosial: TEXT - predikat sikap sosial
- marhalah: VARCHAR(50)
```

**Predikat:** Sangat Baik, Baik, Cukup, Kurang

---

##### REQ-RAPOR-001: Generate Rapor
| Atribut | Detail |
|---------|--------|
| ID | REQ-RAPOR-001 |
| Nama | Cetak Rapor Digital |
| Prioritas | **Mandatory** |

**Output:**
- PDF format resmi
- Data lengkap: nilai, sikap, absensi
- Tanda tangan digital (wali kelas, kepala sekolah)
- QR code verifikasi

---

#### 3.1.5 Modul Tahfidz

##### REQ-TAHFIDZ-001: Input Setoran Hafalan
| Atribut | Detail |
|---------|--------|
| ID | REQ-TAHFIDZ-001 |
| Nama | Sistem Tracking Hafalan Al-Quran |
| Prioritas | High |
| Aktor | Guru Tahfidz |

**Data Tahfidz:**
```
- id: PRIMARY KEY
- nis: FK siswa
- juz: INT - nomor juz
- surat: VARCHAR
- ayat_dari: INT
- ayat_sampai: INT
- nilai: INT
- predikat: VARCHAR
- tanggal: DATE
- guru: VARCHAR - NIK guru
- keterangan: TEXT
```

**Fitur:**
- Progress chart per siswa
- Target hafalan per semester
- Ujian tahfidz
- Laporan per kelas

---

#### 3.1.6 Modul Kesantrian (Kepribadian)

##### REQ-KESANTRIAN-001: Penilaian Kepribadian
| Atribut | Detail |
|---------|--------|
| ID | REQ-KESANTRIAN-001 |
| Nama | Input Penilaian Karakter Santri |
| Prioritas | High |

**Data Kesantrian (berdasarkan tabel kesantrian):**
```
- nourut: PRIMARY KEY
- nis: VARCHAR(20)
- tanggal: DATE

Aspek Adab:
- adab_teman: VARCHAR(50)
- adab_guru: VARCHAR(50)
- adab_lingkungan: VARCHAR(50)
- adab_agama: VARCHAR(50)
- adab_orangtua: VARCHAR(100)

Bahasa:
- bahasaarab: VARCHAR(50)
- bahasainggris: VARCHAR(50)
- conversation: VARCHAR(200)

Evaluasi:
- muhasabah: VARCHAR(50)

Ibadah:
- sholatrawatib: VARCHAR(50)
- sholatwajib: VARCHAR(50)
- sholatdhuha: VARCHAR(50)
- wudhu: VARCHAR(50)

Baca Quran:
- tadarus: VARCHAR(200)
- iqra: VARCHAR(50)

Karakter:
- infaq_harian: VARCHAR(50)
- infaq_jumat: VARCHAR(50)
- menabung: VARCHAR(50)
- kebersihandiri: VARCHAR(50)

Catatan:
- catatanasrama: VARCHAR(200)
```

---

#### 3.1.7 Modul Kesiswaan

##### REQ-KESEHATAN-001: Rekam Kesehatan
| Atribut | Detail |
|---------|--------|
| ID | REQ-KESEHATAN-001 |
| Nama | Sistem UKS |
| Prioritas | Medium |

**Data Kesehatan:**
```
- nourut: PRIMARY KEY
- tanggal: DATETIME
- nis: VARCHAR(15)
- keluhan: VARCHAR(200)
- obat: VARCHAR(200)
- catatan: VARCHAR(200)
- keparahan: VARCHAR(50)
- pengguna: VARCHAR(200)
- tanggalakhir: DATETIME
- pemeriksa: VARCHAR(200)
```

---

##### REQ-IZIN-001: Sistem Perizinan
| Atribut | Detail |
|---------|--------|
| ID | REQ-IZIN-001 |
| Nama | Izin Keluar/Pulang Siswa |
| Prioritas | Medium |

**Workflow:**
1. Request izin (oleh siswa/orangtua)
2. Approval wali asrama/guru
3. Cetak surat izin
4. Check-out / check-in

---

##### REQ-PELANGGARAN-001: Catatan Pelanggaran
| Atribut | Detail |
|---------|--------|
| ID | REQ-PELANGGARAN-001 |
| Nama | Sistem Pelanggaran dan Poin |
| Prioritas | Medium |

**Data Pelanggaran:**
```
- id: PRIMARY KEY
- nis: FK siswa
- tanggal: DATE
- jenis_pelanggaran: FK pelanggaranlist
- deskripsi: TEXT
- poin: INT
- sanksi: VARCHAR
- penanganan: TEXT
- pengguna: VARCHAR - pelapor
```

---

#### 3.1.8 Modul Keuangan

##### REQ-TAGIHAN-001: Manajemen Tagihan
| Atribut | Detail |
|---------|--------|
| ID | REQ-TAGIHAN-001 |
| Nama | CRUD Tagihan Siswa |
| Prioritas | **Mandatory** |
| Aktor | Kabid Keuangan, Staf Keuangan |

**Data Tagihan (keuangantagihan):**
```
- nourut: INT PRIMARY KEY
- nis: VARCHAR(100)
- tahunajaran: VARCHAR(50)
- tagihan: VARCHAR(150) - nama tagihan (januari, februari, dll)
- tipe: VARCHAR(64) - jenis (SPP KELAS 1, SPP KELAS 7, dll)
- nominal: INT
- terbayar: ENUM('Y','N')
- sort: INT
- tanggal_jatuh_tempo: DATE
```

**Fitur:**
- Generate tagihan bulk per kelas
- Setting tagihan SPP per tipe kelas
- Tagihan non-rutin (daftar ulang, komite)
- Reminder otomatis jatuh tempo

---

##### REQ-BAYAR-001: Proses Pembayaran
| Atribut | Detail |
|---------|--------|
| ID | REQ-BAYAR-001 |
| Nama | Input dan Validasi Pembayaran |
| Prioritas | **Mandatory** |

**Data Pembayaran (keuanganpembayaran):**
```
- nonota: VARCHAR(50) PRIMARY KEY
- nis: VARCHAR(100)
- tanggal: DATE
- pengguna: VARCHAR(50) - kasir
- transfer: VARCHAR(50) - TUNAI/TRANSFER
- tanggaldokumen: DATE
- trx_id: INT
- catatan: VARCHAR(100)
- metode_pembayaran: VARCHAR(100) - ADMIN/ONLINE
```

**Data Detail Pembayaran (keuanganpembayaran_detail):**
```
- id: PRIMARY KEY
- nonota: FK keuanganpembayaran
- tagihan: VARCHAR
- tagihan_id: INT - FK keuangantagihan
- nominal: INT
- tanggal: DATE
- status: CHAR - N/Y
```

**Fitur:**
- Input pembayaran tunai
- Validasi transfer bank
- Cetak kwitansi
- Pembayaran partial (cicilan)

---

##### REQ-JURNAL-001: Jurnal Keuangan
| Atribut | Detail |
|---------|--------|
| ID | REQ-JURNAL-001 |
| Nama | Jurnal Masuk dan Keluar |
| Prioritas | High |

**Data Jurnal:**
```
- nourut: PRIMARY KEY
- tanggal: DATE
- keterangan: TEXT
- jenis: ENUM('MASUK','KELUAR')
- kategori: VARCHAR
- nominal: INT
- saldo: INT
- pengguna: VARCHAR
```

---

##### REQ-LAP-KEU-001: Laporan Keuangan
| Atribut | Detail |
|---------|--------|
| ID | REQ-LAP-KEU-001 |
| Nama | Laporan dan Rekap Keuangan |
| Prioritas | High |

**Jenis Laporan:**
- Laporan harian (kas)
- Laporan bulanan
- Rekap pembayaran per kelas
- Daftar tunggakan
- Neraca sederhana

---

#### 3.1.9 Modul Kepegawaian dan Penggajian

##### REQ-GAJI-001: Kalkulasi Gaji
| Atribut | Detail |
|---------|--------|
| ID | REQ-GAJI-001 |
| Nama | Sistem Penggajian |
| Prioritas | High |
| Aktor | Kabid Keuangan |

**Komponen Gaji:**

**Pendapatan:**
```
Gaji Pokok (gajipokok):
- golongan: VARCHAR
- masakerja: INT
- nominal: INT

Tunjangan (gajitunjangan):
- tunjanganmasakerja
- load_staff
- load_staff_guru
- load_staff_umum
- tunjangan_staff_masakerja
- tunjanganpendidikan
- tunjanganlc
- tunjanganwalikelas
- jamkbm * honorjamkbm
- jamtahfizh * honorjamtahfizh
- transportperhari * hari_hadir

Tunjangan Struktural (gajitunjanganstruktural):
- jabatanstruktural
- nominalstruktural
```

**Potongan (gajipotonganyayasan):**
```
- kasbon
- listrik
- daftarulang (anak)
- spp (anak)
- qurban
- kpr
- infaq
- mart1, mart2, mart3
- bmttabungan
- bmtpinjamanwaserda
- bmtpinjamanbmt
- bmtsimpananwajib
- bmtsimpananpokok
- bmtsimpanansukarela
- bmtpiutangwaserda
- bankdaerah
- bpjs
- pph
- taawun
```

**Output:**
- Slip gaji PDF
- Rekap gaji bulanan
- Export Excel

---

#### 3.1.10 Modul Inventaris

##### REQ-INV-001: Manajemen Inventaris
| Atribut | Detail |
|---------|--------|
| ID | REQ-INV-001 |
| Nama | CRUD Inventaris Barang |
| Prioritas | Medium |

**Data Inventaris (invinventaris):**
```
- kode_barang: PRIMARY KEY
- nama_barang
- kategori
- departemen
- lokasi
- kondisi
- tanggal_pengadaan
- harga
- foto
```

---

#### 3.1.11 Modul CMS (Content Management System)

> **Catatan:** CMS memungkinkan admin/tata usaha mengelola konten landing page tanpa perlu coding. Struktur konten mengacu pada **8 Standar Nasional Pendidikan (SNP)** untuk akreditasi.

##### REQ-CMS-001: Login CMS
| Atribut | Detail |
|---------|--------|
| ID | REQ-CMS-001 |
| Nama | Autentikasi Admin CMS |
| Prioritas | **Mandatory** |
| Aktor | Superadmin, Tata Usaha |

**Fungsionalitas:**
- Login terpisah untuk CMS (/admin/login)
- Session management
- Role: cms_admin, cms_editor

---

##### REQ-CMS-002: Page Manager
| Atribut | Detail |
|---------|--------|
| ID | REQ-CMS-002 |
| Nama | Manajemen Halaman Statis |
| Prioritas | **Mandatory** |

**Data Halaman (cms_pages):**
```
- id: INT PRIMARY KEY
- title: VARCHAR(255)
- slug: VARCHAR(255) UNIQUE
- content: TEXT (HTML/Markdown)
- meta_title: VARCHAR(255)
- meta_description: TEXT
- featured_image: VARCHAR(255) - URL
- status: ENUM('draft','published')
- parent_id: INT - for hierarchical pages
- sort_order: INT
- created_by: INT FK users
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- published_at: TIMESTAMP
```

**Fitur:**
- WYSIWYG editor (TipTap/Quill)
- Draft dan publish workflow
- SEO settings per halaman
- Preview mode
- Version history

---

##### REQ-CMS-003: Media Library
| Atribut | Detail |
|---------|--------|
| ID | REQ-CMS-003 |
| Nama | Manajemen File & Media |
| Prioritas | **Mandatory** |

**Data Media (cms_media):**
```
- id: INT PRIMARY KEY
- filename: VARCHAR(255)
- original_name: VARCHAR(255)
- mime_type: VARCHAR(100)
- size: INT (bytes)
- url: VARCHAR(500) - Cloudflare R2/Cloudinary URL
- thumbnail_url: VARCHAR(500)
- alt_text: VARCHAR(255)
- folder: VARCHAR(255)
- uploaded_by: INT FK users
- created_at: TIMESTAMP
```

**Fitur:**
- Upload gambar (JPG, PNG, WebP) max 5MB
- Upload video (MP4) max 100MB atau YouTube embed
- Upload dokumen (PDF) max 10MB
- Auto-generate thumbnail
- Folder organization
- Drag & drop upload
- Search & filter

---

##### REQ-CMS-004: Menu Manager
| Atribut | Detail |
|---------|--------|
| ID | REQ-CMS-004 |
| Nama | Pengaturan Navigasi Website |
| Prioritas | High |

**Data Menu (cms_menus):**
```
- id: INT PRIMARY KEY
- location: VARCHAR(50) - 'main', 'footer', 'mobile'
- title: VARCHAR(100)
- url: VARCHAR(255)
- target: ENUM('_self', '_blank')
- parent_id: INT - for dropdown
- sort_order: INT
- is_active: BOOLEAN
```

**Fitur:**
- Drag & drop reorder
- Nested menu (dropdown/mega menu)
- Multiple menu locations (header, footer, mobile)

---

##### REQ-CMS-005: Banner & Slider Manager
| Atribut | Detail |
|---------|--------|
| ID | REQ-CMS-005 |
| Nama | Kelola Hero Banner & Slider |
| Prioritas | High |

**Data Slider (cms_sliders):**
```
- id: INT PRIMARY KEY
- title: VARCHAR(255)
- subtitle: TEXT
- image_url: VARCHAR(500)
- video_url: VARCHAR(500) - YouTube/Vimeo
- cta_text: VARCHAR(100)
- cta_url: VARCHAR(255)
- sort_order: INT
- is_active: BOOLEAN
- start_date: DATE
- end_date: DATE
```

---

##### REQ-CMS-006: Settings Manager
| Atribut | Detail |
|---------|--------|
| ID | REQ-CMS-006 |
| Nama | Pengaturan Website |
| Prioritas | High |

**Settings yang dapat dikelola:**
- Nama sekolah/yayasan
- Logo (light & dark)
- Favicon
- Tagline
- Alamat tiap unit
- Telepon, WhatsApp, Email
- Social media links
- Google Maps embed
- Google Analytics ID
- WhatsApp floating button

---

##### REQ-CMS-007: Statistik Website (Editable)
| Atribut | Detail |
|---------|--------|
| ID | REQ-CMS-007 |
| Nama | Edit Angka Statistik Homepage |
| Prioritas | Medium |

**Data Statistik (cms_stats):**
```
- id: INT PRIMARY KEY
- label: VARCHAR(100) - "Siswa", "Guru", "Alumni"
- value: VARCHAR(50) - "800+", "50+"
- icon: VARCHAR(50)
- sort_order: INT
```

---

#### 3.1.12 Landing Page Publik

##### REQ-LP-001: Homepage
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-001 |
| Nama | Halaman Utama Website |
| Prioritas | **Mandatory** |

**Sections (Top to Bottom):**

| No | Section | Konten | Sumber Data |
|----|---------|--------|-------------|
| 1 | Header | Logo, menu navigasi, tombol login | CMS Settings, CMS Menus |
| 2 | Hero Banner | Video/slideshow + tagline + CTA | CMS Sliders |
| 3 | Statistik | 4 angka key metrics | CMS Stats |
| 4 | 3 Unit Cards | RA, SDIT, SMPIT quick access | CMS Pages |
| 5 | Program Unggulan | 4-6 program dengan icon | CMS - Program section |
| 6 | Video Profil | YouTube embed "Sekapur Sirih" | CMS Settings |
| 7 | Testimoni | Slider testimoni alumni/ortu | cms_testimonials |
| 8 | Berita Terbaru | 3 artikel terbaru | cms_posts (auto) |
| 9 | CTA PPDB | Banner pendaftaran | CMS Banner |
| 10 | Footer | Alamat, kontak, links, sosmed | CMS Settings |

**Responsive:**
- Desktop: Full layout
- Tablet: 2-column grid
- Mobile: Single column, hamburger menu

---

##### REQ-LP-002: Halaman Profil Yayasan
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-002 |
| Nama | Profil Lengkap Yayasan |
| Prioritas | **Mandatory** |

**Subhalaman:**

| Slug | Judul | Konten |
|------|-------|--------|
| /profil/tentang | Tentang Yayasan | Sekapur sirih, sejarah, legalitas |
| /profil/visi-misi | Visi, Misi & Motto | Text + visual |
| /profil/struktur | Struktur Organisasi | Org chart + profil pimpinan |
| /profil/program-unggulan | Program Unggulan | Grid program dengan gambar |

---

##### REQ-LP-003: Halaman Unit Pendidikan
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-003 |
| Nama | Informasi per Unit (RA/SDIT/SMPIT) |
| Prioritas | **Mandatory** |

**Struktur untuk setiap unit (/ra, /sdit, /smpit):**

| Subhalaman | Konten |
|------------|--------|
| /{unit}/profil | Tentang unit, visi khusus unit, fasilitas |
| /{unit}/kurikulum | Struktur kurikulum, muatan lokal |
| /{unit}/target-lulusan | Kompetensi lulusan unit |
| /{unit}/galeri | Album foto kegiatan unit |
| /{unit}/tenaga-pendidik | Daftar guru unit + foto |

**Data Tenaga Pendidik (public view):**
```
- foto: thumbnail
- nama: nama lengkap dengan gelar
- jabatan: Guru Kelas 1A, Guru Mapel Matematika, dll
- mapel_diampu: untuk guru mapel
- pendidikan_terakhir: S1 Pendidikan, dll
```

---

##### REQ-LP-004: Standar Kompetensi Lulusan (SKL)
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-004 |
| Nama | Halaman SKL & Alumni |
| Prioritas | High |

**Subhalaman:**

| Slug | Judul | Konten |
|------|-------|--------|
| /standar/skl/alumni | Data Alumni | Statistik lulusan per tahun |
| /standar/skl/rekam-jejak | Rekam Jejak | Tracking lanjut kemana |
| /standar/skl/testimoni | Testimoni | Kesan & pesan alumni + ortu |

**Data Alumni (cms_alumni):**
```
- id: PRIMARY KEY
- nama: VARCHAR(100)
- tahun_lulus: INT
- unit_asal: ENUM('RA','SDIT','SMPIT')
- sekolah_lanjut: VARCHAR(200) - SMP/SMA/Universitas
- prestasi: TEXT
- foto: VARCHAR(255)
```

**Data Testimoni (cms_testimonials):**
```
- id: PRIMARY KEY
- nama: VARCHAR(100)
- relasi: VARCHAR(100) - "Alumni 2020", "Wali Murid"
- foto: VARCHAR(255)
- testimoni: TEXT
- rating: INT (1-5)
- is_featured: BOOLEAN
- is_active: BOOLEAN
```

---

##### REQ-LP-005: Standar Isi (Kurikulum)
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-005 |
| Nama | Halaman Kurikulum & Kalender |
| Prioritas | High |

**Subhalaman:**

| Slug | Konten |
|------|--------|
| /standar/isi/kurikulum | Struktur kurikulum per unit |
| /standar/isi/target | Target & visi per unit |
| /standar/isi/muatan-lokal | Program khas sekolah |
| /standar/isi/kalender | Kalender pendidikan tahunan |

**Kalender Akademik (cms_calendar):**
```
- id: PRIMARY KEY
- title: VARCHAR(255)
- start_date: DATE
- end_date: DATE
- type: ENUM('libur','ujian','kegiatan','pendaftaran')
- description: TEXT
- is_public: BOOLEAN
```

---

##### REQ-LP-006: Standar Pendidik & Tenaga Kependidikan
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-006 |
| Nama | Data Pendidik Publik |
| Prioritas | High |

**Subhalaman:**

| Slug | Konten |
|------|--------|
| /standar/pendidik/data | Grid foto + bio guru |
| /standar/pendidik/kualifikasi | Statistik S1/S2, sertifikasi |
| /standar/pendidik/tugas | Mapping tugas mengajar |
| /standar/pendidik/prestasi | Penghargaan guru |
| /standar/pendidik/tenaga | Data staff non-guru |

**Display Mode:**
- Grid view dengan foto
- Filter by unit (RA/SDIT/SMPIT)
- Search by nama

---

##### REQ-LP-007: Dokumentasi KBM (Standar Proses)
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-007 |
| Nama | Galeri Kegiatan Belajar |
| Prioritas | High |

**Subhalaman:**

| Slug | Konten |
|------|--------|
| /dokumentasi/kbm | Foto/video pembelajaran di kelas |
| /dokumentasi/kegiatan | Kegiatan sekolah (upacara, dll) |
| /dokumentasi/ekskul | Daftar ekskul + foto |
| /dokumentasi/outdoor | Fieldtrip, outbound, lomba |
| /dokumentasi/video | Playlist YouTube |

**Data Galeri (cms_gallery):**
```
- id: PRIMARY KEY
- album_id: FK cms_albums
- title: VARCHAR(255)
- media_url: VARCHAR(500)
- media_type: ENUM('image','video','youtube')
- caption: TEXT
- sort_order: INT
- created_at: TIMESTAMP
```

**Data Album (cms_albums):**
```
- id: PRIMARY KEY
- title: VARCHAR(255)
- slug: VARCHAR(255)
- description: TEXT
- cover_image: VARCHAR(500)
- category: ENUM('kbm','ekskul','kegiatan','outdoor','video')
- unit: ENUM('all','ra','sdit','smpit')
- is_public: BOOLEAN
```

---

##### REQ-LP-008: Sarana Prasarana
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-008 |
| Nama | Fasilitas Sekolah |
| Prioritas | High |

**Subhalaman:**

| Slug | Konten |
|------|--------|
| /fasilitas | Overview dengan statistik |
| /fasilitas/ruang-kelas | Galeri ruang kelas |
| /fasilitas/perpustakaan | Info perpustakaan |
| /fasilitas/lab-komputer | Lab IT |
| /fasilitas/media-belajar | Buku, alat peraga |
| /fasilitas/lainnya | Masjid, UKS, kantin, lapangan |

**Data Fasilitas (cms_facilities):**
```
- id: PRIMARY KEY
- name: VARCHAR(100)
- slug: VARCHAR(100)
- description: TEXT
- image_url: VARCHAR(500)
- quantity: INT
- category: VARCHAR(50)
- is_featured: BOOLEAN
```

---

##### REQ-LP-009: Prestasi
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-009 |
| Nama | Showcase Prestasi |
| Prioritas | High |

**Subhalaman:**

| Slug | Konten |
|------|--------|
| /prestasi/siswa | Prestasi siswa |
| /prestasi/pendidik | Prestasi guru |
| /prestasi/hall-of-fame | Featured achievements |

**Data Prestasi (cms_achievements):**
```
- id: PRIMARY KEY
- title: VARCHAR(255)
- winner_type: ENUM('siswa','guru')
- winner_name: VARCHAR(100)
- competition: VARCHAR(200)
- level: ENUM('sekolah','kecamatan','kota','provinsi','nasional','internasional')
- rank: VARCHAR(50) - "Juara 1", "Finalis"
- year: INT
- unit: ENUM('ra','sdit','smpit')
- photo: VARCHAR(500)
- certificate: VARCHAR(500)
- is_featured: BOOLEAN
```

**Display:**
- Filter by tahun, unit, level
- Card grid dengan foto
- Badge untuk level (gold/silver/bronze)

---

##### REQ-LP-010: Berita & Informasi
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-010 |
| Nama | Blog/News System |
| Prioritas | **Mandatory** |

**Data Berita (cms_posts):**
```
- id: PRIMARY KEY
- title: VARCHAR(255)
- slug: VARCHAR(255) UNIQUE
- excerpt: TEXT - ringkasan 150 karakter
- content: TEXT - HTML/Markdown
- featured_image: VARCHAR(500)
- category_id: FK cms_categories
- author_id: FK users
- status: ENUM('draft','published')
- views: INT
- published_at: TIMESTAMP
- created_at: TIMESTAMP
```

**Fitur:**
- Kategori: Akademik, Kegiatan, Pengumuman, PPDB
- Featured image
- Social share buttons
- Related posts
- Archive by month/year
- Search

---

##### REQ-LP-011: PPDB
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-011 |
| Nama | Pendaftaran Peserta Didik Baru |
| Prioritas | **Mandatory** |

**Subhalaman:**

| Slug | Konten |
|------|--------|
| /ppdb | Landing PPDB dengan CTA |
| /ppdb/alur | Flowchart pendaftaran |
| /ppdb/syarat | Persyaratan dokumen |
| /ppdb/jadwal | Timeline pendaftaran |
| /ppdb/biaya | Rincian biaya per unit |
| /ppdb/faq | Pertanyaan umum |
| /ppdb/brosur | Download PDF brosur |
| /ppdb/formulir | Form pra-pendaftaran |

**Data Leads/Pra-Pendaftaran (cms_ppdb_leads):**
```
- id: PRIMARY KEY
- nama_anak: VARCHAR(100)
- tanggal_lahir: DATE
- jenis_kelamin: ENUM('L','P')
- unit_tujuan: ENUM('ra','sdit','smpit')
- nama_orangtua: VARCHAR(100)
- telepon: VARCHAR(20)
- email: VARCHAR(100)
- alamat: TEXT
- asal_sekolah: VARCHAR(200)
- catatan: TEXT
- status: ENUM('new','contacted','registered','cancelled')
- source: VARCHAR(50) - tracking marketing
- created_at: TIMESTAMP
```

**Flow:**
1. Visitor isi form
2. Data masuk ke admin
3. Notifikasi WhatsApp/email ke admin
4. Follow up oleh tim PPDB

---

##### REQ-LP-012: Kontak
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-012 |
| Nama | Halaman Kontak |
| Prioritas | **Mandatory** |

**Konten:**
- Alamat tiap unit dengan tab
- Google Maps embed
- Form kontak
- Jam operasional
- Social media links
- WhatsApp quick link

**Data Pesan Kontak (cms_contact_messages):**
```
- id: PRIMARY KEY
- nama: VARCHAR(100)
- email: VARCHAR(100)
- telepon: VARCHAR(20)
- subject: VARCHAR(255)
- message: TEXT
- is_read: BOOLEAN
- replied_at: TIMESTAMP
- created_at: TIMESTAMP
```

---

##### REQ-LP-013: SEO & Performance
| Atribut | Detail |
|---------|--------|
| ID | REQ-LP-013 |
| Nama | Optimasi SEO & Loading |
| Prioritas | High |

**Requirements:**
- Meta title & description per halaman (dari CMS)
- Open Graph tags untuk sharing
- Sitemap.xml auto-generate
- robots.txt
- Lazy loading images
- WebP image format
- Lighthouse score > 80
- Mobile-first responsive



#### 3.1.13 Portal Orangtua

##### REQ-PO-001: Dashboard Orangtua
| Atribut | Detail |
|---------|--------|
| ID | REQ-PO-001 |
| Nama | Halaman Utama Portal Wali |
| Prioritas | **Mandatory** |

**Konten:**
- Info anak (bisa >1)
- Ringkasan: kehadiran, nilai, tahfidz
- Tagihan yang belum dibayar
- Pengumuman terbaru

---

##### REQ-PO-002: Lihat Nilai Anak
| Atribut | Detail |
|---------|--------|
| ID | REQ-PO-002 |
| Nama | View Read-only Nilai |
| Prioritas | **Mandatory** |

- Nilai per semester
- Nilai per mapel
- Progress chart
- Download rapor PDF

---

##### REQ-PO-003: Lihat Tagihan
| Atribut | Detail |
|---------|--------|
| ID | REQ-PO-003 |
| Nama | View Tagihan dan Pembayaran |
| Prioritas | **Mandatory** |

- Daftar tagihan aktif
- History pembayaran
- Download kwitansi

---

##### REQ-PO-004: Pembayaran Online (Future)
| Atribut | Detail |
|---------|--------|
| ID | REQ-PO-004 |
| Nama | Integrasi Payment Gateway |
| Prioritas | Low (Fase 2) |

- VA (Virtual Account)
- E-wallet
- Invoice online

---

### 3.2 Kebutuhan Non-Fungsional

#### 3.2.1 Performance Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PERF-001 | Page load time | < 3 detik |
| NFR-PERF-002 | API response time | < 500ms (average) |
| NFR-PERF-003 | Concurrent users | 100+ users |
| NFR-PERF-004 | Database query | < 100ms (simple), < 500ms (complex) |

---

#### 3.2.2 Security Requirements

| ID | Requirement | Detail |
|----|-------------|--------|
| NFR-SEC-001 | HTTPS | All traffic encrypted via TLS 1.3 |
| NFR-SEC-002 | Password hashing | bcrypt atau Argon2 |
| NFR-SEC-003 | JWT token | Access 24h, Refresh 7d |
| NFR-SEC-004 | Input validation | Server-side validation wajib |
| NFR-SEC-005 | SQL injection prevention | Parameterized queries |
| NFR-SEC-006 | XSS prevention | Content Security Policy |
| NFR-SEC-007 | CSRF protection | Token-based |
| NFR-SEC-008 | Rate limiting | 100 req/min per IP |
| NFR-SEC-009 | Audit logging | Semua action CRUD di-log |

---

#### 3.2.3 Reliability Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-REL-001 | System uptime | 99.5% |
| NFR-REL-002 | Database backup | Daily automated |
| NFR-REL-003 | Backup retention | 30 hari |
| NFR-REL-004 | Recovery time | < 4 jam |

---

#### 3.2.4 Usability Requirements

| ID | Requirement | Detail |
|----|-------------|--------|
| NFR-USE-001 | Responsive design | Mobile-first, 320px - 1920px |
| NFR-USE-002 | Browser support | Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| NFR-USE-003 | Bahasa | Indonesia |
| NFR-USE-004 | Form validation | Real-time client-side |
| NFR-USE-005 | Loading states | Skeleton loader / spinner |
| NFR-USE-006 | Error messages | User-friendly, action-oriented |

---

#### 3.2.5 Scalability Requirements

| ID | Requirement | Detail |
|----|-------------|--------|
| NFR-SCA-001 | Database indexing | Proper indexing untuk query umum |
| NFR-SCA-002 | File storage | External (Cloudflare R2 / Cloudinary) |
| NFR-SCA-003 | Containerization | Docker-ready |
| NFR-SCA-004 | Stateless API | Support horizontal scaling |

---

## 4. Data Design

### 4.1 Entity Relationship Diagram (ERD) - Simplified

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SISWA     │────<│   ABSEN     │     │   PEGAWAI   │
│   (NIS)     │     │             │     │    (NIK)    │
└──────┬──────┘     └─────────────┘     └──────┬──────┘
       │                                        │
       │            ┌─────────────┐            │
       │            │    KELAS    │            │
       └───────────>│  (nourut)   │<───────────┘
                    └──────┬──────┘     (walikelas)
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   NILAI2    │     │   TAHFIDZ   │     │ KESANTRIAN  │
└─────────────┘     └─────────────┘     └─────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SISWA     │────<│KEU_TAGIHAN  │     │ KEU_PEMBYR  │
│   (NIS)     │     │    (nis)    │────>│  (nonota)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                        ┌──────┴──────┐
                                        │KEU_PBR_DTL  │
                                        └─────────────┘

┌─────────────┐     ┌─────────────┐
│  ACL_USERS  │────<│  ACL_GROUPS │
│    (id)     │     │    (id)     │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  ACL_MENUS  │
                    │    (id)     │
                    └─────────────┘
```

### 4.2 Database Tables Summary

| Category | Tables |
|----------|--------|
| **User & Auth** | acl_users, acl_groups, acl_menus, acl_routes, groups |
| **Siswa** | siswa |
| **Pegawai** | pegawai, gurutugas, gurutugaspengabdian, gurutugassetting |
| **Akademik** | kelas, mapel, nilai2, nilaikonversi, nilaisikap, nilaisikap_master |
| **Absensi** | absen, absenhalaqoh, absenkesantrian, absentahfidz, absen_guru |
| **Tahfidz** | tahfidz, tahfidzkhusus, tahfidzlist, tahfidzujian, tahfidz_baru, tahfidz_juzz, tahfidz_kitab, juz |
| **Kesantrian** | kesantrian |
| **Kesiswaan** | kesehatan, izin, izin_baru, pelanggaran, pelanggaranlist, ekskul |
| **Keuangan** | keuangantagihan, keuanganpembayaran, keuanganpembayaran_detail, keuanganbantuan, jurnal, jurnalmasuk, bayarrutin, bayarlaundry |
| **Penggajian** | gajian, gajipokok, gajitunjangan, gajitunjanganstruktural, gajipotonganyayasan |
| **Inventaris** | invbarang, invinventaris, invdepartment, invsarpras, barang, barang_golongan |
| **Lainnya** | berita, forum, kalenderakademik, kalenderakademikjam, organisasi, anekdot, edc, edc_detail |

### 4.3 Data Migration Strategy

**Fase 1: Schema Migration**
- Export schema dari MySQL existing
- Convert ke PostgreSQL syntax
- Tambah field baru yang dibutuhkan
- Buat migration scripts

**Fase 2: Data Migration**
- Export data dari MySQL
- Transform data jika perlu
- Import ke PostgreSQL
- Validasi record count

**Fase 3: Verification**
- Spot check data
- Test query results
- Verify relationships

---

## 5. API Design

### 5.1 API Standards
- RESTful architecture
- Base URL: `/api/v1/`
- JSON format
- Bearer token authentication
- Standard HTTP status codes

### 5.2 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | User login |
| POST | /api/v1/auth/logout | User logout |
| POST | /api/v1/auth/refresh | Refresh token |
| POST | /api/v1/auth/forgot-password | Request password reset |
| POST | /api/v1/auth/reset-password | Reset password |

### 5.3 Sample API Endpoints

**Siswa:**
```
GET    /api/v1/siswa             - List siswa
GET    /api/v1/siswa/{nis}       - Detail siswa
POST   /api/v1/siswa             - Create siswa
PUT    /api/v1/siswa/{nis}       - Update siswa
DELETE /api/v1/siswa/{nis}       - Delete siswa (soft)
GET    /api/v1/siswa/{nis}/nilai - Nilai siswa
GET    /api/v1/siswa/{nis}/absen - Absensi siswa
```

**Keuangan:**
```
GET    /api/v1/keuangan/tagihan           - List tagihan
POST   /api/v1/keuangan/tagihan           - Create tagihan
GET    /api/v1/keuangan/tagihan/{nis}     - Tagihan per siswa
POST   /api/v1/keuangan/pembayaran        - Create pembayaran
GET    /api/v1/keuangan/laporan/harian    - Laporan harian
```

### 5.4 Response Format

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "OK",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Nama tidak boleh kosong",
    "details": [...]
  }
}
```

---

## 6. User Interface Requirements

### 6.1 Design System
- Color palette: Islamic green (#006847), gold accent, neutral grays
- Typography: Inter / Poppins (Google Fonts)
- Icon set: Lucide icons
- Component library: shadcn/ui atau custom

### 6.2 Key Screens

**Admin Dashboard:**
- Sidebar navigation (collapsible)
- Top header (user menu, notifications)
- Main content area
- Footer

**Landing Page:**
- Header dengan navigation
- Hero section
- Content sections
- Footer

**Portal Orangtua:**
- Clean, simple layout
- Card-based information
- Mobile-optimized

### 6.3 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, hamburger menu |
| Tablet | 640-1024px | 2 column, sidebar collapse |
| Desktop | > 1024px | Full layout, sidebar expanded |

---

## 7. Deployment Requirements

### 7.1 Infrastructure

```
┌──────────────────────────────────────────────────────┐
│                   BiznetGio VPS                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              EasyPanel/CyberPanel             │   │
│  │  ┌────────────┐  ┌────────────┐              │   │
│  │  │   Nginx    │  │  Docker    │              │   │
│  │  │  (Reverse  │  │  Engine    │              │   │
│  │  │   Proxy)   │  │            │              │   │
│  │  └─────┬──────┘  └──────┬─────┘              │   │
│  │        │                │                     │   │
│  │        │         ┌──────┴──────┐             │   │
│  │        └────────>│             │             │   │
│  │                  │  Container  │             │   │
│  │                  │   Stack     │             │   │
│  │                  ├─────────────┤             │   │
│  │                  │ Frontend    │             │   │
│  │                  │ Backend     │             │   │
│  │                  │ PostgreSQL  │             │   │
│  │                  │ Redis       │             │   │
│  │                  └─────────────┘             │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
          │
          │  (CDN)
          ▼
┌──────────────────┐
│  Cloudflare R2   │
│  (File Storage)  │
└──────────────────┘
```

### 7.2 Docker Setup

**docker-compose.yml structure:**
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db, redis]
    
  db:
    image: postgres:15
    volumes: [pgdata:/var/lib/postgresql/data]
    
  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

### 7.3 Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@db:5432/asyuraa

# JWT
JWT_SECRET=xxx
JWT_EXPIRE=86400

# Storage
CLOUDFLARE_R2_ACCESS_KEY=xxx
CLOUDFLARE_R2_SECRET_KEY=xxx
CLOUDFLARE_R2_BUCKET=asyuraa

# App
APP_URL=https://asyuraa.sch.id
APP_ENV=production
```

---

## 8. Testing Requirements

### 8.1 Testing Types

| Type | Description | Coverage Target |
|------|-------------|-----------------|
| Unit Testing | Test individual functions | 80% |
| Integration Testing | Test API endpoints | All critical paths |
| E2E Testing | Test user flows | Major features |
| Performance Testing | Load testing | 100 concurrent users |

### 8.2 Test Scenarios (Sample)

**Login Flow:**
1. User access login page
2. Input valid credentials
3. System validates
4. Redirect to dashboard
5. Show user menu

**Pembayaran Flow:**
1. Staf select siswa
2. View tagihan
3. Input amount
4. Process payment
5. Generate receipt

---

## 9. Documentation Requirements

| Document | Audience | Format |
|----------|----------|--------|
| Technical Documentation | Developers | Markdown / Wiki |
| API Documentation | Developers | OpenAPI / Swagger |
| User Manual | End users | PDF / Web |
| Admin Guide | IT Admin | PDF |
| Database Documentation | DBA | ERD + Data Dictionary |

---

## 10. Appendices

### Appendix A: Glossary
*(See section 1.3)*

### Appendix B: Reference SQL Tables
*(Based on analysis of asyuraa.sql - 88,424 lines)*

Key tables analyzed:
- siswa (student data) - ~609 records
- pegawai (employee data) - ~52 records
- kelas (class data) - ~18 records
- keuangantagihan (tuition billing) - ~34,472 records
- keuanganpembayaran (payments)
- nilai2 (grades)
- absen (attendance)
- tahfidz (Quran memorization)
- kesantrian (character assessment)

### Appendix C: Approval Signatures

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | Project Sponsor | | |
| | Technical Lead | | |
| | QA Lead | | |

---

*Document prepared for review - Subject to change based on stakeholder feedback*
