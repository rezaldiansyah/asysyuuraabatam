<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Kalender Pendidikan</h1>
        <p class="text-slate-600 dark:text-slate-400">Atur jadwal kegiatan akademik, libur nasional, dan ujian.</p>
      </div>
      <Button label="Tambah Kegiatan" icon="pi pi-plus" @click="openDialog()" />
    </div>

    <!-- Calendar & List Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Event List (Simple for now, maybe replace with FullCalendar later if needed) -->
      <Card class="lg:col-span-2">
        <template #title>Daftar Kegiatan {{ currentYearLabel }}</template>
        <template #content>
          <DataTable :value="events" :loading="loading" paginator :rows="10">
            <Column field="date" header="Tanggal" sortable>
              <template #body="slotProps">
                {{ formatDate(slotProps.data.date) }}
              </template>
            </Column>
            <Column field="type" header="Tipe" sortable>
              <template #body="slotProps">
                <Tag :value="getEventLabel(slotProps.data.type)" :severity="getEventSeverity(slotProps.data.type)" />
              </template>
            </Column>
            <Column field="description" header="Keterangan" />
            <Column field="is_holiday" header="Libur?">
              <template #body="slotProps">
                <i v-if="slotProps.data.is_holiday" class="pi pi-check text-red-500"></i>
                <span v-else>-</span>
              </template>
            </Column>
            <Column header="Aksi" style="width: 100px">
              <template #body="slotProps">
                <div class="flex gap-2">
                  <Button icon="pi pi-pencil" size="small" outlined @click="openDialog(slotProps.data)" />
                  <Button icon="pi pi-trash" size="small" outlined severity="danger" @click="confirmDelete(slotProps.data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Summary / Legend -->
      <Card>
        <template #title>Keterangan</template>
        <template #content>
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <Tag value="Hari Efektif" severity="info" />
              <span class="text-sm">Kegiatan Belajar Mengajar (KBM) biasa</span>
            </div>
            <div class="flex items-center gap-2">
              <Tag value="Libur" severity="danger" />
              <span class="text-sm">Tanggal merah / Cuti bersama</span>
            </div>
            <div class="flex items-center gap-2">
              <Tag value="Ujian" severity="warning" />
              <span class="text-sm">PTS, PAS, US (Tidak ada KBM reguler)</span>
            </div>
            <div class="flex items-center gap-2">
              <Tag value="Kegiatan" severity="success" />
              <span class="text-sm">Classmeeting, Lomba, Upacara</span>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Dialog Form -->
    <Dialog v-model:visible="dialogVisible" :header="isEditing ? 'Edit Kegiatan' : 'Tambah Kegiatan'" modal class="w-full max-w-lg">
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Tanggal</label>
          <Calendar v-model="form.date" dateFormat="dd/mm/yy" showIcon />
        </div>
        
        <div class="flex flex-col gap-2">
          <label class="font-medium">Tipe Kegiatan</label>
          <Dropdown v-model="form.type" :options="eventTypes" optionLabel="label" optionValue="value" placeholder="Pilih Tipe" />
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium">Keterangan</label>
          <InputText v-model="form.description" placeholder="Contoh: Libur Awal Ramadhan" />
        </div>

        <div class="flex items-center gap-2">
          <Checkbox v-model="form.is_holiday" :binary="true" inputId="is_holiday" />
          <label for="is_holiday">Tandai sebagai Hari Libur (Tidak Absen)</label>
        </div>
      </div>
      
      <template #footer>
        <Button label="Batal" text @click="dialogVisible = false" />
        <Button label="Simpan" icon="pi pi-save" @click="saveEvent" :loading="saving" />
      </template>
    </Dialog>

    <!-- Delete Confirmation -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

definePageMeta({
  layout: 'dashboard'
})

const { $api } = useNuxtApp() // Assuming custom plugin or useFetch
const confirm = useConfirm()
const toast = useToast()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const loading = ref(false)
const saving = ref(false)
const events = ref([])
const dialogVisible = ref(false)
const isEditing = ref(false)
const currentYearLabel = ref('')

// Form State
const form = reactive({
  id: null,
  date: new Date(),
  type: 'EFFECTIVE',
  description: '',
  is_holiday: false,
  academic_year_id: 1 // TODO: Fetch active academic year
})

const eventTypes = [
  { label: 'Hari Efektif', value: 'EFFECTIVE' },
  { label: 'Libur', value: 'HOLIDAY' },
  { label: 'Ujian', value: 'EXAM' },
  { label: 'Event Sekolah', value: 'EVENT' }
]

// Fetch Data
async function fetchEvents() {
  loading.value = true
  try {
    // TODO: Get active academic year first
    const data = await $fetch(`${apiBase}/academic-calendar`, {
      headers: { Authorization: `Bearer ${useAuthStore().token}` }
    })
    events.value = data
  } catch (e) {
    console.error(e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data', life: 3000 })
  } finally {
    loading.value = false
  }
}

function openDialog(data = null) {
  isEditing.value = !!data
  if (data) {
    form.id = data.id
    form.date = new Date(data.date)
    form.type = data.type
    form.description = data.description
    form.is_holiday = data.is_holiday
    form.academic_year_id = data.academic_year_id
  } else {
    // Reset form
    form.id = null
    form.date = new Date()
    form.type = 'EFFECTIVE'
    form.description = ''
    form.is_holiday = false
    // Keep academic_year_id
  }
  dialogVisible.value = true
}

async function saveEvent() {
  if (!form.description) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Keterangan wajib diisi', life: 3000 })
    return
  }

  saving.value = true
  try {
    const payload = { ...form }
    
    if (isEditing.value) {
      await $fetch(`${apiBase}/academic-calendar/${form.id}`, {
        method: 'PUT',
        body: payload,
        headers: { Authorization: `Bearer ${useAuthStore().token}` }
      })
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data diperbarui', life: 3000 })
    } else {
      await $fetch(`${apiBase}/academic-calendar`, {
        method: 'POST',
        body: payload,
        headers: { Authorization: `Bearer ${useAuthStore().token}` }
      })
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data ditambahkan', life: 3000 })
    }
    
    dialogVisible.value = false
    fetchEvents()
  } catch (e) {
    console.error(e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal menyimpan data', life: 3000 })
  } finally {
    saving.value = false
  }
}

function confirmDelete(data) {
  confirm.require({
    message: `Hapus kegiatan "${data.description}"?`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await $fetch(`${apiBase}/academic-calendar/${data.id}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${useAuthStore().token}` }
        })
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data dihapus', life: 3000 })
        fetchEvents()
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal menghapus data', life: 3000 })
      }
    }
  })
}

// Utils
function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

function getEventSeverity(type) {
  switch (type) {
    case 'HOLIDAY': return 'danger'
    case 'EXAM': return 'warning'
    case 'EVENT': return 'success'
    default: return 'info'
  }
}

function getEventLabel(type) {
  const found = eventTypes.find(t => t.value === type)
  return found ? found.label : type
}

// Init
import { useAuthStore } from '~/stores/auth'
onMounted(() => {
  fetchEvents()
})
</script>
