<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Pengaturan PPDB</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola informasi publik, poster, dan kontak pendaftaran.</p>
      </div>
    </div>

    <!-- Main Form -->
    <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-lg p-6">
      <div class="space-y-6 max-w-3xl">
        <div class="flex flex-col gap-2">
          <CmsImageUploader 
            v-model="ppdbSettings.poster_url" 
            label="Poster Utama PPDB" 
            placeholder="Upload Poster/Brosur PPDB" 
          />
          <p class="text-sm text-slate-500 mt-1">Gunakan gambar resolusi tinggi, orientasi landscape atau banner.</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium">Nomor WhatsApp Admin PPDB</label>
          <InputText v-model="ppdbSettings.wa_number" placeholder="Contoh: 6281234567890" />
          <p class="text-sm text-slate-500">Awali dengan 62 tanpa spasi atau strip.</p>
        </div>

        <div class="pt-4 border-t">
          <Button label="Simpan Pengaturan" icon="pi pi-save" :loading="loading" @click="saveSettings" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useToast } from 'primevue/usetoast'

definePageMeta({
  layout: 'dashboard'
})

const toast = useToast()
const config = useRuntimeConfig()
const authStore = useAuthStore()

const loading = ref(false)
const ppdbSettings = ref({
  poster_url: '',
  wa_number: '6281234567890'
})

// Load existing
async function loadSettings() {
  try {
    const data = await $fetch(`${config.public.apiBase}/public/content/settings_ppdb`)
    if (data && data.content) {
      const parsed = JSON.parse(data.content)
      ppdbSettings.value = { ...ppdbSettings.value, ...parsed }
    }
  } catch (e) {
    // If 404, just use default
  }
}

async function saveSettings() {
  loading.value = true
  try {
    await $fetch(`${config.public.apiBase}/cms/content/settings_ppdb`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${authStore.token}`
      },
      body: {
        section_key: 'settings_ppdb',
        content_json: JSON.stringify(ppdbSettings.value)
      }
    })
    toast.add({ severity: 'success', summary: 'Tersimpan', detail: 'Pengaturan PPDB berhasil diperbarui', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Terjadi kesalahan saat menyimpan', life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>
