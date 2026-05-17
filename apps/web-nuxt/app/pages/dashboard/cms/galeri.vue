<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Galeri Foto</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola album foto kegiatan & prestasi siswa.</p>
      </div>
      <Button label="Buat Album Baru" icon="pi pi-plus" @click="openAlbumDialog()" />
    </div>

    <!-- Category Filter -->
    <div class="flex gap-2">
      <Button :label="'Semua (' + albums.length + ')'" :outlined="filter !== 'all'" size="small" @click="filter = 'all'" />
      <Button :label="'Kegiatan (' + albums.filter(a => a.category === 'kegiatan').length + ')'" :outlined="filter !== 'kegiatan'" size="small" severity="info" @click="filter = 'kegiatan'" />
      <Button :label="'Prestasi (' + albums.filter(a => a.category === 'prestasi').length + ')'" :outlined="filter !== 'prestasi'" size="small" severity="warning" @click="filter = 'prestasi'" />
    </div>

    <!-- Albums Grid -->
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="album in filteredAlbums" :key="album.id" 
        class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group"
        @click="openAlbumDetail(album)"
      >
        <div class="relative h-48 bg-slate-100 dark:bg-slate-700 overflow-hidden">
          <img v-if="album.cover_url" :src="album.cover_url" :alt="album.title" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
          <div v-else class="w-full h-full flex items-center justify-center text-slate-300">
            <i class="pi pi-images text-5xl"></i>
          </div>
          <Badge :value="album.category === 'kegiatan' ? 'Kegiatan' : 'Prestasi'" :severity="album.category === 'kegiatan' ? 'info' : 'warning'" class="absolute top-3 left-3" />
          <Badge :value="album.photo_count + ' foto'" severity="secondary" class="absolute top-3 right-3" />
        </div>
        <div class="p-4">
          <h3 class="font-semibold text-slate-800 dark:text-white">{{ album.title }}</h3>
          <p class="text-sm text-slate-400 line-clamp-2">{{ album.description || 'Tidak ada deskripsi' }}</p>
          <div class="flex gap-2 mt-3" @click.stop>
            <Button icon="pi pi-pencil" text rounded size="small" @click="openAlbumDialog(album)" title="Edit" />
            <Button icon="pi pi-images" text rounded size="small" severity="info" @click="openAlbumDetail(album)" title="Kelola Foto" />
            <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="confirmDeleteAlbum(album)" title="Hapus" />
          </div>
        </div>
      </div>
    </div>

    <div v-if="!albums.length && !loading" class="text-center py-16 text-slate-400">
      <i class="pi pi-images text-5xl mb-4 block"></i>
      <p>Belum ada album. Klik "Buat Album Baru" untuk mulai.</p>
    </div>

    <!-- Album Form Dialog -->
    <Dialog v-model:visible="albumDialogVisible" :header="editingAlbum ? 'Edit Album' : 'Buat Album Baru'" modal class="w-full max-w-lg">
      <div class="space-y-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Judul Album *</label>
          <InputText v-model="albumForm.title" placeholder="Contoh: Classmeeting Semester 2" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Deskripsi</label>
          <Textarea v-model="albumForm.description" rows="3" placeholder="Deskripsi singkat album..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Kategori *</label>
          <div class="flex gap-3">
            <div class="flex items-center gap-2">
              <RadioButton v-model="albumForm.category" inputId="cat1" value="kegiatan" />
              <label for="cat1">Kegiatan</label>
            </div>
            <div class="flex items-center gap-2">
              <RadioButton v-model="albumForm.category" inputId="cat2" value="prestasi" />
              <label for="cat2">Prestasi</label>
            </div>
          </div>
        </div>
        <CmsImageUploader v-model="albumForm.cover_url" label="Cover Album" />
        <div class="flex items-center gap-3">
          <Checkbox v-model="albumForm.is_published" :binary="true" inputId="pub2" />
          <label for="pub2" class="text-sm">Tampilkan di halaman publik</label>
        </div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text @click="albumDialogVisible = false" />
        <Button :label="editingAlbum ? 'Simpan' : 'Buat'" icon="pi pi-check" :loading="saving" @click="saveAlbum" />
      </template>
    </Dialog>

    <!-- Photo Manager Dialog -->
    <Dialog v-model:visible="photoDialogVisible" :header="'Foto: ' + (selectedAlbum?.title || '')" modal class="w-full max-w-3xl">
      <div class="space-y-4">
        <CmsImageUploader v-model="newPhotoUrl" label="Upload Foto Baru" />
        <div class="flex gap-2">
          <InputText v-model="newPhotoCaption" placeholder="Caption (opsional)" class="flex-1" />
          <Button label="Tambah" icon="pi pi-plus" :disabled="!newPhotoUrl" @click="addPhoto" :loading="saving" />
        </div>

        <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4">
          <div v-for="photo in albumPhotos" :key="photo.id" class="relative group rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700">
            <img :src="photo.image_url" :alt="photo.caption" class="w-full h-32 object-cover" />
            <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
              <p class="text-xs text-white truncate">{{ photo.caption || 'Tanpa caption' }}</p>
            </div>
            <button @click="deletePhoto(photo)" class="absolute top-2 right-2 w-7 h-7 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <i class="pi pi-times text-xs"></i>
            </button>
          </div>
        </div>
        <p v-if="!albumPhotos.length" class="text-center text-slate-400 py-8">Belum ada foto di album ini.</p>
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

const albums = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const filter = ref('all')

// Album form
const albumDialogVisible = ref(false)
const editingAlbum = ref<any>(null)
const albumForm = reactive({ title: '', description: '', category: 'kegiatan', cover_url: '', is_published: true })

// Photo manager
const photoDialogVisible = ref(false)
const selectedAlbum = ref<any>(null)
const albumPhotos = ref<any[]>([])
const newPhotoUrl = ref('')
const newPhotoCaption = ref('')

const filteredAlbums = computed(() => {
  if (filter.value === 'all') return albums.value
  return albums.value.filter(a => a.category === filter.value)
})

onMounted(() => fetchAlbums())

async function fetchAlbums() {
  loading.value = true
  try { albums.value = await api.get('/marketing/gallery/albums') }
  catch { toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data', life: 3000 }) }
  finally { loading.value = false }
}

function openAlbumDialog(album: any = null) {
  editingAlbum.value = album
  if (album) {
    Object.assign(albumForm, { title: album.title, description: album.description || '', category: album.category, cover_url: album.cover_url || '', is_published: album.is_published })
  } else {
    Object.assign(albumForm, { title: '', description: '', category: 'kegiatan', cover_url: '', is_published: true })
  }
  albumDialogVisible.value = true
}

async function saveAlbum() {
  if (!albumForm.title) { toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Judul album harus diisi', life: 3000 }); return }
  saving.value = true
  try {
    if (editingAlbum.value) {
      await api.put(`/marketing/gallery/albums/${editingAlbum.value.id}`, { ...albumForm })
    } else {
      await api.post('/marketing/gallery/albums', { ...albumForm })
    }
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Album berhasil disimpan', life: 3000 })
    albumDialogVisible.value = false
    fetchAlbums()
  } catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan album', life: 3000 }) }
  finally { saving.value = false }
}

async function openAlbumDetail(album: any) {
  selectedAlbum.value = album
  try {
    const data = await api.get(`/marketing/gallery/albums/${album.id}`)
    albumPhotos.value = data.photos || []
    photoDialogVisible.value = true
  } catch { toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat foto', life: 3000 }) }
}

async function addPhoto() {
  if (!newPhotoUrl.value || !selectedAlbum.value) return
  saving.value = true
  try {
    await api.post(`/marketing/gallery/albums/${selectedAlbum.value.id}/photos`, {
      photos: [{ image_url: newPhotoUrl.value, caption: newPhotoCaption.value }]
    })
    newPhotoUrl.value = ''
    newPhotoCaption.value = ''
    // Refresh
    const data = await api.get(`/marketing/gallery/albums/${selectedAlbum.value.id}`)
    albumPhotos.value = data.photos || []
    fetchAlbums() // Refresh count
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Foto ditambahkan', life: 3000 })
  } catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menambah foto', life: 3000 }) }
  finally { saving.value = false }
}

async function deletePhoto(photo: any) {
  try {
    await api.delete(`/marketing/gallery/photos/${photo.id}`)
    albumPhotos.value = albumPhotos.value.filter(p => p.id !== photo.id)
    fetchAlbums()
  } catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus foto', life: 3000 }) }
}

function confirmDeleteAlbum(album: any) {
  confirm.require({
    message: `Hapus album "${album.title}" beserta semua fotonya?`, header: 'Konfirmasi', icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try { await api.delete(`/marketing/gallery/albums/${album.id}`); fetchAlbums(); toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Album dihapus', life: 3000 }) }
      catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus', life: 3000 }) }
    }
  })
}
</script>
