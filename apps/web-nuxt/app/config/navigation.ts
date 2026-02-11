export interface MenuItem {
    label: string
    icon: string
    to?: string
    children?: MenuItem[]
    roles?: string[] // If undefined, accessible by all authenticated users
    desc?: string
}

export const navigation: MenuItem[] = [
    {
        label: 'Dashboard',
        icon: 'pi pi-home',
        to: '/dashboard'
    },
    {
        label: 'Akademik',
        icon: 'pi pi-book',
        roles: ['admin', 'superadmin', 'guru', 'kepsek', 'tu'],
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
        roles: ['admin', 'superadmin', 'guru_tahfidz', 'guru', 'kepsek'],
        children: [
            { label: 'Setoran Hafalan', to: '/dashboard/tahfidz' },
            { label: 'Ujian Tahfidz', to: '/dashboard/tahfidz/ujian' },
            { label: 'Laporan', to: '/dashboard/tahfidz/laporan' },
        ],
    },
    {
        label: 'Kesiswaan',
        icon: 'pi pi-trophy',
        roles: ['admin', 'superadmin', 'kesiswaan', 'kepsek'],
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
        roles: ['admin', 'superadmin', 'bendahara', 'kepsek', 'yayasan'],
        children: [
            { label: 'Tagihan & SPP', to: '/dashboard/keuangan/tagihan' },
            { label: 'Transaksi Pembayaran', to: '/dashboard/keuangan/transaksi' },
            { label: 'Jenis Penerimaan', to: '/dashboard/keuangan/kategori' },
            { label: 'Laporan Keuangan', to: '/dashboard/keuangan/laporan' },
        ],
    },
    {
        label: 'Kepegawaian',
        icon: 'pi pi-users',
        roles: ['admin', 'superadmin', 'hrd', 'kepsek', 'yayasan', 'tu'],
        children: [
            { label: 'Data Pegawai', to: '/dashboard/sdm/pegawai' },
            { label: 'Presensi Pegawai', to: '/dashboard/sdm/presensi' },
        ],
    },
    {
        label: 'CMS Portal',
        icon: 'pi pi-globe',
        roles: ['admin', 'superadmin', 'humas'],
        children: [
            { label: 'Konten Landing Page', to: '/dashboard/cms/konten' },
            { label: 'Berita & Artikel', to: '/dashboard/cms/berita' },
            { label: 'Pengumuman / Mading', to: '/dashboard/cms/pengumuman' },
        ],
    },
    {
        label: 'Pengaturan',
        icon: 'pi pi-cog',
        roles: ['admin', 'superadmin'],
        children: [
            { label: 'Identitas Sekolah', to: '/dashboard/settings/sekolah' },
            { label: 'Manajemen User', to: '/dashboard/users' },
            { label: 'Role & Permissions', to: '/dashboard/settings/roles' },
            { label: 'Backup & Restore', to: '/dashboard/settings/backup' },
        ],
    },
]
