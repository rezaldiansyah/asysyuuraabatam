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
            { label: 'Data Siswa', to: '/dashboard/siswa' },
            { label: 'Data Guru', to: '/dashboard/guru' },
            { label: 'Rombel (Kelas)', to: '/dashboard/rombel' },
            { label: 'Jadwal Pelajaran', to: '/dashboard/jadwal' },
            // New Feature
            { label: 'Kalender Pendidikan', to: '/dashboard/akademik/kalender' },
            { label: 'Absensi Siswa', to: '/dashboard/absensi' },
            { label: 'Nilai & Rapor', to: '/dashboard/nilai' },
        ],
    },
    {
        label: 'Tahfidz',
        icon: 'pi pi-bookmark',
        key: 'tahfidz',
        children: [
            { label: 'Setoran Hafalan', to: '/dashboard/tahfidz' },
            { label: 'Ujian Tahfidz', to: '/dashboard/tahfidz/ujian' },
            { label: 'Laporan', to: '/dashboard/tahfidz/laporan' },
        ],
    },
    {
        label: 'Kesiswaan',
        icon: 'pi pi-trophy',
        key: 'kesiswaan',
        children: [
            { label: 'Prestasi', to: '/dashboard/kesiswaan/prestasi', desc: 'Coming Soon' },
            { label: 'Pelanggaran', to: '/dashboard/kesiswaan/pelanggaran', desc: 'Coming Soon' },
            { label: 'Konseling (BK)', to: '/dashboard/kesiswaan/bk', desc: 'Coming Soon' },
            { label: 'UKS / Kesehatan', to: '/dashboard/kesiswaan/uks', desc: 'Coming Soon' },
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
            { label: 'Data Pegawai', to: '/dashboard/sdm/pegawai' },
            { label: 'Presensi Pegawai', to: '/dashboard/sdm/presensi' },
        ],
    },
    {
        label: 'Manajemen Internal',
        icon: 'pi pi-folder',
        key: 'internal',
        children: [
            { label: 'Pusat Unduhan', to: '/dashboard/internal/dokumen' },
            { label: 'Mutabaah Harian', to: '/dashboard/internal/mutabaah' },
            { label: 'Rekap Mutabaah', to: '/dashboard/internal/mutabaah/rekap' },
        ],
    },
    {
        label: 'Manajemen PPDB',
        icon: 'pi pi-id-card',
        key: 'ppdb',
        children: [
            { label: 'Data Pendaftar', to: '/dashboard/ppdb/pendaftar' },
            { label: 'Pengaturan PPDB', to: '/dashboard/ppdb/pengaturan' },
        ],
    },
    {
        label: 'CMS Portal',
        icon: 'pi pi-globe',
        key: 'cms',
        children: [
            { label: 'Konten Landing Page', to: '/dashboard/cms/konten' },
            { label: 'Berita & Artikel', to: '/dashboard/cms/berita' },
            { label: 'Pengumuman / Mading', to: '/dashboard/cms/pengumuman' },
            { label: 'Testimoni', to: '/dashboard/cms/testimoni' },
            { label: 'Galeri Foto', to: '/dashboard/cms/galeri' },
            { label: 'Galeri Video', to: '/dashboard/cms/video' },
            { label: 'Teacher of the Month', to: '/dashboard/cms/teacher-of-month' },
        ],
    },
    {
        label: 'Pengaturan',
        icon: 'pi pi-cog',
        key: 'pengaturan',
        children: [
            { label: 'Identitas Sekolah', to: '/dashboard/settings/sekolah' },
            { label: 'Manajemen User', to: '/dashboard/users' },
            { label: 'Role & Permissions', to: '/dashboard/settings/roles' },
            { label: 'Backup & Restore', to: '/dashboard/settings/backup' },
        ],
    },
]
