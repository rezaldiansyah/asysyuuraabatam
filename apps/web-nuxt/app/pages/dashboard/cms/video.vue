<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Galeri Video</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola video YouTube profil sekolah, kegiatan, dan dokumentasi.</p>
      </div>
      <Button label="Tambah Video" icon="pi pi-plus" @click="openDialog()" />
    </div>

    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="video in videos" :key="video.id" class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl overflow-hidden group">
        <!-- Thumbnail -->
        <div class="relative aspect-video bg-slate-100 dark:bg-slate-700 cursor-pointer" @click="previewVideo(video)">
          <img :src="getThumb(video)" :alt="video.title" class="w-full h-full object-cover" />
          <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <div class="w-14 h-14 bg-red-600 rounded-full flex items-center justify-center shadow-lg">
              <i class="pi pi-play-circle text-white text-3xl"></i>
            </div>
          </div>
          <Badge v-if="!video.is_published" value="Draft" severity="secondary" class="absolute top-2 right-2" />
        </div>
        <div class="p-4">
          <h3 class="font-semibold text-slate-800 dark:text-white line-clamp-1">{{ video.title }}</h3>
          <p class="text-xs text-slate-400 mt-1 line-clamp-1">{{ video.youtube_url }}</p>
          <div class="flex gap-2 mt-3">
            <Button icon="pi pi-pencil" text rounded size="small" @click="openDialog(video)" title="Edit" />
            <Button icon="pi pi-external-link" text rounded size="small" severity="info" @click="openYoutube(video.youtube_url)" title="Buka di YouTube" />
            <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="confirmDelete(video)" title="Hapus" />
          </div>
        </div>
      </div>
    </div>

    <div v-if="!videos.length && !loading" class="text-center py-16 text-slate-400">
      <i class="pi pi-youtube text-5xl mb-4 block"></i>
      <p>Belum ada video. Klik "Tambah Video" untuk mulai.</p>
    </div>

    <!-- Form Dialog -->
    <Dialog v-model:visible="dialogVisible" :header="editingItem ? 'Edit Video' : 'Tambah Video'" modal class="w-full max-w-lg">
      <div class="space-y-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Judul Video *</label>
          <InputText v-model="form.title" placeholder="Contoh: Profil Yayasan Asy-Syuuraa Batam" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Link YouTube *</label>
          <InputText v-model="form.youtube_url" placeholder="https://www.youtube.com/watch?v=..." />
          <small class="text-slate-400">Paste link YouTube video lengkap</small>
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Deskripsi (Opsional)</label>
          <Textarea v-model="form.description" rows="2" placeholder="Deskripsi singkat video..." />
        </div>
        <CmsImageUploader v-model="form.thumbnail_url" label="Custom Thumbnail (Opsional)" />
        <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg text-sm text-blue-700 dark:text-blue-400">
          <i class="pi pi-info-circle mr-1"></i>
          Jika thumbnail tidak diupload, sistem akan otomatis menggunakan thumbnail dari YouTube.
        </div>
        <div class="flex items-center gap-3">
          <Checkbox v-model="form.is_published" :binary="true" inputId="vpub" />
          <label for="vpub" class="text-sm">Tampilkan di halaman publik</label>
        </div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text @click="dialogVisible = false" />
        <Button :label="editingItem ? 'Simpan' : 'Tambah'" icon="pi pi-check" :loading="saving" @click="saveVideo" />
      </template>
    </Dialog>

    <!-- Preview Dialog -->
    <Dialog v-model:visible="previewVisible" header="Preview Video" modal class="w-full max-w-3xl">
      <div v-if="previewUrl" class="aspect-video">
        <iframe :src="previewUrl" class="w-full h-full rounded-lg" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
      </div>
    </Dialog>

    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const confirm = useConfirm()

const videos = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const previewVisible = ref(false)
const previewUrl = ref('')
const editingItem = ref<any>(null)

const form = reactive({
  title: '', youtube_url: '', thumbnail_url: '', description: '', is_published: true
})

onMounted(() => fetchData())

function extractYoutubeId(url: string): string {
  if (!url) return ''
  const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([^&?\s]+)/)
  return match ? match[1] : ''
}

function getThumb(video: any): string {
  if (video.thumbnail_url) return video.thumbnail_url
  const id = extractYoutubeId(video.youtube_url)
  return id ? `https://img.youtube.com/vi/${id}/hqdefault.jpg` : ''
}

function openYoutube(url: string) { window.open(url, '_blank') }

function previewVideo(video: any) {
  const id = extractYoutubeId(video.youtube_url)
  if (id) {
    previewUrl.value = `https://www.youtube.com/embed/${id}?autoplay=1`
    previewVisible.value = true
  } else {
    openYoutube(video.youtube_url)
  }
}

async function fetchData() {
  loading.value = true
  try { videos.value = await api.get('/marketing/videos') }
  catch { toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data', life: 3000 }) }
  finally { loading.value = false }
}

function openDialog(item: any = null) {
  editingItem.value = item
  if (item) {
    Object.assign(form, { title: item.title, youtube_url: item.youtube_url, thumbnail_url: item.thumbnail_url || '', description: item.description || '', is_published: item.is_published })
  } else {
    Object.assign(form, { title: '', youtube_url: '', thumbnail_url: '', description: '', is_published: true })
  }
  dialogVisible.value = true
}

async function saveVideo() {
  if (!form.title || !form.youtube_url) { toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Judul dan link YouTube harus diisi', life: 3000 }); return }
  saving.value = true
  try {
    if (editingItem.value) {
      await api.put(`/marketing/videos/${editingItem.value.id}`, { ...form })
    } else {
      await api.post('/marketing/videos', { ...form })
    }
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Video berhasil disimpan', life: 3000 })
    dialogVisible.value = false
    fetchData()
  } catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan video', life: 3000 }) }
  finally { saving.value = false }
}

function confirmDelete(item: any) {
  confirm.require({
    message: `Hapus video "${item.title}"?`, header: 'Konfirmasi', icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try { await api.delete(`/marketing/videos/${item.id}`); fetchData(); toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Video dihapus', life: 3000 }) }
      catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus', life: 3000 }) }
    }
  })
}
</script>
