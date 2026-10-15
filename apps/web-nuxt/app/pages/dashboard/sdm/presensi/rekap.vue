<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <i class="pi pi-chart-bar text-emerald-600"></i>
          Rekapitulasi Presensi Pegawai
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
          Laporan agregat kehadiran, keterlambatan, izin, dan cuti pegawai per bulan.
        </p>
      </div>
      <div class="flex gap-2">
        <NuxtLink 
          to="/dashboard/sdm/presensi"
          class="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 rounded-xl shadow-sm transition"
        >
          <i class="pi pi-arrow-left text-xs"></i>
          Presensi Harian
        </NuxtLink>
        <Button 
          label="Export Excel (CSV)" 
          icon="pi pi-file-excel" 
          severity="success" 
          outlined 
          size="small"
          class="text-xs font-semibold"
          @click="exportExcel" 
          :disabled="recapData.length === 0 || monthlyStats.totalTercatat === 0" 
        />
      </div>
    </div>

    <!-- Filter Bar -->
    <Card>
      <template #content>
        <div class="flex flex-wrap gap-4 items-end justify-between">
          <div class="flex flex-wrap gap-4 items-end">
            <div>
              <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Pilih Bulan &amp; Tahun</label>
              <Calendar 
                v-model="filterMonth" 
                view="month" 
                dateFormat="mm/yy" 
                :showIcon="true" 
                class="w-48 text-xs" 
                @date-select="fetchData" 
              />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Pilih Unit Sekolah</label>
              <Dropdown 
                v-model="filterUnit" 
                :options="units" 
                optionLabel="name" 
                optionValue="id" 
                placeholder="Semua Unit" 
                showClear 
                class="w-56 text-xs" 
                @change="fetchData" 
              />
            </div>
          </div>

          <div>
            <Button 
              label="Tampilkan Laporan" 
              icon="pi pi-search" 
              size="small" 
              class="text-xs font-semibold"
              @click="fetchData" 
              :loading="loading" 
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Monthly KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" v-if="recapData.length > 0">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 flex items-center justify-center shrink-0">
          <i class="pi pi-users text-xl"></i>
        </div>
        <div>
          <div class="text-xs text-slate-500 font-medium">Total Pegawai Terdaftar</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white mt-0.5">{{ monthlyStats.totalEmployees }} Orang</div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 flex items-center justify-center shrink-0">
          <i class="pi pi-chart-pie text-xl"></i>
        </div>
        <div>
          <div class="text-xs text-slate-500 font-medium">Rata-rata Kehadiran</div>
          <div class="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">{{ monthlyStats.avgPresence }}%</div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 flex items-center justify-center shrink-0">
          <i class="pi pi-check-circle text-xl"></i>
        </div>
        <div>
          <div class="text-xs text-slate-500 font-medium">Total Hari Hadir Staf</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white mt-0.5">{{ monthlyStats.totalHadir }} Kali</div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 flex items-center justify-center shrink-0">
          <i class="pi pi-calendar-times text-xl"></i>
        </div>
        <div>
          <div class="text-xs text-slate-500 font-medium">Izin / Sakit / Cuti</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white mt-0.5">{{ monthlyStats.totalIzinSakitCuti }} Kali</div>
        </div>
      </div>
    </div>

    <!-- Empty State Alert when zero records found for the whole month -->
    <div 
      v-if="hasFetched && monthlyStats.totalTercatat === 0" 
      class="p-6 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left"
    >
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-300 flex items-center justify-center shrink-0">
          <i class="pi pi-inbox text-2xl"></i>
        </div>
        <div>
          <h3 class="font-bold text-slate-800 dark:text-white text-base">Belum Ada Presensi yang Tersimpan untuk Bulan {{ formattedMonth }}</h3>
          <p class="text-xs text-amber-800 dark:text-amber-300 mt-1 max-w-xl">
            Tabel rekap saat ini masih bernilai 0 karena belum ada rekaman kehadiran harian yang disimpan di menu <b>Presensi Harian</b> untuk bulan ini.
          </p>
        </div>
      </div>
      <NuxtLink 
        to="/dashboard/sdm/presensi"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-sm transition shrink-0"
      >
        <i class="pi pi-calendar-plus"></i>
        Buka Presensi Hari Ini
      </NuxtLink>
    </div>

    <!-- Data Table -->
    <Card v-if="recapData.length > 0">
      <template #content>
        <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white">Laporan Presensi Bulan: {{ formattedMonth }}</h2>
            <p class="text-xs text-slate-400 mt-0.5">Rekapitulasi otomatis dari check-in GPS mandiri dan verifikasi TU.</p>
          </div>
          <span class="text-xs text-slate-500 font-medium bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-full">
            {{ recapData.length }} Pegawai Aktif
          </span>
        </div>
        
        <DataTable 
          :value="recapData" 
          :loading="loading" 
          paginator 
          :rows="20" 
          dataKey="employee_id" 
          class="p-datatable-sm" 
          stripedRows 
          responsiveLayout="scroll"
        >
          <Column field="nama_lengkap" header="Nama Pegawai" sortable style="min-width: 220px">
            <template #body="{ data }">
              <div class="font-semibold text-slate-800 dark:text-white">{{ data.nama_lengkap }}</div>
              <div class="text-xs text-slate-400">NIP: {{ data.nip || '-' }}</div>
            </template>
          </Column>

          <Column field="hadir" header="Hadir Tepat" sortable style="width: 100px">
            <template #body="{ data }">
              <span class="font-bold text-emerald-600">{{ data.hadir }}</span>
            </template>
          </Column>

          <Column field="terlambat" header="Terlambat" sortable style="width: 100px">
            <template #body="{ data }">
              <span class="font-semibold text-amber-600">{{ data.terlambat || 0 }}</span>
            </template>
          </Column>

          <Column field="sakit" header="Sakit" sortable style="width: 80px">
            <template #body="{ data }">
              <span class="font-semibold text-yellow-600">{{ data.sakit }}</span>
            </template>
          </Column>

          <Column field="izin" header="Izin" sortable style="width: 80px">
            <template #body="{ data }">
              <span class="font-semibold text-blue-600">{{ data.izin }}</span>
            </template>
          </Column>

          <Column field="cuti" header="Cuti" sortable style="width: 80px">
            <template #body="{ data }">
              <span class="font-semibold text-purple-600">{{ data.cuti || 0 }}</span>
            </template>
          </Column>

          <Column field="alpa" header="Alpa" sortable style="width: 80px">
            <template #body="{ data }">
              <span class="font-semibold text-rose-600">{{ data.alpa }}</span>
            </template>
          </Column>

          <Column field="total" header="Total Hari" sortable style="width: 110px">
            <template #body="{ data }">
              <span class="font-bold text-slate-700 dark:text-slate-200">{{ data.total }}</span>
            </template>
          </Column>

          <Column field="persentase" header="Tingkat Kehadiran" sortable style="min-width: 160px">
            <template #body="{ data }">
              <div class="space-y-1">
                <div class="flex justify-between text-[11px] font-semibold">
                  <span class="text-slate-600 dark:text-slate-300">{{ data.persentase }}</span>
                </div>
                <ProgressBar 
                  :value="parseFloat(data.persentase) || 0" 
                  :showValue="false" 
                  class="!h-2"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const toast = useToast()
const api = useApi()

const filterMonth = ref(new Date())
const filterUnit = ref(null)
const units = ref<any[]>([])
const recapData = ref<any[]>([])
const loading = ref(false)
const hasFetched = ref(false)

const formattedMonth = computed(() => {
  if (!filterMonth.value) return ''
  return filterMonth.value.toLocaleDateString('id-ID', { year: 'numeric', month: 'long' })
})

const monthlyStats = computed(() => {
  const list = recapData.value || []
  const totalEmployees = list.length
  let totalHadir = 0
  let totalIzinSakitCuti = 0
  let totalTercatat = 0
  let sumPercentage = 0

  for (const item of list) {
    totalHadir += (item.hadir || 0)
    totalIzinSakitCuti += (item.sakit || 0) + (item.izin || 0) + (item.cuti || 0)
    totalTercatat += (item.total || 0)
    const pct = parseFloat(item.persentase) || 0
    sumPercentage += pct
  }

  const avgPresence = totalEmployees > 0 && totalTercatat > 0
    ? (sumPercentage / totalEmployees).toFixed(1)
    : '0.0'

  return { totalEmployees, totalHadir, totalIzinSakitCuti, totalTercatat, avgPresence }
})

const fetchUnits = async () => {
  try {
    const data = await api.get<any[]>('/units')
    units.value = data || []
  } catch (error) {
    console.error('Failed to fetch units')
  }
}

const fetchData = async () => {
  if (!filterMonth.value) return
  
  loading.value = true
  try {
    const d = filterMonth.value
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const monthStr = `${year}-${month}`
    
    const query = new URLSearchParams({ month: monthStr })
    if (filterUnit.value) query.append('unit_id', filterUnit.value)
    
    const data = await api.get<any[]>(`/sdm/attendance/recap?${query.toString()}`)
    recapData.value = data || []
    hasFetched.value = true
  } catch (error) {
    console.error('Fetch recap error:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat rekap presensi', life: 3000 })
  } finally {
    loading.value = false
  }
}

const exportExcel = () => {
  const headers = ['Nama Pegawai', 'NIP', 'Hadir Tepat', 'Terlambat', 'Sakit', 'Izin', 'Cuti', 'Alpa', 'Total Hari', 'Persentase Hadir']
  const rows = recapData.value.map((r: any) => [
    `"${r.nama_lengkap}"`, 
    `"${r.nip || '-'}"`, 
    r.hadir, 
    r.terlambat || 0,
    r.sakit, 
    r.izin, 
    r.cuti || 0,
    r.alpa, 
    r.total, 
    `"${r.persentase}"`
  ])
  
  const csvContent = "data:text/csv;charset=utf-8,\uFEFF" 
    + headers.join(",") + "\n" 
    + rows.map(e => e.join(",")).join("\n")
    
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  const filename = `Rekap_Presensi_${formattedMonth.value.replace(/\s+/g, '_')}.csv`
  link.setAttribute("download", filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  fetchUnits()
  fetchData()
})
</script>
