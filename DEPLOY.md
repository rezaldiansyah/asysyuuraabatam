# Panduan Deployment ke Easypanel (BiznetGio)

Panduan ini dirancang untuk struktur **Monorepo** (API & Web dalam satu repo). Anda **TIDAK PERLU** memisah repo.

## Persiapan
1.  **Push Code**: Pastikan semua perubahan terakhir (termasuk `Dockerfile.prod` yang baru dibuat) sudah di-push ke GitHub repository Anda.
2.  **Login Easypanel**: Buka dashboard Easypanel di VPS Anda.

---

## Langkah 1: Buat Project
1.  Di Easypanel, klik tombol **"Create Project"**.
2.  Beri nama project, misal: `asyuraa`.
3.  Klik **"Create"**.

---

## Langkah 2: Setup Database (PostgreSQL)
Aplikasi butuh database. Kita deploy ini dulu.

1.  Di dalam project `asyuraa`, klik **"Services"** -> **"Templates"**.
2.  Cari **"PostgreSQL"** dan pilih.
3.  Beri nama service: `db` (atau `postgres`).
4.  Klik **"Create"**.
5.  Setelah jadi, buka setting servicenya, cari bagian **Credentials** atau **Connection Details**.
    *   Catat `Host`, `Port`, `Username`, `Password`, dan `Database Name`.
    *   *Tips: Di Easypanel, sesama satu project biasanya bisa panggil pakai nama service. Misal hostnya: `db`.*

---

## Langkah 3: Deploy API (Backend)
1.  Klik **"Services"** -> **"App"** (Custom App/Source).
2.  Pilih **Source**: "GitHub".
3.  **Repository**: Masukkan URL Repo GitHub Anda (misal `user/asy-syuuraabatam`).
    *   *Jika private repo, pastikan sudah connect akun GitHub atau pakai Token.*
4.  **Branch**: `main` (atau branch yang mau dideploy).
5.  **Build Settings** (PENTING!):
    *   **Root Directory**: `apps/api`
    *   **Dockerfile Path**: `Dockerfile.prod`
6.  **Environment Variables**:
    Isi sesuai koneksi database tadi:
    ```
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=password_dari_langkah_2
    POSTGRES_DB=asyuraa_db
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    SECRET_KEY=isi_random_secret_string
    ```
7.  **Network/Port**:
    *   Container Port: `8000` (Sesuai `Dockerfile.prod`).
    *   Expose ke Public: Ya (Aktifkan domainnya).
8.  Klik **"Deploy"** atau **"Save & Deploy"**.
9.  Tunggu sampai status **Running**. Copy URL domain API-nya (misal `https://api-asyuraa.vps-anda.com`).

---

## Langkah 4: Deploy Web (Frontend)
1.  Buat Service baru lagi (**"App"**).
2.  **Source**: "GitHub" (Repo yang sama).
3.  **Branch**: `main`.
4.  **Build Settings** (PENTING!):
    *   **Root Directory**: `apps/web`
    *   **Dockerfile Path**: `Dockerfile.prod`
5.  **Environment Variables**:
    *   `NEXT_PUBLIC_API_URL`: `https://api-asyuraa.vps-anda.com` (Ganti dengan URL API dari Langkah 3).
6.  **Network/Port**:
    *   Container Port: `3000`.
    *   Expose ke Public: Ya.
7.  Klik **"Deploy"**.

---

## Troubleshooting Umum

### "Build Error" / "Memory Exceeded"
Jika proses build berhenti di tengah jalan atau VPS hang:
*   Mungkin RAM 4GB penuh saat `npm run build`.
*   **Solusi**: Pastikan Anda sudah mengaktifkan **SWAP Memory** di VPS.
    *   Cek via terminal VPS: `free -h`. Jika Swap `0B`, minta bantuan support BiznetGio atau saya bisa buatkan script aktivasinya.

### "Internal Server Error" saat buka API
*   Cek Logs di tab **"Logs"** pada service API.
*   Biasanya karena gagal connect ke Database. Pastikan `POSTGRES_HOST` benar (nama service db).
