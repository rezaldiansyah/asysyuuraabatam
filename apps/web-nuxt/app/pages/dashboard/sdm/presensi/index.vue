<template>
  <div class="space-y-6">
    <!-- Header with Quick Action to Presensi Mandiri -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <i class="pi pi-calendar-check text-emerald-600"></i>
          Presensi Harian Pegawai
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
          Verifikasi kehadiran, pantau presensi mandiri GPS, dan kelola absensi harian guru &amp; karyawan.
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <NuxtLink 
          to="/dashboard/sdm/presensi/mandiri"
          class="inline-flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-semibold text-xs shadow-sm transition"
        >
          <i class="pi pi-map-marker"></i>
          Presensi Mandiri GPS Saya
        </NuxtLink>
        <NuxtLink 
          to="/dashboard/sdm/presensi/rekap"
          class="inline-flex items-center gap-2 px-3.5 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-semibold text-xs shadow-sm transition"
        >
          <i class="pi pi-chart-bar text-slate-500"></i>
          Rekapitulasi Bulanan
        </NuxtLink>
      </div>
    </div>

    <!-- Filter & Date Navigator Bar -->
    <Card>
      <template #content>
        <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <!-- Date Navigator -->
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700">
              <Button 
                icon="pi pi-chevron-left" 
                text 
                rounded 
                size="small" 
                title="Hari Kemarin" 
                @click="changeDate(-1)" 
              />
              <Button 
                label="Kemarin" 
                text 
                size="small" 
                class="!text-xs !py-1 !px-2.5 font-medium" 
                @click="changeDate(-1)" 
              />
              <Button 
                label="Hari Ini" 
                size="small" 
                class="!text-xs !py-1 !px-3 font-bold" 
                :outlined="!isTodaySelected" 
                :severity="isTodaySelected ? 'primary' : 'secondary'"
                @click="setToday" 
              />
              <Button 
                label="Besok" 
                text 
                size="small" 
                class="!text-xs !py-1 !px-2.5 font-medium" 
                @click="changeDate(1)" 
              />
              <Button 
                icon="pi pi-chevron-right" 
                text 
                rounded 
                size="small" 
                title="Hari Besok" 
                @click="changeDate(1)" 
              />
            </div>

            <Calendar 
              v-model="filterDate" 
              dateFormat="yy-mm-dd" 
              :showIcon="true" 
              class="w-44 text-xs" 
              @date-select="fetchData" 
            />
          </div>

          <!-- Unit Selector & Reload -->
          <div class="flex flex-wrap items-center gap-2.5 w-full lg:w-auto">
            <Dropdown 
              v-model="filterUnit" 
              :options="units" 
              optionLabel="name" 
              optionValue="id" 
              placeholder="Semua Unit Sekolah" 
              showClear 
              class="w-full sm:w-52 text-xs" 
              @change="fetchData" 
            />
            <Button 
              icon="pi pi-cloud-download" 
              label="Tarik Data Mesin (Fingerprint)" 
              severity="info" 
              size="small" 
              class="text-xs font-semibold shadow-sm" 
              :loading="syncingFingerprint" 
              @click="syncFingerprint" 
            />
            <Button 
              icon="pi pi-refresh" 
              label="Muat Ulang" 
              outlined 
              size="small" 
              class="text-xs" 
              :loading="loading" 
              @click="fetchData" 
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Status Banner: Saved in Database vs Draft/Unsaved -->
    <div 
      v-if="attendances.length > 0"
      class="p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-sm transition"
      :class="isSavedInDb 
        ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200' 
        : 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200'"
    >
      <div class="flex items-start sm:items-center gap-3">
        <i 
          class="text-2xl shrink-0 mt-0.5 sm:mt-0" 
          :class="isSavedInDb ? 'pi pi-check-circle text-emerald-600 dark:text-emerald-400' : 'pi pi-exclamation-triangle text-amber-600 dark:text-amber-400'"
        ></i>
        <div>
          <div class="font-bold text-sm flex items-center gap-2">
            <span>{{ isSavedInDb ? 'Data Presensi Telah Tersimpan di Sistem' : 'Presensi Tanggal Ini Belum Tersimpan / Masih Draft' }}</span>
            <span 
              class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
              :class="isSavedInDb ? 'bg-emerald-200/80 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200' : 'bg-amber-200/80 text-amber-800 dark:bg-amber-900 dark:text-amber-200'"
            >
              {{ isSavedInDb ? 'Tersimpan (DB)' : 'Belum Disimpan' }}
            </span>
          </div>
          <p class="text-xs opacity-90 mt-1 leading-relaxed">
            <template v-if="isSavedInDb">
              Kehadiran untuk <b>{{ formattedDate }}</b> sudah tersimpan permanen. Sebanyak <b>{{ summary.hadir }} Hadir</b>, <b>{{ summary.sakit + summary.izin + summary.cuti }} Izin/Sakit/Cuti</b>, dan <b>{{ summary.alpa }} Alpa</b>. Data otomatis terhubung dengan Rekap Bulanan.
            </template>
            <template v-else>
              Belum ada data presensi yang difinalisasi untuk <b>{{ formattedDate }}</b> ({{ summary.belum }} dari {{ attendances.length }} pegawai belum diabsen). Klik <b>"Set Semua Hadir"</b> untuk mengisi cepat, lalu klik <b>"Simpan Perubahan"</b>.
            </template>
          </p>
        </div>
      </div>

      <div class="shrink-0 flex items-center gap-2 pt-2 sm:pt-0 border-t sm:border-t-0 border-amber-200/60 dark:border-amber-800/60">
        <Button 
          label="Set Semua Hadir" 
          icon="pi pi-check" 
          severity="success" 
          size="small" 
          outlined
          class="text-xs font-semibold" 
          @click="setAllPresent" 
        />
        <Button 
          label="Simpan Perubahan" 
          icon="pi pi-save" 
          severity="primary" 
          size="small" 
          class="text-xs font-semibold shadow-sm" 
          :loading="saving" 
          @click="saveAttendance" 
        />
      </div>
    </div>

    <!-- Ringkasan Cards (6 Cards Lengkap Proporsional) -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" v-if="attendances.length > 0">
      <!-- 1. Hadir / Tepat -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-emerald-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-[11px] font-semibold text-slate-500">Hadir / Tepat</div>
          <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.hadir }}</div>
          <div class="text-[10px] text-amber-500 font-medium" v-if="summary.terlambat > 0">({{ summary.terlambat }} Terlambat)</div>
        </div>
        <i class="pi pi-check-circle text-emerald-500 text-2xl opacity-50"></i>
      </div>

      <!-- 2. Sakit -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-yellow-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-[11px] font-semibold text-slate-500">Sakit</div>
          <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.sakit }}</div>
          <div class="text-[10px] text-slate-400">Surat dokter / ket.</div>
        </div>
        <i class="pi pi-exclamation-triangle text-yellow-500 text-2xl opacity-50"></i>
      </div>

      <!-- 3. Izin / Tugas Luar -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-blue-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-[11px] font-semibold text-slate-500">Izin / Tugas Luar</div>
          <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.izin }}</div>
          <div class="text-[10px] text-slate-400">Pribadi / Dinas luar</div>
        </div>
        <i class="pi pi-info-circle text-blue-500 text-2xl opacity-50"></i>
      </div>

      <!-- 4. Cuti Resmi -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-purple-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-[11px] font-semibold text-slate-500">Cuti Resmi</div>
          <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.cuti }}</div>
          <div class="text-[10px] text-slate-400">Melahirkan, Nikah, Duka</div>
        </div>
        <i class="pi pi-calendar text-purple-500 text-2xl opacity-50"></i>
      </div>

      <!-- 5. Alpa -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-rose-500 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-[11px] font-semibold text-slate-500">Alpa</div>
          <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.alpa }}</div>
          <div class="text-[10px] text-slate-400">Tanpa keterangan</div>
        </div>
        <i class="pi pi-times-circle text-rose-500 text-2xl opacity-50"></i>
      </div>

      <!-- 6. Belum Presensi (Status Riil Baru) -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-slate-400 dark:border-slate-600 shadow-sm flex items-center justify-between">
        <div>
          <div class="text-[11px] font-semibold text-slate-500">Belum Presensi</div>
          <div class="text-2xl font-extrabold text-slate-700 dark:text-slate-200 mt-0.5">{{ summary.belum }}</div>
          <div class="text-[10px] text-slate-400 font-medium">Dari total {{ attendances.length }} staf</div>
        </div>
        <i class="pi pi-clock text-slate-400 text-2xl opacity-50"></i>
      </div>
    </div>

    <!-- Data Table -->
    <Card>
      <template #content>
        <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3" v-if="attendances.length > 0">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
              <span>Daftar Presensi: {{ formattedDate }}</span>
              <span class="text-xs font-normal px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                {{ summary.totalSudah }} / {{ attendances.length }} Tercatat
              </span>
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">
              Input manual oleh Tata Usaha atau hasil sinkronisasi check-in mandiri GPS oleh pegawai.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <Button 
              label="Set Semua Hadir" 
              icon="pi pi-check" 
              severity="success" 
              outlined 
              size="small" 
              class="text-xs"
              @click="setAllPresent" 
            />
            <Button 
              label="Simpan Perubahan" 
              icon="pi pi-save" 
              size="small" 
              class="text-xs font-semibold"
              :loading="saving" 
              @click="saveAttendance" 
            />
          </div>
        </div>

        <DataTable :value="attendances" :loading="loading" dataKey="employee_id" class="p-datatable-sm" stripedRows responsiveLayout="scroll">
          <Column header="Pegawai" style="min-width: 220px">
            <template #body="{ data }">
              <div class="flex items-center gap-3">
                <Avatar 
                  :image="data.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.nama_lengkap || '')}&background=random`" 
                  shape="circle" 
                  size="normal"
                  class="shrink-0"
                />
                <div class="min-w-0">
                  <div class="font-semibold text-slate-800 dark:text-white truncate">{{ data.nama_lengkap }}</div>
                  <div class="text-xs text-slate-400 truncate">
                    {{ data.position || 'Pegawai' }} - <span class="font-medium text-emerald-600 dark:text-emerald-400">{{ data.unit_name || 'Yayasan' }}</span>
                  </div>
                  <!-- GPS Badge Indicator -->
                  <div v-if="data.check_in_distance != null" class="text-[10px] text-emerald-600 dark:text-emerald-400 flex items-center gap-1 mt-0.5 font-medium">
                    <i class="pi pi-map-marker text-[10px]"></i>
                    <span>GPS Mandiri (Jarak {{ data.check_in_distance }}m)</span>
                  </div>
                </div>
              </div>
            </template>
          </Column>

          <Column header="Status Presensi" style="min-width: 230px">
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
                  <span v-else class="px-2 py-0.5 rounded text-xs text-slate-400 bg-slate-100 dark:bg-slate-700">
                    Belum Presensi
                  </span>
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

          <Column header="Jam Masuk" style="width: 140px">
            <template #body="{ data }">
              <Calendar 
                v-model="data.check_in" 
                timeOnly 
                dateFormat=""
                placeholder="--:--" 
                class="w-full text-xs"
                :disabled="!isAttendancePhysical(data.status)"
              />
            </template>
          </Column>

          <Column header="Jam Pulang" style="width: 140px">
            <template #body="{ data }">
              <Calendar 
                v-model="data.check_out" 
                timeOnly 
                dateFormat=""
                placeholder="--:--" 
                class="w-full text-xs"
                :disabled="!isAttendancePhysical(data.status)"
              />
            </template>
          </Column>

          <Column header="Catatan / Keterangan" style="min-width: 180px">
            <template #body="{ data }">
              <InputText 
                v-model="data.notes" 
                placeholder="Alasan / catatan..." 
                class="w-full text-xs p-inputtext-sm" 
              />
            </template>
          </Column>

          <template #empty>
            <div class="text-center py-12 text-slate-500">
              <i class="pi pi-users text-3xl text-slate-300 mb-2"></i>
              <p>Tidak ada data pegawai yang ditemukan untuk unit ini.</p>
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
const api = useApi()

// Local timezone safe helper
function formatLocalDate(d: Date): string {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatLocalDateTime(dateBase: Date, timeObj: Date | null): string | null {
  if (!timeObj) return null
  const year = dateBase.getFullYear()
  const month = String(dateBase.getMonth() + 1).padStart(2, '0')
  const day = String(dateBase.getDate()).padStart(2, '0')
  const hours = String(timeObj.getHours()).padStart(2, '0')
  const minutes = String(timeObj.getMinutes()).padStart(2, '0')
  const seconds = String(timeObj.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
}

const filterDate = ref(new Date())
const filterUnit = ref(null)
const units = ref<any[]>([])
const attendances = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const syncingFingerprint = ref(false)
const isSavedInDb = ref(false)

// Grouped status options with extended leave types
const statusOptions = [
  {
    group: 'Status Awal',
    items: [
      { label: 'Belum Presensi', value: 'UNRECORDED' }
    ]
  },
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
    group: 'Cuti Resmi Yayasan',
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

const isTodaySelected = computed(() => {
  if (!filterDate.value) return false
  return formatLocalDate(filterDate.value) === formatLocalDate(new Date())
})

function changeDate(offsetDays: number) {
  const d = new Date(filterDate.value)
  d.setDate(d.getDate() + offsetDays)
  filterDate.value = d
  fetchData()
}

function setToday() {
  filterDate.value = new Date()
  fetchData()
}

function isAttendancePhysical(status?: string | null) {
  return status === 'PRESENT' || status === 'LATE'
}

function getStatusLabel(val?: string | null) {
  if (!val || val === 'UNRECORDED') return 'Belum Presensi'
  for (const group of statusOptions) {
    const found = group.items.find(i => i.value === val)
    if (found) return found.label
  }
  return val
}

function getStatusBadgeClass(status?: string | null) {
  if (!status || status === 'UNRECORDED') return 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600'
  if (status === 'PRESENT') return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
  if (status === 'LATE') return 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
  if (status === 'SICK') return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300'
  if (status === 'PERMIT' || status === 'DISPENSATION') return 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
  if (status.startsWith('LEAVE_')) return 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300'
  return 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
}

const summary = computed(() => {
  const hadir = attendances.value.filter(a => a.status === 'PRESENT' || a.status === 'LATE').length
  const terlambat = attendances.value.filter(a => a.status === 'LATE').length
  const sakit = attendances.value.filter(a => a.status === 'SICK').length
  const izin = attendances.value.filter(a => a.status === 'PERMIT' || a.status === 'DISPENSATION').length
  const cuti = attendances.value.filter(a => typeof a.status === 'string' && a.status.startsWith('LEAVE_')).length
  const alpa = attendances.value.filter(a => a.status === 'ABSENT').length
  const belum = attendances.value.filter(a => !a.status || a.status === 'UNRECORDED').length
  const totalSudah = attendances.value.length - belum

  return { hadir, terlambat, sakit, izin, cuti, alpa, belum, totalSudah }
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
  if (!filterDate.value) return
  
  loading.value = true
  try {
    const dateStr = formatLocalDate(filterDate.value)
    
    // Fetch active employees
    const empQuery = new URLSearchParams({ is_active: 'true' })
    if (filterUnit.value) empQuery.append('unit_id', filterUnit.value)
    
    const emps = await api.get<any[]>(`/sdm/employees?${empQuery.toString()}`)
    
    // Fetch existing attendance records from database for this date
    const attQuery = new URLSearchParams({ date: dateStr })
    if (filterUnit.value) attQuery.append('unit_id', filterUnit.value)
    
    const existingAtts = await api.get<any[]>(`/sdm/attendance?${attQuery.toString()}`) || []
    
    // Check if there are real saved records in database for this date
    isSavedInDb.value = existingAtts.length > 0
    
    // Merge data: If record exists in DB, use its real status & check-in. If not, mark as UNRECORDED
    attendances.value = (emps || []).map(emp => {
      const existing = existingAtts.find((a: any) => a.employee_id === emp.id)
      
      let check_in: Date | null = null
      let check_out: Date | null = null
      
      if (existing) {
        if (existing.check_in) check_in = new Date(existing.check_in)
        if (existing.check_out) check_out = new Date(existing.check_out)
      }
      
      return {
        employee_id: emp.id,
        nama_lengkap: emp.nama_lengkap,
        position: emp.position,
        unit_name: emp.unit?.name,
        photo_url: emp.photo_url,
        status: existing?.status || 'UNRECORDED',
        check_in: check_in,
        check_out: check_out,
        check_in_distance: existing?.check_in_distance,
        notes: existing?.notes || ''
      }
    })
    
  } catch (error) {
    console.error('Failed to load attendance:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data presensi', life: 3000 })
  } finally {
    loading.value = false
  }
}

const syncFingerprint = async () => {
  if (!filterDate.value) return
  syncingFingerprint.value = true
  try {
    const dateStr = formatLocalDate(filterDate.value)
    const res = await api.post<any>('/sdm/attendance/sync-fingerprint', { date: dateStr })
    if (res?.status === 'empty') {
      toast.add({
        severity: 'warn',
        summary: 'Data Kosong',
        detail: res.message || `Tidak ada data tap mesin fingerprint pada tanggal ${dateStr}.`,
        life: 4000
      })
    } else {
      const extraInfo = res?.unmatched_logs?.length
        ? ` (${res.unmatched_logs.length} log belum cocok NIK/Nama)`
        : ''
      toast.add({
        severity: 'success',
        summary: 'Sinkronisasi Berhasil',
        detail: (res?.message || `Berhasil menarik data mesin presensi tanggal ${dateStr}.`) + extraInfo,
        life: 4500
      })
      await fetchData()
    }
  } catch (error: any) {
    console.error('Sync fingerprint error:', error)
    toast.add({
      severity: 'error',
      summary: 'Gagal Sinkronisasi',
      detail: error?.data?.detail || 'Gagal menarik data dari mesin presensi.',
      life: 4000
    })
  } finally {
    syncingFingerprint.value = false
  }
}

const setAllPresent = () => {
  attendances.value.forEach(a => {
    // Only update if not already an official permit/sick/cuti
    if (!a.status || a.status === 'UNRECORDED' || a.status === 'ABSENT') {
      a.status = 'PRESENT'
      if (!a.check_in) {
        const def = new Date(filterDate.value)
        def.setHours(7, 0, 0, 0)
        a.check_in = def
      }
    }
  })
  toast.add({ 
    severity: 'info', 
    summary: 'Set Hadir', 
    detail: 'Semua pegawai yang belum presensi telah diatur Hadir Tepat Waktu (07:00). Klik Simpan untuk mempermanenkan.', 
    life: 3000 
  })
}

const saveAttendance = async () => {
  if (!filterDate.value || attendances.value.length === 0) return
  
  saving.value = true
  try {
    const dateStr = formatLocalDate(filterDate.value)
    
    // Filter out UNRECORDED items if any, or convert UNRECORDED to ABSENT if saving
    // If user clicked save, any remaining UNRECORDED is marked ABSENT (or saved with valid status)
    const payloadItems = attendances.value.map(a => {
      let finalStatus = a.status
      if (!finalStatus || finalStatus === 'UNRECORDED') {
        finalStatus = 'ABSENT' // Default remaining unrecorded becomes absent
      }

      let inDateStr: string | null = null
      let outDateStr: string | null = null
      
      if (isAttendancePhysical(finalStatus)) {
        if (a.check_in) {
          inDateStr = formatLocalDateTime(filterDate.value, a.check_in)
        } else {
          // Default physical attendance check-in time 07:00 if not filled
          const defTime = new Date(filterDate.value)
          defTime.setHours(7, 0, 0, 0)
          inDateStr = formatLocalDateTime(filterDate.value, defTime)
        }
        if (a.check_out) {
          outDateStr = formatLocalDateTime(filterDate.value, a.check_out)
        }
      }
      
      return {
        employee_id: a.employee_id,
        status: finalStatus,
        check_in: inDateStr,
        check_out: outDateStr,
        notes: a.notes || null
      }
    })
    
    await api.post('/sdm/attendance/bulk', {
      date: dateStr,
      items: payloadItems
    })
    
    toast.add({ 
      severity: 'success', 
      summary: 'Berhasil Disimpan', 
      detail: `Data presensi tanggal ${dateStr} berhasil disimpan dan disinkronkan dengan Rekap Bulanan.`, 
      life: 3500 
    })
    
    await fetchData()
    
  } catch (error: any) {
    console.error('Save attendance error:', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Gagal Menyimpan', 
      detail: error?.data?.detail || 'Terjadi kesalahan saat menyimpan presensi', 
      life: 4000 
    })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUnits()
  fetchData()
})
</script>
