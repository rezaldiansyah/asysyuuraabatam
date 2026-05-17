<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Testimoni</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola testimoni orang tua & alumni untuk landing page.</p>
      </div>
      <Button label="Tambah Testimoni" icon="pi pi-plus" @click="openDialog()" />
    </div>

    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="item in testimonials" :key="item.id" class="bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl p-5 space-y-3 relative">
        <!-- Status Badge -->
        <Badge :value="item.is_published ? 'Tampil' : 'Draft'" :severity="item.is_published ? 'success' : 'secondary'" class="absolute top-3 right-3" />
        
        <!-- Rating -->
        <div class="flex gap-0.5">
          <i v-for="s in 5" :key="s" class="pi pi-star-fill text-sm" :class="s <= item.rating ? 'text-yellow-400' : 'text-slate-200 dark:text-slate-600'"></i>
        </div>

        <!-- Content -->
        <p class="text-slate-600 dark:text-slate-300 text-sm italic line-clamp-3">"{{ item.content }}"</p>
        
        <!-- Author -->
        <div class="flex items-center gap-3 pt-2 border-t border-slate-100 dark:border-slate-700">
          <Avatar :image="item.photo_url || undefined" :label="item.name?.charAt(0)" shape="circle" size="normal" class="bg-primary/10 text-primary" />
          <div>
            <p class="font-semibold text-sm text-slate-800 dark:text-white">{{ item.name }}</p>
            <p class="text-xs text-slate-400">{{ item.role }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-2 pt-2">
          <Button icon="pi pi-pencil" text rounded size="small" @click="openDialog(item)" title="Edit" />
          <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="confirmDelete(item)" title="Hapus" />
        </div>
      </div>
    </div>

    <div v-if="!testimonials.length && !loading" class="text-center py-16 text-slate-400">
      <i class="pi pi-comments text-5xl mb-4 block"></i>
      <p>Belum ada testimoni. Klik "Tambah Testimoni" untuk mulai.</p>
    </div>

    <!-- Form Dialog -->
    <Dialog v-model:visible="dialogVisible" :header="editingItem ? 'Edit Testimoni' : 'Tambah Testimoni'" modal class="w-full max-w-lg">
      <div class="space-y-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Nama *</label>
          <InputText v-model="form.name" placeholder="Nama lengkap" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Jabatan / Role</label>
          <InputText v-model="form.role" placeholder='Contoh: Orang Tua Siswa SDIT' />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Isi Testimoni *</label>
          <Textarea v-model="form.content" rows="4" placeholder="Tulis testimoni di sini..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Rating</label>
          <div class="flex gap-1">
            <button v-for="s in 5" :key="s" @click="form.rating = s" class="text-2xl transition-transform hover:scale-110">
              <i class="pi pi-star-fill" :class="s <= form.rating ? 'text-yellow-400' : 'text-slate-200 dark:text-slate-600'"></i>
            </button>
          </div>
        </div>
        <CmsImageUploader v-model="form.photo_url" label="Foto (Opsional)" />
        <div class="flex items-center gap-3">
          <Checkbox v-model="form.is_published" :binary="true" inputId="pub" />
          <label for="pub" class="text-sm">Tampilkan di halaman publik</label>
        </div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text @click="dialogVisible = false" />
        <Button :label="editingItem ? 'Simpan' : 'Tambah'" icon="pi pi-check" :loading="saving" @click="saveTestimonial" />
      </template>
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

const testimonials = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingItem = ref<any>(null)

const form = reactive({
  name: '', role: '', content: '', photo_url: '', rating: 5, is_published: true
})

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  try { testimonials.value = await api.get('/marketing/testimonials') }
  catch { toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data', life: 3000 }) }
  finally { loading.value = false }
}

function openDialog(item: any = null) {
  editingItem.value = item
  if (item) {
    Object.assign(form, { name: item.name, role: item.role, content: item.content, photo_url: item.photo_url || '', rating: item.rating, is_published: item.is_published })
  } else {
    Object.assign(form, { name: '', role: '', content: '', photo_url: '', rating: 5, is_published: true })
  }
  dialogVisible.value = true
}

async function saveTestimonial() {
  if (!form.name || !form.content) { toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama dan isi testimoni harus diisi', life: 3000 }); return }
  saving.value = true
  try {
    if (editingItem.value) {
      await api.put(`/marketing/testimonials/${editingItem.value.id}`, { ...form })
    } else {
      await api.post('/marketing/testimonials', { ...form })
    }
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Testimoni berhasil disimpan', life: 3000 })
    dialogVisible.value = false
    fetchData()
  } catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan testimoni', life: 3000 }) }
  finally { saving.value = false }
}

function confirmDelete(item: any) {
  confirm.require({
    message: `Hapus testimoni dari "${item.name}"?`, header: 'Konfirmasi', icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try { await api.delete(`/marketing/testimonials/${item.id}`); fetchData(); toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Testimoni dihapus', life: 3000 }) }
      catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus', life: 3000 }) }
    }
  })
}
</script>
