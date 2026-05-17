<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Identitas & Kontak Sekolah</h1>
      <p class="text-slate-500 dark:text-slate-400">Kelola informasi kontak dan profil singkat untuk footer website.</p>
    </div>

    <div class="card space-y-4">
      <div class="flex flex-col gap-2">
        <label class="font-medium">Tentang Kami (Footer)</label>
        <Textarea v-model="form.about" rows="3" placeholder="Sekolah Islam Terpadu yang..." />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Alamat</label>
          <InputText v-model="form.address" placeholder="Batam, Kepulauan Riau" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">No. Telepon</label>
          <InputText v-model="form.phone" placeholder="(0778) xxx-xxxx" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Email</label>
          <InputText v-model="form.email" placeholder="info@asy-syuuraa.sch.id" />
        </div>
      </div>

      <h3 class="font-bold text-lg mt-6 mb-2">Media Sosial</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Link Facebook</label>
          <InputText v-model="form.facebook" placeholder="https://facebook.com/..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Link Instagram</label>
          <InputText v-model="form.instagram" placeholder="https://instagram.com/..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Link YouTube</label>
          <InputText v-model="form.youtube" placeholder="https://youtube.com/@..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Link TikTok</label>
          <InputText v-model="form.tiktok" placeholder="https://tiktok.com/@..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">No. WhatsApp (format: 628xxx)</label>
          <InputText v-model="form.whatsapp" placeholder="628123456789" />
        </div>
      </div>

      <div class="pt-4">
        <Button label="Simpan Pengaturan" icon="pi pi-save" :loading="loading" @click="saveData" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const loading = ref(false)

const form = reactive({
  about: '',
  address: '',
  phone: '',
  email: '',
  instagram: '',
  facebook: '',
  youtube: '',
  tiktok: '',
  whatsapp: ''
})

async function fetchData() {
  try {
    const res = await api.get<any>('/public/content/settings_footer')
    if (res && res.content_json) {
      const data = JSON.parse(res.content_json)
      Object.assign(form, data)
    }
  } catch (e: any) {
    // 404 is expected if settings haven't been saved yet
    if (e?.statusCode !== 404 && e?.status !== 404) {
      console.error('Failed to load settings', e)
    }
  }
}

async function saveData() {
  loading.value = true
  try {
    await api.put('/cms/content/settings_footer', {
      title: 'Pengaturan Footer',
      content_json: JSON.stringify(form)
    })
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pengaturan kontak berhasil disimpan', life: 3000 })
  } catch (e) {
    console.error('Failed to save settings', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan pengaturan', life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
