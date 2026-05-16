<template>
  <NuxtLayout name="default">
    <div class="min-h-screen bg-slate-50 dark:bg-slate-800">
      
      <!-- CMS Poster / Hero -->
      <section class="relative bg-white dark:bg-slate-900 border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col items-center">
          <img v-if="content.poster_url" :src="`${config.public.apiBase}${content.poster_url}`" alt="Poster PPDB" class="w-full max-w-4xl rounded-2xl shadow-xl mb-8 object-cover" />
          <div v-else class="w-full max-w-4xl aspect-[21/9] bg-gradient-to-br from-primary to-secondary rounded-2xl shadow-xl mb-8 flex items-center justify-center text-white">
            <h1 class="text-4xl font-bold">Penerimaan Peserta Didik Baru</h1>
          </div>
          
          <div class="flex flex-col gap-4 w-full sm:max-w-sm mt-4">
            <Button size="large" class="w-full justify-center shadow-lg bg-blue-600 hover:bg-blue-700 border-none text-white font-bold py-4 text-lg" @click="scrollToForm">
              <i class="pi pi-pencil mr-2 text-xl"></i> Daftar Sekarang
            </Button>
            <Button size="large" class="w-full justify-center shadow-lg bg-green-500 hover:bg-green-600 border-none text-white font-bold py-4 text-lg" as="a" :href="waLink" target="_blank">
              <i class="pi pi-whatsapp mr-2 text-xl"></i> Tanya Admin (WA)
            </Button>
          </div>
        </div>
      </section>

      <!-- Registration Form Wizard -->
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
const content = ref({
  poster_url: '',
  wa_number: '6281234567890'
})

// Fetch settings from CMS
try {
  const data = await $fetch(`${config.public.apiBase}/public/content/settings_ppdb`)
  if (data && data.content_json) {
    const parsed = JSON.parse(data.content_json)
    content.value = { ...content.value, ...parsed }
  }
} catch (e) {
  console.log("PPDB settings not found, using defaults")
}

const waLink = computed(() => {
  const number = content.value.wa_number.replace(/\D/g, '')
  const text = encodeURIComponent('Halo Admin, saya ingin bertanya mengenai Pendaftaran Siswa Baru (PPDB).')
  return `https://wa.me/${number}?text=${text}`
})

function scrollToForm() {
  document.getElementById('form-section')?.scrollIntoView({ behavior: 'smooth' })
}
</script>
