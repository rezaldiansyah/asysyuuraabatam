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
        <div class="flex flex-col gap-4">
          <label class="font-bold text-lg text-slate-800 dark:text-white">Daftar Poster PPDB</label>
          <p class="text-sm text-slate-500 -mt-2">Anda bisa mengupload lebih dari satu poster. Poster pertama akan menjadi poster utama.</p>
          
          <div v-for="(poster, index) in ppdbSettings.posters" :key="index" class="p-4 border rounded-xl bg-slate-50 dark:bg-slate-800/50 space-y-3 relative group">
            <div class="flex justify-between items-center">
              <span class="text-sm font-semibold">Poster #{{ index + 1 }}</span>
              <Button v-if="ppdbSettings.posters.length > 1" icon="pi pi-trash" severity="danger" text rounded size="small" @click="removePoster(index)" />
            </div>
            
            <CmsImageUploader 
              v-model="ppdbSettings.posters[index]" 
              :label="index === 0 ? 'Poster Utama (Muncul di paling atas)' : `Poster Tambahan #${index}`" 
              placeholder="Upload Poster/Brosur PPDB" 
            />
          </div>

          <Button label="Tambah Poster Baru" icon="pi pi-plus" outlined severity="secondary" class="w-full" @click="addPoster" />

          <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800">
            <h5 class="text-blue-800 dark:text-blue-300 font-bold text-sm mb-2"><i class="pi pi-info-circle mr-1"></i> Rekomendasi Gambar:</h5>
            <ul class="text-xs text-blue-700 dark:text-blue-400 space-y-1 list-disc ml-4">
              <li><strong>Dimensi:</strong> Gunakan rasio 16:9 (misal 1920x1080px) untuk banner lebar, atau 1:1 (1080x1080px) untuk brosur.</li>
              <li><strong>Ukuran File:</strong> Usahakan di bawah 1MB per gambar agar halaman pendaftaran tidak lambat dibuka.</li>
              <li><strong>Format:</strong> Gunakan .WEBP atau .JPG untuk kompresi terbaik.</li>
            </ul>
          </div>
        </div>

        <div class="flex flex-col gap-2 pt-4">
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
const api = useApi()

const loading = ref(false)
const ppdbSettings = ref({
  posters: [''],
  wa_number: '6281234567890'
})

function addPoster() {
  ppdbSettings.value.posters.push('')
}

function removePoster(index: number) {
  ppdbSettings.value.posters.splice(index, 1)
}

// Load existing
async function loadSettings() {
  try {
    const data = await api.get('/public/content/settings_ppdb')
    if (data && data.content_json) {
      const parsed = JSON.parse(data.content_json)
      // Migration: if old data has poster_url, convert to posters array
      if (parsed.poster_url && !parsed.posters) {
        parsed.posters = [parsed.poster_url]
        delete parsed.poster_url
      }
      ppdbSettings.value = { ...ppdbSettings.value, ...parsed }
    }
  } catch (e) {
    // If 404, just use default
  }
}

async function saveSettings() {
  loading.value = true
  try {
    await api.put('/cms/content/settings_ppdb', {
      content_json: JSON.stringify(ppdbSettings.value)
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
