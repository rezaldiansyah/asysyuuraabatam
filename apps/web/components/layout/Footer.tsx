export function Footer() {
    return (
        <footer className="bg-slate-900 text-slate-300 py-12">
            <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* KOLOM 1: IDENTITAS */}
                <div>
                    <h3 className="text-xl font-bold text-white mb-4">Asy-Syuuraa Batam</h3>
                    <p className="text-sm leading-relaxed mb-4">
                        Membentuk generasi Qurani yang cerdas, mandiri, dan berakhlaq mulia.
                        Pendidikan terpadu dari RA hingga SMP.
                    </p>
                    <div className="flex gap-4">
                        {/* Social Icons Placeholder */}
                        <div className="h-8 w-8 bg-slate-700 rounded-full" />
                        <div className="h-8 w-8 bg-slate-700 rounded-full" />
                        <div className="h-8 w-8 bg-slate-700 rounded-full" />
                    </div>
                </div>

                {/* KOLOM 2: LINK */}
                <div>
                    <h4 className="text-white font-semibold mb-4">Akses Cepat</h4>
                    <ul className="space-y-2 text-sm">
                        <li><a href="/profil" className="hover:text-[var(--syuura-gold)]">Profil Yayasan</a></li>
                        <li><a href="/ppdb" className="hover:text-[var(--syuura-gold)]">Info PPDB</a></li>
                        <li><a href="/berita" className="hover:text-[var(--syuura-gold)]">Berita Sekolah</a></li>
                        <li><a href="/login" className="hover:text-[var(--syuura-gold)]">Login Portal</a></li>
                    </ul>
                </div>

                {/* KOLOM 3: KONTAK */}
                <div>
                    <h4 className="text-white font-semibold mb-4">Hubungi Kami</h4>
                    <ul className="space-y-2 text-sm">
                        <li>Jl. Bengkong Laut, Batam</li>
                        <li>Telp: (0778) 1234567</li>
                        <li>WA: 0812-3456-7890</li>
                        <li>Email: info@asysyuura.sch.id</li>
                    </ul>
                </div>
            </div>

            <div className="container mx-auto px-4 border-t border-slate-800 mt-8 pt-8 text-center text-xs text-slate-500">
                &copy; {new Date().getFullYear()} Yayasan Asy-Syuuraa Batam. All rights reserved.
            </div>
        </footer>
    );
}
