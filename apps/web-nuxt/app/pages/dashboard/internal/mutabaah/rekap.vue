<template>
  <div class="space-y-6">
    <!-- Header with KPI statistics -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <i class="pi pi-chart-bar text-primary text-2xl"></i>
          Rekapitulasi Mutaba'ah
        </h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1">Laporan pencapaian ibadah, tilawah, dan pembiasaan seluruh pegawai.</p>
      </div>
      <div class="flex gap-2">
        <Button label="Export Excel/CSV" icon="pi pi-file-excel" severity="success" @click="exportCSV" />
        <Button label="Cetak Laporan" icon="pi pi-print" severity="secondary" @click="printReport" />
      </div>
    </div>

    <!-- Filters Panel -->
    <div class="card bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Tarbiyah Cycle Dropdown -->
        <div class="flex flex-col gap-2">
          <label class="font-semibold text-slate-700 dark:text-slate-300">Siklus Tarbiyah (Bulan):</label>
          <Select
            v-model="selectedCycle"
            :options="cycleOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Pilih Siklus"
            class="w-full"
            @change="fetchRekapData"
          />
        </div>

        <!-- Unit Filter -->
        <div class="flex flex-col gap-2">
          <label class="font-semibold text-slate-700 dark:text-slate-300">Unit Sekolah:</label>
          <Select
            v-model="selectedUnit"
            :options="unitOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Semua Unit"
            class="w-full"
            @change="fetchRekapData"
          />
        </div>

        <!-- Search input -->
        <div class="flex flex-col gap-2">
          <label class="font-semibold text-slate-700 dark:text-slate-300">Cari Pegawai:</label>
          <InputText
            v-model="searchQuery"
            placeholder="Nama atau NIP..."
            class="w-full"
          />
        </div>
      </div>
    </div>

    <!-- KPI Summary Row -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-emerald-50 dark:bg-emerald-950/30 flex items-center justify-center text-emerald-500 text-xl font-bold">
          <i class="pi pi-check-square"></i>
        </div>
        <div>
          <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Rata-rata Pengisian</p>
          <h3 class="text-2xl font-extrabold text-slate-800 dark:text-white mt-1">{{ avgDaysFilledPercent }}%</h3>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-950/30 flex items-center justify-center text-blue-500 text-xl font-bold">
          <i class="pi pi-book"></i>
        </div>
        <div>
          <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Rerata Tilawah</p>
          <h3 class="text-2xl font-extrabold text-slate-800 dark:text-white mt-1">{{ avgTilawahPages }} <span class="text-xs font-normal text-slate-400">hal/hari</span></h3>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-indigo-50 dark:bg-indigo-950/30 flex items-center justify-center text-indigo-500 text-xl font-bold">
          <i class="pi pi-star"></i>
        </div>
        <div>
          <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Kepatuhan Harian</p>
          <h3 class="text-2xl font-extrabold text-slate-800 dark:text-white mt-1">{{ avgDailyCompliance }}%</h3>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-rose-50 dark:bg-rose-950/30 flex items-center justify-center text-rose-500 text-xl font-bold">
          <i class="pi pi-calendar-times"></i>
        </div>
        <div>
          <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Kepatuhan Pekanan</p>
          <h3 class="text-2xl font-extrabold text-slate-800 dark:text-white mt-1">{{ avgWeeklyCompliance }}%</h3>
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm">
      <DataTable
        ref="dt"
        :value="filteredRecords"
        :loading="loading"
        stripedRows
        responsiveLayout="scroll"
        class="text-sm"
        :paginator="true"
        :rows="10"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Menampilkan {first} sampai {last} dari {totalRecords} pegawai"
      >
        <Column header="Nama Pegawai" style="min-width: 200px">
          <template #body="{ data }">
            <div class="font-bold text-slate-800 dark:text-white">{{ data.name }}</div>
            <div class="text-xs text-slate-400 mt-0.5">NIP/NIK: {{ data.nip }}</div>
          </template>
        </Column>

        <Column header="Role" style="min-width: 130px">
          <template #body="{ data }">
            <Tag :value="data.role_name" severity="secondary" />
          </template>
        </Column>

        <Column header="Unit" style="min-width: 100px">
          <template #body="{ data }">
            <span class="font-semibold text-slate-600 dark:text-slate-300">{{ data.unit_name }}</span>
          </template>
        </Column>

        <Column header="Hari Diisi" style="min-width: 110px">
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <span class="font-semibold">{{ data.days_filled }} / {{ data.total_days }}</span>
              <span class="text-xxs text-slate-400">({{ roundPct(data.days_filled / data.total_days * 100) }}%)</span>
            </div>
          </template>
        </Column>

        <Column header="Tilawah (Rerata)" style="min-width: 140px">
          <template #body="{ data }">
            <span class="font-bold" :class="data.avg_tilawah >= 10 ? 'text-emerald-500' : 'text-slate-600 dark:text-slate-300'">
              {{ data.avg_tilawah }} lembar/hal
            </span>
          </template>
        </Column>

        <Column header="Kepatuhan Harian" style="min-width: 140px">
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <div class="flex-1 w-16 bg-slate-100 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                <div class="h-full rounded-full transition-all" :class="getScoreColor(data.daily_percentage)" :style="{ width: data.daily_percentage + '%' }"></div>
              </div>
              <span class="font-bold">{{ data.daily_percentage }}%</span>
            </div>
          </template>
        </Column>

        <Column header="Kepatuhan Pekanan" style="min-width: 140px">
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <div class="flex-1 w-16 bg-slate-100 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                <div class="h-full rounded-full transition-all" :class="getScoreColor(data.weekly_percentage)" :style="{ width: data.weekly_percentage + '%' }"></div>
              </div>
              <span class="font-bold">{{ data.weekly_percentage }}%</span>
            </div>
          </template>
        </Column>

        <Column header="Skor Indeks" style="min-width: 120px">
          <template #body="{ data }">
            <Tag :value="data.overall_score + '%'" :severity="getScoreSeverity(data.overall_score)" class="text-sm font-extrabold px-3 py-1" />
          </template>
        </Column>

        <template #empty>
          <div class="text-center py-8 text-slate-400">
            <i class="pi pi-users text-4xl mb-3 block"></i>
            <p>Tidak ada data laporan ditemukan untuk filter yang dipilih.</p>
          </div>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const dt = ref<any>(null)

// State
const loading = ref(false)
const searchQuery = ref('')
const selectedUnit = ref<string>('')
const selectedCycle = ref<string>('')
const cycleOptions = ref<{ label: string; value: string }[]>([])
const unitOptions = ref<{ label: string; value: string }[]>([{ label: 'Semua Unit', value: '' }])
const rekapRecords = ref<any[]>([])

// Generate Tarbiyah Cycle Option Lists (26th of month M-1 to 25th of month M)
function generateCycleOptions() {
  const options = []
  const today = new Date()
  
  // Create options for past 5 months
  for (let i = 0; i < 5; i++) {
    const current = new Date(today.getFullYear(), today.getMonth() - i, 15)
    const year = current.getFullYear()
    const month = current.getMonth() // 0-indexed
    
    // Names of months in Indonesian
    const monthsName = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    // Start bounds: 26th of month M-1
    const prevMonthIdx = month === 0 ? 11 : month - 1
    const prevMonthYear = month === 0 ? year - 1 : year
    const startStr = `${prevMonthYear}-${String(prevMonthIdx + 1).padStart(2, '0')}-26`
    
    // End bounds: 25th of month M
    const endStr = `${year}-${String(month + 1).padStart(2, '0')}-25`
    
    const currentMonthName = monthsName[month] || ''
    const prevMonthName = monthsName[prevMonthIdx] || ''
    
    options.push({
      label: `Siklus ${currentMonthName} ${year} (26 ${prevMonthName.substring(0,3)} - 25 ${currentMonthName.substring(0,3)})`,
      value: `${startStr}|${endStr}`
    })
  }
  
  cycleOptions.value = options
  const firstOpt = options[0]
  if (firstOpt) {
    selectedCycle.value = firstOpt.value
  }
}

// Fetch Units to populate dropdown
async function fetchUnits() {
  try {
    const units = await api.get<any[]>('/units')
    units.forEach(u => {
      unitOptions.value.push({
        label: u.name,
        value: String(u.id)
      })
    })
  } catch (e) {
    console.error('Failed to load units list', e)
  }
}

// Fetch report stats
async function fetchRekapData() {
  if (!selectedCycle.value) return
  loading.value = true
  
  const [start, end] = selectedCycle.value.split('|')
  
  try {
    let url = `/internal/mutabaah/rekap?start_date=${start}&end_date=${end}`
    if (selectedUnit.value) {
      url += `&unit_id=${selectedUnit.value}`
    }
    
    rekapRecords.value = await api.get<any[]>(url)
  } catch (e: any) {
    console.error('Failed to fetch rekap mutabaah report', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.message || 'Gagal memuat rekap laporan mutabaah', life: 3000 })
  } finally {
    loading.value = false
  }
}

// Search Filter computed
const filteredRecords = computed(() => {
  if (!searchQuery.value.trim()) {
    return rekapRecords.value
  }
  const q = searchQuery.value.toLowerCase().trim()
  return rekapRecords.value.filter(rec => 
    rec.name.toLowerCase().includes(q) || 
    rec.nip.toLowerCase().includes(q) ||
    rec.role_name.toLowerCase().includes(q)
  )
})

// KPI Aggregation computed values
const avgDaysFilledPercent = computed(() => {
  if (filteredRecords.value.length === 0) return 0
  const sum = filteredRecords.value.reduce((acc, rec) => acc + (rec.days_filled / rec.total_days), 0)
  return Math.round((sum / filteredRecords.value.length) * 100)
})

const avgTilawahPages = computed(() => {
  if (filteredRecords.value.length === 0) return 0
  const sum = filteredRecords.value.reduce((acc, rec) => acc + rec.avg_tilawah, 0)
  return Math.round((sum / filteredRecords.value.length) * 10) / 10
})

const avgDailyCompliance = computed(() => {
  if (filteredRecords.value.length === 0) return 0
  const sum = filteredRecords.value.reduce((acc, rec) => acc + rec.daily_percentage, 0)
  return Math.round(sum / filteredRecords.value.length)
})

const avgWeeklyCompliance = computed(() => {
  if (filteredRecords.value.length === 0) return 0
  const sum = filteredRecords.value.reduce((acc, rec) => acc + rec.weekly_percentage, 0)
  return Math.round(sum / filteredRecords.value.length)
})

// Helpers
function roundPct(val: number) {
  return Math.round(val)
}

function getScoreColor(val: number) {
  if (val >= 85) return 'bg-emerald-500'
  if (val >= 70) return 'bg-blue-500'
  return 'bg-amber-500'
}

function getScoreSeverity(val: number) {
  if (val >= 85) return 'success'
  if (val >= 70) return 'info'
  return 'warn'
}

// Print report
function printReport() {
  window.print()
}

// Export CSV
function exportCSV() {
  if (dt.value) {
    dt.value.exportCSV()
  }
}

onMounted(async () => {
  generateCycleOptions()
  await fetchUnits()
  await fetchRekapData()
})
</script>

<style scoped>
.text-xxs {
  font-size: 0.65rem;
}

@media print {
  /* Print layouts premium cleanup */
  body * {
    visibility: hidden;
  }
  .card, .card *, DataTable, DataTable * {
    visibility: visible;
  }
  .card {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
  }
}
</style>
