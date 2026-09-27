<template>
  <NuxtLayout name="default">
    <div class="min-h-screen bg-slate-50 dark:bg-slate-800">

      <!-- Dynamic LP Sections (if configured) -->
      <template v-if="hasLPConfig">
        <template v-for="section in visibleSections" :key="section.id">

          <!-- Hero Carousel -->
          <section v-if="section.type === 'hero_carousel'" class="relative bg-white dark:bg-slate-900 border-b">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col items-center">
              <div v-if="filteredImages(section.images).length > 0" class="w-full max-w-4xl">
                <Carousel
                  :value="filteredImages(section.images)"
                  :numVisible="1"
                  :numScroll="1"
                  :showNavigators="filteredImages(section.images).length > 1"
                  :showIndicators="filteredImages(section.images).length > 1"
                  circular
                  :autoplayInterval="5000"
                >
                  <template #item="slotProps">
                    <img
                      :src="resolveUrl(slotProps.data)"
                      alt="Poster SPMB"
                      class="w-full rounded-2xl shadow-xl object-cover"
                    />
                  </template>
                </Carousel>
              </div>
              <div v-else class="w-full max-w-4xl aspect-[21/9] bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-xl flex items-center justify-center text-white">
                <h1 class="text-3xl lg:text-4xl font-bold">{{ lpConfig.spmb_label || 'Penerimaan Peserta Didik Baru' }}</h1>
              </div>
            </div>
          </section>

          <!-- Stacked Image -->
          <section v-if="section.type === 'stacked_image' && filteredImages(section.images).length > 0">
            <div :class="section.border_radius !== 'none' ? 'max-w-4xl mx-auto px-4 py-4' : ''">
              <h3 v-if="section.title" class="text-xl lg:text-2xl font-bold text-center text-slate-800 dark:text-white py-4">{{ section.title }}</h3>
              <PpdbStackedImageSection
                :images="filteredImages(section.images).map(resolveUrl)"
                :gap="section.gap"
                :border-radius="section.border_radius"
              />
            </div>
          </section>

          <!-- CTA Buttons -->
          <section v-if="section.type === 'cta_button'" class="bg-white dark:bg-slate-900 border-b">
            <div class="flex flex-col gap-4 w-full sm:max-w-sm mx-auto px-4 py-8">
              <Button size="large" class="w-full justify-center shadow-lg !bg-indigo-600 hover:!bg-indigo-700 !border-none text-white font-bold py-4 text-lg" @click="scrollToForm">
                <i class="pi pi-pencil mr-2 text-xl"></i> {{ section.cta_label || 'Daftar Sekarang' }}
              </Button>
              <Button size="large" class="w-full justify-center shadow-lg !bg-[#25D366] hover:!bg-[#128C7E] !border-none text-white font-bold py-4 text-lg" as="a" :href="waLink" target="_blank">
                <i class="pi pi-whatsapp mr-2 text-xl"></i> {{ section.wa_label || 'Tanya Admin (WA)' }}
              </Button>
            </div>
          </section>

          <!-- Info Text -->
          <section v-if="section.type === 'info_text'" class="bg-white dark:bg-slate-900">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
              <h3 v-if="section.title" class="text-xl lg:text-2xl font-bold text-slate-800 dark:text-white mb-6">{{ section.title }}</h3>
              <div class="prose dark:prose-invert max-w-none whitespace-pre-line text-slate-600 dark:text-slate-300">{{ section.content }}</div>
            </div>
          </section>

          <!-- Timeline -->
          <section v-if="section.type === 'timeline' && section.steps?.length > 0" class="bg-slate-50 dark:bg-slate-800">
            <PpdbTimelineSection :title="section.title" :steps="section.steps" :theme-hex="themeHex" />
          </section>

          <!-- Unit Cards -->
          <section v-if="section.type === 'unit_cards'" class="bg-white dark:bg-slate-900">
            <PpdbUnitCardsSection :title="section.title" :units="section.units" :theme-hex="themeHex" />
          </section>

        </template>
      </template>

      <!-- Fallback: Original Layout (poster carousel + CTA) -->
      <template v-else>
        <section class="relative bg-white dark:bg-slate-900 border-b">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col items-center">
            <div v-if="content.posters && content.posters.length > 0" class="w-full max-w-4xl">
              <Carousel :value="content.posters" :numVisible="1" :numScroll="1" :showNavigators="content.posters.length > 1" :showIndicators="content.posters.length > 1" circular :autoplayInterval="5000">
                <template #item="slotProps">
                  <img :src="resolveUrl(slotProps.data)"
                    alt="Poster PPDB"
                    class="w-full rounded-2xl shadow-xl object-cover"
                  />
                </template>
              </Carousel>
            </div>
            <div v-else-if="content.poster_url" class="w-full max-w-4xl">
               <img :src="resolveUrl(content.poster_url)"
                alt="Poster PPDB"
                class="w-full rounded-2xl shadow-xl mb-8 object-cover" />
            </div>
            <div v-else class="w-full max-w-4xl aspect-[21/9] bg-gradient-to-br from-primary to-secondary rounded-2xl shadow-xl mb-8 flex items-center justify-center text-white">
              <h1 class="text-4xl font-bold">Penerimaan Peserta Didik Baru</h1>
            </div>

            <div class="flex flex-col gap-4 w-full sm:max-w-sm mt-4">
              <Button size="large" class="w-full justify-center shadow-lg !bg-indigo-600 hover:!bg-indigo-700 !border-none text-white font-bold py-4 text-lg" @click="scrollToForm">
                <i class="pi pi-pencil mr-2 text-xl"></i> Daftar Sekarang
              </Button>
              <Button size="large" class="w-full justify-center shadow-lg !bg-[#25D366] hover:!bg-[#128C7E] !border-none text-white font-bold py-4 text-lg" as="a" :href="waLink" target="_blank">
                <i class="pi pi-whatsapp mr-2 text-xl"></i> Tanya Admin (WA)
              </Button>
            </div>
          </div>
        </section>
      </template>

      <!-- Registration Form Wizard (always shown) -->
      <section id="form-section" class="py-16">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-10">
            <h2 class="text-3xl font-bold text-slate-800 dark:text-white">Formulir Pendaftaran</h2>
            <p class="text-slate-500 mt-2">Mohon lengkapi data berikut dengan benar.</p>
          </div>

          <PPDBWizard />
        </div>
      </section>
    </div>
  </NuxtLayout>
</template>

<script setup>
definePageMeta({ layout: false })

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const content = ref({
  posters: [],
  poster_url: '',
  wa_number: '6281234567890'
})

const lpConfig = ref({
  sections: [],
  spmb_label: 'PPDB',
  theme_color: 'indigo',
  wa_number: '6281234567890',
})

const themeColorMap = {
  indigo: '#4F46E5',
  blue: '#2563EB',
  green: '#16A34A',
  teal: '#0D9488',
  purple: '#7C3AED',
  rose: '#E11D48',
}

const hasLPConfig = computed(() => {
  return lpConfig.value.sections && lpConfig.value.sections.length > 0
})

const visibleSections = computed(() => {
  return (lpConfig.value.sections || []).filter(s => s.visible)
})

const themeHex = computed(() => {
  return themeColorMap[lpConfig.value.theme_color] || '#4F46E5'
})

const waLink = computed(() => {
  const num = lpConfig.value.wa_number || content.value.wa_number || '6281234567890'
  const number = num.toString().replace(/\D/g, '')
  const text = encodeURIComponent('Halo Admin, saya ingin bertanya mengenai Pendaftaran Siswa Baru (PPDB).')
  return `https://wa.me/${number}?text=${text}`
})

function resolveUrl(url) {
  if (!url) return ''
  return url.startsWith('http') ? url : `${apiBase}${url}`
}

function filteredImages(images) {
  return (images || []).filter(u => u && u.trim() !== '')
}

function scrollToForm() {
  document.getElementById('form-section')?.scrollIntoView({ behavior: 'smooth' })
}

// Fetch settings from CMS
async function loadContent() {
  try {
    const data = await $fetch(`${apiBase}/public/content/settings_ppdb`)
    if (data && data.content_json) {
      const parsed = JSON.parse(data.content_json)
      content.value = { ...content.value, ...parsed }

      // Load LP config if it exists
      if (parsed.lp_config) {
        lpConfig.value = {
          ...lpConfig.value,
          ...parsed.lp_config,
          wa_number: parsed.wa_number || lpConfig.value.wa_number,
        }
      }
    }
  } catch (e) {
    console.log("PPDB settings not found, using defaults")
  }
}

onMounted(() => {
  loadContent()
})
</script>
