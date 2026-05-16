# Daftar Task Pending / Backlog

## 1. Integrasi Google SSO (Login with Google)
**Status:** ⏳ Pending (Ditunda)

**Alur yang diinginkan:**
1. User (Guru/Karyawan) bisa mendaftar (Signup) atau masuk (Login) menggunakan akun Google (SSO) di halaman web.
2. Ketika baru mendaftar via Google, akun akan dibuatkan namun dengan status **Menunggu Verifikasi Admin** (dashboard akan terkunci/dibatasi).
3. **Admin** memiliki halaman khusus di CMS (misal: "Verifikasi Akun") untuk melihat daftar pendaftar SSO yang tertunda.
4. Admin dapat melakukan verifikasi dengan cara menentukan:
   - *Role* akun tersebut (Guru / Karyawan / Admin).
   - Melakukan *mapping* / menghubungkan akun Google tersebut dengan data Pegawai (Employee) yang sudah ada di database.
5. Setelah diverifikasi dan di-mapping, akun akan otomatis aktif dan memiliki hak akses penuh sesuai rolenya.

**Kebutuhan Teknis (saat akan dikerjakan nanti):**
- Diperlukan pembuatan **Google Client ID** dari Google Cloud Console (sebagai "Web Application").
- Backend (FastAPI): Endpoint `POST /auth/google` untuk memvalidasi token dari Google dan mendaftarkan user dengan role `Unverified`.
- Frontend (Nuxt): Integrasi tombol Google Sign-In dan penambahan halaman CMS untuk verifikasi admin.
