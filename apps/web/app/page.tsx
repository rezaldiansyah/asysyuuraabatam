import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { UnitSection } from "@/components/home/UnitSection";
import { DynamicFeatureSection } from "@/components/home/DynamicFeatureSection";

const DEFAULT_FEATURES = [
  {
    id: "1",
    icon: "BookOpen", // Lucide Icon Name
    title: "Kurikulum Terpadu",
    description: "Memadukan Kurikulum Nasional (Merdeka) dengan Kurikulum Khas Sekolah Islam Terpadu.",
  },
  {
    id: "2",
    icon: "Heart",
    title: "Bina Pribadi Islami",
    description: "Pembentukan karakter (adab & akhlaq) yang intensif melalui mentoring dan keteladanan.",
  },
  {
    id: "3",
    icon: "Sun",
    title: "Program Tahfidz",
    description: "Target hafalan yang terukur dengan metode yang menyenangkan sesuai jenjang usia.",
  },
  {
    id: "4",
    icon: "Users",
    title: "Pengajar Berkualitas",
    description: "Didukung oleh asatidz/asatidzah yang kompeten, berdedikasi, dan menyayangi anak didik.",
  },
  {
    id: "5",
    icon: "Trophy",
    title: "Ekstrakurikuler",
    description: "Beragam kegiatan penyaluran bakat dan minat siswa (Pramuka, Panahan, Futsal, dll).",
  },
  {
    id: "6",
    icon: "ShieldCheck",
    title: "Lingkungan Aman",
    description: "Lingkungan sekolah yang kondusif, aman, dan nyaman untuk tumbuh kembang anak.",
  },
];

export default async function Home() {
  let heroContent = {
    title: "Mendidik Generasi Qurani",
    body: "Sekolah Islam Terpadu Asy-Syuuraa Batam berkomitmen mencetak pemimpin masa depan yang cerdas, berwawasan global, dan berakhlak mulia.",
    cta_text: "Daftar Sekarang",
    cta_link: "/daftar",
    image_url: ""
  };

  let featuresContent = DEFAULT_FEATURES;

  try {
    const API_URL = "http://localhost:8000";
    // Parallel Fetch
    const [heroRes, featureRes] = await Promise.all([
      fetch(`${API_URL}/public/content/home_hero`, { next: { revalidate: 0 } }),
      fetch(`${API_URL}/public/content/home_features`, { next: { revalidate: 0 } })
    ]);

    if (heroRes.ok) {
      const data = await heroRes.json();
      heroContent = { ...heroContent, ...data };
    }

    if (featureRes.ok) {
      const data = await featureRes.json();
      if (data.content_json) {
        const parsed = JSON.parse(data.content_json);
        if (Array.isArray(parsed) && parsed.length > 0) {
          featuresContent = parsed;
        }
      }
    }

  } catch (e) {
    console.error("Failed to fetch CMS content", e);
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <main className="flex-1">
        {/* HERO SECTION */}
        <section className="relative py-20 lg:py-32 text-center overflow-hidden bg-[var(--syuura-green-surface)]">
          {/* Background Image Overlay if exists */}
          {heroContent.image_url && (
            <div
              className="absolute inset-0 bg-cover bg-center z-0 opacity-20"
              style={{ backgroundImage: `url(${heroContent.image_url})` }}
            />
          )}

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
        <DynamicFeatureSection
          features={featuresContent}
        />
      </main>

      <Footer />
    </div>
  );
}
