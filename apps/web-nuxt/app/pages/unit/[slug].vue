<template>
  <div class="min-h-screen bg-white dark:bg-slate-900">
    <!-- Hero -->
    <section class="relative bg-gradient-to-br py-24 lg:py-32 overflow-hidden" :class="unitTheme.heroGradient">
      <div v-if="hero.image_url" class="absolute inset-0 bg-cover bg-center z-0 opacity-20" :style="{ backgroundImage: `url(${hero.image_url})` }" />
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="text-white">
            <div class="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium mb-6 bg-white/20 backdrop-blur-sm">
              <span class="text-2xl mr-2">{{ unitTheme.emoji }}</span> {{ unitTheme.ageRange }}
            </div>
            <h1 class="text-4xl lg:text-5xl font-bold leading-tight mb-6">{{ hero.title || unitTheme.defaultTitle }}</h1>
            <p class="text-lg text-white/90 mb-8 whitespace-pre-line">{{ hero.body || unitTheme.defaultDesc }}</p>
            <div class="flex flex-wrap gap-4">
              <NuxtLink :to="hero.cta_link || '/ppdb'" class="px-6 py-3 bg-white font-semibold rounded-lg hover:bg-slate-100 transition" :class="unitTheme.ctaTextColor">
                {{ hero.cta_text || 'Daftar Sekarang' }}
              </NuxtLink>
              <NuxtLink to="/unit" class="px-6 py-3 border-2 border-white text-white font-semibold rounded-lg hover:bg-white/10 transition">
                Semua Unit
              </NuxtLink>
            </div>
          </div>
          <div class="hidden lg:block">
            <img v-if="hero.image_url" :src="hero.image_url" :alt="hero.title" class="w-full h-96 object-cover rounded-2xl shadow-2xl" />
            <div v-else class="w-full h-80 bg-white/10 rounded-2xl backdrop-blur-sm flex items-center justify-center border border-white/20">
              <span class="text-8xl">{{ unitTheme.emoji }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Sambutan Kepala Unit -->
    <section v-if="sambutan.title" class="py-20 bg-slate-50 dark:bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="bg-white dark:bg-slate-700 rounded-3xl shadow-lg overflow-hidden border border-slate-100 dark:border-slate-600">
          <div class="grid md:grid-cols-5 gap-0">
            <div class="md:col-span-2 h-64 md:h-auto relative" :class="unitTheme.sambutanBg">
              <img v-if="sambutan.image_url" :src="sambutan.image_url" :alt="sambutan.title" class="w-full h-full object-cover absolute inset-0" />
              <div v-else class="w-full h-full flex items-center justify-center">
                <i class="pi pi-user text-5xl" :class="unitTheme.iconColor"></i>
              </div>
            </div>
            <div class="md:col-span-3 p-8 lg:p-12 flex flex-col justify-center">
              <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-2">{{ sambutan.title }}</h2>
              <p class="font-medium mb-6" :class="unitTheme.subtitleColor">{{ sambutan.subtitle }}</p>
              <div class="text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">{{ sambutan.body }}</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Keunggulan -->
    <section v-if="features.length" class="py-20 bg-white dark:bg-slate-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">Keunggulan {{ unitTheme.shortName }}</h2>
          <p class="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">Mengapa memilih {{ unitTheme.defaultTitle }}?</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="(f, idx) in features" :key="idx" class="text-center p-6 rounded-2xl border border-slate-100 dark:border-slate-700 hover:shadow-lg transition-shadow">
            <div class="w-14 h-14 rounded-xl mx-auto mb-4 flex items-center justify-center" :class="unitTheme.featureBg">
              <span class="text-2xl">{{ iconMap[f.icon] || '✨' }}</span>
            </div>
            <h3 class="font-bold text-slate-800 dark:text-white mb-2">{{ f.title }}</h3>
            <p class="text-sm text-slate-600 dark:text-slate-400">{{ f.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimoni -->
    <section v-if="testimonials.length" class="py-20 bg-slate-50 dark:bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">Apa Kata Mereka?</h2>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="(t, idx) in testimonials" :key="idx" class="bg-white dark:bg-slate-700 rounded-2xl p-6 shadow-md border border-slate-100 dark:border-slate-600">
            <p class="text-slate-600 dark:text-slate-300 italic mb-4 leading-relaxed">"{{ t.description }}"</p>
            <div class="flex items-center gap-3 pt-4 border-t border-slate-100 dark:border-slate-600">
              <div class="w-10 h-10 rounded-full flex items-center justify-center overflow-hidden flex-shrink-0" :class="unitTheme.featureBg">
                <img v-if="t.image" :src="t.image" :alt="t.title" class="w-full h-full object-cover" />
                <span v-else class="font-bold" :class="unitTheme.iconColor">{{ t.title?.charAt(0) }}</span>
              </div>
              <div>
                <p class="font-semibold text-sm text-slate-800 dark:text-white">{{ t.title }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-16" :class="unitTheme.ctaBg">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold text-white mb-4">Tertarik Bergabung di {{ unitTheme.shortName }}?</h2>
        <p class="text-white/90 mb-8 text-lg">Daftarkan putra-putri Anda melalui PPDB Online sekarang</p>
        <NuxtLink to="/ppdb" class="inline-flex items-center px-8 py-4 bg-white font-bold rounded-lg hover:bg-slate-100 transition" :class="unitTheme.ctaTextColor">
          <i class="pi pi-arrow-right mr-2"></i> Daftar PPDB
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

const route = useRoute()
const slug = computed(() => route.params.slug as string) // ra, sdit, smpit

const { public: { apiBase } } = useRuntimeConfig()

// Theme per unit
const themes: Record<string, any> = {
  ra: {
    shortName: 'RA',
    defaultTitle: 'RA (TK Islam) Asy-Syuuraa',
    defaultDesc: 'Raudhatul Athfal menyediakan pendidikan anak usia dini dengan kurikulum bermain dan belajar berbasis Islam.',
    ageRange: 'Usia 4-6 Tahun',
    emoji: '🎨',
    heroGradient: 'from-blue-600 via-blue-700 to-blue-900',
    sambutanBg: 'bg-blue-50 dark:bg-blue-900/30',
    featureBg: 'bg-blue-100 dark:bg-blue-900/30',
    iconColor: 'text-blue-500',
    subtitleColor: 'text-blue-600 dark:text-blue-400',
    ctaBg: 'bg-blue-700',
    ctaTextColor: 'text-blue-700',
  },
  sdit: {
    shortName: 'SDIT',
    defaultTitle: 'SDIT Asy-Syuuraa Batam',
    defaultDesc: 'Sekolah Dasar Islam Terpadu dengan kurikulum nasional plus tahfidz Al-Quran.',
    ageRange: 'Kelas 1-6',
    emoji: '📚',
    heroGradient: 'from-emerald-600 via-emerald-700 to-emerald-900',
    sambutanBg: 'bg-emerald-50 dark:bg-emerald-900/30',
    featureBg: 'bg-emerald-100 dark:bg-emerald-900/30',
    iconColor: 'text-emerald-500',
    subtitleColor: 'text-emerald-600 dark:text-emerald-400',
    ctaBg: 'bg-emerald-700',
    ctaTextColor: 'text-emerald-700',
  },
  smpit: {
    shortName: 'SMPIT',
    defaultTitle: 'SMPIT Asy-Syuuraa Batam',
    defaultDesc: 'SMP Islam Terpadu dengan program boarding untuk pembinaan karakter intensif.',
    ageRange: 'Kelas 7-9',
    emoji: '🎓',
    heroGradient: 'from-purple-600 via-purple-700 to-purple-900',
    sambutanBg: 'bg-purple-50 dark:bg-purple-900/30',
    featureBg: 'bg-purple-100 dark:bg-purple-900/30',
    iconColor: 'text-purple-500',
    subtitleColor: 'text-purple-600 dark:text-purple-400',
    ctaBg: 'bg-purple-700',
    ctaTextColor: 'text-purple-700',
  }
}

const unitTheme = computed(() => themes[slug.value] || themes.sdit)

const iconMap: Record<string, string> = {
  BookOpen: '📖', Heart: '❤️', Sun: '☀️', Users: '👥',
  Trophy: '🏆', ShieldCheck: '🛡️', Star: '⭐', Sparkles: '✨', CheckCircle: '✅'
}

const defaultFeatures = [
  { icon: 'BookOpen', title: 'Kurikulum Terpadu', description: 'Memadukan Kurikulum Nasional dengan Kurikulum Khas Sekolah Islam Terpadu.' },
  { icon: 'Heart', title: 'Bina Pribadi Islami', description: 'Pembentukan karakter melalui mentoring dan keteladanan.' },
  { icon: 'Star', title: 'Program Tahfidz', description: 'Target hafalan Al-Quran terintegrasi dalam kegiatan harian.' },
  { icon: 'Users', title: 'Lingkungan Islami', description: 'Lingkungan belajar yang mendukung tumbuh kembang anak.' },
]

// Fetch data
const { data: pageData } = await useAsyncData(`unit-${slug.value}`, async () => {
  const prefix = slug.value // ra, sdit, smpit
  try {
    const [heroRes, sambutanRes, featuresRes, testimonialsRes] = await Promise.all([
      $fetch<any>(`${apiBase}/public/content/${prefix}_hero`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/${prefix}_sambutan`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/${prefix}_features`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/${prefix}_testimonials`).catch(() => null),
    ])

    let features = defaultFeatures
    if (featuresRes?.content_json) {
      try {
        const parsed = JSON.parse(featuresRes.content_json)
        if (Array.isArray(parsed) && parsed.length > 0) features = parsed
      } catch {}
    }

    let testimonials: any[] = []
    if (testimonialsRes?.content_json) {
      try {
        const parsed = JSON.parse(testimonialsRes.content_json)
        if (Array.isArray(parsed)) testimonials = parsed
      } catch {}
    }

    return {
      hero: heroRes || {},
      sambutan: sambutanRes || {},
      features,
      testimonials
    }
  } catch {
    return { hero: {}, sambutan: {}, features: defaultFeatures, testimonials: [] }
  }
})

const hero = computed(() => pageData.value?.hero || {})
const sambutan = computed(() => pageData.value?.sambutan || {})
const features = computed(() => pageData.value?.features || defaultFeatures)
const testimonials = computed(() => pageData.value?.testimonials || [])

useSeoMeta({
  title: () => `${unitTheme.value.shortName} - Asy-Syuuraa Batam`,
  description: () => unitTheme.value.defaultDesc,
})
</script>
