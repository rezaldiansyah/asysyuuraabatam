# Product Requirements Document (PRD)
# Sistem Informasi Sekolah Asy-Syuuraa Batam

> **Version:** 1.0  
> **Tanggal:** 22 Januari 2026  
> **Dibuat oleh:** Tim Pengembangan  
> **Status:** Draft untuk Review

---

## 1. Ringkasan Eksekutif

### 1.1 Latar Belakang
Yayasan Asy-Syuuraa Batam adalah lembaga pendidikan Islam terpadu yang mengelola beberapa unit pendidikan:
- **RA (Raudhatul Athfal)** - TK/PAUD Islam
- **SDIT (Sekolah Dasar Islam Terpadu)** - Kelas 1-6
- **SMPIT (Sekolah Menengah Pertama Islam Terpadu)** - Kelas 7-9

Saat ini, sekolah sudah memiliki sistem informasi yang berjalan namun perlu **dimodernisasi** dan **diperluas** dengan tambahan:
- **Landing page publik** untuk promosi dan informasi sekolah
- **Portal orangtua** untuk akses informasi anak
- **Sistem dashboard modern** dengan teknologi terkini

### 1.2 Tujuan Produk
1. **Landing Page Promosi** - Website publik modern untuk:
   - Menampilkan profil dan program sekolah
   - Menyediakan informasi pendaftaran siswa baru (PPDB)
   - Showcase kegiatan dan prestasi sekolah
   - Contact dan lokasi sekolah

2. **Sistem Informasi Sekolah (Internal)** - Dashboard untuk:
   - Manajemen data siswa, guru, dan karyawan
   - Sistem keuangan (SPP, tagihan, pembayaran)
   - Sistem akademik (nilai, rapor, absensi)
   - Manajemen tahfidz dan kepribadian santri
   - Sistem kepegawaian dan penggajian
   - Portal khusus orangtua

### 1.3 Stakeholder Utama

| Stakeholder | Level | Peran | Kebutuhan Utama |
|-------------|-------|-------|-----------------| 
| Superadmin | Sistem | Administrator sistem | Full access ke semua modul, konfigurasi |
| Kabid Umum | Yayasan | Kepala Bidang Umum | Inventaris, kesehatan, perizinan semua unit |
| Kabid Keuangan | Yayasan | Kepala Bidang Keuangan | Keuangan, laporan, penggajian semua unit |
| TU Yayasan | Yayasan | Tata Usaha Yayasan | Administrasi lintas unit |
| Staf Keuangan | Yayasan | Operator keuangan | Pembayaran, tagihan SPP semua unit |
| Kepala Unit | Unit | Kepala RA/SDIT/SMPIT | Full access data unit yang dipimpin |
| Wakil Kepala Unit | Unit | Wakil Kepala RA/SDIT/SMPIT | Akses data unit (non-keuangan) |
| TU Unit | Unit | Tata Usaha Unit | Administrasi unit spesifik |
| Guru | Unit | Pengajar | Nilai, absensi, tahfidz di unitnya |
| Karyawan | Unit | Non-pengajar | Akses minimal di unitnya |
| Orangtua | Portal | Wali murid | Monitoring anak, pembayaran |

---

## 2. Visi dan Scope Produk

### 2.1 Visi
Membangun **ekosistem digital terpadu** yang menghubungkan sekolah, guru/karyawan, dan orangtua dalam satu platform modern yang mudah diakses, aman, dan informatif.

### 2.2 Target User
| User Type | Jumlah Estimasi | Akses |
|-----------|-----------------|-------|
| Admin & Staff | ~20 orang | Dashboard internal |
| Guru/Karyawan | ~50 orang | Dashboard internal (terbatas) |
| Orangtua/Wali | ~600 keluarga | Portal orangtua |
| Publik | N/A | Landing page |

### 2.3 Batasan Scope (Out of Scope)
- E-learning / LMS (tidak termasuk fase ini)
- Aplikasi mobile native (menggunakan responsive web)
- Integrasi dengan sistem pemerintah (Dapodik) - fase selanjutnya
- Sistem PPDB online otomatis - fase selanjutnya

---

## 3. Fitur dan Modul Produk

### 3.1 BAGIAN A: Landing Page (Publik) dengan CMS

> **Catatan Penting:** Landing page ini memiliki **CMS (Content Management System)** yang memungkinkan admin/tata usaha untuk mengelola konten tanpa perlu coding. Struktur navigasi dirancang berdasarkan **8 Standar Nasional Pendidikan** untuk memenuhi persyaratan akreditasi.

#### A.0 CMS Dashboard (Admin Login) ✅
| Fitur | Deskripsi |
|-------|-----------|
| Login CMS | Akses khusus admin untuk kelola website |
| Page Manager | CRUD halaman statis |
| Media Library | Upload dan kelola gambar, video, dokumen |
| Menu Manager | Atur navigasi website |
| Banner Manager | Kelola hero slider dan banner |
| Content Editor | WYSIWYG editor untuk konten |
| SEO Settings | Meta title, description per halaman |
| Preview Mode | Preview sebelum publish |
| Version History | Riwayat perubahan konten |

---

#### A.1 Homepage ✅
**Tujuan:** First impression yang kuat, navigasi mudah, CTA jelas

| Section | Konten | CMS Editable |
|---------|--------|--------------|
| **Hero Banner** | Video profil yayasan + slideshow gambar | ✅ |
| **Statistik** | Jumlah siswa, guru, lulusan, prestasi | ✅ |
| **3 Unit Cards** | RA, SDIT, SMPIT dengan link ke detail | ✅ |
| **Keunggulan** | 4-6 program unggulan (Tahfidz, dll) | ✅ |
| **Video Sekapur Sirih** | Video sambutan pimpinan | ✅ |
| **Testimoni Slider** | 4-6 testimoni alumni/orangtua | ✅ |
| **Berita Terbaru** | 3 berita terbaru (auto) | Auto |
| **CTA PPDB** | Banner pendaftaran | ✅ |
| **Footer** | Kontak, alamat, sosmed, link penting | ✅ |

---

#### A.2 Profil Yayasan
**Menu Dropdown:**

##### A.2.1 Tentang Yayasan
- Sekapur sirih (sambutan pimpinan)
- Video profil yayasan
- Sejarah singkat
- Legalitas yayasan

##### A.2.2 Visi, Misi & Motto
- Visi yayasan
- Misi yayasan
- Motto/tagline
- Nilai-nilai (values)

##### A.2.3 Struktur Organisasi
- Diagram struktur yayasan
- Profil pengurus yayasan
- Profil kepala sekolah per unit

##### A.2.4 Program Unggulan
- Tahfidz Al-Quran
- Bahasa Arab & Inggris
- Pendidikan karakter Islami
- Program lainnya (dengan gambar)

---

#### A.3 Unit Pendidikan (Mega Menu)
**Setiap unit memiliki subhalaman terpisah:**

##### A.3.1 RA Asy-Syuuraa (TK/PAUD)
| Subhalaman | Konten |
|------------|--------|
| Profil RA | Tentang, fasilitas, keunggulan |
| Kurikulum RA | Kurikulum 2013 PAUD, muatan lokal |
| Target Lulusan | Kompetensi yang dicapai |
| Galeri RA | Foto kegiatan RA |
| Tenaga Pendidik | Data guru RA |

##### A.3.2 SDIT Asy-Syuuraa (SD)
| Subhalaman | Konten |
|------------|--------|
| Profil SDIT | Tentang, fasilitas, keunggulan |
| Kurikulum SDIT | Kurikulum Merdeka + Muatan IT |
| Target Lulusan | Kompetensi SD (6 tahun) |
| Galeri SDIT | Foto kegiatan SDIT |
| Tenaga Pendidik | Data guru SDIT |

##### A.3.3 SMPIT Asy-Syuuraa (SMP)
| Subhalaman | Konten |
|------------|--------|
| Profil SMPIT | Tentang, fasilitas, keunggulan |
| Kurikulum SMPIT | Kurikulum Merdeka + Muatan IT |
| Target Lulusan | Kompetensi SMP (3 tahun) |
| Galeri SMPIT | Foto kegiatan SMPIT |
| Tenaga Pendidik | Data guru SMPIT |

---

#### A.4 Standar Pendidikan (Mega Menu - 8 SNP)
> **Catatan:** Struktur ini mengacu pada 8 Standar Nasional Pendidikan untuk keperluan akreditasi.

##### A.4.1 Standar Kompetensi Lulusan (SKL)
| Subhalaman | Konten |
|------------|--------|
| **Data Alumni** | Statistik dan daftar alumni per tahun |
| **Rekam Jejak Lulusan** | Tracking: lanjut kemana (SMP/SMA/Univ) |
| **Testimoni Alumni** | Kesan & pesan alumni |
| **Testimoni Orangtua** | Kesan & pesan wali murid |

##### A.4.2 Standar Isi
| Subhalaman | Konten |
|------------|--------|
| **Kurikulum** | Struktur kurikulum per unit |
| **Target Pembelajaran** | Visi & target setiap unit |
| **Muatan Lokal** | Program khas sekolah |
| **Kalender Pendidikan** | Kalender akademik tahunan |

##### A.4.3 Standar Pendidik & Tenaga Kependidikan
| Subhalaman | Konten |
|------------|--------|
| **Data Pendidik** | Profil guru dengan foto |
| **Kualifikasi** | Pendidikan, sertifikasi |
| **Tugas Mengajar** | Mapel yang diampu |
| **Prestasi Pendidik** | Penghargaan dan prestasi guru |
| **Data Tenaga Kependidikan** | Staff non-guru |

##### A.4.4 Standar Proses (Dokumentasi KBM)
| Subhalaman | Konten |
|------------|--------|
| **Proses KBM** | Galeri & video pembelajaran di kelas |
| **Kegiatan Sekolah** | Upacara, assembly, dll |
| **Ekstrakurikuler** | Daftar ekskul dengan foto kegiatan |
| **Kegiatan Luar Sekolah** | Field trip, outbound, lomba |
| **Dokumentasi Video** | Playlist YouTube kegiatan |

##### A.4.5 Standar Sarana Prasarana
| Subhalaman | Konten |
|------------|--------|
| **Overview Fasilitas** | Ringkasan dengan statistik |
| **Ruang Kelas** | Galeri foto kelas |
| **Perpustakaan** | Foto dan info perpustakaan |
| **Lab Komputer** | Fasilitas IT |
| **Media Pembelajaran** | Buku, alat peraga |
| **Fasilitas Lainnya** | Masjid, UKS, kantin, lapangan |

##### A.4.6 Standar Pengelolaan
- Tata kelola yayasan
- SOP dan kebijakan
- Akreditasi (sertifikat)

##### A.4.7 Standar Pembiayaan
- Info biaya pendidikan (overview)
- Skema pembayaran
- Program beasiswa

##### A.4.8 Standar Penilaian
- Sistem penilaian
- Kriteria kelulusan
- Rapor digital (sample)

---

#### A.5 Prestasi & Kegiatan

##### A.5.1 Prestasi Siswa
| Fitur | Deskripsi |
|-------|-----------|
| Daftar Prestasi | Filter by tahun, unit, jenis |
| Detail Prestasi | Nama, lomba, tingkat, foto |
| Hall of Fame | Showcase prestasi terbaik |

##### A.5.2 Prestasi Pendidik
- Penghargaan guru
- Sertifikasi dan pelatihan
- Karya ilmiah

##### A.5.3 Galeri Kegiatan
- Album foto per kategori
- Video kegiatan
- Slideshow gallery

---

#### A.6 Berita & Informasi ✅

| Fitur | Deskripsi |
|-------|-----------|
| Daftar Berita | Artikel dengan thumbnail |
| Kategori | Akademik, Kegiatan, Pengumuman |
| Detail Berita | Konten lengkap + galeri |
| Share | Social media sharing |
| Search | Pencarian berita |
| Archive | Arsip per bulan/tahun |

---

#### A.7 PPDB (Pendaftaran Peserta Didik Baru)

| Fitur | Deskripsi |
|-------|-----------|
| Info PPDB | Jadwal, syarat, alur |
| Biaya Pendidikan | Rincian biaya per unit |
| Brosur Digital | Download PDF |
| FAQ PPDB | Pertanyaan umum |
| Form Pra-Pendaftaran | Leads capture |
| Kontak PPDB | WhatsApp, telepon |

---

#### A.8 Kontak & Lokasi

| Fitur | Deskripsi |
|-------|-----------|
| Alamat | Alamat lengkap tiap unit |
| Google Maps | Embed peta interaktif |
| Form Kontak | Nama, email, pesan |
| Jam Operasional | Hari dan jam kerja |
| Social Media | Links Instagram, Facebook, YouTube |
| WhatsApp | Float button WA Business |

---

#### A.9 Wireframe & UX Recommendations

> **Rekomendasi sebagai Digital Marketing Expert:**

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER                                                         │
│  ┌────────┐ ┌──────────────────────────────────────────┐ ┌────┐ │
│  │  LOGO  │ │ Profil│Unit Pendidikan│Standar│Prestasi│ │Login│ │
│  └────────┘ │       ▼               ▼       ▼         │ └────┘ │
│             └──────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               HERO SECTION                                 │  │
│  │     Video Background + Tagline + CTA PPDB                 │  │
│  │                  "Mendidik Generasi Qurani"               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │  800+   │ │   50+   │ │  1000+  │ │   20+   │              │
│  │ Siswa   │ │  Guru   │ │ Alumni  │ │Prestasi │              │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘              │
│                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │     RA      │ │    SDIT     │ │   SMPIT     │ ← 3 CARDS   │
│  │  [Image]    │ │   [Image]   │ │   [Image]   │              │
│  │  TK Islam   │ │  SD Islam   │ │  SMP Islam  │              │
│  │ [Selengkap] │ │ [Selengkap] │ │ [Selengkap] │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  PROGRAM UNGGULAN                                          │  │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐                       │  │
│  │  │Tah │ │Arab│ │Eng │ │ICT │ │Char│ ← Icon Cards          │  │
│  │  │fidz│ │    │ │    │ │    │ │    │                       │  │
│  │  └────┘ └────┘ └────┘ └────┘ └────┘                       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────┐ ┌───────────────────────────────────┐   │
│  │  VIDEO PROFIL     │ │   TESTIMONI SLIDER                │   │
│  │  [YouTube Embed]  │ │  ← "Alumni & Orangtua berkata..." │   │
│  │  Sekapur Sirih    │ │  [Foto] [Nama] [Kesan]            │   │
│  └───────────────────┘ └───────────────────────────────────┘   │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  BERITA TERBARU                               [Lihat Semua]│  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐                         │  │
│  │  │[Image] │ │[Image] │ │[Image] │                         │  │
│  │  │Title   │ │Title   │ │Title   │                         │  │
│  │  │Date    │ │Date    │ │Date    │                         │  │
│  │  └────────┘ └────────┘ └────────┘                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  CTA PPDB BANNER                                           │  │
│  │  "Pendaftaran 2026/2027 Dibuka!"  [DAFTAR SEKARANG]       │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  FOOTER                                                         │
│  ┌─────────────────┐ ┌───────────────┐ ┌────────────────────┐  │
│  │ Logo + Alamat   │ │ Quick Links   │ │ Kontak + Sosmed    │  │
│  │ + Deskripsi     │ │ Profil        │ │ Telp: xxx          │  │
│  │                 │ │ PPDB          │ │ WA: xxx            │  │
│  │                 │ │ Kontak        │ │ [FB][IG][YT]       │  │
│  └─────────────────┘ └───────────────┘ └────────────────────┘  │
│                    © 2026 Yayasan Asy-Syuuraa Batam            │
└─────────────────────────────────────────────────────────────────┘
```

**Tips UX untuk Menghindari "Terlalu Penuh":**

| Masalah | Solusi |
|---------|--------|
| Terlalu banyak menu | Gunakan **Mega Menu** dropdown untuk grouping |
| Konten overwhelming | Gunakan **tabs** dan **accordion** di dalam halaman |
| Visual crowded | Desain dengan **whitespace** yang cukup |
| Loading lambat | **Lazy loading** images, compress media |
| Mobile unfriendly | Priority content, **hamburger menu** mobile |
| Navigasi membingungkan | **Breadcrumbs** di setiap halaman |

**Prioritas Konten Homepage (Above the Fold):**
1. Hero dengan video/image yang menarik
2. Statistik sekolah (social proof)
3. 3 Unit cards (navigasi cepat)
4. 1 CTA yang jelas (PPDB)

---

### 3.2 BAGIAN B: Sistem Informasi Internal

#### B.1 Modul Autentikasi & User Management ✅
| Fitur | Deskripsi |
|-------|-----------|
| Login sistem | Multi-role authentication |
| Manajemen user | CRUD akun dengan role-based access |
| ACL Groups | Pengaturan hak akses per grup |
| ACL Menus | Kontrol menu berdasarkan role |
| Reset password | Self-service password reset |
| Audit log | Logging aktivitas user |

**Definisi Unit:**
| Kode Unit | Nama Unit | Keterangan |
|-----------|-----------|------------|
| `YYS` | Yayasan | Level tertinggi, mengawasi semua unit |
| `RA` | RA Asy-Syuuraa | Raudhatul Athfal (TK/PAUD) |
| `SDIT` | SDIT Asy-Syuuraa | Sekolah Dasar Islam Terpadu |
| `SMPIT` | SMPIT Asy-Syuuraa | Sekolah Menengah Pertama Islam Terpadu |

**Hierarki Role & Level Akses:**

| Role | Kode | Level | Unit | Akses Data |
|------|------|-------|------|------------|
| **Superadmin** | `superadmin` | Sistem | Semua | Full access, konfigurasi sistem |
| **Kepala Bidang Umum** | `kabid_umum` | Yayasan | Semua | Data umum semua unit |
| **Kepala Bidang Keuangan** | `kabid_keuangan` | Yayasan | Semua | Data keuangan semua unit |
| **Tata Usaha Yayasan** | `tu_yayasan` | Yayasan | Semua | Administrasi semua unit |
| **Staf Keuangan** | `staf_keuangan` | Yayasan | Semua | Pembayaran & tagihan semua unit |
| **Kepala Unit** | `kepala_unit` | Unit | Spesifik | Full access data unitnya |
| **Wakil Kepala Unit** | `wakil_kepala` | Unit | Spesifik | Akses data unitnya (selain keuangan) |
| **Tata Usaha Unit** | `tu_unit` | Unit | Spesifik | Administrasi unitnya |
| **Guru** | `guru` | Unit | Spesifik | Nilai, absensi di unitnya |
| **Karyawan** | `karyawan` | Unit | Spesifik | Akses minimal di unitnya |
| **Orangtua** | `orangtua` | Portal | - | Data anak sendiri saja |

**Aturan Akses berdasarkan Level:**

| Level | Deskripsi | Contoh Akses |
|-------|-----------|--------------|
| **Sistem** | Superadmin only | Semua data, setting sistem, user management |
| **Yayasan** | Bisa melihat semua unit | Kabid, TU Yayasan bisa lihat data RA + SDIT + SMPIT |
| **Unit** | Hanya unitnya sendiri | Kepala SDIT hanya bisa lihat data SDIT |
| **Portal** | Data personal | Orangtua hanya lihat data anaknya |

**Contoh Implementasi:**
- Kepala Unit SDIT login → Dashboard hanya menampilkan data siswa, guru, keuangan SDIT
- Kabid Keuangan login → Dashboard menampilkan rekapitulasi keuangan RA + SDIT + SMPIT
- Guru yang mengajar di SDIT dan SMPIT → bisa akses kelas di kedua unit (multi-unit assignment)

---

#### B.2 Modul Data Master ✅

##### B.2.1 Manajemen Siswa
| Fitur | Deskripsi |
|-------|-----------|
| Data Siswa | CRUD data lengkap siswa |
| Data Orangtua | Data ayah, ibu, wali |
| Riwayat Pendidikan | Asal sekolah, tanggal masuk |
| Kelas & Marhalah | Penempatan kelas |
| Foto Siswa | Upload foto profil |
| Status Aktif/Lulus | Tracking status siswa |
| Export Data | Excel, PDF |

**Field data siswa (berdasarkan analisis SQL):**
- Data pribadi: NIS, nama, TTL, jenis kelamin, NIK, NISN
- Data orangtua: nama ayah/ibu, pekerjaan, HP, alamat lengkap
- Data akademik: kelas, marhalah, asal sekolah
- Data tambahan: asrama, wali asrama, kamar, murobbi
- Data keuangan: SPP, uang pangkal, daftar ulang

##### B.2.2 Manajemen Pegawai (Guru/Karyawan)
| Fitur | Deskripsi |
|-------|-----------|
| Data Pegawai | NIK, biodata lengkap |
| Jabatan & Divisi | Unit kerja dan posisi |
| Riwayat Pendidikan | SD s/d Universitas |
| Pelatihan | Riwayat pelatihan guru |
| Status Kepegawaian | Aktif/keluar |
| Mapel Diampu | Untuk guru |

##### B.2.3 Master Data Akademik
| Fitur | Deskripsi |
|-------|-----------|
| Data Kelas | Nama kelas, marhalah, wali kelas |
| Mata Pelajaran | Daftar mapel per marhalah |
| Tahun Ajaran | Setting tahun ajaran |
| Kalender Akademik | Event dan jadwal akademik |
| Setting Nilai | Bobot dan konversi nilai |

---

#### B.3 Modul Akademik

##### B.3.1 Sistem Absensi Siswa
| Fitur | Deskripsi |
|-------|-----------|
| Input Absensi Harian | S, I, A per siswa |
| Rekap Bulanan | Summary per bulan |
| Laporan per Kelas | Report kehadiran |
| Catatan Absensi | Keterangan tambahan |

##### B.3.2 Sistem Nilai
| Fitur | Deskripsi |
|-------|-----------|
| Input Nilai | Harian, UTS, UAS |
| Setting Mapel & Guru | Penugasan pengajar |
| Konversi Predikat | A, B, C, D, E dengan deskripsi |
| Nilai Sikap | Spiritual & Sosial |
| Cetak Rapor | Generate PDF rapor |

##### B.3.3 Sistem Tahfidz (Al-Quran)
| Fitur | Deskripsi |
|-------|-----------|
| Setoran Hafalan | Juz dan surat |
| Progress Hafalan | Tracking per siswa |
| Ujian Tahfidz | Nilai ujian tahfidz |
| Absen Halaqoh | Kehadiran halaqoh quran |
| Laporan Tahfidz | Report progress |

##### B.3.4 Penilaian Kepribadian (Kesantrian)
| Fitur | Deskripsi |
|-------|-----------|
| Adab | Teman, guru, lingkungan, agama, orangtua |
| Bahasa | Arab & Inggris |
| Ibadah | Sholat wajib, rawatib, dhuha, wudhu |
| Tadarus & Iqra | Progress baca quran |
| Kemandirian | Kebersihan diri, menabung, infaq |
| Catatan Asrama | Untuk siswa asrama |

---

#### B.4 Modul Kesiswaan

##### B.4.1 Sistem Kesehatan
| Fitur | Deskripsi |
|-------|-----------|
| Input Data Kesehatan | Keluhan, obat, penanganan |
| Riwayat Kesehatan | Histori per siswa |
| Laporan UKS | Report kesehatan |

##### B.4.2 Sistem Perizinan
| Fitur | Deskripsi |
|-------|-----------|
| Input Izin | Keluar/pulang |
| Approval | Workflow persetujuan |
| Kuota Izin | Batas izin per siswa |
| History Izin | Tracking perizinan |

##### B.4.3 Sistem Pelanggaran
| Fitur | Deskripsi |
|-------|-----------|
| Input Pelanggaran | Jenis, deskripsi |
| Poin Pelanggaran | Perhitungan poin |
| Sanksi | Tindak lanjut |
| Histori | Rekap per siswa |

##### B.4.4 Sistem Prestasi
| Fitur | Deskripsi |
|-------|-----------|
| Input Prestasi | Lomba, kejuaraan |
| Level | Sekolah, kota, provinsi, nasional |
| Poin Prestasi | Reward point |

---

#### B.5 Modul Keuangan ✅

##### B.5.1 Manajemen Tagihan
| Fitur | Deskripsi |
|-------|-----------|
| Setting Tagihan | Jenis dan nominal |
| Generate Tagihan | Bulk generate per kelas |
| Tagihan Rutin | SPP bulanan |
| Tagihan Non-rutin | Daftar ulang, komite |
| Jatuh Tempo | Tanggal deadline |

##### B.5.2 Pembayaran
| Fitur | Deskripsi |
|-------|-----------|
| Input Pembayaran | Tunai, transfer |
| Cetak Kwitansi | Bukti pembayaran |
| Validasi Transfer | Konfirmasi transfer |
| Pembayaran Partial | Cicilan |

##### B.5.3 Jurnal Keuangan
| Fitur | Deskripsi |
|-------|-----------|
| Jurnal Masuk | Pemasukan |
| Jurnal Keluar | Pengeluaran |
| Kategori | Klasifikasi transaksi |
| Laporan Keuangan | Neraca, laba rugi |

##### B.5.4 Uang Saku (Opsional - untuk asrama)
| Fitur | Deskripsi |
|-------|-----------|
| Saldo Uang Saku | Per siswa |
| Penarikan | Transaksi keluar |
| EDC | Integrasi EDC |
| Laporan | Rekap saldo |

---

#### B.6 Modul Kepegawaian

##### B.6.1 Data Tugas Guru
| Fitur | Deskripsi |
|-------|-----------|
| Penugasan Mengajar | Mapel & kelas |
| Jam KBM | Jumlah jam mengajar |
| Jam Tahfidz | Jam halaqoh |
| Wali Kelas | Penugasan wali kelas |

##### B.6.2 Absensi Pegawai
| Fitur | Deskripsi |
|-------|-----------|
| Kehadiran Guru | Hadir, ijin, sakit |
| Laporan Kehadiran | Report bulanan |

##### B.6.3 Penggajian
| Fitur | Deskripsi |
|-------|-----------|
| Gaji Pokok | Per golongan & masa kerja |
| Tunjangan | Pendidikan, walikelas, struktural |
| Potongan | BPJS, kasbon, BMT |
| Slip Gaji | Generate & cetak |
| Laporan Gaji | Summary bulanan |

---

#### B.7 Modul Inventaris & Sarpras

##### B.7.1 Inventaris Barang
| Fitur | Deskripsi |
|-------|-----------|
| Data Barang | CRUD inventaris |
| Kategori Barang | Klasifikasi |
| Departemen | Unit pemilik |
| Status Barang | Kondisi baik/rusak |

##### B.7.2 Sarana Prasarana
| Fitur | Deskripsi |
|-------|-----------|
| Gedung & Ruangan | Data ruangan |
| Perawatan | Jadwal maintenance |

---

#### B.8 Modul Komunikasi

##### B.8.1 Broadcast Berita
| Fitur | Deskripsi |
|-------|-----------|
| Buat Pengumuman | WYSIWYG editor |
| Target Audience | Per kelas/unit |
| Push Notification | Notifikasi orangtua |

##### B.8.2 Forum (Opsional)
| Fitur | Deskripsi |
|-------|-----------|
| Diskusi | Thread diskusi |
| Kategori | Per topik |

---

### 3.3 BAGIAN C: Portal Orangtua

#### C.1 Dashboard Orangtua
| Fitur | Deskripsi |
|-------|-----------|
| Overview Anak | Ringkasan per anak |
| Notifikasi | Pengumuman dari sekolah |
| Quick Actions | Akses cepat ke fitur |

#### C.2 Akademik Anak
| Fitur | Deskripsi |
|-------|-----------|
| Nilai Anak | Lihat nilai per semester |
| Absensi | Rekap kehadiran |
| Rapor Digital | Download PDF |
| Progress Tahfidz | Hafalan Al-Quran |
| Kepribadian | Penilaian karakter |

#### C.3 Keuangan
| Fitur | Deskripsi |
|-------|-----------|
| Tagihan | Daftar tagihan |
| Histori Pembayaran | Riwayat bayar |
| Pembayaran Online | Integrasi payment gateway |

#### C.4 Informasi
| Fitur | Deskripsi |
|-------|-----------|
| Pengumuman | Berita sekolah |
| Kalender | Jadwal kegiatan |
| Kontak Guru | Wali kelas |

---

## 4. Teknologi Stack

### 4.1 Frontend
| Layer | Teknologi |
|-------|-----------|
| Framework | **Next.js 14+** (React) atau **Nuxt.js 3** (Vue) |
| Styling | **Tailwind CSS** |
| UI Components | Shadcn/ui atau Radix UI |
| State Management | Zustand / Pinia |
| Forms | React Hook Form / VeeValidate |
| Data Fetching | TanStack Query |

### 4.2 Backend
| Layer | Teknologi |
|-------|-----------|
| Language | **Python 3.11+** |
| Framework | **FastAPI** atau **Django REST Framework** |
| ORM | SQLAlchemy / Django ORM |
| Authentication | JWT + OAuth2 |
| Validation | Pydantic |

### 4.3 Database & Storage
| Layer | Teknologi |
|-------|-----------|
| Database | **PostgreSQL 15+** |
| Cache | Redis (opsional) |
| File Storage | **Cloudflare R2** atau **Cloudinary** |
| Image CDN | Cloudflare / Cloudinary transformation |

### 4.4 Infrastructure
| Layer | Teknologi |
|-------|-----------|
| Hosting | **BiznetGio VPS** |
| Container | **Docker** + Docker Compose |
| Panel | **EasyPanel** atau **CyberPanel** |
| CI/CD | GitHub Actions |
| Reverse Proxy | Nginx / Caddy |
| SSL | Let's Encrypt |

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Halaman loading < 3 detik
- API response time < 500ms
- Support 100+ concurrent users

### 5.2 Security
- HTTPS enforced
- Password hashing (bcrypt/argon2)
- Input validation & sanitization
- CSRF protection
- Rate limiting

### 5.3 Accessibility
- Mobile-responsive design
- Support browser modern (Chrome, Firefox, Safari, Edge)
- Minimum screen: 320px width

### 5.4 Scalability
- Horizontal scaling ready
- Database optimization with indexing
- File storage CDN-based

### 5.5 Backup & Recovery
- Daily database backup
- Backup retention 30 hari
- Recovery point objective (RPO): 24 jam

---

## 6. Milestone dan Timeline (Estimasi)

| Fase | Durasi | Deliverables |
|------|--------|--------------|
| **Fase 1: Foundation** | 2-3 minggu | Setup project, database design, auth system |
| **Fase 2: Landing Page** | 2 minggu | Homepage, profil, informasi PPDB |
| **Fase 3: Core Admin** | 4-5 minggu | Master data (siswa, guru, kelas), user management |
| **Fase 4: Akademik** | 3-4 minggu | Nilai, absensi, tahfidz, kepribadian |
| **Fase 5: Keuangan** | 3 minggu | Tagihan, pembayaran, laporan |
| **Fase 6: Portal Orangtua** | 2-3 minggu | Dashboard orangtua, view anak |
| **Fase 7: Testing & Deploy** | 2 minggu | UAT, bug fixing, deployment |

**Total estimasi: 18-22 minggu**

---

## 7. Risiko dan Mitigasi

| Risiko | Impact | Mitigasi |
|--------|--------|----------|
| Migrasi data lama gagal | High | Mapping field detail, testing migrasi |
| User adoption rendah | Medium | Training, dokumentasi, support |
| Performance issue | Medium | Load testing, optimization |
| Security breach | High | Security audit, penetration test |

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Landing page visitor | 500+ per bulan |
| Orangtua aktif | 80% registrasi |
| Admin adoption | 100% staff menggunakan sistem |
| Payment online usage | 50% transaksi |
| System uptime | 99.5% |

---

## 9. Approval

| Nama | Jabatan | Tanda Tangan | Tanggal |
|------|---------|--------------|---------|
| | Ketua Yayasan | | |
| | Kepala SDIT | | |
| | Kepala SMPIT | | |
| | Kabid Umum | | |
| | Kabid Keuangan | | |

---

*Dokumen ini adalah draft dan memerlukan review dari stakeholder sebelum implementasi.*
