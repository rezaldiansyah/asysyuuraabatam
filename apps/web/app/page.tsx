import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { UnitSection } from "@/components/home/UnitSection";
import { FeatureSection } from "@/components/home/FeatureSection";

export default async function Home() {
  let heroContent = {
    title: "Mendidik Generasi Qurani",
    body: "Sekolah Islam Terpadu Asy-Syuuraa Batam berkomitmen mencetak pemimpin masa depan yang cerdas, berwawasan global, dan berakhlak mulia.",
    cta_text: "Daftar Sekarang",
    cta_link: "/daftar"
  };

  try {
    const API_URL = "http://localhost:8000";
    const res = await fetch(`${API_URL}/public/content/home_hero`, {
      next: { revalidate: 60 }
    });
    if (res.ok) {
      const data = await res.json();
      heroContent = { ...heroContent, ...data };
    }
  } catch (e) {
    console.error("Failed to fetch CMS content", e);
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1">
        {/* HERO SECTION */}
        <section className="bg-[var(--syuura-green-surface)] py-20 lg:py-32 text-center relative overflow-hidden">
          {/* Decorative Circle */}
          <div className="hidden lg:block absolute -top-24 -right-24 w-96 h-96 bg-green-200/20 rounded-full blur-3xl pointer-events-none" />
          <div className="hidden lg:block absolute -bottom-24 -left-24 w-72 h-72 bg-yellow-200/20 rounded-full blur-3xl pointer-events-none" />

          <div className="container mx-auto px-4 relative z-10">
            <h1 className="text-4xl md:text-6xl font-bold text-[var(--syuura-green)] mb-6 tracking-tight">
              {heroContent.title}
            </h1>
            <p className="text-lg md:text-xl text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed whitespace-pre-line">
              {heroContent.body}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button className="bg-[var(--syuura-gold)] text-white px-8 py-3 rounded-full font-bold shadow-lg hover:bg-yellow-600 transition hover:shadow-xl transform hover:-translate-y-0.5">
                {heroContent.cta_text || "Daftar Sekarang"}
              </button>
              <button className="bg-white text-[var(--syuura-green)] border-2 border-[var(--syuura-green)] px-8 py-3 rounded-full font-bold hover:bg-[var(--syuura-green-surface)] transition">
                Lihat Profil
              </button>
            </div>
          </div>
        </section>

        {/* UNIT PENDIDIKAN */}
        <UnitSection />

        {/* KEUNGGULAN */}
        <FeatureSection />
      </main>

      <Footer />
    </div>
  );
}
