<template>
  <div class="space-y-4 text-sm">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
      <div>
        <h1 class="text-xl font-semibold text-slate-800 dark:text-white">Kalender Pendidikan</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400">Atur jadwal kegiatan akademik, libur nasional, dan agenda ujian sekolah.</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <Select
          v-model="selectedAcademicYearId"
          :options="academicYears"
          optionLabel="label"
          optionValue="id"
          placeholder="Pilih Tahun Ajaran"
          size="small"
          class="w-64"
          @change="onYearRowChange"
        />
        <Button label="Tambah Kegiatan" icon="pi pi-plus" size="small" @click="openDialog()" />
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <div v-for="s in statCards" :key="s.label" class="bg-white dark:bg-slate-800 rounded-xl px-3 py-2.5 border border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <div>
          <div class="text-[11px] text-slate-500">{{ s.label }}</div>
          <div class="text-lg font-semibold leading-tight" :class="s.color">{{ s.value }}</div>
        </div>
        <i :class="['pi', s.icon, 'text-base opacity-70', s.color]"></i>
      </div>
    </div>

    <!-- Tab switch -->
    <SelectButton
      v-model="activeTab"
      :options="[{ label: 'Daftar Kegiatan', value: 'list' }, { label: 'Tampilan Kalender', value: 'calendar' }]"
      optionLabel="label"
      optionValue="value"
      :allowEmpty="false"
      size="small"
    />

    <!-- ===================== TAB: DAFTAR ===================== -->
    <div v-show="activeTab === 'list'" class="grid grid-cols-1 xl:grid-cols-4 gap-4">
      <div class="xl:col-span-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <div class="mb-3">
          <h2 class="text-sm font-semibold text-slate-800 dark:text-slate-100">Daftar Kegiatan Akademik</h2>
          <span class="text-xs text-slate-400">{{ activeYearLabel }}</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3">
          <IconField>
            <InputIcon class="pi pi-search" />
            <InputText v-model="searchQuery" placeholder="Cari kegiatan..." size="small" fluid />
          </IconField>
          <Select v-model="filterType" :options="typeFilterOptions" optionLabel="label" optionValue="value" size="small" fluid />
        </div>

        <DataTable :value="filteredEvents" :loading="loading" paginator :rows="10" :rowsPerPageOptions="[10, 20, 50]" size="small" class="text-sm" stripedRows responsiveLayout="scroll">
          <template #empty>
            <div class="text-center py-10 text-slate-400">
              <i class="pi pi-calendar text-3xl mb-2 text-slate-300"></i>
              <p class="text-slate-600 dark:text-slate-300">Belum ada agenda kegiatan pada periode ini</p>
              <p class="text-xs mt-1">Klik "Tambah Kegiatan" untuk menambahkan jadwal baru.</p>
            </div>
          </template>

          <Column field="date" header="Tanggal" sortable style="min-width: 150px">
            <template #body="{ data }">
              <div class="text-xs font-medium text-slate-800 dark:text-slate-200">{{ formatDate(data.date) }}</div>
              <div v-if="data.end_date" class="text-[11px] text-slate-400">s/d {{ formatDate(data.end_date) }}</div>
            </template>
          </Column>
          <Column field="type" header="Tipe" sortable style="width: 150px">
            <template #body="{ data }">
              <Tag :value="getEventLabel(data.type)" :severity="getEventSeverity(data.type)" class="!text-[11px] whitespace-nowrap" />
            </template>
          </Column>
          <Column field="description" header="Keterangan Kegiatan" style="min-width: 200px">
            <template #body="{ data }"><span class="text-slate-700 dark:text-slate-200">{{ data.description }}</span></template>
          </Column>
          <Column field="is_holiday" header="Libur / KBM" style="width: 110px">
            <template #body="{ data }">
              <span v-if="data.is_holiday" class="inline-flex items-center gap-1 text-[11px] font-medium text-red-600 bg-red-50 dark:bg-red-950/40 px-2 py-0.5 rounded-full whitespace-nowrap"><i class="pi pi-times-circle text-[10px]"></i>Libur</span>
              <span v-else class="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded-full whitespace-nowrap"><i class="pi pi-check-circle text-[10px]"></i>KBM Aktif</span>
            </template>
          </Column>
          <Column header="Aksi" style="width: 90px">
            <template #body="{ data }">
              <div class="flex items-center justify-end">
                <Button icon="pi pi-pencil" size="small" text severity="secondary" @click="openDialog(data)" title="Edit" />
                <Button icon="pi pi-trash" size="small" text severity="danger" @click="confirmDelete(data)" title="Hapus" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Legend -->
      <div class="space-y-3">
        <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 pb-2 mb-2">
            <div class="text-xs font-semibold text-slate-700 dark:text-slate-100 flex items-center gap-1.5"><i class="pi pi-info-circle text-primary text-xs"></i>Keterangan</div>
            <span class="text-[11px] text-slate-400">Tipe Kegiatan</span>
          </div>
          <div class="space-y-2">
            <div v-for="l in legendItems" :key="l.label" class="flex items-start gap-2">
              <span class="w-20 shrink-0 px-1.5 py-0.5 text-center rounded text-[11px] font-medium border" :class="l.cls">{{ l.label }}</span>
              <div class="min-w-0">
                <div class="text-xs font-medium text-slate-700 dark:text-slate-200">{{ l.title }}</div>
                <div class="text-[11px] text-slate-400">{{ l.desc }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="p-3 bg-primary/5 rounded-xl border border-primary/20 text-xs text-slate-600 dark:text-slate-300">
          <div class="font-semibold text-primary flex items-center gap-1.5 mb-1"><i class="pi pi-bookmark text-[11px]"></i>Informasi Periode</div>
          <p class="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">Agenda kalender yang dicatat di sini menjadi acuan resmi hari efektif belajar dan jadwal libur seluruh unit di bawah Yayasan Asy-Syuuraa Batam.</p>
        </div>
      </div>
    </div>

    <!-- ===================== TAB: KALENDER ===================== -->
    <div v-show="activeTab === 'calendar'" class="space-y-3">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3 flex flex-col lg:flex-row lg:items-end gap-3">
        <div class="flex flex-col gap-1">
          <label class="text-[11px] text-slate-500">Tahun Ajaran</label>
          <Select v-model="viewYearName" :options="yearNames" size="small" class="w-40" @change="onViewYearChange" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[11px] text-slate-500">Tampilan</label>
          <SelectButton
            v-model="viewMode"
            :options="[{ label: 'Per Bulan', value: 'month' }, { label: 'Per Semester', value: 'semester' }, { label: 'Tahun Ajaran', value: 'year' }]"
            optionLabel="label"
            optionValue="value"
            :allowEmpty="false"
            size="small"
          />
        </div>
        <div v-if="viewMode === 'month'" class="flex flex-col gap-1">
          <label class="text-[11px] text-slate-500">Bulan</label>
          <Select v-model="viewMonthIdx" :options="monthOptions" optionLabel="label" optionValue="value" size="small" class="w-44" />
        </div>
        <div v-if="viewMode === 'semester'" class="flex flex-col gap-1">
          <label class="text-[11px] text-slate-500">Semester</label>
          <SelectButton v-model="viewSemester" :options="['Ganjil', 'Genap']" :allowEmpty="false" size="small" />
        </div>
        <div class="lg:ml-auto flex gap-2">
          <Button label="Cetak / Simpan PDF" icon="pi pi-file-pdf" size="small" severity="danger" outlined @click="printCalendar" />
        </div>
      </div>

      <div class="overflow-x-auto">
        <div id="kalender-print" class="kp-paper">
          <div class="kp-head">
            <h2>KALENDER PENDIDIKAN</h2>
            <p>Yayasan Asy-Syuuraa Batam</p>
            <p><b>{{ viewTitle }}</b></p>
          </div>

          <div class="kp-legend">
            <span><i class="kp-dot" style="background:#dbeafe"></i>Hari Efektif</span>
            <span><i class="kp-dot" style="background:#fee2e2"></i>Libur</span>
            <span><i class="kp-dot" style="background:#fef3c7"></i>Ujian</span>
            <span><i class="kp-dot" style="background:#d1fae5"></i>Kegiatan</span>
          </div>

          <div v-if="viewMode !== 'month'" class="kp-summary">
            <div class="kp-sum"><b>{{ totals.effective }}</b>Hari Efektif (Sen–Jum)</div>
            <div class="kp-sum"><b style="color:#b91c1c">{{ totals.holidayDays }}</b>Hari Libur (hari kerja)</div>
            <div class="kp-sum"><b style="color:#92400e">{{ totals.exams }}</b>Agenda Ujian</div>
            <div class="kp-sum"><b style="color:#047857">{{ totals.events }}</b>Kegiatan Sekolah</div>
          </div>

          <div v-for="m in monthBlocks" :key="m.key" class="kp-month">
            <div>
              <div class="kp-mtitle">{{ m.title }}</div>
              <table class="kp-grid">
                <thead>
                  <tr>
                    <th>Sen</th><th>Sel</th><th>Rab</th><th>Kam</th><th>Jum</th><th>Sab</th><th class="sun">Min</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(week, wi) in m.weeks" :key="wi">
                    <td v-for="(c, ci) in week" :key="ci" :class="c ? [c.cls, ci === 6 ? 'sun' : ''] : 'empty'" :title="c?.tip || ''">{{ c ? c.day : '' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div>
              <div class="kp-eff">
                <b>Hari efektif: {{ m.effective }} hari</b> <span style="color:#64748b">(Senin–Jumat, di luar libur)</span>
              </div>
              <div v-for="sec in m.sections" :key="sec.title" class="kp-sec">
                <h4><i class="kp-dot" :style="{ background: sec.color }"></i>{{ sec.title }}</h4>
                <div v-for="it in sec.items" :key="it.id" class="kp-item">
                  <span class="d">{{ it.range }}</span>
                  <span>{{ it.description }}</span>
                </div>
              </div>
              <div v-if="m.sections.length === 0" style="color:#94a3b8;font-size:11px">Belum ada agenda pada bulan ini.</div>
            </div>
          </div>
          <div class="kp-foot">Dicetak dari SIST Asy-Syuuraa • {{ printedAt }}</div>
        </div>
      </div>
    </div>

    <!-- Dialog Form Tambah / Edit Kegiatan -->
    <Dialog v-model:visible="dialogVisible" :header="isEditing ? 'Edit Kegiatan Akademik' : 'Tambah Kegiatan Akademik'" modal class="w-full max-w-lg" :breakpoints="{ '960px': '75vw', '640px': '95vw' }">
      <div class="flex flex-col gap-3 py-1 text-sm">
        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium text-slate-600 dark:text-slate-300">Tahun Ajaran <span class="text-red-500">*</span></label>
          <Select v-model="form.academic_year_id" :options="academicYears" optionLabel="label" optionValue="id" placeholder="Pilih Tahun Ajaran" size="small" fluid />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="flex flex-col gap-1">
            <label class="text-xs font-medium text-slate-600 dark:text-slate-300">Tanggal Mulai <span class="text-red-500">*</span></label>
            <DatePicker v-model="form.date" dateFormat="dd/mm/yy" showIcon size="small" fluid placeholder="Pilih tanggal" />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-xs font-medium text-slate-600 dark:text-slate-300">Tanggal Selesai <span class="text-[10px] text-slate-400">(opsional)</span></label>
            <DatePicker v-model="form.end_date" dateFormat="dd/mm/yy" showIcon showButtonBar :minDate="form.date || undefined" size="small" fluid placeholder="Pilih tanggal" />
          </div>
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium text-slate-600 dark:text-slate-300">Tipe Kegiatan <span class="text-red-500">*</span></label>
          <Select v-model="form.type" :options="eventTypes" optionLabel="label" optionValue="value" placeholder="Pilih Tipe Kegiatan" size="small" fluid @change="handleTypeChange" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-xs font-medium text-slate-600 dark:text-slate-300">Keterangan / Nama Kegiatan <span class="text-red-500">*</span></label>
          <InputText v-model="form.description" placeholder="Contoh: Libur Awal Ramadhan 1447 H" size="small" fluid />
        </div>
        <div class="flex items-center gap-2 p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-200 dark:border-slate-700">
          <Checkbox v-model="form.is_holiday" :binary="true" inputId="is_holiday" />
          <label for="is_holiday" class="text-xs text-slate-700 dark:text-slate-300 cursor-pointer select-none">Tandai sebagai Hari Libur Resmi (bebas kewajiban presensi)</label>
        </div>
      </div>
      <template #footer>
        <Button label="Batal" text severity="secondary" size="small" @click="dialogVisible = false" />
        <Button label="Simpan Kegiatan" icon="pi pi-save" size="small" @click="saveEvent" :loading="saving" />
      </template>
    </Dialog>

    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { useConfirm } from "primevue/useconfirm"
import { useToast } from "primevue/usetoast"

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const confirm = useConfirm()
const toast = useToast()

const loading = ref(false)
const saving = ref(false)
const events = ref<any[]>([])        // events of selected academic-year row (list tab)
const allEvents = ref<any[]>([])     // all events (calendar tab)
const academicYears = ref<any[]>([])
const selectedAcademicYearId = ref<number | null>(null)
const dialogVisible = ref(false)
const isEditing = ref(false)
const searchQuery = ref('')
const filterType = ref('ALL')
const activeTab = ref<'list' | 'calendar'>('list')

// ---- Form ----
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
  { label: 'Event Sekolah', value: 'EVENT' },
]
const typeFilterOptions = [
  { label: 'Semua Tipe', value: 'ALL' },
  { label: 'Hari Efektif', value: 'EFFECTIVE' },
  { label: 'Libur', value: 'HOLIDAY' },
  { label: 'Ujian', value: 'EXAM' },
  { label: 'Event Sekolah', value: 'EVENT' },
]
const legendItems = [
  { label: 'Hari Efektif', title: 'KBM Biasa', desc: 'Wajib presensi kehadiran guru dan siswa', cls: 'bg-blue-50 text-blue-700 border-blue-200' },
  { label: 'Libur', title: 'Tanggal Merah / Cuti', desc: 'Sistem presensi meniadakan kewajiban absen', cls: 'bg-red-50 text-red-700 border-red-200' },
  { label: 'Ujian', title: 'PTS, PAS, Asesmen / US', desc: 'Fokus ujian, tidak ada KBM reguler', cls: 'bg-amber-50 text-amber-700 border-amber-200' },
  { label: 'Kegiatan', title: 'Acara & Perlombaan', desc: 'Classmeeting, Lomba, Upacara, Manasik', cls: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
]

// ---- Stats ----
const isHolidayEv = (e: any) => e.type === 'HOLIDAY' || !!e.is_holiday
const statCards = computed(() => [
  { label: 'Total Agenda', value: events.value.length, color: 'text-slate-800 dark:text-white', icon: 'pi-calendar' },
  { label: 'Hari Libur', value: events.value.filter(isHolidayEv).length, color: 'text-red-600', icon: 'pi-flag' },
  { label: 'Jadwal Ujian', value: events.value.filter(e => e.type === 'EXAM').length, color: 'text-amber-600', icon: 'pi-file-edit' },
  { label: 'Event Sekolah', value: events.value.filter(e => e.type === 'EVENT').length, color: 'text-purple-600', icon: 'pi-sparkles' },
])
const activeYearLabel = computed(() => academicYears.value.find(y => y.id === selectedAcademicYearId.value)?.label || 'Seluruh Kegiatan')

const filteredEvents = computed(() =>
  events.value.filter(e => {
    if (filterType.value !== 'ALL' && e.type !== filterType.value) return false
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      return (e.description || '').toLowerCase().includes(q) || getEventLabel(e.type).toLowerCase().includes(q)
    }
    return true
  })
)

function handleTypeChange() {
  if (form.type === 'HOLIDAY') form.is_holiday = true
}

// ---- Fetch ----
async function fetchAcademicYears() {
  try {
    const data = await api.get<any[]>('/academic/years')
    academicYears.value = (data || []).map(y => ({
      id: y.id,
      name: y.name,
      semester: y.semester,
      label: `${y.name} - Semester ${y.semester}${y.is_active ? ' (Aktif)' : ''}`,
      is_active: y.is_active,
    }))
    const active = academicYears.value.find(y => y.is_active) || academicYears.value[0]
    if (active) {
      selectedAcademicYearId.value = active.id
      viewYearName.value = active.name
      viewSemester.value = active.semester === 'Genap' ? 'Genap' : 'Ganjil'
      initViewMonth()
    }
  } catch (e) {
    console.error('Gagal memuat tahun ajaran:', e)
  }
}

async function fetchEvents() {
  loading.value = true
  try {
    const q = selectedAcademicYearId.value ? `?academic_year_id=${selectedAcademicYearId.value}&limit=1000` : '?limit=1000'
    events.value = (await api.get<any[]>(`/academic-calendar${q}`)) || []
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data kalender pendidikan', life: 3000 })
  } finally {
    loading.value = false
  }
}
async function fetchAllEvents() {
  try {
    allEvents.value = (await api.get<any[]>('/academic-calendar?limit=2000')) || []
  } catch { allEvents.value = [] }
}
async function refreshAll() {
  await Promise.all([fetchEvents(), fetchAllEvents()])
}
function onYearRowChange() {
  const row = academicYears.value.find(y => y.id === selectedAcademicYearId.value)
  if (row) {
    viewYearName.value = row.name
    viewSemester.value = row.semester === 'Genap' ? 'Genap' : 'Ganjil'
    initViewMonth()
  }
  fetchEvents()
}

// ---- Dialog CRUD ----
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

function toLocalDateString(d: Date | string | null): string | null {
  if (!d) return null
  const dt = new Date(d)
  if (isNaN(dt.getTime())) return null
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}T00:00:00`
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
      academic_year_id: form.academic_year_id || selectedAcademicYearId.value,
    }
    if (isEditing.value && form.id) {
      await api.put(`/academic-calendar/${form.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kegiatan berhasil diperbarui', life: 3000 })
    } else {
      await api.post('/academic-calendar', payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kegiatan berhasil ditambahkan', life: 3000 })
    }
    dialogVisible.value = false
    await refreshAll()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.data?.detail || e.message || 'Gagal menyimpan kegiatan', life: 4000 })
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
        await refreshAll()
      } catch (e: any) {
        toast.add({ severity: 'error', summary: 'Error', detail: e.data?.detail || e.message || 'Gagal menghapus kegiatan', life: 3000 })
      }
    },
  })
}

// ---- Utils ----
function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' })
}
function getEventSeverity(type: string) {
  return type === 'HOLIDAY' ? 'danger' : type === 'EXAM' ? 'warn' : type === 'EVENT' ? 'success' : 'info'
}
function getEventLabel(type: string) {
  return eventTypes.find(t => t.value === type)?.label || type
}

// =====================================================================
// CALENDAR VIEW
// =====================================================================
const MONTH_NAMES = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
const MONTH_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

const viewYearName = ref('')
const viewMode = ref<'month' | 'semester' | 'year'>('semester')
const viewSemester = ref<'Ganjil' | 'Genap'>('Ganjil')
const viewMonthIdx = ref(0) // 0..11 within the academic year (0 = Juli)
const printedAt = ref('')

const yearNames = computed(() => Array.from(new Set(academicYears.value.map(y => y.name))))
const startYear = computed(() => {
  const n = parseInt((viewYearName.value || '').split('/')[0])
  return isNaN(n) ? new Date().getFullYear() : n
})

// Academic year runs Jul (startYear) .. Jun (startYear + 1)
const academicMonths = computed(() =>
  Array.from({ length: 12 }, (_, i) => {
    const m = (6 + i) % 12
    const y = i < 6 ? startYear.value : startYear.value + 1
    return { y, m }
  })
)
const monthOptions = computed(() =>
  academicMonths.value.map((x, i) => ({ label: `${MONTH_NAMES[x.m]} ${x.y}`, value: i }))
)

function initViewMonth() {
  const now = new Date()
  const idx = academicMonths.value.findIndex(x => x.y === now.getFullYear() && x.m === now.getMonth())
  viewMonthIdx.value = idx >= 0 ? idx : (viewSemester.value === 'Genap' ? 6 : 0)
}
function onViewYearChange() {
  initViewMonth()
}

const visibleMonths = computed(() => {
  if (viewMode.value === 'month') return [academicMonths.value[viewMonthIdx.value]].filter(Boolean)
  if (viewMode.value === 'semester') return viewSemester.value === 'Ganjil' ? academicMonths.value.slice(0, 6) : academicMonths.value.slice(6)
  return academicMonths.value
})

const viewTitle = computed(() => {
  if (viewMode.value === 'month') {
    const x = visibleMonths.value[0]
    return x ? `Bulan ${MONTH_NAMES[x.m]} ${x.y} • Tahun Ajaran ${viewYearName.value}` : ''
  }
  if (viewMode.value === 'semester') return `Semester ${viewSemester.value} • Tahun Ajaran ${viewYearName.value}`
  return `Tahun Ajaran ${viewYearName.value}`
})

const pad = (n: number) => String(n).padStart(2, '0')
const keyOf = (y: number, m: number, d: number) => `${y}-${pad(m + 1)}-${pad(d)}`
const strKey = (s: string) => (s || '').slice(0, 10)
const parseKey = (k: string) => {
  const [y, m, d] = k.split('-').map(Number)
  return new Date(y, m - 1, d)
}
function eachDayKey(startK: string, endK: string, cb: (k: string, dt: Date) => void) {
  const s = parseKey(startK)
  const e = parseKey(endK < startK ? startK : endK)
  let guard = 0
  for (const dt = new Date(s); dt <= e && guard < 400; dt.setDate(dt.getDate() + 1), guard++) {
    cb(keyOf(dt.getFullYear(), dt.getMonth(), dt.getDate()), dt)
  }
}
const evKind = (e: any): 'holiday' | 'exam' | 'event' | 'effective' =>
  isHolidayEv(e) ? 'holiday' : e.type === 'EXAM' ? 'exam' : e.type === 'EVENT' ? 'event' : 'effective'

// Coverage map: dateKey -> { kinds:Set, tips:string[] }
const coverage = computed(() => {
  const map = new Map<string, { kinds: Set<string>; tips: string[] }>()
  for (const e of allEvents.value) {
    const sk = strKey(e.date)
    if (!sk) continue
    const ek = e.end_date ? strKey(e.end_date) : sk
    const kind = evKind(e)
    eachDayKey(sk, ek, (k) => {
      let c = map.get(k)
      if (!c) { c = { kinds: new Set(), tips: [] }; map.set(k, c) }
      c.kinds.add(kind)
      c.tips.push(e.description)
    })
  }
  return map
})

function cellClass(kinds?: Set<string>) {
  if (!kinds) return ''
  if (kinds.has('holiday')) return 'holiday'
  if (kinds.has('exam')) return 'exam'
  if (kinds.has('event')) return 'event'
  if (kinds.has('effective')) return 'effective'
  return ''
}

function fmtRange(sk: string, ek: string) {
  const s = parseKey(sk), e = parseKey(ek)
  if (sk === ek) return `${s.getDate()} ${MONTH_SHORT[s.getMonth()]} ${s.getFullYear()}`
  if (s.getFullYear() === e.getFullYear() && s.getMonth() === e.getMonth()) {
    return `${s.getDate()}–${e.getDate()} ${MONTH_SHORT[s.getMonth()]} ${s.getFullYear()}`
  }
  if (s.getFullYear() === e.getFullYear()) {
    return `${s.getDate()} ${MONTH_SHORT[s.getMonth()]} – ${e.getDate()} ${MONTH_SHORT[e.getMonth()]} ${s.getFullYear()}`
  }
  return `${s.getDate()} ${MONTH_SHORT[s.getMonth()]} ${s.getFullYear()} – ${e.getDate()} ${MONTH_SHORT[e.getMonth()]} ${e.getFullYear()}`
}

const SECTION_DEFS = [
  { kind: 'effective', title: 'Periode Hari Efektif', color: '#93c5fd' },
  { kind: 'holiday', title: 'Libur', color: '#fca5a5' },
  { kind: 'exam', title: 'Ujian', color: '#fcd34d' },
  { kind: 'event', title: 'Kegiatan Yayasan / Sekolah', color: '#6ee7b7' },
]

function buildMonth(y: number, m: number) {
  const first = new Date(y, m, 1)
  const daysIn = new Date(y, m + 1, 0).getDate()
  const offset = (first.getDay() + 6) % 7 // Monday = 0
  const cells: any[] = []
  for (let i = 0; i < offset; i++) cells.push(null)
  let effective = 0
  let holidayDays = 0
  for (let d = 1; d <= daysIn; d++) {
    const k = keyOf(y, m, d)
    const cov = coverage.value.get(k)
    const dow = new Date(y, m, d).getDay()
    const weekday = dow !== 0 && dow !== 6
    const isHoliday = !!cov?.kinds.has('holiday')
    if (weekday) {
      if (isHoliday) holidayDays++
      else effective++
    }
    cells.push({ day: d, cls: cellClass(cov?.kinds), tip: cov ? cov.tips.join(' • ') : '' })
  }
  while (cells.length % 7 !== 0) cells.push(null)
  const weeks: any[][] = []
  for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7))

  // events overlapping this month
  const mStart = keyOf(y, m, 1), mEnd = keyOf(y, m, daysIn)
  const inMonth = allEvents.value
    .filter(e => {
      const sk = strKey(e.date); const ek = e.end_date ? strKey(e.end_date) : sk
      return sk <= mEnd && ek >= mStart
    })
    .sort((a, b) => strKey(a.date).localeCompare(strKey(b.date)))
  const sections = SECTION_DEFS
    .map(def => ({
      title: def.title,
      color: def.color,
      items: inMonth.filter(e => evKind(e) === def.kind).map(e => ({
        id: e.id,
        range: fmtRange(strKey(e.date), e.end_date ? strKey(e.end_date) : strKey(e.date)),
        description: e.description,
      })),
    }))
    .filter(s => s.items.length > 0)

  return {
    key: `${y}-${m}`,
    title: `${MONTH_NAMES[m]} ${y}`,
    weeks,
    effective,
    holidayDays,
    sections,
    examCount: inMonth.filter(e => evKind(e) === 'exam').length,
    eventCount: inMonth.filter(e => evKind(e) === 'event').length,
  }
}

const monthBlocks = computed(() => visibleMonths.value.map(x => buildMonth(x.y, x.m)))

const totals = computed(() => {
  // exam/event counted once per agenda, not per month
  const range = visibleMonths.value
  if (range.length === 0) return { effective: 0, holidayDays: 0, exams: 0, events: 0 }
  const first = range[0], last = range[range.length - 1]
  const rs = keyOf(first.y, first.m, 1)
  const re = keyOf(last.y, last.m, new Date(last.y, last.m + 1, 0).getDate())
  const inRange = allEvents.value.filter(e => {
    const sk = strKey(e.date); const ek = e.end_date ? strKey(e.end_date) : sk
    return sk <= re && ek >= rs
  })
  return {
    effective: monthBlocks.value.reduce((a, b) => a + b.effective, 0),
    holidayDays: monthBlocks.value.reduce((a, b) => a + b.holidayDays, 0),
    exams: inRange.filter(e => evKind(e) === 'exam').length,
    events: inRange.filter(e => evKind(e) === 'event').length,
  }
})

// ---- Print / PDF ----
const PRINT_CSS = `
.kp-paper{background:#fff;color:#1e293b;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;font-size:12px;padding:18px;border:1px solid #e2e8f0;border-radius:12px;min-width:640px;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.kp-head{text-align:center;border-bottom:2px solid #0f766e;padding-bottom:8px;margin-bottom:8px}
.kp-head h2{font-size:17px;margin:0;font-weight:700;letter-spacing:.5px}
.kp-head p{margin:2px 0 0;font-size:11px;color:#475569}
.kp-legend{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;font-size:10px;margin:6px 0 10px;color:#475569}
.kp-dot{width:10px;height:10px;border-radius:2px;display:inline-block;margin-right:5px;vertical-align:-1px;border:1px solid rgba(0,0,0,.08)}
.kp-summary{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}
.kp-sum{border:1px solid #e2e8f0;border-radius:8px;padding:6px 8px;text-align:center;font-size:10px;color:#64748b}
.kp-sum b{display:block;font-size:16px;color:#0f172a}
.kp-month{display:grid;grid-template-columns:1.15fr 1fr;gap:14px;margin-bottom:12px;border:1px solid #e2e8f0;border-radius:10px;padding:10px;break-inside:avoid;page-break-inside:avoid}
.kp-mtitle{font-weight:700;font-size:13px;color:#0f766e;margin-bottom:6px}
.kp-grid{width:100%;border-collapse:collapse;table-layout:fixed}
.kp-grid th{font-size:10px;padding:3px 0;background:#f1f5f9;color:#475569;border:1px solid #e2e8f0;font-weight:600}
.kp-grid th.sun{color:#dc2626}
.kp-grid td{height:28px;border:1px solid #e2e8f0;text-align:center;vertical-align:middle;font-size:11px}
.kp-grid td.empty{background:#fafafa}
.kp-grid td.sun{color:#dc2626}
.kp-grid td.effective{background:#dbeafe}
.kp-grid td.event{background:#d1fae5;color:#047857;font-weight:700}
.kp-grid td.exam{background:#fef3c7;color:#92400e;font-weight:700}
.kp-grid td.holiday{background:#fee2e2;color:#b91c1c;font-weight:700}
.kp-eff{background:#eff6ff;border:1px solid #bfdbfe;border-radius:6px;padding:5px 8px;font-size:11px;margin-bottom:8px}
.kp-sec{margin-bottom:8px}
.kp-sec h4{font-size:11px;margin:0 0 3px;font-weight:700;color:#334155}
.kp-item{display:flex;gap:8px;font-size:11px;padding:2px 0;border-bottom:1px dotted #e2e8f0;line-height:1.35}
.kp-item .d{width:104px;flex:none;color:#475569;font-weight:600}
.kp-foot{text-align:right;font-size:9px;color:#94a3b8;margin-top:6px}
@media screen and (max-width:720px){.kp-month{grid-template-columns:1fr}.kp-summary{grid-template-columns:repeat(2,1fr)}}
`
useHead({ style: [{ key: 'kalender-print-css', innerHTML: PRINT_CSS }] })

function printCalendar() {
  printedAt.value = new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
  nextTick(() => {
    const el = document.getElementById('kalender-print')
    if (!el) return
    const w = window.open('', '_blank')
    if (!w) {
      toast.add({ severity: 'warn', summary: 'Pop-up diblokir', detail: 'Izinkan pop-up untuk mencetak/menyimpan PDF', life: 4000 })
      return
    }
    const title = `Kalender Pendidikan ${viewTitle.value}`
    w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${title}</title><style>${PRINT_CSS}
      body{margin:0;background:#fff}
      .kp-paper{border:none;border-radius:0;padding:0;min-width:0}
      @page{size:A4 portrait;margin:12mm}
    </style></head><body>${el.outerHTML}</body></html>`)
    w.document.close()
    w.focus()
    setTimeout(() => w.print(), 400)
  })
}

onMounted(async () => {
  printedAt.value = new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
  await fetchAcademicYears()
  await refreshAll()
})
</script>
