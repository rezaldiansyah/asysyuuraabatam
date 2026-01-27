# Product Backlog - Sistem Informasi Asy-Syuuraa Batam

> **Status:** Active Development
> **Last Updated:** 26 Januari 2026

## 📌 Epics Overview
1. **Epic-01: Infrastructure & Foundation** - Setup server, database, dan environment development.
2. **Epic-02: Authentication & RBAC** - Sistem login, manajemen user, dan hak akses.
3. **Epic-03: Landing Page (Public)** - Website profil sekolah dan informasi publik.
4. **Epic-04: Content Management System (CMS)** - Manajemen konten untuk landing page.
5. **Epic-05: Master Data Management** - Manajemen data siswa, guru, kelas, dan mapel.
6. **Epic-06: Academic System** - Absensi, nilai, rapor, dan kurikulum.
7. **Epic-07: Tahfidz & Kesantrian** - Sistem khusus hafalan dan penilaian karakter.
8. **Epic-08: Finance System** - Tagihan SPP, pembayaran, dan laporan keuangan.
9. **Epic-09: Parent Portal** - Dashboard wali murid.
10. **Epic-10: HR & Payroll** - Kepegawaian dan penggajian.
11. **Epic-11: Data Migration** - Migrasi data dari database lama (`asyuraa.sql`) ke sistem baru.

---

## 📋 Backlog Items

### Priority: High (Phase 1 - Foundation & Core)

#### Epic-01: Infrastructure & Foundation
- [x] **INF-001** Setup Repository (Monorepo/Polyrepo) & Git Workflow
- [ ] **INF-002** Setup Docker Environment (Local & Production)
- [x] **INF-003** Design Database Schema (PostgreSQL) berdasarkan `asyuraa.sql`
- [x] **INF-004** Setup Backend Framework (Python FastAPI/Django)
- [x] **INF-005** Setup Frontend Framework (Next.js + Tailwind)
- [ ] **INF-006** Setup CI/CD Pipeline (GitHub Actions)

#### Epic-02: Authentication & RBAC
- [x] **AUTH-001** Implementasi Login & Logout (JWT)
- [x] **AUTH-002** Design & Seed Roles & Permissions (RBAC)
- [x] **AUTH-003** CRUD User Management (Superadmin)
- [x] **AUTH-004** Middleware untuk proteksi route berdasarkan Role/Scope
- [x] **AUTH-005** Implementasi Multi-unit assignment untuk User

#### Epic-03: Landing Page (Public)
- [x] **WEB-001** Implementasi UI Layout Utama (Header, Footer, Navigation)
- [x] **WEB-002** Homepage Section (Hero, Info Sekolah, Unit Cards)
- [ ] **WEB-003** Halaman Profil Yayasan (Visi Misi, Sejarah)
- [ ] **WEB-004** Halaman Detail Unit (RA, SDIT, SMPIT)
- [ ] **WEB-005** Halaman PPDB Static (Info & Kontak)

### Priority: Medium (Phase 2 - Academic & Operations)

#### Epic-04: CMS
- [x] **CMS-001** Dashboard CMS Admin
- [x] **CMS-002** CRUD Artikel/Berita
- [x] **CMS-003** CRUD Banner/Slider (Implemented as PageContent)
- [ ] **CMS-004** Media Library Manager (Upload Images)

#### Epic-05: Master Data Management
- [x] **MSTR-001** CRUD Data Siswa (Multistep Form)
- [x] **MSTR-002** CRUD Data Pegawai (Guru/Staff)
- [x] **MSTR-003** CRUD Data Kelas & Tahun Ajaran
- [x] **MSTR-004** Setup Mata Pelajaran per Unit

#### Epic-06: Academic System
- [ ] **ACD-001** Input Absensi Siswa (Harian)
- [ ] **ACD-002** Input Nilai (Harian, UTS, UAS)
- [ ] **ACD-003** Generate Rapor Digital (PDF)

#### Epic-07: Tahfidz & Kesantrian
- [ ] **THF-001** Input Setoran Hafalan Tahfidz
- [ ] **THF-002** Dashboard Progress Tahfidz Siswa
- [ ] **KST-001** Input Penilaian Adab & Ibadah

### Priority: Low (Phase 3 - Expansion)

#### Epic-08: Finance System
- [x] **FIN-001** Generate Tagihan SPP Bulanan (Bulk)
- [x] **FIN-002** Input Pembayaran (Kasir)
- [x] **FIN-003** Laporan Tunggakan & Pemasukan (Dashboard Basic)

#### Epic-09: Parent Portal
- [ ] **PRT-001** Login Wali Murid
- [ ] **PRT-002** Dashboard Wali Murid (View Nilai & Taqihan)

#### Epic-10: HR & Payroll
- [ ] **HR-001** Absensi Pegawai
- [ ] **HR-002** Generate Slip Gaji

### Special Phase: Data Migration (Legacy)

#### Epic-11: Data Migration
- [ ] **MIG-001** Mapping Schema Lama (`asyuraa.sql`) ke Schema Baru
- [ ] **MIG-002** Develop Migration Scripts (Users, Roles, Units)
- [ ] **MIG-003** Develop Migration Scripts (Master Data: Siswa, Pegawai)
- [ ] **MIG-004** Develop Migration Scripts (Transactional: Nilai, Keuangan)
- [ ] **MIG-005** Dry Run & Data Validation Test
