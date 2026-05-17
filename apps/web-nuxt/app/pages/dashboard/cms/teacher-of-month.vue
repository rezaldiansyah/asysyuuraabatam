<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Teacher of the Month</h1>
        <p class="text-slate-500 dark:text-slate-400">Pilih guru terbaik bulan ini untuk ditampilkan di landing page.</p>
      </div>
      <Button label="Tambah Guru" icon="pi pi-plus" @click="openDialog()" />
    </div>

    <!-- Current Active -->
    <div v-if="activeTeacher" class="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6">
      <div class="flex items-center gap-2 mb-4">
        <i class="pi pi-star-fill text-amber-500"></i>
        <span class="font-bold text-amber-700 dark:text-amber-400">Sedang Ditampilkan di Landing Page</span>
      </div>
      <div class="flex items-center gap-6">
        <div class="w-24 h-24 rounded-full overflow-hidden bg-white shadow-md flex-shrink-0">
          <img v-if="activeTeacher.photo_url" :src="activeTeacher.photo_url" :alt="activeTeacher.name" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full bg-amber-100 flex items-center justify-center text-amber-400 text-3xl font-bold">
            {{ activeTeacher.name?.charAt(0) }}
          </div>
        </div>
        <div>
          <h3 class="text-xl font-bold text-slate-800 dark:text-white">{{ activeTeacher.name }}</h3>
          <p class="text-amber-600 dark:text-amber-400 font-medium">{{ activeTeacher.title }}</p>
          <p v-if="activeTeacher.quote" class="text-slate-500 dark:text-slate-400 italic mt-2">"{{ activeTeacher.quote }}"</p>
          <p class="text-xs text-slate-400 mt-2">Bulan: {{ formatMonth(activeTeacher.month) }}</p>
        </div>
      </div>
    </div>

    <!-- History -->
    <div class="card bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl overflow-hidden">
      <DataTable :value="teachers" :loading="loading" paginator :rows="10">
        <template #empty>Belum ada data.</template>
        <Column header="Foto" style="width: 60px">
          <template #body="{ data }">
            <Avatar :image="data.photo_url || undefined" :label="data.name?.charAt(0)" shape="circle" size="normal" class="bg-primary/10 text-primary" />
          </template>
        </Column>
        <Column field="name" header="Nama" sortable></Column>
        <Column field="title" header="Jabatan"></Column>
        <Column field="month" header="Bulan" sortable>
          <template #body="{ data }">{{ formatMonth(data.month) }}</template>
        </Column>
        <Column header="Status" style="width: 100px">
          <template #body="{ data }">
            <Badge :value="data.is_active ? 'Aktif' : 'Arsip'" :severity="data.is_active ? 'success' : 'secondary'" />
          </template>
        </Column>
        <Column header="Aksi" style="width: 120px">
          <template #body="{ data }">
            <div class="flex gap-1">
              <Button v-if="!data.is_active" icon="pi pi-star" text rounded size="small" severity="warning" @click="setActive(data)" title="Jadikan Aktif" />
              <Button icon="pi pi-pencil" text rounded size="small" @click="openDialog(data)" title="Edit" />
              <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="confirmDelete(data)" title="Hapus" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Form Dialog -->
    <Dialog v-model:visible="dialogVisible" :header="editingItem ? 'Edit Guru' : 'Tambah Guru'" modal class="w-full max-w-lg">
      <div class="space-y-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Nama Guru *</label>
          <InputText v-model="form.name" placeholder="Nama lengkap guru" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Jabatan</label>
          <InputText v-model="form.title" placeholder='Contoh: Guru Tahfidz SDIT' />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Quote / Motivasi</label>
          <Textarea v-model="form.quote" rows="3" placeholder="Kata-kata motivasi dari guru..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Bulan *</label>
          <InputText v-model="form.month" placeholder="2026-05" />
          <small class="text-slate-400">Format: YYYY-MM (misal: 2026-05 untuk Mei 2026)</small>
        </div>
        <CmsImageUploader v-model="form.photo_url" label="Foto Guru" />
        <div class="flex items-center gap-3">
          <Checkbox v-model="form.is_active" :binary="true" inputId="tactive" />
          <label for="tactive" class="text-sm">Jadikan guru bulan ini (aktif di landing page)</label>
        </div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text @click="dialogVisible = false" />
        <Button :label="editingItem ? 'Simpan' : 'Tambah'" icon="pi pi-check" :loading="saving" @click="saveTeacher" />
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

const teachers = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingItem = ref<any>(null)

const form = reactive({
  name: '', title: '', quote: '', photo_url: '', month: '', is_active: true
})

const activeTeacher = computed(() => teachers.value.find(t => t.is_active))

const monthNames = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

function formatMonth(m: string) {
  if (!m) return '-'
  const [year, month] = m.split('-')
  return `${monthNames[parseInt(month) - 1] || month} ${year}`
}

onMounted(() => fetchData())

async function fetchData() {
  loading.value = true
  try { teachers.value = await api.get('/marketing/teacher-of-month') }
  catch { toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data', life: 3000 }) }
  finally { loading.value = false }
}

function openDialog(item: any = null) {
  editingItem.value = item
  const now = new Date()
  const defaultMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  if (item) {
    Object.assign(form, { name: item.name, title: item.title || '', quote: item.quote || '', photo_url: item.photo_url || '', month: item.month, is_active: item.is_active })
  } else {
    Object.assign(form, { name: '', title: '', quote: '', photo_url: '', month: defaultMonth, is_active: true })
  }
  dialogVisible.value = true
}

async function saveTeacher() {
  if (!form.name || !form.month) { toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama dan bulan harus diisi', life: 3000 }); return }
  saving.value = true
  try {
    if (editingItem.value) {
      await api.put(`/marketing/teacher-of-month/${editingItem.value.id}`, { ...form })
    } else {
      await api.post('/marketing/teacher-of-month', { ...form })
    }
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data guru berhasil disimpan', life: 3000 })
    dialogVisible.value = false
    fetchData()
  } catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan data', life: 3000 }) }
  finally { saving.value = false }
}

async function setActive(teacher: any) {
  try {
    await api.put(`/marketing/teacher-of-month/${teacher.id}`, { is_active: true })
    fetchData()
    toast.add({ severity: 'success', summary: 'Berhasil', detail: `${teacher.name} dijadikan guru bulan ini`, life: 3000 })
  } catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengubah status', life: 3000 }) }
}

function confirmDelete(item: any) {
  confirm.require({
    message: `Hapus data "${item.name}"?`, header: 'Konfirmasi', icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try { await api.delete(`/marketing/teacher-of-month/${item.id}`); fetchData(); toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data dihapus', life: 3000 }) }
      catch { toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus', life: 3000 }) }
    }
  })
}
</script>
