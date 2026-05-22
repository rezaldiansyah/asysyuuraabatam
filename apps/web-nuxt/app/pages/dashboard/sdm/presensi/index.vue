<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Presensi Harian</h1>
      <p class="text-slate-500 dark:text-slate-400">Input dan kelola data presensi pegawai.</p>
    </div>

    <!-- Filter Bar -->
    <Card>
      <template #content>
        <div class="flex flex-wrap gap-4 items-end">
          <div>
            <label class="block text-sm font-medium mb-1">Pilih Tanggal</label>
            <Calendar v-model="filterDate" dateFormat="yy-mm-dd" :showIcon="true" class="w-48" @date-select="fetchData" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Pilih Unit</label>
            <Dropdown v-model="filterUnit" :options="units" optionLabel="name" optionValue="id" placeholder="Semua Unit" showClear class="w-48" @change="fetchData" />
          </div>
          <div class="flex-1 text-right">
            <Button label="Ambil Data Pegawai" icon="pi pi-refresh" outlined @click="fetchData" />
          </div>
        </div>
      </template>
    </Card>

    <!-- Ringkasan Card -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4" v-if="attendances.length > 0">
      <div class="bg-white dark:bg-slate-800 rounded-lg p-4 border-l-4 border-green-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-sm text-slate-500">Hadir</div>
          <div class="text-2xl font-bold">{{ summary.hadir }}</div>
        </div>
        <i class="pi pi-check-circle text-green-500 text-3xl opacity-50"></i>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-lg p-4 border-l-4 border-yellow-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-sm text-slate-500">Sakit</div>
          <div class="text-2xl font-bold">{{ summary.sakit }}</div>
        </div>
        <i class="pi pi-exclamation-triangle text-yellow-500 text-3xl opacity-50"></i>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-lg p-4 border-l-4 border-blue-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-sm text-slate-500">Izin</div>
          <div class="text-2xl font-bold">{{ summary.izin }}</div>
        </div>
        <i class="pi pi-info-circle text-blue-500 text-3xl opacity-50"></i>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-lg p-4 border-l-4 border-red-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-sm text-slate-500">Alpa</div>
          <div class="text-2xl font-bold">{{ summary.alpa }}</div>
        </div>
        <i class="pi pi-times-circle text-red-500 text-3xl opacity-50"></i>
      </div>
    </div>

    <!-- Data Table -->
    <Card>
      <template #content>
        <div class="mb-4 flex justify-between items-center" v-if="attendances.length > 0">
          <h2 class="font-semibold text-lg">Input Presensi: {{ formattedDate }}</h2>
          <div class="flex gap-2">
            <Button label="Set Semua Hadir" icon="pi pi-check" severity="success" outlined size="small" @click="setAllPresent" />
            <Button label="Simpan Presensi" icon="pi pi-save" @click="saveAttendance" :loading="saving" />
          </div>
        </div>

        <DataTable :value="attendances" :loading="loading" dataKey="employee_id" class="p-datatable-sm" stripedRows responsiveLayout="scroll">
          <Column header="Pegawai">
            <template #body="{ data }">
              <div class="font-medium">{{ data.nama_lengkap }}</div>
              <div class="text-xs text-slate-500">{{ data.position }} - {{ data.unit_name || 'Tanpa Unit' }}</div>
            </template>
          </Column>
          <Column header="Status" style="min-width: 150px">
            <template #body="{ data }">
              <Dropdown v-model="data.status" :options="statusOptions" optionLabel="label" optionValue="value" class="w-full" />
            </template>
          </Column>
          <Column header="Jam Masuk" style="width: 120px">
            <template #body="{ data }">
              <Calendar v-model="data.check_in" timeOnly :disabled="data.status !== 'PRESENT'" class="w-full" />
            </template>
          </Column>
          <Column header="Jam Keluar" style="width: 120px">
            <template #body="{ data }">
              <Calendar v-model="data.check_out" timeOnly :disabled="data.status !== 'PRESENT'" class="w-full" />
            </template>
          </Column>
          <Column header="Catatan">
            <template #body="{ data }">
              <InputText v-model="data.notes" class="w-full" placeholder="Keterangan..." />
            </template>
          </Column>
          
          <template #empty>
            <div class="text-center py-8 text-slate-500">
              Pilih tanggal dan unit untuk menampilkan form presensi.
            </div>
          </template>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const toast = useToast()
const apiToken = useCookie('auth_token')
const config = useRuntimeConfig()

const filterDate = ref(new Date())
const filterUnit = ref(null)
const units = ref([])
const attendances = ref([])
const loading = ref(false)
const saving = ref(false)

const statusOptions = [
  { label: 'Hadir', value: 'PRESENT' },
  { label: 'Sakit', value: 'SICK' },
  { label: 'Izin', value: 'PERMIT' },
  { label: 'Alpa', value: 'ABSENT' }
]

const formattedDate = computed(() => {
  if (!filterDate.value) return ''
  return filterDate.value.toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

const summary = computed(() => {
  return {
    hadir: attendances.value.filter(a => a.status === 'PRESENT').length,
    sakit: attendances.value.filter(a => a.status === 'SICK').length,
    izin: attendances.value.filter(a => a.status === 'PERMIT').length,
    alpa: attendances.value.filter(a => a.status === 'ABSENT').length
  }
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
  if (!filterDate.value) return
  
  loading.value = true
  try {
    const dateStr = filterDate.value.toISOString().split('T')[0]
    
    // Fetch employees
    const empQuery = new URLSearchParams({ is_active: 'true' })
    if (filterUnit.value) empQuery.append('unit_id', filterUnit.value)
    
    const emps = await $fetch(`${config.public.apiBase}/sdm/employees?${empQuery.toString()}`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    
    // Fetch existing attendances for this date
    const attQuery = new URLSearchParams({ date: dateStr })
    if (filterUnit.value) attQuery.append('unit_id', filterUnit.value)
    
    const existingAtts = await $fetch(`${config.public.apiBase}/sdm/attendance?${attQuery.toString()}`, {
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
        // Default check in for new present (7:00 AM)
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
        notes: existing?.notes || ''
      }
    })
    
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data' })
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
      // Create proper date strings with time if present
      let inDate = null
      let outDate = null
      
      if (a.status === 'PRESENT') {
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
    fetchData() // Refresh
    
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
