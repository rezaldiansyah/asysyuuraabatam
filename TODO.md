# Road Map & TODO List: Pengembangan Website Asy-Syuuraa Batam

## 1. Integrasi Google SSO (Login with Google)
**Prioritas:** Tinggi ⏳ — **BELUM DIKERJAKAN**
**Objektif:** Memudahkan akses Guru/Karyawan dan keamanan verifikasi admin.

- [ ] Konfigurasi Google Cloud Console (Client ID & Secret).
- [ ] Implementasi Endpoint Backend `POST /auth/google`.
- [ ] Logic "Unverified User" (User terdaftar tapi tertahan sampai Admin verifikasi).
- [ ] Dashboard Admin: Halaman Verifikasi & Mapping User ke Data Pegawai.

---

## 2. Fase 1: Penyempurnaan & Finalisasi PPDB
**Prioritas:** Sangat Tinggi 🚀 — **SEBAGIAN BESAR SELESAI ✅**
**Objektif:** Menuntaskan alur pendaftaran sesuai standar dokumen saran perbaikan.

- [x] **Upload Berkas Wizard:** Input file KK dan Akta Kelahiran pada step Data Fisik & Berkas. ✅
- [x] **Multi-Poster Carousel:** Admin bisa upload lebih dari 1 poster, ditampilkan sebagai slider. ✅
- [x] **Pengaturan PPDB Dinamis:** Poster & No WA bisa dikelola lewat CMS, tersimpan ke DB. ✅
- [x] **Tombol Navigasi PPDB:** Layout vertikal, warna kontras (Indigo + Hijau WA). ✅
- [x] **Perbaikan Wizard:** Tombol "Selanjutnya" yang macet sudah diperbaiki (v-if). ✅
- [x] **Export CSV Lengkap:** Data pendaftar termasuk nama ortu, link KK/Akta, tanggal daftar. ✅
- [x] **Kolom Berkas Admin:** Admin bisa langsung lihat/download KK & Akta dari tabel. ✅
- [ ] **Cetak PDF Formulir:** Generasi otomatis file PDF pendaftaran per siswa. ❌
- [ ] **Sistem Pembayaran (Opsional/Next):** Ditunda — integrasi Payment Gateway.

---

## 3. Fase 1.5: Sistem Role & Permissions ✅ SELESAI
**Prioritas:** Tinggi — **SELESAI ✅**
**Objektif:** SuperAdmin bisa mengontrol akses menu setiap role secara fleksibel.

- [x] **Kolom Permissions di Database:** JSON array menu keys per role. ✅
- [x] **Halaman Role & Permissions:** Matriks interaktif checkbox (menu × role). ✅
- [x] **Sidebar Dinamis:** Menu sidebar berubah berdasarkan permissions dari DB. ✅
- [x] **API /auth/me:** Mengembalikan permissions bersama data role user. ✅
- [x] **Fix Global: PrimeIcons CSS:** Semua ikon di seluruh aplikasi kini tampil. ✅
- [x] **Fix Tombol Aksi User Management:** Ikon edit/hapus kini terlihat. ✅
- [x] **Fix Tombol Hapus Gambar:** Ikon tong sampah di Image Uploader terlihat jelas. ✅

---

## 4. Fase 2: Content Marketing & Branding
**Prioritas:** Sedang 📈 — **SELESAI ✅**
**Objektif:** Meningkatkan daya tarik sekolah bagi calon orang tua murid (Saran Perbaikan Poin 3).

- [x] **Modul Testimoni:** CMS khusus untuk mengelola testimoni Orang Tua & Alumni (CRUD + rating bintang + foto). ✅
- [x] **Galeri Foto (Kegiatan & Prestasi):** Album foto dengan tab kategori, lightbox viewer, thumbnail strip. ✅
- [x] **Halaman Publik Galeri:** `/galeri` dengan navigasi tab + dialog viewer responsif. ✅
- [x] **Halaman "Mengapa Memilih Kami":** Sudah ada sebagai section "Keunggulan Kami" di landing page (CMS-driven). ✅
- [x] **Teacher of the Month:** CMS admin + banner di landing page (gold card + foto + quote). ✅
- [x] **Galeri Video Profil:** CMS admin kelola link YouTube + custom thumbnail + embedded player di landing page. ✅

---

## 5. Fase 3: Sistem Manajemen Internal
**Prioritas:** Tinggi 📂 — **BELUM DIKERJAKAN**
**Objektif:** Modul-modul internal yang diakses semua role kecuali Orangtua.

### 5.1 Pusat Unduhan (Digital Repository)
- [ ] **Model & API:** Tabel `documents` (judul, kategori, file_url, visibility, uploader).
- [ ] **Kategori Dokumen:** SK Yayasan, SOP, Kalender Akademik, Juknis, Lain-lain.
- [ ] **Visibility:** Internal (hanya pegawai) / Publik (bisa diakses semua).
- [ ] **Admin CMS:** Upload, edit, hapus, filter dokumen.
- [ ] **Halaman Unduhan:** Tampilan list/grid dokumen untuk pegawai.

### 5.2 Rekap Presensi
- [ ] **Model & API:** Tabel `attendance_recap` (user_id, tanggal, status, keterangan).
- [ ] **Dashboard Ringkasan:** Statistik kehadiran bulanan per pegawai (hadir, izin, sakit, alfa).
- [ ] **Filter:** Per bulan, per unit, per pegawai.
- [ ] **Export:** Download rekap ke Excel/PDF.
- [ ] **Akses:** Kepala Sekolah, Admin HR, SuperAdmin.

### 5.3 Rapor Pegawai (Penilaian Kinerja)
- [ ] **Model & API:** Tabel `employee_report` (user_id, periode, aspek_penilaian, nilai, catatan).
- [ ] **Form Penilaian:** Multi-aspek (Kedisiplinan, Kompetensi, Kerjasama, dll).
- [ ] **Histori Rapor:** Riwayat penilaian per semester/tahun.
- [ ] **Akses:** Kepala Sekolah, SuperAdmin (input). Pegawai (lihat milik sendiri).

### 5.4 Mutabaah Harian Guru/Karyawan
- [ ] **Model & API:** Tabel `mutabaah` (user_id, tanggal, checklist ibadah harian).
- [ ] **Checklist Ibadah:** Sholat 5 waktu, Sholat Dhuha, Tilawah, Puasa Sunnah, Dzikir, dll.
- [ ] **Self-Report:** Setiap pegawai mengisi sendiri setiap hari.
- [ ] **Dashboard Rekap:** Ringkasan per minggu/bulan untuk atasan.
- [ ] **Akses:** Semua pegawai (self-input), Kepala Sekolah/SuperAdmin (lihat semua).

### 5.5 Navigasi Sidebar
- [ ] **Menu Group Baru:** "Manajemen Internal" di sidebar dashboard.
- [ ] **Sub-menu:** Pusat Unduhan, Rekap Presensi, Rapor Pegawai, Mutabaah Harian.
- [ ] **Permission:** Integrasi dengan RBAC matrix yang sudah ada.

---

## 6. Fase 4: Optimasi UI/UX & Teknis
**Prioritas:** Rendah 🛠️ — **BELUM DIKERJAKAN**
**Objektif:** Kelancaran akses dan integritas media sosial (Saran Perbaikan Poin 5).

- [x] **Social Media Feed:** Section "Ikuti Kami" di landing page + Facebook Page Plugin (feed live) + link cards Instagram/YouTube/TikTok/WhatsApp. Admin kelola via CMS Pengaturan. ✅
- [ ] **Optimasi Database:** Indexing pada tabel pendaftaran dan dokumen untuk kecepatan akses.
- [ ] **Dark Mode Polishing:** Memastikan semua halaman baru nyaman di mata saat mode gelap aktif.

---
*Last Updated: 17 Mei 2026*
