<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Kalender Pendidikan</h1>
        <p class="text-slate-500 dark:text-slate-400">Atur jadwal kegiatan akademik, libur nasional, dan agenda ujian sekolah.</p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <!-- Academic Year Selector -->
        <div class="flex items-center gap-2 bg-white dark:bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <i class="pi pi-calendar text-primary text-sm"></i>
          <span class="text-xs font-medium text-slate-500 dark:text-slate-400 whitespace-nowrap">Tahun Ajaran:</span>
          <Dropdown 
            v-model="selectedAcademicYearId" 
            :options="academicYears" 
            optionLabel="label" 
            optionValue="id" 
            placeholder="Pilih Tahun Ajaran" 
            class="w-56 !border-0 !shadow-none !p-0 text-xs font-semibold"
            @change="fetchEvents"
          />
        </div>

        <Button label="Tambah Kegiatan" icon="pi pi-plus" @click="openDialog()" class="shadow-sm whitespace-nowrap" />
      </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200/80 dark:border-slate-700 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-400 font-medium">Total Agenda</div>
          <div class="text-2xl font-bold text-slate-800 dark:text-white mt-0.5">{{ events.length }}</div>
        </div>
        <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400">
          <i class="pi pi-calendar-times text-lg"></i>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200/80 dark:border-slate-700 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-400 font-medium">Hari Libur</div>
          <div class="text-2xl font-bold text-red-600 dark:text-red-400 mt-0.5">{{ holidayCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-xl bg-red-50 dark:bg-red-900/30 flex items-center justify-center text-red-600 dark:text-red-400">
          <i class="pi pi-flag text-lg"></i>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200/80 dark:border-slate-700 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-400 font-medium">Jadwal Ujian</div>
          <div class="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-0.5">{{ examCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-900/30 flex items-center justify-center text-amber-600 dark:text-amber-400">
          <i class="pi pi-file-edit text-lg"></i>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200/80 dark:border-slate-700 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-400 font-medium">Event Sekolah</div>
          <div class="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-0.5">{{ eventCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400">
          <i class="pi pi-sparkles text-lg"></i>
        </div>
      </div>
    </div>

    <!-- Main Content Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Event List Table (2 Columns) -->
      <Card class="lg:col-span-2 shadow-sm border border-slate-200/80 dark:border-slate-800 rounded-xl">
        <template #header>
          <div class="p-5 pb-0 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <h2 class="text-base font-bold text-slate-800 dark:text-slate-100">
                Daftar Kegiatan Akademik
              </h2>
              <span class="text-xs text-slate-400 font-normal">
                {{ activeYearLabel }}
              </span>
            </div>

            <!-- Filters -->
            <div class="flex items-center gap-2">
              <span class="p-input-icon-left">
                <i class="pi pi-search text-xs"></i>
                <InputText 
                  v-model="searchQuery" 
                  placeholder="Cari kegiatan..." 
                  class="p-inputtext-sm w-44 sm:w-56" 
                />
              </span>
              <Dropdown 
                v-model="filterType" 
                :options="typeFilterOptions" 
                optionLabel="label" 
                optionValue="value" 
                class="p-inputtext-sm w-36"
              />
            </div>
          </div>
        </template>

        <template #content>
          <DataTable 
            :value="filteredEvents" 
            :loading="loading" 
            paginator 
            :rows="10" 
            class="p-datatable-sm"
            stripedRows
            responsiveLayout="scroll"
          >
            <template #empty>
              <div class="text-center py-12 text-slate-400">
                <i class="pi pi-calendar text-4xl mb-3 text-slate-300 dark:text-slate-600"></i>
                <p class="font-medium text-slate-600 dark:text-slate-300">Belum ada agenda kegiatan pada periode ini</p>
                <p class="text-xs text-slate-400 mt-1">Klik tombol "Tambah Kegiatan" di atas untuk menambahkan jadwal baru.</p>
              </div>
            </template>

            <Column field="date" header="Tanggal" sortable style="min-width: 170px">
              <template #body="slotProps">
                <div class="flex flex-col">
                  <span class="font-medium text-slate-800 dark:text-slate-200 text-xs">
                    {{ formatDate(slotProps.data.date) }}
                  </span>
                  <span v-if="slotProps.data.end_date" class="text-[11px] text-slate-400 mt-0.5">
                    s/d {{ formatDate(slotProps.data.end_date) }}
                  </span>
                </div>
              </template>
            </Column>

            <Column field="type" header="Tipe" sortable style="width: 130px">
              <template #body="slotProps">
                <Tag :value="getEventLabel(slotProps.data.type)" :severity="getEventSeverity(slotProps.data.type)" class="text-xs" />
              </template>
            </Column>

            <Column field="description" header="Keterangan Kegiatan" style="min-width: 220px">
              <template #body="slotProps">
                <div class="font-medium text-slate-700 dark:text-slate-200">
                  {{ slotProps.data.description }}
                </div>
              </template>
            </Column>

            <Column field="is_holiday" header="Libur / KBM" style="width: 120px" class="text-center">
              <template #body="slotProps">
                <span 
                  v-if="slotProps.data.is_holiday" 
                  class="inline-flex items-center gap-1 text-[11px] font-semibold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 px-2 py-0.5 rounded-full"
                >
                  <i class="pi pi-times-circle text-[10px]"></i> Libur
                </span>
                <span 
                  v-else 
                  class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full"
                >
                  <i class="pi pi-check-circle text-[10px]"></i> KBM Aktif
                </span>
              </template>
            </Column>

            <Column header="Aksi" style="width: 100px" class="text-right">
              <template #body="slotProps">
                <div class="flex items-center justify-end gap-1">
                  <Button 
                    icon="pi pi-pencil" 
                    size="small" 
                    text 
                    severity="secondary" 
                    @click="openDialog(slotProps.data)" 
                    title="Edit Kegiatan"
                  />
                  <Button 
                    icon="pi pi-trash" 
                    size="small" 
                    text 
                    severity="danger" 
                    @click="confirmDelete(slotProps.data)" 
                    title="Hapus Kegiatan"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Sidebar Legend & Mini Guide (1 Column) -->
      <div class="space-y-6">
        <Card class="shadow-sm border border-slate-200/80 dark:border-slate-800 rounded-xl">
          <template #title>
            <div class="text-base font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <i class="pi pi-info-circle text-primary"></i>
              Panduan Tipe Kegiatan
            </div>
          </template>
          <template #content>
            <div class="space-y-3.5 pt-2">
              <div class="flex items-start gap-3">
                <Tag value="Hari Efektif" severity="info" class="mt-0.5" />
                <div class="text-xs text-slate-600 dark:text-slate-300">
                  <strong>Kegiatan Belajar Mengajar (KBM)</strong> biasa, wajib presensi kehadiran guru dan siswa.
                </div>
              </div>

              <div class="flex items-start gap-3">
                <Tag value="Libur" severity="danger" class="mt-0.5" />
                <div class="text-xs text-slate-600 dark:text-slate-300">
                  <strong>Tanggal Merah / Cuti Bersama</strong>. Sistem presensi otomatis meniadakan kewajiban absen.
                </div>
              </div>

              <div class="flex items-start gap-3">
                <Tag value="Ujian" severity="warning" class="mt-0.5" />
                <div class="text-xs text-slate-600 dark:text-slate-300">
                  <strong>PTS, PAS, Asesmen Madrasah / US</strong>. Tidak ada KBM reguler, fokus pada ujian.
                </div>
              </div>

              <div class="flex items-start gap-3">
                <Tag value="Event Sekolah" severity="success" class="mt-0.5" />
                <div class="text-xs text-slate-600 dark:text-slate-300">
                  <strong>Acara & Perlombaan</strong> seperti Classmeeting, Pawai Muharram, Upacara, Manasik Haji.
                </div>
              </div>
            </div>
          </template>
        </Card>

        <!-- Academic Year Summary Box -->
        <div class="p-4 bg-primary/5 dark:bg-primary/10 rounded-xl border border-primary/20 text-xs space-y-2 text-slate-600 dark:text-slate-300">
          <div class="font-bold text-primary flex items-center gap-1.5">
            <i class="pi pi-bookmark"></i>
            Informasi Periode
          </div>
          <p>
            Agenda kalender yang dicatat di sini menjadi acuan resmi hari efektif belajar dan jadwal libur seluruh unit di bawah Yayasan Asy-Syuuraa Batam.
          </p>
        </div>
      </div>
    </div>

    <!-- Dialog Form Tambah / Edit Kegiatan -->
    <Dialog 
      v-model:visible="dialogVisible" 
      :header="isEditing ? 'Edit Kegiatan Akademik' : 'Tambah Kegiatan Akademik'" 
      modal 
      class="w-full max-w-lg"
      :breakpoints="{ '960px': '75vw', '640px': '95vw' }"
    >
      <div class="flex flex-col gap-4 py-2">
        <!-- Tahun Ajaran -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-bold text-slate-700 dark:text-slate-300">Tahun Ajaran <span class="text-red-500">*</span></label>
          <Dropdown 
            v-model="form.academic_year_id" 
            :options="academicYears" 
            optionLabel="label" 
            optionValue="id" 
            placeholder="Pilih Tahun Ajaran" 
            class="w-full"
          />
        </div>

        <!-- Rentang Tanggal -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-bold text-slate-700 dark:text-slate-300">Tanggal Mulai <span class="text-red-500">*</span></label>
            <Calendar 
              v-model="form.date" 
              dateFormat="dd/mm/yy" 
              showIcon 
              class="w-full"
              placeholder="Pilih tanggal"
            />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-bold text-slate-700 dark:text-slate-300">
              Tanggal Selesai 
              <span class="text-[10px] font-normal text-slate-400">(opsional, untuk rentang)</span>
            </label>
            <Calendar 
              v-model="form.end_date" 
              dateFormat="dd/mm/yy" 
              showIcon 
              :minDate="form.date || undefined" 
              class="w-full"
              placeholder="Pilih tanggal"
            />
          </div>
        </div>
        
        <!-- Tipe Kegiatan -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-bold text-slate-700 dark:text-slate-300">Tipe Kegiatan <span class="text-red-500">*</span></label>
          <Dropdown 
            v-model="form.type" 
            :options="eventTypes" 
            optionLabel="label" 
            optionValue="value" 
            placeholder="Pilih Tipe Kegiatan" 
            class="w-full"
            @change="handleTypeChange"
          />
        </div>

        <!-- Keterangan -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-bold text-slate-700 dark:text-slate-300">Keterangan / Nama Kegiatan <span class="text-red-500">*</span></label>
          <InputText 
            v-model="form.description" 
            placeholder="Contoh: Libur Awal Ramadhan 1447 H, Ujian Tengah Semester..." 
            class="w-full"
          />
        </div>

        <!-- Checkbox Hari Libur -->
        <div class="flex items-center gap-2.5 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700">
          <Checkbox v-model="form.is_holiday" :binary="true" inputId="is_holiday" />
          <label for="is_holiday" class="text-xs font-medium text-slate-700 dark:text-slate-300 cursor-pointer select-none">
            Tandai sebagai Hari Libur Resmi (Bebas Kewajiban Presensi)
          </label>
        </div>
      </div>
      
      <template #footer>
        <div class="flex items-center justify-end gap-2 pt-2">
          <Button label="Batal" text severity="secondary" @click="dialogVisible = false" />
          <Button label="Simpan Kegiatan" icon="pi pi-save" @click="saveEvent" :loading="saving" />
        </div>
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { useConfirm } from "primevue/useconfirm"
import { useToast } from "primevue/usetoast"

definePageMeta({
  layout: 'dashboard'
})

const api = useApi()
const confirm = useConfirm()
const toast = useToast()

const loading = ref(false)
const saving = ref(false)
const events = ref<any[]>([])
const academicYears = ref<any[]>([])
const selectedAcademicYearId = ref<number | null>(null)
const dialogVisible = ref(false)
const isEditing = ref(false)
const searchQuery = ref('')
const filterType = ref('ALL')

// Form State
const form = reactive({
  id: null as number | null,
  date: new Date() as Date | null,
  end_date: null as Date | null,
  type: 'EFFECTIVE',
  description: '',
  is_holiday: false,
  academic_year_id: null as number | null,
})

const eventTypes = [
  { label: 'Hari Efektif Belajar', value: 'EFFECTIVE' },
  { label: 'Libur Nasional / Cuti Bersama', value: 'HOLIDAY' },
  { label: 'Ujian (PTS/PAS/US)', value: 'EXAM' },
  { label: 'Event Sekolah', value: 'EVENT' }
]

const typeFilterOptions = [
  { label: 'Semua Tipe', value: 'ALL' },
  { label: 'Hari Efektif', value: 'EFFECTIVE' },
  { label: 'Libur', value: 'HOLIDAY' },
  { label: 'Ujian', value: 'EXAM' },
  { label: 'Event Sekolah', value: 'EVENT' },
]

// Computed Stats
const holidayCount = computed(() => events.value.filter(e => e.type === 'HOLIDAY' || e.is_holiday).length)
const examCount = computed(() => events.value.filter(e => e.type === 'EXAM').length)
const eventCount = computed(() => events.value.filter(e => e.type === 'EVENT').length)

const activeYearLabel = computed(() => {
  const current = academicYears.value.find(y => y.id === selectedAcademicYearId.value)
  return current ? current.label : 'Seluruh Kegiatan'
})

// Filtered Events
const filteredEvents = computed(() => {
  return events.value.filter(e => {
    // Filter by type
    if (filterType.value !== 'ALL' && e.type !== filterType.value) {
      return false
    }
    // Filter by search query
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const desc = (e.description || '').toLowerCase()
      const typeLabel = getEventLabel(e.type).toLowerCase()
      return desc.includes(q) || typeLabel.includes(q)
    }
    return true
  })
})

function handleTypeChange() {
  if (form.type === 'HOLIDAY') {
    form.is_holiday = true
  }
}

// Fetch Academic Years
async function fetchAcademicYears() {
  try {
    const data = await api.get<any[]>('/academic/years')
    academicYears.value = (data || []).map(y => ({
      id: y.id,
      label: `${y.name} - Semester ${y.semester} ${y.is_active ? '(Aktif)' : ''}`,
      is_active: y.is_active
    }))
    
    // Auto-select active year
    const active = academicYears.value.find(y => y.is_active)
    if (active) {
      selectedAcademicYearId.value = active.id
    } else if (academicYears.value.length > 0) {
      selectedAcademicYearId.value = academicYears.value[0].id
    }
  } catch (e) {
    console.error('Gagal memuat tahun ajaran:', e)
  }
}

// Fetch Calendar Events
async function fetchEvents() {
  loading.value = true
  try {
    const queryParam = selectedAcademicYearId.value ? `?academic_year_id=${selectedAcademicYearId.value}` : ''
    const data = await api.get<any[]>(`/academic-calendar${queryParam}`)
    events.value = data || []
  } catch (e: any) {
    console.error('Gagal memuat data kalender:', e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data kalender pendidikan', life: 3000 })
  } finally {
    loading.value = false
  }
}

function openDialog(data: any = null) {
  isEditing.value = !!data
  if (data) {
    form.id = data.id
    form.date = data.date ? new Date(data.date) : new Date()
    form.end_date = data.end_date ? new Date(data.end_date) : null
    form.type = data.type || 'EFFECTIVE'
    form.description = data.description || ''
    form.is_holiday = !!data.is_holiday
    form.academic_year_id = data.academic_year_id || selectedAcademicYearId.value
  } else {
    // Reset form
    form.id = null
    form.date = new Date()
    form.end_date = null
    form.type = 'EFFECTIVE'
    form.description = ''
    form.is_holiday = false
    form.academic_year_id = selectedAcademicYearId.value
  }
  dialogVisible.value = true
}

// Format local date to avoid timezone shift
function toLocalDateString(d: Date | string | null): string | null {
  if (!d) return null
  const dt = new Date(d)
  if (isNaN(dt.getTime())) return null
  const year = dt.getFullYear()
  const month = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}T00:00:00`
}

async function saveEvent() {
  if (!form.description.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Keterangan kegiatan wajib diisi', life: 3000 })
    return
  }

  if (!form.date) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Tanggal mulai wajib dipilih', life: 3000 })
    return
  }

  saving.value = true
  try {
    const payload = {
      date: toLocalDateString(form.date),
      end_date: form.end_date ? toLocalDateString(form.end_date) : null,
      type: form.type,
      description: form.description.trim(),
      is_holiday: form.is_holiday,
      academic_year_id: form.academic_year_id || selectedAcademicYearId.value
    }
    
    if (isEditing.value && form.id) {
      await api.put(`/academic-calendar/${form.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kegiatan berhasil diperbarui', life: 3000 })
    } else {
      await api.post('/academic-calendar', payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kegiatan berhasil ditambahkan', life: 3000 })
    }
    
    dialogVisible.value = false
    await fetchEvents()
  } catch (e: any) {
    console.error('Error saving event:', e)
    const errorMsg = e.data?.detail || e.message || 'Gagal menyimpan kegiatan'
    toast.add({ severity: 'error', summary: 'Gagal', detail: errorMsg, life: 4000 })
  } finally {
    saving.value = false
  }
}

function confirmDelete(data: any) {
  confirm.require({
    message: `Hapus kegiatan "${data.description}"?`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Ya, Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/academic-calendar/${data.id}`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kegiatan berhasil dihapus', life: 3000 })
        await fetchEvents()
      } catch (e: any) {
        console.error('Error deleting event:', e)
        const errorMsg = e.data?.detail || e.message || 'Gagal menghapus kegiatan'
        toast.add({ severity: 'error', summary: 'Error', detail: errorMsg, life: 3000 })
      }
    }
  })
}

// Utils
function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', { 
    weekday: 'short', 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

function getEventSeverity(type: string) {
  switch (type) {
    case 'HOLIDAY': return 'danger'
    case 'EXAM': return 'warning'
    case 'EVENT': return 'success'
    default: return 'info'
  }
}

function getEventLabel(type: string) {
  const found = eventTypes.find(t => t.value === type)
  return found ? found.label : type
}

// Lifecycle
onMounted(async () => {
  await fetchAcademicYears()
  await fetchEvents()
})
</script>
