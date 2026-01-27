import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

export default function ProfilPage() {
    return (
        <div className="flex min-h-screen flex-col">
            <Navbar />
            <main className="flex-1">
                <section className="bg-[var(--syuura-green)] text-white py-20">
                    <div className="container mx-auto px-4 text-center">
                        <h1 className="text-4xl font-bold mb-4">Tentang Asy-Syuuraa</h1>
                        <p className="text-lg opacity-90 max-w-2xl mx-auto">
                            Mengenal lebih dekat Sekolah Islam Terpadu Asy-Syuuraa Batam.
                        </p>
                    </div>
                </section>

                <section className="py-16 container mx-auto px-4">
                    <div className="grid md:grid-cols-2 gap-12 items-center">
                        <div>
                            <h2 className="text-3xl font-bold text-slate-800 mb-6">Sejarah Kami</h2>
                            <div className="prose prose-lg text-slate-600">
                                <p>
                                    Sekolah Islam Terpadu Asy-Syuuraa Batam didirikan dengan semangat untuk menghadirkan
                                    pendidikan berkualitas yang memadukan kurikulum nasional dengan nilai-nilai Islami.
                                </p>
                                <p>
                                    Berawal dari sebuah visi sederhana, kami terus tumbuh menjadi lembaga pendidikan
                                    yang dipercaya oleh masyarakat Batam untuk mendidik generasi penerus yang berakhlak
                                    mulia dan berprestasi.
                                </p>
                            </div>
                        </div>
                        <div className="bg-slate-100 rounded-2xl h-80 flex items-center justify-center">
                            {/* Placeholder Image */}
                            <span className="text-slate-400 font-medium">Foto Gedung Sekolah</span>
                        </div>
                    </div>
                </section>

                <section className="bg-[var(--syuura-green-surface)] py-16">
                    <div className="container mx-auto px-4">
                        <div className="text-center mb-12">
                            <h2 className="text-3xl font-bold text-slate-800">Visi & Misi</h2>
                        </div>

                        <div className="grid md:grid-cols-2 gap-8">
                            <div className="bg-white p-8 rounded-xl shadow-sm border border-green-100">
                                <h3 className="text-2xl font-bold text-[var(--syuura-green)] mb-4">Visi</h3>
                                <p className="text-lg text-slate-700 italic">
                                    "Menjadi lembaga pendidikan Islam terdepan yang mencetak generasi Qurani,
                                    cerdas, mandiri, dan berwawasan global."
                                </p>
                            </div>

                            <div className="bg-white p-8 rounded-xl shadow-sm border border-green-100">
                                <h3 className="text-2xl font-bold text-[var(--syuura-green)] mb-4">Misi</h3>
                                <ul className="space-y-3 text-slate-700 list-disc list-inside">
                                    <li>Menanamkan nilai-nilai tauhid dan akhlak mulia dalam setiap aspek pembelajaran.</li>
                                    <li>Menyelenggarakan pendidikan yang integratif dan holistik.</li>
                                    <li>Membangun lingkungan belajar yang kondusif, kreatif, dan inovatif.</li>
                                    <li>Mengembangkan potensi siswa melalui kegiatan intrakurikuler dan ekstrakurikuler.</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
            <Footer />
        </div>
    );
}
