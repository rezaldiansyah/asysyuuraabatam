# Database Comparison: Proyek Baru vs Legacy SQL

> **Tanggal Analisis**: 31 Januari 2026
> **Reference File**: `asyuraa.sql` (88,000+ baris, 170+ tabel)
> **New Project Models**: `apps/api/models.py` (18 models)

---

## ✅ Model yang SUDAH Ada di Proyek Baru

| Model Baru | Tabel Legacy Equivalent | Catatan |
|---|---|---|
| `Unit` | - | **Baru** - Multi-unit support |
| `Role` | `acl_groups`, `groups` | ✅ |
| `User` | `acl_users`, `users` | ✅ |
| `UserUnit` | - | **Baru** - Pivot multi-unit |
| `AcademicYear` | `tahunajaran` | ✅ |
| `Classroom` | `kelas` | ✅ |
| `Student` | `siswa` | ✅ |
| `Subject` | `matapelajaran` | ✅ |
| `Schedule` | `kalenderakademik` | ✅ |
| `Scholarship` | `keuanganbantuan` | ✅ |
| `PaymentCategory` | `keuangantagihan_template` | ✅ |
| `StudentBill` | `keuangantagihan` | ✅ |
| `PaymentTransaction` | `keuanganpembayaran` | ✅ |
| `Account` | `rekening` | ✅ |
| `JournalEntry` | `jurnal` | ✅ |
| `JournalItem` | `jurnalmasuk` | ✅ |
| `Post` | `berita` | ✅ CMS |
| `PageContent` | - | **Baru** - Landing page CMS |

---

## 🔴 Gap Analysis: Tabel Legacy yang BELUM Ada

### 1. Modul Absensi (HIGH PRIORITY)
| Tabel | Deskripsi | Fields Kunci |
|---|---|---|
| `absen` | Absensi siswa | `nis`, `tanggal`, `sakit`, `ijin`, `alpa` |
| `absen_guru` | Absensi guru | - |
| `absenhalaqoh` | Absensi halaqoh | - |
| `absenkesantrian` | Absensi kesantrian | - |

### 2. Modul SDM/Kepegawaian (HIGH PRIORITY)
| Tabel | Deskripsi |
|---|---|
| `pegawai` | Data pegawai/guru |
| `gajian` | Penggajian |
| `gajipokok` | Gaji pokok |
| `gajitunjangan` | Tunjangan |
| `gajipotonganyayasan` | Potongan |
| `utangpegawai` | Utang pegawai |

### 3. Modul Tahfidz (MEDIUM PRIORITY)
| Tabel | Deskripsi |
|---|---|
| `tahfidz`, `tahfidz_baru` | Data tahfidz |
| `tahfidz_juzz` | Tracking per juz |
| `tahfidzlist` | Daftar capaian |
| `tahfidzujian` | Ujian tahfidz |
| `juz`, `quran` | Master data |

### 4. Modul Kesantrian/Asrama (MEDIUM PRIORITY)
| Tabel | Deskripsi |
|---|---|
| `kesantrian` | Data kesantrian |
| `settingasrama` | Setting asrama |
| `pelanggaran` | Pelanggaran siswa |
| `izin`, `izin_baru` | Perizinan |

### 5. Modul Nilai Akademik (MEDIUM PRIORITY)
| Tabel | Deskripsi |
|---|---|
| `nilai2` | Nilai siswa |
| `nilaisikap` | Nilai sikap |

### 6. Modul Lainnya (LOW PRIORITY)
- `ekskul` - Ekstrakurikuler
- `kesehatan` - Kesehatan siswa
- `invbarang`, `invsarpras` - Inventaris
- `laundry` - Laundry
- `psb*` - PSB
- `perpus_*` - Perpustakaan

---

## 🎯 Roadmap Pengembangan

### Fase 1: Core MVP ✅ (SELESAI)
- [x] User, Role, Unit management
- [x] Student & Classroom
- [x] Payment & Finance (Tagihan, Transaksi)
- [x] Accounting (Journal, Account)
- [x] CMS (Post, PageContent)

### Fase 2: Absensi & Pegawai (NEXT)
- [ ] Model `Employee` (data kepegawaian)
- [ ] Model `Attendance` (absensi siswa)
- [ ] Model `EmployeeAttendance` (absensi pegawai)
- [ ] API endpoints untuk absensi

### Fase 3: Akademik
- [ ] Model `Grade` / `Score` (nilai)
- [ ] Model `GradeCategory` (kategori nilai)
- [ ] Model `Extracurricular` (ekstra)

### Fase 4: Tahfidz (Jika relevan)
- [ ] Model `TahfidzProgress`
- [ ] Model `TahfidzExam`
- [ ] Master `Juz`, `Surah`

### Fase 5: Kesantrian/Asrama
- [ ] Model `Dormitory` (asrama)
- [ ] Model `Violation` (pelanggaran)
- [ ] Model `Leave` (perizinan)

### Fase 6: SDM/HR
- [ ] Model `Payroll`
- [ ] Model `Allowance`, `Deduction`
- [ ] Model `EmployeeLoan`

---

## 💡 Catatan Arsitektur

1. **Employee vs User**: Gunakan `User` dengan role GURU/PEGAWAI, tambah tabel `Employee` untuk data spesifik (NIP, NUPTK, jabatan fungsional).

2. **Legacy Views**: Tabel `v*` di legacy adalah denormalized views. Di sistem baru, hitung secara dinamis atau gunakan materialized view jika perlu.

3. **Naming Convention**: Proyek baru sudah menggunakan snake_case English - maintain consistency.
