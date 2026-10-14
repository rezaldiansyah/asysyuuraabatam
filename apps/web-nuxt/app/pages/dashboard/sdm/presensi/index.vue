<template>
  <div class="space-y-6">
    <!-- Header with Quick Action to Presensi Mandiri -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Presensi Pegawai</h1>
        <p class="text-slate-500 dark:text-slate-400">Input, kelola, dan verifikasi kehadiran pegawai harian.</p>
      </div>

      <div class="flex flex-wrap gap-2">
        <NuxtLink 
          to="/dashboard/sdm/presensi/mandiri"
          class="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-sm transition"
        >
          <i class="pi pi-map-marker"></i>
          Presensi Mandiri GPS Saya
        </NuxtLink>
        <NuxtLink 
          to="/dashboard/sdm/presensi/rekap"
          class="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-bold text-xs shadow-sm transition"
        >
          <i class="pi pi-chart-bar text-slate-500"></i>
          Rekapitulasi Bulanan
        </NuxtLink>
      </div>
    </div>

    <!-- Filter Bar -->
    <Card>
      <template #content>
        <div class="flex flex-wrap gap-4 items-end">
          <div>
            <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Pilih Tanggal</label>
            <Calendar v-model="filterDate" dateFormat="yy-mm-dd" :showIcon="true" class="w-48" @date-select="fetchData" />
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Pilih Unit</label>
            <Dropdown v-model="filterUnit" :options="units" optionLabel="name" optionValue="id" placeholder="Semua Unit" showClear class="w-52" @change="fetchData" />
          </div>
          <div class="flex-1 text-right">
            <Button label="Muat Ulang Data" icon="pi pi-refresh" outlined size="small" @click="fetchData" />
          </div>
        </div>
      </template>
    </Card>

    <!-- Ringkasan Cards (5 Cards) -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3" v-if="attendances.length > 0">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-emerald-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-500">Hadir / Tepat</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white">{{ summary.hadir }}</div>
          <div class="text-[10px] text-amber-500" v-if="summary.terlambat > 0">({{ summary.terlambat }} Terlambat)</div>
        </div>
        <i class="pi pi-check-circle text-emerald-500 text-2xl opacity-60"></i>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-yellow-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-500">Sakit</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white">{{ summary.sakit }}</div>
        </div>
        <i class="pi pi-exclamation-triangle text-yellow-500 text-2xl opacity-60"></i>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-blue-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-500">Izin / Tugas Luar</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white">{{ summary.izin }}</div>
        </div>
        <i class="pi pi-info-circle text-blue-500 text-2xl opacity-60"></i>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-purple-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-500">Cuti Resmi</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white">{{ summary.cuti }}</div>
        </div>
        <i class="pi pi-calendar text-purple-500 text-2xl opacity-60"></i>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-rose-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-xs text-slate-500">Alpa</div>
          <div class="text-xl font-bold text-slate-800 dark:text-white">{{ summary.alpa }}</div>
        </div>
        <i class="pi pi-times-circle text-rose-500 text-2xl opacity-60"></i>
      </div>
    </div>

    <!-- Data Table -->
    <Card>
      <template #content>
        <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3" v-if="attendances.length > 0">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white">Daftar Presensi: {{ formattedDate }}</h2>
            <span class="text-xs text-slate-400">Total: {{ attendances.length }} Pegawai</span>
          </div>
          <div class="flex gap-2">
            <Button label="Set Semua Hadir" icon="pi pi-check" severity="success" outlined size="small" @click="setAllPresent" />
            <Button label="Simpan Perubahan" icon="pi pi-save" size="small" @click="saveAttendance" :loading="saving" />
          </div>
        </div>

        <DataTable :value="attendances" :loading="loading" dataKey="employee_id" class="p-datatable-sm" stripedRows responsiveLayout="scroll">
          <Column header="Pegawai" style="min-width: 200px">
            <template #body="{ data }">
              <div class="font-semibold text-slate-800 dark:text-white">{{ data.nama_lengkap }}</div>
              <div class="text-xs text-slate-400">{{ data.position || 'Pegawai' }} - <span class="font-medium text-emerald-600">{{ data.unit_name || 'Tanpa Unit' }}</span></div>
              <div v-if="data.check_in_distance != null" class="text-[10px] text-slate-400 flex items-center gap-1 mt-0.5">
                <i class="pi pi-map-marker text-[10px] text-emerald-500"></i>
                GPS: Jarak {{ data.check_in_distance }}m
              </div>
            </template>
          </Column>

          <Column header="Status Presensi" style="min-width: 220px">
            <template #body="{ data }">
              <Dropdown 
                v-model="data.status" 
                :options="statusOptions" 
                optionLabel="label" 
                optionValue="value" 
                optionGroupLabel="group"
                optionGroupChildren="items"
                class="w-full text-xs" 
              >
                <template #value="slotProps">
                  <span v-if="slotProps.value" class="px-2 py-0.5 rounded text-xs font-semibold" :class="getStatusBadgeClass(slotProps.value)">
                    {{ getStatusLabel(slotProps.value) }}
                  </span>
                  <span v-else>Pilih Status</span>
                </template>
                <template #option="slotProps">
                  <div class="flex items-center justify-between text-xs py-0.5">
                    <span>{{ slotProps.option.label }}</span>
                    <span class="text-[10px] px-1.5 py-0.2 rounded" :class="getStatusBadgeClass(slotProps.option.value)">
                      {{ slotProps.option.value }}
                    </span>
                  </div>
                </template>
              </Dropdown>
            </template>
          </Column>

          <Column header="Jam Masuk" style="width: 130px">
            <template #body="{ data }">
              <Calendar 
                v-model="data.check_in" 
                timeOnly 
                :disabled="!isAttendancePhysical(data.status)" 
                class="w-full text-xs" 
              />
            </template>
          </Column>

          <Column header="Jam Keluar" style="width: 130px">
            <template #body="{ data }">
              <Calendar 
                v-model="data.check_out" 
                timeOnly 
                :disabled="!isAttendancePhysical(data.status)" 
                class="w-full text-xs" 
              />
            </template>
          </Column>

          <Column header="Catatan / Keterangan" style="min-width: 180px">
            <template #body="{ data }">
              <InputText v-model="data.notes" class="w-full text-xs" placeholder="Keterangan..." />
            </template>
          </Column>
          
          <template #empty>
            <div class="text-center py-12 text-slate-500">
              <i class="pi pi-users text-3xl text-slate-300 mb-2"></i>
              <p>Pilih tanggal dan unit untuk menampilkan form presensi pegawai.</p>
            </div>
          </template>
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
const apiToken = useCookie('auth_token')
const config = useRuntimeConfig()

const filterDate = ref(new Date())
const filterUnit = ref(null)
const units = ref<any[]>([])
const attendances = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)

// Grouped status options with extended leave types
const statusOptions = [
  {
    group: 'Kehadiran Fisik',
    items: [
      { label: 'Hadir Tepat Waktu', value: 'PRESENT' },
      { label: 'Hadir Terlambat', value: 'LATE' },
    ]
  },
  {
    group: 'Izin & Medis',
    items: [
      { label: 'Sakit (Surat Dokter / Ket.)', value: 'SICK' },
      { label: 'Izin Biasa / Pribadi', value: 'PERMIT' },
      { label: 'Dispensasi / Tugas Luar', value: 'DISPENSATION' },
    ]
  },
  {
    group: 'Cuti Resmi',
    items: [
      { label: 'Cuti Melahirkan (3 Bulan)', value: 'LEAVE_MATERNITY' },
      { label: 'Cuti Menikah (3 Hari)', value: 'LEAVE_MARRIAGE' },
      { label: 'Cuti Berkabung (Kedukaan)', value: 'LEAVE_BEREAVEMENT' },
      { label: 'Cuti Ibadah (Haji / Umroh)', value: 'LEAVE_PILGRIMAGE' },
      { label: 'Cuti di Luar Tanggungan', value: 'LEAVE_UNPAID' },
      { label: 'Cuti Tahunan', value: 'LEAVE_ANNUAL' },
    ]
  },
  {
    group: 'Kedisiplinan',
    items: [
      { label: 'Alpa / Mangkir', value: 'ABSENT' },
    ]
  }
]

const formattedDate = computed(() => {
  if (!filterDate.value) return ''
  return filterDate.value.toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

function isAttendancePhysical(status: string) {
  return status === 'PRESENT' || status === 'LATE'
}

function getStatusLabel(val: string) {
  for (const group of statusOptions) {
    const found = group.items.find(i => i.value === val)
    if (found) return found.label
  }
  return val
}

function getStatusBadgeClass(status?: string | null) {
  if (!status) return 'bg-slate-100 text-slate-700'
  if (status === 'PRESENT') return 'bg-emerald-100 text-emerald-800'
  if (status === 'LATE') return 'bg-amber-100 text-amber-800'
  if (status === 'SICK') return 'bg-yellow-100 text-yellow-800'
  if (status === 'PERMIT' || status === 'DISPENSATION') return 'bg-blue-100 text-blue-800'
  if (status.startsWith('LEAVE_')) return 'bg-purple-100 text-purple-800'
  return 'bg-rose-100 text-rose-800'
}

const summary = computed(() => {
  const hadir = attendances.value.filter(a => a.status === 'PRESENT' || a.status === 'LATE').length
  const terlambat = attendances.value.filter(a => a.status === 'LATE').length
  const sakit = attendances.value.filter(a => a.status === 'SICK').length
  const izin = attendances.value.filter(a => a.status === 'PERMIT' || a.status === 'DISPENSATION').length
  const cuti = attendances.value.filter(a => typeof a.status === 'string' && a.status.startsWith('LEAVE_')).length
  const alpa = attendances.value.filter(a => a.status === 'ABSENT').length

  return { hadir, terlambat, sakit, izin, cuti, alpa }
})

const fetchUnits = async () => {
  try {
    const data = await $fetch<any[]>(`${config.public.apiBase}/units`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    units.value = data
  } catch (error) {
    console.error('Failed to fetch units')
  }
}

const fetchData = async () => {
  if (!filterDate.value) return
  
  loading.value = true
  try {
    const dateStr = filterDate.value.toISOString().split('T')[0]
    
    // Fetch employees
    const empQuery = new URLSearchParams({ is_active: 'true' })
    if (filterUnit.value) empQuery.append('unit_id', filterUnit.value)
    
    const emps = await $fetch<any[]>(`${config.public.apiBase}/sdm/employees?${empQuery.toString()}`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    
    // Fetch existing attendances for this date
    const attQuery = new URLSearchParams({ date: dateStr })
    if (filterUnit.value) attQuery.append('unit_id', filterUnit.value)
    
    const existingAtts = await $fetch<any[]>(`${config.public.apiBase}/sdm/attendance?${attQuery.toString()}`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    
    // Merge data
    attendances.value = emps.map(emp => {
      const existing = existingAtts.find(a => a.employee_id === emp.id)
      
      let check_in = null
      let check_out = null
      
      if (existing) {
        if (existing.check_in) check_in = new Date(existing.check_in)
        if (existing.check_out) check_out = new Date(existing.check_out)
      } else {
        const defCheckIn = new Date(filterDate.value)
        defCheckIn.setHours(7, 0, 0, 0)
        check_in = defCheckIn
      }
      
      return {
        employee_id: emp.id,
        nama_lengkap: emp.nama_lengkap,
        position: emp.position,
        unit_name: emp.unit?.name,
        status: existing?.status || 'PRESENT',
        check_in: check_in,
        check_out: check_out,
        check_in_distance: existing?.check_in_distance,
        notes: existing?.notes || ''
      }
    })
    
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data presensi' })
  } finally {
    loading.value = false
  }
}

const setAllPresent = () => {
  attendances.value.forEach(a => {
    a.status = 'PRESENT'
  })
}

const saveAttendance = async () => {
  if (!filterDate.value || attendances.value.length === 0) return
  
  saving.value = true
  try {
    const dateStr = filterDate.value.toISOString().split('T')[0]
    
    const payloadItems = attendances.value.map(a => {
      let inDate = null
      let outDate = null
      
      if (isAttendancePhysical(a.status)) {
        if (a.check_in) {
          const d = new Date(filterDate.value)
          d.setHours(a.check_in.getHours(), a.check_in.getMinutes(), 0, 0)
          inDate = d.toISOString()
        }
        if (a.check_out) {
          const d = new Date(filterDate.value)
          d.setHours(a.check_out.getHours(), a.check_out.getMinutes(), 0, 0)
          outDate = d.toISOString()
        }
      }
      
      return {
        employee_id: a.employee_id,
        status: a.status,
        check_in: inDate,
        check_out: outDate,
        notes: a.notes
      }
    })
    
    await $fetch(`${config.public.apiBase}/sdm/attendance/bulk`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiToken.value}` },
      body: {
        date: dateStr,
        items: payloadItems
      }
    })
    
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data presensi berhasil disimpan' })
    fetchData()
    
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal menyimpan presensi' })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUnits()
  fetchData()
})
</script>
