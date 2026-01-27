export default function DashboardPage() {
    return (
        <div className="flex flex-1 flex-col gap-4 p-4 pt-8">
            <div className="grid auto-rows-min gap-4 md:grid-cols-3">
                <div className="aspect-video rounded-xl bg-white shadow-sm p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-lg font-medium text-slate-900">Total Siswa</h3>
                        <p className="text-3xl font-bold text-[var(--syuura-green)] mt-2">1,240</p>
                    </div>
                    <p className="text-sm text-slate-500">+12% dari bulan lalu</p>
                </div>
                <div className="aspect-video rounded-xl bg-white shadow-sm p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-lg font-medium text-slate-900">Tagihan Lunas</h3>
                        <p className="text-3xl font-bold text-emerald-600 mt-2">85%</p>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full mt-2">
                        <div className="h-2 bg-emerald-500 rounded-full w-[85%]"></div>
                    </div>
                </div>
                <div className="aspect-video rounded-xl bg-white shadow-sm p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-lg font-medium text-slate-900">Hadir Hari Ini</h3>
                        <p className="text-3xl font-bold text-blue-600 mt-2">98%</p>
                    </div>
                    <p className="text-sm text-slate-500">Guru & Karyawan</p>
                </div>
            </div>
            <div className="min-h-[100vh] flex-1 rounded-xl bg-white shadow-sm p-6">
                <h2 className="text-xl font-bold text-[var(--syuura-green)] mb-4">Selamat Datang di Dashboard Asy-Syuuraa</h2>
                <p className="text-slate-600">
                    Anda telah berhasil masuk ke sistem. Gunakan menu di samping kiri untuk mengelola data akademik, keuangan, dan pengaturan sekolah.
                </p>
            </div>
        </div>
    )
}
