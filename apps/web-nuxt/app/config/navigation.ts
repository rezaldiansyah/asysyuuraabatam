export interface MenuItem {
    label: string
    icon: string
    to?: string
    children?: MenuItem[]
    key?: string // Used for permission matching
    desc?: string
}

// Master navigation definition - all possible menus
// Access is controlled by role permissions stored in database
export const navigation: MenuItem[] = [
    {
        label: 'Dashboard',
        icon: 'pi pi-home',
        to: '/dashboard',
        key: 'dashboard'
    },
    {
        label: 'Akademik',
        icon: 'pi pi-book',
        key: 'akademik',
        children: [
            { label: 'Data Siswa', to: '/dashboard/siswa', key: 'akademik.siswa' },
            { label: 'Data Guru', to: '/dashboard/guru', key: 'akademik.guru' },
            { label: 'Rombel (Kelas)', to: '/dashboard/rombel', key: 'akademik.rombel' },
            { label: 'Jadwal Pelajaran', to: '/dashboard/jadwal', key: 'akademik.jadwal' },
            { label: 'Kalender Pendidikan', to: '/dashboard/akademik/kalender', key: 'akademik.kalender' },
            { label: 'Absensi Siswa', to: '/dashboard/absensi', key: 'akademik.absensi' },
            { label: 'Nilai & Rapor', to: '/dashboard/nilai', key: 'akademik.nilai' },
        ],
    },
    {
        label: 'Tahfidz',
        icon: 'pi pi-bookmark',
        key: 'tahfidz',
        children: [
            { label: 'Setoran Hafalan', to: '/dashboard/tahfidz', key: 'tahfidz.setoran' },
            { label: 'Ujian Tahfidz', to: '/dashboard/tahfidz/ujian', key: 'tahfidz.ujian' },
            { label: 'Laporan', to: '/dashboard/tahfidz/laporan', key: 'tahfidz.laporan' },
        ],
    },
    {
        label: 'Kesiswaan',
        icon: 'pi pi-trophy',
        key: 'kesiswaan',
        children: [
            { label: 'Prestasi', to: '/dashboard/kesiswaan/prestasi', key: 'kesiswaan.prestasi', desc: 'Coming Soon' },
            { label: 'Pelanggaran', to: '/dashboard/kesiswaan/pelanggaran', key: 'kesiswaan.pelanggaran', desc: 'Coming Soon' },
            { label: 'Konseling (BK)', to: '/dashboard/kesiswaan/bk', key: 'kesiswaan.bk', desc: 'Coming Soon' },
            { label: 'UKS / Kesehatan', to: '/dashboard/kesiswaan/uks', key: 'kesiswaan.uks', desc: 'Coming Soon' },
        ],
    },
    {
        label: 'Keuangan',
        icon: 'pi pi-wallet',
        key: 'keuangan',
        to: '/dashboard/keuangan',
    },
    {
        label: 'Kepegawaian',
        icon: 'pi pi-users',
        key: 'kepegawaian',
        children: [
            { label: 'Data Pegawai', to: '/dashboard/sdm/pegawai', key: 'kepegawaian.pegawai' },
            { label: 'Presensi Pegawai', to: '/dashboard/sdm/presensi', key: 'kepegawaian.presensi' },
        ],
    },
    {
        label: 'Manajemen Internal',
        icon: 'pi pi-folder',
        key: 'internal',
        children: [
            { label: 'Pusat Unduhan', to: '/dashboard/internal/dokumen', key: 'internal.dokumen' },
            { label: 'Notulen Rapat', to: '/dashboard/internal/notulen', key: 'internal.notulen' },
            { label: 'Mutabaah Harian', to: '/dashboard/internal/mutabaah', key: 'internal.mutabaah' },
            { label: 'Rekap Mutabaah', to: '/dashboard/internal/mutabaah/rekap', key: 'internal.rekap_mutabaah' },
        ],
    },
    {
        label: 'Manajemen PPDB',
        icon: 'pi pi-id-card',
        key: 'ppdb',
        children: [
            { label: 'Data Pendaftar', to: '/dashboard/ppdb/pendaftar', key: 'ppdb.pendaftar' },
            { label: 'Setup Landing Page', to: '/dashboard/ppdb/pengaturan-lp', key: 'ppdb.pengaturan-lp' },
            { label: 'Pengaturan PPDB', to: '/dashboard/ppdb/pengaturan', key: 'ppdb.pengaturan' },
        ],
    },
    {
        label: 'CMS Portal',
        icon: 'pi pi-globe',
        key: 'cms',
        children: [
            { label: 'Konten Landing Page', to: '/dashboard/cms/konten', key: 'cms.konten' },
            { label: 'Berita & Artikel', to: '/dashboard/cms/berita', key: 'cms.berita' },
            { label: 'Pengumuman / Mading', to: '/dashboard/cms/pengumuman', key: 'cms.pengumuman' },
            { label: 'Testimoni', to: '/dashboard/cms/testimoni', key: 'cms.testimoni' },
            { label: 'Galeri Foto', to: '/dashboard/cms/galeri', key: 'cms.galeri' },
            { label: 'Galeri Video', to: '/dashboard/cms/video', key: 'cms.video' },
            { label: 'Teacher of the Month', to: '/dashboard/cms/teacher-of-month', key: 'cms.teacher-of-month' },
        ],
    },
    {
        label: 'Pengaturan',
        icon: 'pi pi-cog',
        key: 'pengaturan',
        children: [
            { label: 'Identitas Sekolah', to: '/dashboard/settings/sekolah', key: 'pengaturan.sekolah' },
            { label: 'Manajemen User', to: '/dashboard/users', key: 'pengaturan.users' },
            { label: 'Role & Permissions', to: '/dashboard/settings/roles', key: 'pengaturan.roles' },
            { label: 'Backup & Restore', to: '/dashboard/settings/backup', key: 'pengaturan.backup' },
        ],
    },
]
