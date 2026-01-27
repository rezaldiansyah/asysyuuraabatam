# Database Schema Design - Asy-Syuuraa Batam

> **Status:** Draft (Sprint 1)
> **Engine:** PostgreSQL (Production) / SQLite (Local Dev)
> **ORM:** SQLAlchemy

## 1. Authentication & RBAC (Core)

Modul ini menangani user management, role, dan pembagian akses berdasarkan unit sekolah.

### ER Diagram

```mermaid
erDiagram
    users ||--o{ user_units : "assigned to"
    units ||--o{ user_units : "has members"
    roles ||--o{ users : "defines role for"

    users {
        int id pk
        string nik "Unique"
        string email "Unique"
        string password_hash
        string full_name
        boolean is_active
        datetime last_login
        datetime created_at
    }

    roles {
        int id pk
        string code "Unique (e.g. superadmin, guru)"
        string name
        string scope "Enum: sistem, yayasan, unit, portal"
        int priority "Lower = Higher access"
    }

    units {
        int id pk
        string code "Unique (YYS, RA, SDIT, SMPIT)"
        string name
        string address
        boolean is_active
    }

    user_units {
        int id pk
        int user_id fk
        int unit_id fk
        boolean is_primary "Main unit for dashboard"
    }
```

### Table Definitions

#### `roles`
Tabel referensi untuk semua role yang ada di sistem.
- **code**: Identifier unik untuk di code (e.g., `superadmin`, `kepala_unit`).
- **scope**: Menentukan batasan akses data (`sistem`, `yayasan`, `unit`, `portal`).

#### `units`
Daftar unit pendidikan dan yayasan.
- **code**: `YYS`, `RA`, `SDIT`, `SMPIT`.

#### `users`
Tabel utama pengguna.
- **nik**: Nomor induk (bisa NIK KTP atau NIK Yayasan/Sekolah). Digunakan untuk login selain email.
- **role_id**: Role utama user (misal: Guru).

#### `user_units`
Tabel pivot untuk *Many-to-Many* relationship antara User dan Unit.
- Memungkinkan satu guru mengajar di SDIT dan SMPIT sekaligus.
- `is_primary`: Menentukan dashboard mana yang muncul saat login pertama kali.
