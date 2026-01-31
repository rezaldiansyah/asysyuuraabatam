<template>
  <NuxtLayout name="default">
    <div class="min-h-screen">
      <!-- Hero -->
      <section class="relative bg-gradient-to-br from-primary via-primary-dark to-slate-900 py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h1 class="text-4xl lg:text-5xl font-bold mb-4">{{ data.hero.title }}</h1>
          <p class="text-xl opacity-90">{{ data.hero.body }}</p>
        </div>
      </section>

      <!-- Vision & Mission -->
      <section class="py-16 bg-white dark:bg-slate-900">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid lg:grid-cols-2 gap-12">
            <!-- Vision -->
            <div class="bg-gradient-to-br from-primary/10 to-secondary/10 rounded-2xl p-8">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-14 h-14 bg-primary rounded-full flex items-center justify-center">
                  <i class="pi pi-eye text-2xl text-white"></i>
                </div>
                <h2 class="text-2xl font-bold text-slate-800 dark:text-white">Visi</h2>
              </div>
              <p class="text-lg text-slate-700 dark:text-slate-300 leading-relaxed">
                {{ data.visi.body }}
              </p>
            </div>

            <!-- Mission -->
            <div class="bg-gradient-to-br from-secondary/10 to-primary/10 rounded-2xl p-8">
              <div class="flex items-center gap-4 mb-6">
                <div class="w-14 h-14 bg-secondary rounded-full flex items-center justify-center">
                  <i class="pi pi-flag text-2xl text-white"></i>
                </div>
                <h2 class="text-2xl font-bold text-slate-800 dark:text-white">Misi</h2>
              </div>
              <ul class="space-y-3 text-slate-700 dark:text-slate-300">
                <li v-for="(item, index) in data.misi" :key="index" class="flex items-start gap-3">
                  <i class="pi pi-check-circle text-primary mt-1"></i>
                  <span>{{ item.title || item.label || item }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- History -->
      <section class="py-16 bg-slate-50 dark:bg-slate-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-center text-slate-800 dark:text-white mb-12">
            Sejarah Singkat
          </h2>
          <div class="max-w-3xl mx-auto prose prose-lg dark:prose-invert whitespace-pre-line">
            {{ data.history.body }}
          </div>
        </div>
      </section>

      <!-- Stats -->
      <section class="py-16 bg-primary">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center text-white">
            <div>
              <div class="text-4xl font-bold mb-2">500+</div>
              <div class="opacity-80">Siswa Aktif</div>
            </div>
            <div>
              <div class="text-4xl font-bold mb-2">50+</div>
              <div class="opacity-80">Tenaga Pengajar</div>
            </div>
            <div>
              <div class="text-4xl font-bold mb-2">3</div>
              <div class="opacity-80">Unit Pendidikan</div>
            </div>
            <div>
              <div class="text-4xl font-bold mb-2">10+</div>
              <div class="opacity-80">Tahun Pengalaman</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Contact -->
      <section class="py-16 bg-white dark:bg-slate-900">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-8">Hubungi Kami</h2>
          <div class="max-w-lg mx-auto space-y-4 text-slate-600 dark:text-slate-400">
            <p class="flex items-center justify-center gap-3">
              <i class="pi pi-map-marker text-primary"></i>
              Jl. Hang Kesturi, Batam, Kepulauan Riau
            </p>
            <p class="flex items-center justify-center gap-3">
              <i class="pi pi-phone text-primary"></i>
              (0778) 123-4567
            </p>
            <p class="flex items-center justify-center gap-3">
              <i class="pi pi-envelope text-primary"></i>
              info@asy-syuuraa.sch.id
            </p>
          </div>
        </div>
      </section>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const api = useApi()

const data = reactive({
    hero: { title: 'Tentang Kami', body: 'Yayasan Pendidikan Islam Asy-Syuuraa Batam' },
    visi: { title: 'Visi', body: "Mewujudkan generasi Qur'ani yang berakhlak mulia, cerdas, mandiri, dan berwawasan global melalui pendidikan Islam terpadu." },
    misi: [] as any[],
    history: { body: '' }
})

const defaultMisi = [
    "Menyelenggarakan pendidikan Islam yang berkualitas dan terpadu",
    "Membina akhlak dan karakter Islami siswa",
    "Mengembangkan potensi akademik dan non-akademik",
    "Menanamkan kecintaan terhadap Al-Qur'an"
]

onMounted(async () => {
    try {
        const [hero, visimisi, history] = await Promise.all([
            api.get<any>('/public/content/profil_hero').catch(() => ({})),
            api.get<any>('/public/content/profil_visimisi').catch(() => ({})),
            api.get<any>('/public/content/profil_history').catch(() => ({}))
        ])

        if (hero.title) data.hero.title = hero.title
        if (hero.body) data.hero.body = hero.body

        if (visimisi.body) data.visi.body = visimisi.body
        if (visimisi.content_json) data.misi = JSON.parse(visimisi.content_json)
        else data.misi = defaultMisi.map(m => ({ label: m })) // Adapter for legacy/default

        if (history.body) data.history.body = history.body
        else {
             // Default History text if empty
             data.history.body = `Yayasan Asy-Syuuraa didirikan dengan semangat untuk memberikan pendidikan Islam berkualitas bagi masyarakat Batam. Berawal dari sebuah TK Islam kecil, kini telah berkembang menjadi yayasan pendidikan yang menaungi tiga unit pendidikan: RA (Raudhatul Athfal), SDIT (Sekolah Dasar Islam Terpadu), dan SMPIT (Sekolah Menengah Pertama Islam Terpadu).\n\nDengan motto "Mewujudkan Generasi Qur'ani", Yayasan Asy-Syuuraa berkomitmen untuk mencetak lulusan yang tidak hanya unggul dalam akademik, tetapi juga memiliki pemahaman agama yang kuat dan akhlak yang mulia.`
        }

    } catch (e) {
        console.error('Failed to fetch profil content', e)
    }
})
</script>
