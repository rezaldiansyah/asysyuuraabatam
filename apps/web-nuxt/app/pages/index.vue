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

          <!-- Image -->
          <div class="hidden lg:block">
            <img v-if="hero.image_url" :src="hero.image_url" alt="Hero Image" class="w-full h-96 object-cover rounded-2xl shadow-2xl" />
            <div v-else class="w-full h-80 bg-white/10 rounded-2xl backdrop-blur-sm flex items-center justify-center border border-white/20">
              <span class="text-white/50 text-lg">Foto Yayasan</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Sambutan Section -->
    <section v-if="sambutan.title" class="py-20 bg-slate-50 dark:bg-slate-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-lg overflow-hidden border border-slate-100 dark:border-slate-700">
          <div class="grid md:grid-cols-5 gap-0">
            <!-- Foto Pimpinan -->
            <div class="md:col-span-2 h-64 md:h-auto bg-slate-100 dark:bg-slate-700 relative">
              <img v-if="sambutan.image_url" :src="sambutan.image_url" :alt="sambutan.title" class="w-full h-full object-cover absolute inset-0" />
              <div v-else class="w-full h-full flex items-center justify-center text-slate-400">
                <i class="pi pi-user text-5xl"></i>
              </div>
            </div>
            <!-- Teks Sambutan -->
            <div class="md:col-span-3 p-8 lg:p-12 flex flex-col justify-center">
              <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-2">{{ sambutan.title }}</h2>
              <p class="text-primary font-medium mb-6">{{ sambutan.subtitle }}</p>
              <div class="text-slate-600 dark:text-slate-400 leading-relaxed whitespace-pre-line space-y-4">
                {{ sambutan.body }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Units Section -->
    <section class="py-20 bg-white dark:bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">{{ unitsSection.title }}</h2>
          <p class="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            {{ unitsSection.body }}
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8">
          <div
            v-for="(unit, idx) in unitCards"
            :key="idx"
            class="bg-slate-50 dark:bg-slate-700 rounded-2xl p-8 text-center hover:shadow-xl transition"
          >
            <div class="w-16 h-16 rounded-xl mx-auto mb-4 flex items-center justify-center"
              :class="unitColors[idx % unitColors.length]"
            >
              <span class="text-3xl">{{ unit.icon || unitIcons[idx % unitIcons.length] }}</span>
            </div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white mb-2">{{ unit.title }}</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm mb-4">
              {{ unit.description }}
            </p>
            <NuxtLink v-if="unit.link" :to="unit.link" class="text-primary font-medium hover:underline">
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

    <!-- Teacher of the Month -->
    <section v-if="teacherOfMonth" class="py-16 bg-white dark:bg-slate-800">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-8">
          <span class="text-amber-500 text-sm font-bold uppercase tracking-wider">⭐ Apresiasi</span>
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mt-2">Guru Terbaik Bulan Ini</h2>
        </div>
        <div class="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-2xl p-8 border border-amber-200 dark:border-amber-800 shadow-lg">
          <div class="flex flex-col md:flex-row items-center gap-8 text-center md:text-left">
            <div class="w-32 h-32 rounded-full overflow-hidden shadow-xl border-4 border-amber-300 flex-shrink-0">
              <img v-if="teacherOfMonth.photo_url" :src="teacherOfMonth.photo_url" :alt="teacherOfMonth.name" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full bg-amber-100 flex items-center justify-center text-amber-400 text-4xl font-bold">{{ teacherOfMonth.name?.charAt(0) }}</div>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-slate-800 dark:text-white">{{ teacherOfMonth.name }}</h3>
              <p class="text-amber-600 dark:text-amber-400 font-medium mt-1">{{ teacherOfMonth.title }}</p>
              <p v-if="teacherOfMonth.quote" class="text-slate-600 dark:text-slate-400 italic mt-4 text-lg">"{{ teacherOfMonth.quote }}"</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section v-if="testimonials.length" class="py-20 bg-slate-50 dark:bg-slate-900">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">Apa Kata Mereka?</h2>
          <p class="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">Testimoni dari orang tua murid dan alumni Asy-Syuuraa Batam</p>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div v-for="t in testimonials" :key="t.id" class="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-md border border-slate-100 dark:border-slate-700 hover:shadow-lg transition-shadow">
            <div class="flex gap-0.5 mb-4">
              <i v-for="s in 5" :key="s" class="pi pi-star-fill text-sm" :class="s <= t.rating ? 'text-yellow-400' : 'text-slate-200 dark:text-slate-600'"></i>
            </div>
            <p class="text-slate-600 dark:text-slate-300 italic mb-6 leading-relaxed">"{{ t.content }}"</p>
            <div class="flex items-center gap-3 pt-4 border-t border-slate-100 dark:border-slate-700">
              <div class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center overflow-hidden flex-shrink-0">
                <img v-if="t.photo_url" :src="t.photo_url" :alt="t.name" class="w-full h-full object-cover" />
                <span v-else class="text-primary font-bold">{{ t.name?.charAt(0) }}</span>
              </div>
              <div>
                <p class="font-semibold text-sm text-slate-800 dark:text-white">{{ t.name }}</p>
                <p class="text-xs text-slate-400">{{ t.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Video Gallery -->
    <section v-if="videoGallery.length" class="py-20 bg-white dark:bg-slate-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">Video Profil</h2>
          <p class="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">Kenali lebih dekat Yayasan Asy-Syuuraa Batam melalui video</p>
        </div>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div v-for="v in videoGallery" :key="v.id" class="group cursor-pointer" @click="playVideo(v)">
            <div class="relative aspect-video rounded-xl overflow-hidden shadow-md">
              <img :src="getVideoThumb(v)" :alt="v.title" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              <div class="absolute inset-0 bg-black/30 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                <div class="w-16 h-16 bg-red-600 rounded-full flex items-center justify-center shadow-xl group-hover:scale-110 transition-transform">
                  <i class="pi pi-play text-white text-2xl ml-1"></i>
                </div>
              </div>
            </div>
            <h3 class="font-semibold text-slate-800 dark:text-white mt-3">{{ v.title }}</h3>
          </div>
        </div>
      </div>
    </section>

    <!-- Video Player Dialog -->
    <Dialog v-model:visible="videoPlayerVisible" header="" modal class="w-full max-w-4xl" :closable="true">
      <div v-if="activeVideoEmbed" class="aspect-video">
        <iframe :src="activeVideoEmbed" class="w-full h-full rounded-lg" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div>
    </Dialog>

    <!-- CTA / PPDB Section -->
    <section class="py-16 bg-primary">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-2xl lg:text-3xl font-bold text-white mb-4">
          {{ ppdb.title }}
        </h2>
        <p class="text-slate-200 mb-6">
          {{ ppdb.body }}
        </p>
        <NuxtLink
          :to="ppdb.cta_link || '/ppdb'"
          class="inline-block px-8 py-3 bg-white text-primary font-bold rounded-lg hover:bg-secondary hover:text-white transition"
        >
          {{ ppdb.cta_text || 'Daftar Sekarang' }}
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

const defaultUnitsSection = {
  title: 'Unit Pendidikan',
  body: 'Asy-Syuuraa Batam memiliki tiga unit pendidikan Islam terpadu dari tingkat TK hingga SMP.',
}

const defaultSambutan = {
  title: '',
  subtitle: '',
  body: '',
  image_url: ''
}

const defaultUnitCards = [
  { icon: '🎨', title: 'RA (TK Islam)', description: 'Pendidikan anak usia dini dengan kurikulum bermain dan belajar berbasis Islam.', link: '/unit/ra' },
  { icon: '📚', title: 'SDIT', description: 'Sekolah Dasar Islam Terpadu dengan kurikulum nasional plus tahfidz Al-Quran.', link: '/unit/sdit' },
  { icon: '🎓', title: 'SMPIT', description: 'SMP Islam Terpadu dengan boarding program dan kurikulum karakter Islami.', link: '/unit/smpit' }
]

const defaultFeatures = [
  { icon: 'BookOpen', title: 'Program Tahfidz', description: 'Target hafalan Al-Quran terintegrasi' },
  { icon: 'Heart', title: 'Pendidikan Karakter', description: 'Akhlak Islami dalam keseharian' },
  { icon: 'Sun', title: 'Fasilitas Modern', description: 'Lab komputer dan multimedia' },
  { icon: 'Users', title: 'Boarding Program', description: 'Asrama untuk SMPIT (opsional)' }
]

const defaultPpdb = {
  title: 'Pendaftaran Peserta Didik Baru (PPDB) Dibuka!',
  body: 'Daftarkan putra-putri Anda untuk tahun ajaran baru sekarang.',
  cta_text: 'Daftar Sekarang',
  cta_link: '/ppdb'
}

// Unit styling
const unitColors = [
  'bg-pink-100 dark:bg-pink-900/30',
  'bg-blue-100 dark:bg-blue-900/30',
  'bg-green-100 dark:bg-green-900/30'
]
const unitIcons = ['🎨', '📚', '🎓']

// Mapping for dynamic icons
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
const { data: pageContent } = await useAsyncData('home-content', async () => {
  try {
    const [heroRes, featuresRes, unitsRes, ppdbRes, sambutanRes, testimonialsRes, teacherRes, videosRes] = await Promise.all([
      $fetch<any>(`${apiBase}/public/content/home_hero`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/home_features`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/home_units`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/home_ppdb`).catch(() => null),
      $fetch<any>(`${apiBase}/public/content/home_sambutan`).catch(() => null),
      $fetch<any[]>(`${apiBase}/marketing/testimonials?published_only=true`).catch(() => []),
      $fetch<any>(`${apiBase}/marketing/teacher-of-month/active`).catch(() => null),
      $fetch<any[]>(`${apiBase}/marketing/videos?published_only=true`).catch(() => [])
    ])

    // Parse features
    let features = defaultFeatures
    if (featuresRes && featuresRes.content_json) {
      try {
        const parsed = JSON.parse(featuresRes.content_json)
        if (Array.isArray(parsed) && parsed.length > 0) features = parsed
      } catch (e) { console.error('Failed to parse features JSON', e) }
    }

    // Parse unit cards
    let unitCards = defaultUnitCards
    if (unitsRes && unitsRes.content_json) {
      try {
        const parsed = JSON.parse(unitsRes.content_json)
        if (Array.isArray(parsed) && parsed.length > 0) unitCards = parsed
      } catch (e) { console.error('Failed to parse units JSON', e) }
    }

    return {
      hero: heroRes || defaultHero,
      features,
      unitsSection: {
        title: unitsRes?.title || defaultUnitsSection.title,
        body: unitsRes?.body || defaultUnitsSection.body,
      },
      unitCards,
      ppdb: ppdbRes || defaultPpdb,
      sambutan: sambutanRes || defaultSambutan,
      testimonials: testimonialsRes || [],
      teacherOfMonth: teacherRes,
      videoGallery: videosRes || []
    }
  } catch (e) {
    console.error('Failed to fetch home content', e)
    return { hero: defaultHero, features: defaultFeatures, unitsSection: defaultUnitsSection, unitCards: defaultUnitCards, ppdb: defaultPpdb, sambutan: defaultSambutan, testimonials: [], teacherOfMonth: null, videoGallery: [] }
  }
})

// Use computed for safe access
const hero = computed(() => pageContent.value?.hero || defaultHero)
const features = computed(() => pageContent.value?.features || defaultFeatures)
const unitsSection = computed(() => pageContent.value?.unitsSection || defaultUnitsSection)
const unitCards = computed(() => pageContent.value?.unitCards || defaultUnitCards)
const ppdb = computed(() => pageContent.value?.ppdb || defaultPpdb)
const sambutan = computed(() => pageContent.value?.sambutan || defaultSambutan)
const testimonials = computed(() => pageContent.value?.testimonials || [])
const teacherOfMonth = computed(() => pageContent.value?.teacherOfMonth || null)
const videoGallery = computed(() => pageContent.value?.videoGallery || [])

// Video helpers
const videoPlayerVisible = ref(false)
const activeVideoEmbed = ref('')

function extractYoutubeId(url: string): string {
  if (!url) return ''
  const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([^&?\s]+)/)
  return match ? match[1] : ''
}

function getVideoThumb(video: any): string {
  if (video.thumbnail_url) return video.thumbnail_url
  const id = extractYoutubeId(video.youtube_url)
  return id ? `https://img.youtube.com/vi/${id}/hqdefault.jpg` : ''
}

function playVideo(video: any) {
  const id = extractYoutubeId(video.youtube_url)
  if (id) {
    activeVideoEmbed.value = `https://www.youtube.com/embed/${id}?autoplay=1`
    videoPlayerVisible.value = true
  } else {
    window.open(video.youtube_url, '_blank')
  }
}

useSeoMeta({
  title: 'Asy-Syuuraa Batam - Sekolah Islam Terpadu',
  description: 'Yayasan Asy-Syuuraa Batam - Pendidikan Islam Terpadu dengan program Tahfidz Al-Quran untuk RA, SDIT, dan SMPIT.',
})
</script>
