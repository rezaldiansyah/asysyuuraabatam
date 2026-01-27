import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { CheckCircle2, FileText, UserPlus, CreditCard, School } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function PPDBPage() {
    const steps = [
        {
            icon: <UserPlus className="h-8 w-8" />,
            title: "1. Buat Akun",
            desc: "Daftar akun orang tua calon siswa melalui website ini."
        },
        {
            icon: <FileText className="h-8 w-8" />,
            title: "2. Isi Formulir",
            desc: "Lengkapi data diri siswa dan orang tua secara online."
        },
        {
            icon: <CreditCard className="h-8 w-8" />,
            title: "3. Pembayaran",
            desc: "Lakukan pembayaran biaya pendaftaran sesuai instruksi."
        },
        {
            icon: <School className="h-8 w-8" />,
            title: "4. Seleksi & Wawancara",
            desc: "Ikuti rangkaian tes seleksi dan wawancara sesuai jadwal."
        }
    ];

    return (
        <div className="flex min-h-screen flex-col">
            <Navbar />
            <main className="flex-1">
                {/* Hero */}
                <section className="bg-[var(--syuura-green)] text-white py-20">
                    <div className="container mx-auto px-4 text-center">
                        <h1 className="text-4xl font-bold mb-4">Penerimaan Peserta Didik Baru</h1>
                        <p className="text-lg opacity-90 max-w-2xl mx-auto mb-8">
                            Bergabunglah bersama keluarga besar Asy-Syuuraa. Tahun Ajaran 2026/2027.
                        </p>
                        <Button asChild size="lg" className="bg-[var(--syuura-gold)] hover:bg-yellow-600 text-white rounded-full px-8">
                            <Link href="/ppdb/daftar">Daftar Sekarang</Link>
                        </Button>
                    </div>
                </section>

                {/* Kenapa Memilih Kami */}
                <section className="py-20 container mx-auto px-4">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold text-slate-800">Kenapa Memilih Asy-Syuuraa?</h2>
                    </div>
                    <div className="grid md:grid-cols-3 gap-8">
                        {[
                            "Kurikulum Terpadu (Nasional & Islam)",
                            "Program Tahfidz Al-Qur'an",
                            "Fasilitas Pembelajaran Modern",
                            "Lingkungan yang Islami & Kondusif",
                            "Tenaga Pengajar Profesional & Berdedikasi",
                            "Ekstrakurikuler Beragam"
                        ].map((item, idx) => (
                            <div key={idx} className="flex items-start gap-4 p-6 bg-white border rounded-xl hover:shadow-md transition">
                                <CheckCircle2 className="h-6 w-6 text-[var(--syuura-green)] shrink-0" />
                                <span className="font-medium text-slate-700">{item}</span>
                            </div>
                        ))}
                    </div>
                </section>

                {/* Alur Pendaftaran */}
                <section className="bg-slate-50 py-20">
                    <div className="container mx-auto px-4">
                        <div className="text-center mb-16">
                            <h2 className="text-3xl font-bold text-slate-800">Alur Pendaftaran</h2>
                        </div>

                        <div className="grid md:grid-cols-4 gap-8 relative">
                            {/* Connector Line (Desktop) */}
                            <div className="hidden md:block absolute top-12 left-0 w-full h-0.5 bg-slate-200 -z-10" />

                            {steps.map((step, idx) => (
                                <div key={idx} className="flex flex-col items-center text-center bg-white md:bg-transparent p-6 md:p-0 rounded-xl md:rounded-none shadow-sm md:shadow-none">
                                    <div className="w-24 h-24 rounded-full bg-white border-4 border-[var(--syuura-green)] flex items-center justify-center text-[var(--syuura-green)] mb-6 shadow-sm">
                                        {step.icon}
                                    </div>
                                    <h3 className="text-xl font-bold text-slate-800 mb-2">{step.title}</h3>
                                    <p className="text-slate-600 text-sm leading-relaxed">{step.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* CTA */}
                <section className="py-20 text-center">
                    <div className="container mx-auto px-4">
                        <h2 className="text-3xl font-bold text-slate-800 mb-6">Siap untuk Bergabung?</h2>
                        <p className="text-slate-600 mb-8 max-w-xl mx-auto">
                            Kuota terbatas. Segera daftarkan putra-putri Ayah/Bunda untuk mendapatkan pendidikan terbaik.
                        </p>
                        <div className="flex justify-center gap-4">
                            <Button asChild size="lg" className="bg-[var(--syuura-green)] hover:bg-[#14532D]">
                                <Link href="/ppdb/daftar">Buat Akun PPDB</Link>
                            </Button>
                            <Button asChild variant="outline" size="lg">
                                <Link href="/kontak">Hubungi Kami</Link>
                            </Button>
                        </div>
                    </div>
                </section>
            </main>
            <Footer />
        </div>
    );
}
