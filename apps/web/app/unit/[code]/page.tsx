import { notFound } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { DynamicFeatureSection } from "@/components/home/DynamicFeatureSection";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const UNITS = ["ra", "sdit", "smpit"];

const UNIT_LABELS: Record<string, string> = {
    ra: "RA Asy-Syuuraa",
    sdit: "SDIT Asy-Syuuraa",
    smpit: "SMPIT Asy-Syuuraa"
};

async function getContent(unitCode: string) {
    const API_URL = "http://localhost:8000";
    try {
        const [heroRes, sambutanRes, featuresRes, testimoRes] = await Promise.all([
            fetch(`${API_URL}/public/content/${unitCode}_hero`, { next: { revalidate: 0 } }),
            fetch(`${API_URL}/public/content/${unitCode}_sambutan`, { next: { revalidate: 0 } }),
            fetch(`${API_URL}/public/content/${unitCode}_features`, { next: { revalidate: 0 } }),
            fetch(`${API_URL}/public/content/${unitCode}_testimonials`, { next: { revalidate: 0 } })
        ]);

        const hero = heroRes.ok ? await heroRes.json() : {};
        const sambutan = sambutanRes.ok ? await sambutanRes.json() : {};
        const features = featuresRes.ok ? JSON.parse((await featuresRes.json()).content_json || "[]") : [];
        const testimonials = testimoRes.ok ? JSON.parse((await testimoRes.json()).content_json || "[]") : [];

        return { hero, sambutan, features, testimonials };
    } catch (e) {
        console.error("Failed to fetch unit content", e);
        return { hero: {}, sambutan: {}, features: [], testimonials: [] };
    }
}

export default async function UnitPage({ params }: { params: { code: string } }) {
    const code = params.code.toLowerCase();

    if (!UNITS.includes(code)) {
        notFound();
    }

    const content = await getContent(code);
    const unitName = UNIT_LABELS[code];

    // Default Fallbacks
    const heroTitle = content.hero.title || `Selamat Datang di ${unitName}`;
    const heroBody = content.hero.body || "Mewujudkan generasi Rabbani yang unggul dalam Imtaq dan Iptek.";
    const sambutanTitle = content.sambutan.title || "Sambutan Kepala Sekolah";
    const sambutanBody = content.sambutan.body || "Assalamu'alaikum Warahmatullahi Wabarakatuh...";

    return (
        <div className="flex min-h-screen flex-col">
            <Navbar />

            <main className="flex-1">
                {/* HERO SECTION */}
                <section className="relative py-20 lg:py-32 bg-[var(--syuura-green)] overflow-hidden">
                    {/* Background Image Overlay if exists */}
                    {content.hero.image_url && (
                        <div
                            className="absolute inset-0 bg-cover bg-center z-0 opacity-20"
                            style={{ backgroundImage: `url(${content.hero.image_url})` }}
                        />
                    )}

                    <div className="container mx-auto px-4 relative z-10 text-center text-white">
                        <h1 className="text-4xl md:text-6xl font-bold mb-6">{heroTitle}</h1>
                        <p className="text-lg md:text-xl opacity-90 mb-8 max-w-2xl mx-auto whitespace-pre-line">
                            {heroBody}
                        </p>
                        <div className="flex justify-center gap-4">
                            <Button asChild size="lg" className="bg-[var(--syuura-gold)] hover:bg-yellow-600 text-white rounded-full">
                                <Link href="/ppdb/daftar">Daftar Sekarang</Link>
                            </Button>
                        </div>
                    </div>
                </section>

                {/* SAMBUTAN SECTION */}
                <section className="py-20 container mx-auto px-4">
                    <div className="flex flex-col md:flex-row items-center gap-12">
                        <div className="w-full md:w-1/3">
                            <div className="aspect-square bg-slate-200 rounded-2xl overflow-hidden shadow-lg relative">
                                {content.sambutan.image_url ? (
                                    <img src={content.sambutan.image_url} alt="Kepala Sekolah" className="w-full h-full object-cover" />
                                ) : (
                                    <div className="flex items-center justify-center w-full h-full text-slate-400">
                                        No Photo
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="w-full md:w-2/3">
                            <h2 className="text-3xl font-bold text-[var(--syuura-green)] mb-2">{sambutanTitle}</h2>
                            {content.sambutan.subtitle && (
                                <p className="text-lg font-medium text-slate-600 mb-6">{content.sambutan.subtitle}</p>
                            )}
                            <div className="prose prose-lg text-slate-600 whitespace-pre-line">
                                {sambutanBody}
                            </div>
                        </div>
                    </div>
                </section>

                {/* FEATURES */}
                {content.features.length > 0 && (
                    <DynamicFeatureSection
                        title={`Keunggulan ${unitName}`}
                        features={content.features}
                    />
                )}

                {/* TESTIMONIALS (Optional) */}
                {content.testimonials.length > 0 && (
                    <section className="py-20 bg-[var(--syuura-green-surface)]">
                        <div className="container mx-auto px-4">
                            <h2 className="text-3xl font-bold text-center text-slate-800 mb-12">Kata Mereka</h2>
                            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {content.testimonials.map((item: any, idx: number) => (
                                    <div key={idx} className="bg-white p-6 rounded-xl shadow-sm">
                                        <p className="text-slate-600 italic mb-4">"{item.description}"</p>
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-slate-200 rounded-full overflow-hidden">
                                                {item.image_url && <img src={item.image_url} className="w-full h-full object-cover" />}
                                            </div>
                                            <div>
                                                <p className="font-bold text-sm">{item.title}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>
                )}
            </main>

            <Footer />
        </div>
    );
}
