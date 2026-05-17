# Road Map & TODO List: Pengembangan Website Asy-Syuuraa Batam

## 1. Integrasi Google SSO (Login with Google)
**Prioritas:** Tinggi ⏳ 
**Objektif:** Memudahkan akses Guru/Karyawan dan keamanan verifikasi admin.

- [ ] Konfigurasi Google Cloud Console (Client ID & Secret).
- [ ] Implementasi Endpoint Backend `POST /auth/google`.
- [ ] Logic "Unverified User" (User terdaftar tapi tertahan sampai Admin verifikasi).
- [ ] Dashboard Admin: Halaman Verifikasi & Mapping User ke Data Pegawai.

---

## 2. Fase 1: Penyempurnaan & Finalisasi PPDB
**Prioritas:** Sangat Tinggi 🚀
**Objektif:** Menuntaskan alur pendaftaran sesuai standar dokumen saran perbaikan.

- [ ] **Upload Berkas Wizard:** Tambahkan input file untuk mengunggah scan KK dan Akta Kelahiran pada step terakhir pendaftaran.
- [ ] **Dashboard Admin (PPDB):**
    - [ ] Fitur **Export to Excel/CSV** yang lengkap (semua kolom data pendaftar).
    - [ ] Fitur **Cetak PDF Formulir** (Generasi otomatis file PDF pendaftaran).
- [ ] **Sistem Pembayaran (Opsional/Next):** Penjajakan integrasi Payment Gateway (Xendit/Midtrans) untuk biaya pendaftaran.

---

## 3. Fase 2: Content Marketing & Branding
**Prioritas:** Sedang 📈
**Objektif:** Meningkatkan daya tarik sekolah bagi calon orang tua murid (Saran Perbaikan Poin 3).

- [ ] **Modul Testimoni:** CMS khusus untuk mengelola testimoni Orang Tua & Alumni (Muncul di Landing Page).
- [ ] **Halaman "Mengapa Memilih Kami":** Layout khusus infografis keunggulan kurikulum & fasilitas.
- [ ] **Teacher of the Month:** Fitur apresiasi guru berupa banner/carousel khusus di halaman utama.
- [ ] **Galeri Video Profil:** Integrasi link YouTube sekolah ke dalam galeri video interaktif.

---

## 4. Fase 3: Sistem Manajemen Internal (Digital Repository)
**Prioritas:** Sedang 📂
**Objektif:** Pusat dokumentasi terpusat sesuai Saran Perbaikan Poin 1.

- [ ] **Modul Pusat Unduhan:** Halaman untuk Admin mengunggah dokumen (SOP, SK Yayasan, Kalender Akademik).
- [ ] **Kategori Dokumen:** Filter berdasarkan jenis dokumen (Internal/Publik).
- [ ] **Slip Gaji Digital (Opsional):** Fitur bagi pegawai untuk melihat/unduh slip gaji bulanan secara mandiri.

---

## 5. Fase 4: Optimasi UI/UX & Teknis
**Prioritas:** Rendah 🛠️
**Objektif:** Kelancaran akses dan integritas media sosial (Saran Perbaikan Poin 5).

- [ ] **Social Media Feed:** Menampilkan feed Instagram/Facebook terbaru di bagian footer atau sidebar.
- [ ] **Optimasi Database:** Indexing pada tabel pendaftaran dan dokumen untuk kecepatan akses.
- [ ] **Dark Mode Polishing:** Memastikan semua halaman baru nyaman di mata saat mode gelap aktif.

---
*Last Updated: 16 Mei 2026*
