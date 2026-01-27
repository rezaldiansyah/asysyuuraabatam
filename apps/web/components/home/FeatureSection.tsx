import { BookOpen, Heart, Users, Sun, Trophy, ShieldCheck } from "lucide-react";

export function FeatureSection() {
    const features = [
        {
            icon: <BookOpen className="h-8 w-8" />,
            title: "Kurikulum Terpadu",
            desc: "Memadukan Kurikulum Nasional (Merdeka) dengan Kurikulum Khas Sekolah Islam Terpadu.",
        },
        {
            icon: <Heart className="h-8 w-8" />,
            title: "Bina Pribadi Islami",
            desc: "Pembentukan karakter (adab & akhlaq) yang intensif melalui mentoring dan keteladanan.",
        },
        {
            icon: <Sun className="h-8 w-8" />,
            title: "Program Tahfidz",
            desc: "Target hafalan yang terukur dengan metode yang menyenangkan sesuai jenjang usia.",
        },
        {
            icon: <Users className="h-8 w-8" />,
            title: "Pengajar Berkualitas",
            desc: "Didukung oleh asatidz/asatidzah yang kompeten, berdedikasi, dan menyayangi anak didik.",
        },
        {
            icon: <Trophy className="h-8 w-8" />,
            title: "Ekstrakurikuler",
            desc: "Beragam kegiatan penyaluran bakat dan minat siswa (Pramuka, Panahan, Futsal, dll).",
        },
        {
            icon: <ShieldCheck className="h-8 w-8" />,
            title: "Lingkungan Aman",
            desc: "Lingkungan sekolah yang kondusif, aman, dan nyaman untuk tumbuh kembang anak.",
        },
    ];

    return (
        <section className="py-20 bg-slate-50">
            <div className="container mx-auto px-4">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold text-[var(--syuura-green)] mb-2">Keunggulan Kami</h2>
                    <p className="text-slate-500">Kenapa memilih Sekolah Islam Asy-Syuuraa?</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-12">
                    {features.map((feature, idx) => (
                        <div key={idx} className="flex gap-4 items-start">
                            <div className="p-3 bg-white rounded-lg shadow-sm text-[var(--syuura-gold)]">
                                {feature.icon}
                            </div>
                            <div>
                                <h3 className="text-lg font-bold text-slate-800 mb-2">{feature.title}</h3>
                                <p className="text-sm text-slate-600 leading-relaxed">{feature.desc}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
