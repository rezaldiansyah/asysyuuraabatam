<template>
  <div>
    <!-- Hero Section -->
    <section class="relative bg-gradient-to-br from-primary via-primary-dark to-slate-900 py-24 lg:py-32 overflow-hidden">
      <!-- Background Image Overlay if exists -->
      <div
        v-if="hero.image_url"
        class="absolute inset-0 bg-cover bg-center z-0 opacity-20"
        :style="{ backgroundImage: `url(${hero.image_url})` }"
      />

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <!-- Text Content -->
          <div class="text-white">
            <h1 class="text-4xl lg:text-5xl font-bold leading-tight mb-6">
              {{ hero.title }}
            </h1>
            <p class="text-lg text-slate-200 mb-8 whitespace-pre-line">
              {{ hero.body }}
            </p>
            <div class="flex flex-wrap gap-4">
              <NuxtLink
                :to="hero.cta_link || '/ppdb'"
                class="px-6 py-3 bg-secondary text-white font-semibold rounded-lg hover:bg-secondary-dark transition"
              >
                {{ hero.cta_text || 'Daftar Sekarang' }}
              </NuxtLink>
              <NuxtLink
                to="/profil"
                class="px-6 py-3 border-2 border-white text-white font-semibold rounded-lg hover:bg-white hover:text-primary transition"
              >
                Tentang Kami
              </NuxtLink>
            </div>
          </div>

          <!-- Image Placeholder -->
          <div class="hidden lg:block">
            <div class="w-full h-80 bg-white/10 rounded-2xl backdrop-blur-sm flex items-center justify-center">
              <span class="text-white/50 text-lg">Foto Yayasan</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Units Section -->
    <section class="py-20 bg-white dark:bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">Unit Pendidikan</h2>
          <p class="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Asy-Syuuraa Batam memiliki tiga unit pendidikan Islam terpadu dari tingkat TK hingga SMP.
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <!-- RA -->
          <div class="bg-slate-50 dark:bg-slate-700 rounded-2xl p-8 text-center hover:shadow-xl transition">
            <div class="w-16 h-16 bg-pink-100 dark:bg-pink-900/30 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <span class="text-3xl">🎨</span>
            </div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white mb-2">RA (TK Islam)</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm mb-4">
              Pendidikan anak usia dini dengan kurikulum bermain dan belajar berbasis Islam.
            </p>
            <NuxtLink to="/unit/ra" class="text-primary font-medium hover:underline">
              Selengkapnya →
            </NuxtLink>
          </div>

          <!-- SDIT -->
          <div class="bg-slate-50 dark:bg-slate-700 rounded-2xl p-8 text-center hover:shadow-xl transition">
            <div class="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <span class="text-3xl">📚</span>
            </div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white mb-2">SDIT</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm mb-4">
              Sekolah Dasar Islam Terpadu dengan kurikulum nasional plus tahfidz Al-Quran.
            </p>
            <NuxtLink to="/unit/sdit" class="text-primary font-medium hover:underline">
              Selengkapnya →
            </NuxtLink>
          </div>

          <!-- SMPIT -->
          <div class="bg-slate-50 dark:bg-slate-700 rounded-2xl p-8 text-center hover:shadow-xl transition">
            <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <span class="text-3xl">🎓</span>
            </div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white mb-2">SMPIT</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm mb-4">
              SMP Islam Terpadu dengan boarding program dan kurikulum karakter Islami.
            </p>
            <NuxtLink to="/unit/smpit" class="text-primary font-medium hover:underline">
              Selengkapnya →
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20 bg-slate-50 dark:bg-slate-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">Keunggulan Kami</h2>
        </div>

        <div class="grid md:grid-cols-4 gap-6">
          <div
            v-for="(feature, idx) in features"
            :key="idx"
            class="text-center"
          >
            <div class="w-14 h-14 bg-primary/10 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <span class="text-2xl">{{ iconMap[feature.icon] || '✨' }}</span>
            </div>
            <h3 class="font-bold text-slate-800 dark:text-white">{{ feature.title }}</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400 mt-2">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-16 bg-primary">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-2xl lg:text-3xl font-bold text-white mb-4">
          Pendaftaran Peserta Didik Baru (PPDB) Dibuka!
        </h2>
        <p class="text-slate-200 mb-6">
          Daftarkan putra-putri Anda untuk tahun ajaran baru sekarang.
        </p>
        <NuxtLink
          to="/ppdb"
          class="inline-block px-8 py-3 bg-white text-primary font-bold rounded-lg hover:bg-secondary hover:text-white transition"
        >
          Daftar Sekarang
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const { public: { apiBase } } = useRuntimeConfig()

// Default Data
const defaultHero = {
  title: 'Yayasan Asy-Syuuraa Batam',
  body: 'Mewujudkan generasi Qurani yang berakhlak mulia, cerdas, mandiri, dan berwawasan global melalui pendidikan Islam terpadu.',
  cta_text: 'Daftar PPDB',
  cta_link: '/ppdb',
  image_url: ''
}

const defaultFeatures = [
  { icon: 'BookOpen', title: 'Program Tahfidz', description: 'Target hafalan Al-Quran terintegrasi' },
  { icon: 'Heart', title: 'Pendidikan Karakter', description: 'Akhlak Islami dalam keseharian' },
  { icon: 'Sun', title: 'Fasilitas Modern', description: 'Lab komputer dan multimedia' },
  { icon: 'Users', title: 'Boarding Program', description: 'Asrama untuk SMPIT (opsional)' }
]

// Mapping for dynamic icons (Lucide names to Emojis/Icons for simple rendering)
const iconMap: Record<string, string> = {
  BookOpen: '📖',
  Heart: '❤️',
  Sun: '☀️',
  Users: '👥',
  Trophy: '🏆',
  ShieldCheck: '🛡️',
  Star: '⭐',
  Sparkles: '✨',
  CheckCircle: '✅'
}

// Fetch Data
const { data: pageContent, error } = await useAsyncData('home-content', async () => {
  try {
    const [heroRes, featuresRes] = await Promise.all([
      $fetch<any>(`${apiBase}/public/content/home_hero`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/home_features`).catch(() => null)
    ])

    let features = defaultFeatures
    if (featuresRes && featuresRes.content_json) {
      try {
        const parsed = JSON.parse(featuresRes.content_json)
        if (Array.isArray(parsed) && parsed.length > 0) {
          features = parsed
        }
      } catch (e) {
        console.error('Failed to parse features JSON', e)
      }
    }

    return {
      hero: heroRes || defaultHero,
      features
    }
  } catch (e) {
    console.error('Failed to fetch home content', e)
    return { hero: defaultHero, features: defaultFeatures }
  }
})

// Use computed to safe access
const hero = computed(() => pageContent.value?.hero || defaultHero)
const features = computed(() => pageContent.value?.features || defaultFeatures)

useSeoMeta({
  title: 'Asy-Syuuraa Batam - Sekolah Islam Terpadu',
  description: 'Yayasan Asy-Syuuraa Batam - Pendidikan Islam Terpadu dengan program Tahfidz Al-Quran untuk RA, SDIT, dan SMPIT.',
})
</script>
