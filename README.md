# Sistem Informasi Sekolah Asy-Syuuraa Batam

Sistem Informasi Sekolah Terpadu (SIST) untuk Asy-Syuuraa Batam, mencakup modul Akademik, Keuangan, dan CMS.

## Arsitektur

- **Frontend**: Next.js 14, Tailwind CSS, Shadcn UI (`apps/web`)
- **Backend**: FastAPI, SQLAlchemy, SQLite (`apps/api`)
- **Database**: SQLite (Development)

## Cara Menjalankan Project (Local Development)

### 1. Persiapan Backend
Buka terminal baru untuk Backend:

```bash
# Masuk ke direktori backend
cd apps/api

# Buat virtual environment (jika belum)
python3 -m venv venv

# Aktivasi virtual environment
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Inisialisasi Database & Seed Data Awal
# Script ini akan membuat file 'school.db' dan mengisi data user default
python seed_db.py

# Jalankan Server
uvicorn main:app --reload --port 8000
```

Backend akan berjalan di: [http://localhost:8000](http://localhost:8000)
Dokumentasi API (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Persiapan Frontend
Buka terminal baru untuk Frontend:

```bash
# Masuk ke direktori frontend
cd apps/web

# Install dependencies
npm install

# Jalankan Development Server
npm run dev
```

Frontend akan berjalan di: [http://localhost:3000](http://localhost:3000)

## Kredensial Login (Testing)

Gunakan akun berikut untuk masuk ke dashboard:

| Role | Username (NIK) | Password |
|------|---------------|----------|
| **Superadmin** | `999999` | `admin123` |

> **Catatan**: Jika Anda telah menjalankan script test reset password, password mungkin berubah menjadi `password`.

## Fitur yang Tersedia

- **Landing Page Public**: Beranda, Profil, Unit Pendidikan, PPDB.
- **Dashboard Admin**:
  - **Data Master**: Siswa (`/dashboard/siswa`), Guru (`/dashboard/guru`).
  - **Akademik**: Jadwal Pelajaran (`/dashboard/jadwal`), Data Kelas, Mapel.
  - **Keuangan**: Kategori Pembayaran, Generate Tagihan, Pencatatan Pembayaran (`/dashboard/keuangan`).
  - **CMS**: Manajemen Berita (`/dashboard/cms/berita`), Upload Media.
