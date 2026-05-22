<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Rekap Presensi</h1>
        <p class="text-slate-500 dark:text-slate-400">Laporan kehadiran pegawai per bulan.</p>
      </div>
      <Button label="Export Excel" icon="pi pi-file-excel" severity="success" outlined @click="exportExcel" :disabled="recapData.length === 0" />
    </div>

    <!-- Filter Bar -->
    <Card>
      <template #content>
        <div class="flex flex-wrap gap-4 items-end">
          <div>
            <label class="block text-sm font-medium mb-1">Pilih Bulan</label>
            <Calendar v-model="filterMonth" view="month" dateFormat="mm/yy" :showIcon="true" class="w-48" @date-select="fetchData" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Pilih Unit</label>
            <Dropdown v-model="filterUnit" :options="units" optionLabel="name" optionValue="id" placeholder="Semua Unit" showClear class="w-48" @change="fetchData" />
          </div>
          <div class="flex-1 text-right">
            <Button label="Tampilkan Laporan" icon="pi pi-search" @click="fetchData" :loading="loading" />
          </div>
        </div>
      </template>
    </Card>

    <!-- Data Table -->
    <Card v-if="recapData.length > 0">
      <template #content>
        <div class="mb-4">
          <h2 class="font-semibold text-lg text-center">Laporan Presensi Bulan: {{ formattedMonth }}</h2>
        </div>
        
        <DataTable :value="recapData" :loading="loading" paginator :rows="20" dataKey="employee_id" class="p-datatable-sm" stripedRows responsiveLayout="scroll">
          <Column field="nama_lengkap" header="Nama Pegawai" sortable></Column>
          <Column field="nip" header="NIP" sortable></Column>
          <Column field="hadir" header="Hadir" sortable>
            <template #body="{ data }">
              <span class="font-semibold text-green-600">{{ data.hadir }}</span>
            </template>
          </Column>
          <Column field="sakit" header="Sakit" sortable>
            <template #body="{ data }">
              <span class="font-semibold text-yellow-600">{{ data.sakit }}</span>
            </template>
          </Column>
          <Column field="izin" header="Izin" sortable>
            <template #body="{ data }">
              <span class="font-semibold text-blue-600">{{ data.izin }}</span>
            </template>
          </Column>
          <Column field="alpa" header="Alpa" sortable>
            <template #body="{ data }">
              <span class="font-semibold text-red-600">{{ data.alpa }}</span>
            </template>
          </Column>
          <Column field="total" header="Total Hari" sortable></Column>
          <Column field="persentase" header="Persentase Hadir" sortable>
            <template #body="{ data }">
              <ProgressBar :value="parseFloat(data.persentase)" :showValue="true" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <div v-else-if="!loading && hasFetched" class="text-center py-12 bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700">
      <i class="pi pi-inbox text-5xl text-slate-300 mb-4"></i>
      <h3 class="text-lg font-medium text-slate-600 dark:text-slate-300 mb-2">Tidak Ada Data</h3>
      <p class="text-slate-500">Belum ada data presensi untuk bulan yang dipilih.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const toast = useToast()
const apiToken = useCookie('auth_token')
const config = useRuntimeConfig()

const filterMonth = ref(new Date())
const filterUnit = ref(null)
const units = ref([])
const recapData = ref([])
const loading = ref(false)
const hasFetched = ref(false)

const formattedMonth = computed(() => {
  if (!filterMonth.value) return ''
  return filterMonth.value.toLocaleDateString('id-ID', { year: 'numeric', month: 'long' })
})

const fetchUnits = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/units`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    units.value = data
  } catch (error) {
    console.error('Failed to fetch units')
  }
}

const fetchData = async () => {
  if (!filterMonth.value) return
  
  loading.value = true
  try {
    const year = filterMonth.value.getFullYear()
    const month = String(filterMonth.value.getMonth() + 1).padStart(2, '0')
    const monthStr = `${year}-${month}`
    
    const query = new URLSearchParams({ month: monthStr })
    if (filterUnit.value) query.append('unit_id', filterUnit.value)
    
    const data = await $fetch(`${config.public.apiBase}/sdm/attendance/recap?${query.toString()}`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    
    recapData.value = data
    hasFetched.value = true
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat rekap presensi' })
  } finally {
    loading.value = false
  }
}

const exportExcel = () => {
  // Simple CSV export for now
  const headers = ['Nama Pegawai', 'NIP', 'Hadir', 'Sakit', 'Izin', 'Alpa', 'Total Hari Kerja', 'Persentase']
  const rows = recapData.value.map(r => [
    r.nama_lengkap, 
    r.nip || '-', 
    r.hadir, 
    r.sakit, 
    r.izin, 
    r.alpa, 
    r.total, 
    r.persentase
  ])
  
  const csvContent = "data:text/csv;charset=utf-8," 
    + headers.join(",") + "\n" 
    + rows.map(e => e.join(",")).join("\n")
    
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  const filename = `Rekap_Presensi_${formattedMonth.value.replace(' ', '_')}.csv`
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
