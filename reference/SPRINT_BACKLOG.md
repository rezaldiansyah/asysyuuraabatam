# Sprint Backlog - Sprint 1 (Foundation & Auth)

> **Sprint Goal:** Membangun fondasi teknikal (Infrastructure) dan sistem inti Authentication dengan RBAC yang solid.
> **Durasi:** 2 Minggu (Est. Week 1-2 Project)
> **Status:** Planned

## 🎯 Sprint Goal
1.  **Environment Ready:** Frontend, Backend, dan Database berjalan lancar di local & production (Docker).
2.  **Database Schema:** ERD Final dan migrasi awal siap.
3.  **Secure Access:** User bisa login dan akses menu sesuai Role masing-masing.

---

## 📋 To Do List

### 🏗️ Infrastructure & Setup (Days 1-3)
- [ ] **[INF-001] Setup GIT Repository**
  - [ ] Initialize Monorepo/Polyrepo
  - [ ] Setup folder structure (apps/web, apps/api, packages)
  - [ ] Create `.gitignore` & `README.md`
- [ ] **[INF-002] Setup Docker Environment**
  - [ ] Create `docker-compose.yml` (dev)
  - [ ] Configure PostgreSQL service
  - [ ] Configure Redis service (optional)
  - [ ] Verify container communication
- [ ] **[INF-004] Setup Backend (Python FastAPI)**
  - [ ] Init project FastAPI
  - [ ] Setup SQLAlchemy / Tortoise ORM
  - [ ] Setup Pydantic settings
  - [ ] Create Health Check API (`/api/health`)
- [ ] **[INF-005] Setup Frontend (Next.js)**
  - [ ] Init Next.js 14+ (App Router)
  - [ ] Install Tailwind CSS & Shadcn/UI
  - [ ] Setup wrapper/provider (QueryClient, AuthContext)
  - [ ] Create Basic Layout (Shell)

### 🗄️ Database (Days 3-5)
- [ ] **[INF-003] Design Database Schema**
  - [ ] Create Physical Data Model (ERD) based on `asyuraa.sql` analysis
  - [ ] Define RBAC tables (`roles`, `permissions`, `users`)
  - [ ] Define Core tables (`units`, `employees`)
  - [ ] Create initial migration scripts (Alembic/Django Migrations)

### 🔐 Authentication & RBAC (Days 6-10)
- [ ] **[AUTH-002] Seed Roles & Permissions**
  - [ ] Create Seeder for 4 Units (YYS, RA, SDIT, SMPIT)
  - [ ] Create Seeder for 11 Static Roles (Superadmin, Guru, etc)
  - [ ] Create Seeder for initial Superadmin user
- [ ] **[AUTH-001] Implement Backend Auth**
  - [ ] Implement Login Endpoint (issue JWT Access + Refresh Token)
  - [ ] Implement `Get Me` Endpoint (User Profile + Permissions)
  - [ ] Implement Logout Endpoint (Blacklist Token)
- [ ] **[AUTH-001] Implement Frontend Auth**
  - [ ] Create Login Page UI
  - [ ] Integrate Login API
  - [ ] Handle Token Storage (HttpOnly Cookie / LocalStorage)
  - [ ] Create AuthGuard (Protect Routes)
- [ ] **[AUTH-004] RBAC Middleware**
  - [ ] Implement Backend Dependency `get_current_active_user`
  - [ ] Implement `PermissionChecker` dependency
  - [ ] Test access control (Admin vs Guru)

---

## 📅 Daily Plan (Estimasi)

| Hari | Fokus Utama | Target Deliverable |
|------|-------------|--------------------|
| **Day 1** | Repo & Docker | `docker-compose up` running sukses |
| **Day 2** | Backend Init | Hello World API & DB Connection |
| **Day 3** | Frontend Init | Next.js running dengan Tailwind |
| **Day 4** | DB Schema | ERD Final & Migration file pertama |
| **Day 5** | DB Migration | Tabel-tabel inti terbentuk di DB |
| **Day 6** | Auth Backend | Login API `200 OK` dengan JWT |
| **Day 7** | Auth Frontend | Halaman Login bisa submit ke API |
| **Day 8** | RBAC Seeding | Role & Permission masuk database |
| **Day 9** | Integration | Redirection setelah login berdasarkan role |
| **Day 10** | Testing & Fix | UAT Internal untuk Login Flow |

---

## ⚠️ Dependencies & Risks
- **Risk:** Kompleksitas migrasi data lama (`asyuraa.sql`) mungkin mempengaruhi desain schema baru.
  - *Mitigasi:* Sesuai arahan, **Migrasi Script dibuat terpisah** (masuk Epic-11). Sprint ini hanya fokus pada desain schema ideal, namun tetap melakukan *mapping analysis* agar schema baru kompatibel menerima data lama.
- **Dependency:** Akses ke VPS BiznetGio untuk deployment test (optional di sprint 1, bisa local dulu).
