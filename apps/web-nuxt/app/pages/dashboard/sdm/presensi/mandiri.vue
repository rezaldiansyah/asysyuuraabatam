<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <i class="pi pi-map-marker text-emerald-600"></i>
          Presensi Mandiri (GPS)
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm">
          Check-in dan Check-out kehadiran harian berbasis titik lokasi sekolah.
        </p>
      </div>
      <div class="flex gap-2">
        <NuxtLink 
          to="/dashboard/sdm/presensi"
          class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 rounded-xl shadow-sm transition"
        >
          <i class="pi pi-list text-xs"></i>
          Daftar Presensi Harian
        </NuxtLink>
        <NuxtLink 
          to="/dashboard/sdm/presensi/rekap"
          class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 rounded-xl shadow-sm transition"
        >
          <i class="pi pi-chart-bar text-xs"></i>
          Rekap Saya
        </NuxtLink>
      </div>
    </div>

    <!-- Alert jika user belum memiliki profil pegawai terhubung -->
    <div v-if="!loadingInit && !todayData.has_employee_profile" class="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-amber-800 dark:text-amber-200 text-sm flex items-start gap-3">
      <i class="pi pi-exclamation-triangle text-xl mt-0.5 text-amber-600"></i>
      <div>
        <div class="font-bold">Akun Anda Belum Terhubung dengan Data Pegawai</div>
        <div class="text-xs text-amber-700 dark:text-amber-300 mt-0.5">
          Akun ini belum memiliki profil pegawai di modul SDM. Silakan hubungi bagian Tata Usaha (TU) untuk sinkronisasi NIK akun dengan data pegawai.
        </div>
      </div>
    </div>

    <!-- Main Live Attendance Card -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Left Column: Clock & GPS Radar -->
      <div class="md:col-span-1 space-y-4">
        <!-- Live Clock Card -->
        <div class="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl p-6 shadow-md border border-slate-700 flex flex-col items-center text-center">
          <span class="text-xs font-medium text-emerald-400 uppercase tracking-widest bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-800/60 mb-3">
            Waktu Indonesia Barat (WIB)
          </span>
          <div class="text-4xl font-extrabold tracking-tight font-mono text-emerald-300">
            {{ currentTime }}
          </div>
          <div class="text-xs text-slate-300 mt-2 font-medium">
            {{ currentDate }}
          </div>
          <div class="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-700/60 w-full flex justify-between">
            <span>Masuk: <b>{{ geofence.work_start_time || '06:45' }}</b></span>
            <span>Target Pulang: <b class="text-emerald-300 font-bold">{{ expectedCheckOutTime }}</b></span>
          </div>
        </div>

        <!-- Employee Info Card -->
        <div v-if="todayData.employee" class="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-sm border border-slate-200 dark:border-slate-700 flex items-center gap-3.5">
          <div class="w-14 h-20 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden bg-slate-100 dark:bg-slate-900 shrink-0 shadow-xs flex items-center justify-center">
            <img 
              v-if="todayData.employee.photo_url" 
              :src="todayData.employee.photo_url" 
              :alt="todayData.employee.nama_lengkap" 
              class="w-full h-full object-cover" 
            />
            <Avatar 
              v-else 
              :image="`https://ui-avatars.com/api/?name=${encodeURIComponent(todayData.employee.nama_lengkap || '')}&background=random`" 
              shape="circle" 
              size="normal" 
            />
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Identitas Pegawai</div>
            <div class="font-bold text-slate-800 dark:text-white truncate">{{ todayData.employee.nama_lengkap }}</div>
            <div class="text-xs text-slate-500 mt-0.5 truncate">NIP: {{ todayData.employee.nip || '-' }}</div>
            <div class="text-xs text-emerald-600 dark:text-emerald-400 font-semibold mt-1 truncate">{{ todayData.employee.position || 'Staf / Guru' }}</div>
          </div>
        </div>

        <!-- Radar Status Card -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 shadow-sm border border-slate-200 dark:border-slate-700 space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-xs font-bold text-slate-700 dark:text-slate-300">Deteksi Sinyal GPS</span>
            <Button 
              icon="pi pi-refresh" 
              text 
              rounded 
              size="small" 
              :loading="detectingGPS" 
              title="Perbarui Posisi GPS"
              @click="getLiveLocation"
            />
          </div>

          <!-- Radar Status Indicator -->
          <div 
            class="p-3.5 rounded-xl border flex items-center gap-3 transition"
            :class="{
              'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200': gpsStatus === 'in_radius',
              'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200': gpsStatus === 'out_radius',
              'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200': gpsStatus === 'loading' || gpsStatus === 'error' || gpsStatus === 'prompt',
              'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300': !geofence.is_enabled
            }"
          >
            <div class="relative flex-shrink-0">
              <span v-if="gpsStatus === 'in_radius'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-4 w-4"
                :class="{
                  'bg-emerald-500': gpsStatus === 'in_radius',
                  'bg-rose-500': gpsStatus === 'out_radius',
                  'bg-amber-500': gpsStatus === 'loading' || gpsStatus === 'prompt' || gpsStatus === 'error',
                  'bg-blue-500': !geofence.is_enabled
                }"
              ></span>
            </div>
            
            <div class="text-xs flex-1">
              <div v-if="!geofence.is_enabled" class="font-bold">
                Validasi Radius Nonaktif
              </div>
              <div v-else-if="gpsStatus === 'in_radius'" class="font-bold">
                Dalam Radius Sekolah ({{ currentDistance }}m)
              </div>
              <div v-else-if="gpsStatus === 'out_radius'" class="font-bold">
                Di Luar Radius Sekolah ({{ currentDistance }}m)
              </div>
              <div v-else-if="gpsStatus === 'loading'" class="font-medium">
                Mendeteksi koordinat GPS...
              </div>
              <div v-else class="font-medium">
                {{ gpsErrorMessage || 'Akses lokasi diperlukan' }}
              </div>
              
              <div class="text-[11px] opacity-80 mt-0.5">
                Maksimal radius: {{ geofence.radius_meters }} meter
              </div>
            </div>
          </div>

          <!-- GPS Precision Info -->
          <div v-if="userCoords.lat && userCoords.lng" class="text-[11px] text-slate-400 space-y-0.5">
            <div class="flex justify-between">
              <span>Posisi Anda:</span>
              <span class="font-mono">{{ userCoords.lat.toFixed(5) }}, {{ userCoords.lng.toFixed(5) }}</span>
            </div>
            <div class="flex justify-between" v-if="userCoords.accuracy">
              <span>Akurasi Perangkat:</span>
              <span>±{{ Math.round(userCoords.accuracy) }} meter</span>
            </div>
            <div class="flex justify-between">
              <span>Titik Sekolah:</span>
              <span class="truncate max-w-[150px]">{{ geofence.location_name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Check-in / Check-out Action Card -->
      <div class="md:col-span-2 space-y-5">
        <!-- Status Card Hari Ini -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-700 space-y-6">
          <div class="flex justify-between items-center border-b border-slate-100 dark:border-slate-700 pb-4">
            <div>
              <h2 class="text-base font-bold text-slate-800 dark:text-white">Status Presensi Hari Ini</h2>
              <p class="text-xs text-slate-400">Catatan kehadiran tanggal {{ currentDate }}</p>
            </div>
            <span 
              class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
              :class="getStatusBadgeClass(todayAttendance?.status)"
            >
              {{ getStatusLabel(todayAttendance?.status) }}
            </span>
          </div>

          <!-- Log Check-in & Check-out -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Box Check-in -->
            <div 
              class="rounded-xl p-4 border transition"
              :class="todayAttendance?.check_in ? 'bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800' : 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700'"
            >
              <div class="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                <i class="pi pi-sign-in text-emerald-600"></i>
                <span>Check-in Masuk</span>
              </div>
              <div class="mt-2 text-2xl font-bold font-mono text-slate-800 dark:text-white">
                {{ formatTimeOnly(todayAttendance?.check_in) || '--:--:--' }}
              </div>
              <div class="mt-1 text-xs text-slate-500">
                <span v-if="todayAttendance?.check_in_distance != null">
                  Jarak: {{ todayAttendance.check_in_distance }} meter
                </span>
                <span v-else-if="todayAttendance?.check_in">Tercatat</span>
                <span v-else>Belum check-in</span>
              </div>
            </div>

            <!-- Box Check-out -->
            <div 
              class="rounded-xl p-4 border transition"
              :class="todayAttendance?.check_out ? 'bg-blue-50/60 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800' : 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700'"
            >
              <div class="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                <i class="pi pi-sign-out text-blue-600"></i>
                <span>Check-out Pulang</span>
              </div>
              <div class="mt-2 text-2xl font-bold font-mono text-slate-800 dark:text-white">
                {{ formatTimeOnly(todayAttendance?.check_out) || '--:--:--' }}
              </div>
              <div class="mt-1 text-xs text-slate-500">
                <span v-if="todayAttendance?.check_out_distance != null">
                  Jarak: {{ todayAttendance.check_out_distance }} meter
                </span>
                <span v-else-if="todayAttendance?.check_out">Tercatat</span>
                <span v-else>Belum check-out</span>
              </div>
            </div>
          </div>

          <!-- Banner Peringatan Hari Ahad (Libur) -->
          <div v-if="!isFullyCompleted && isSunday" class="p-3.5 rounded-xl border border-amber-300 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 text-xs flex items-start gap-2.5">
            <i class="pi pi-info-circle text-amber-600 text-base shrink-0 mt-0.5"></i>
            <div>
              <div class="font-bold">Presensi Khusus Hari Ahad (Libur)</div>
              <div class="mt-0.5 text-slate-600 dark:text-slate-300">
                Hari ini adalah akhir pekan. Pastikan Anda memilih <b>Kategori Kegiatan</b> di bawah agar kehadiran lembur/penugasan tercatat resmi untuk evaluasi manajemen yayasan.
              </div>
            </div>
          </div>

          <!-- Opsi Checkbox Tugas Luar / Dinas / Lomba di Luar Sekolah -->
          <div v-if="!isFullyCompleted" class="p-3.5 rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50/70 dark:bg-blue-950/30 space-y-3">
            <div class="flex items-center gap-2.5">
              <Checkbox v-model="isDutyOutside" :binary="true" inputId="is_duty_outside" />
              <label for="is_duty_outside" class="text-xs font-bold text-blue-900 dark:text-blue-200 cursor-pointer select-none">
                Saya sedang Tugas Luar / Dinas / Mengikuti Lomba (Di Luar Sekolah)
              </label>
            </div>
            
            <div v-if="isDutyOutside" class="space-y-2 pt-1 border-t border-blue-200/60 dark:border-blue-800/60 text-xs">
              <div>
                <label class="font-bold text-blue-900 dark:text-blue-200 block mb-1">
                  Keperluan & Lokasi Tugas Luar <span class="text-rose-500">*</span>
                </label>
                <InputText 
                  v-model="dutyReason" 
                  placeholder="Contoh: Rapat Koordinasi Kurikulum di Kantor Dinas Pendidikan / Lomba OSN" 
                  class="w-full text-xs" 
                />
              </div>
              <div class="text-[11px] text-blue-800 dark:text-blue-300 bg-white/70 dark:bg-slate-900/60 p-2 rounded-lg border border-blue-200 dark:border-blue-900">
                <i class="pi pi-map-marker text-blue-600 mr-1"></i>
                Koordinat GPS perangkat Anda (<span class="font-mono">{{ userCoords.lat ? userCoords.lat.toFixed(5) + ', ' + userCoords.lng?.toFixed(5) : 'Mendeteksi...' }}</span>) akan dicatat sebagai bukti kehadiran tugas luar dan status otomatis dicatat sebagai <b>Dispensasi / Tugas Luar</b>.
              </div>
            </div>
          </div>

          <!-- Kategori Kegiatan (Pilihan Cepat untuk Ahad / Tugas Luar / Lembur) -->
          <div v-if="!isFullyCompleted" class="space-y-1.5">
            <div class="flex items-center justify-between">
              <label class="text-xs font-bold text-slate-700 dark:text-slate-300">
                Kategori Kegiatan <span class="text-slate-400 font-normal">(Opsional / Penugasan Khusus)</span>
              </label>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="cat in categoryList"
                :key="cat.value"
                type="button"
                class="px-2.5 py-1 rounded-lg text-xs font-semibold border transition"
                :class="selectedCategory === cat.value ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50'"
                @click="toggleCategory(cat.value)"
              >
                {{ cat.label }}
              </button>
            </div>
          </div>

          <!-- Input Catatan Opsional -->
          <div v-if="!isFullyCompleted" class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Catatan Tambahan (Opsional)</label>
            <InputText 
              v-model="attendanceNotes" 
              placeholder="Contoh: Surat tugas terlampir / pendampingan 3 siswa" 
              class="w-full text-sm" 
            />
          </div>

          <!-- Tombol Aksi Check-in / Check-out -->
          <div class="pt-2">
            <!-- Kasus 1: Belum Check-in -->
            <div v-if="!todayAttendance?.check_in" class="space-y-2">
              <Button 
                :label="isDutyOutside ? 'Check-in Tugas Luar Sekarang' : 'Check-in Masuk Sekarang'" 
                :icon="isDutyOutside ? 'pi pi-briefcase' : 'pi pi-check-circle'" 
                size="large"
                class="w-full !py-4 font-bold text-base shadow-lg hover:shadow-xl transition"
                :severity="isDutyOutside ? 'info' : 'success'"
                :loading="submitting"
                :disabled="!canCheckIn"
                @click="handleCheckIn"
              />
              <p v-if="!canCheckIn && geofence.is_enabled && !isDutyOutside" class="text-xs text-center text-rose-500">
                *Tombol check-in aktif saat posisi Anda berada di dalam radius {{ geofence.radius_meters }} meter dari sekolah, atau centang opsi Tugas Luar di atas jika berada di luar sekolah.
              </p>
            </div>

            <!-- Kasus 2: Sudah Check-in tapi Belum Check-out -->
            <div v-else-if="todayAttendance?.check_in && !todayAttendance?.check_out" class="space-y-2">
              <Button 
                label="Check-out Pulang Sekarang" 
                icon="pi pi-arrow-right-arrow-left" 
                size="large"
                class="w-full !py-4 font-bold text-base shadow-lg hover:shadow-xl transition"
                severity="info"
                :loading="submitting"
                :disabled="!canCheckOut"
                @click="handleCheckOut"
              />
              <p v-if="!canCheckOut && geofence.is_enabled" class="text-xs text-center text-rose-500">
                *Tombol check-out aktif saat posisi Anda berada di dalam radius sekolah.
              </p>
            </div>

            <!-- Kasus 3: Sudah Check-in dan Check-out Lengkap -->
            <div v-else class="p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-xl border border-emerald-200 dark:border-emerald-800 text-center space-y-1">
              <i class="pi pi-verified text-3xl text-emerald-600 dark:text-emerald-400"></i>
              <div class="font-bold text-emerald-800 dark:text-emerald-200 text-sm">
                Presensi Hari Ini Telah Selesai
              </div>
              <p class="text-xs text-emerald-700 dark:text-emerald-300">
                Terima kasih atas dedikasi dan kerja keras Anda hari ini. Selamat beristirahat!
              </p>
            </div>
          </div>
        </div>

        <!-- Panduan & Ketentuan Presensi -->
        <div class="bg-slate-50 dark:bg-slate-900/60 rounded-2xl p-5 border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400 space-y-2">
          <div class="font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
            <i class="pi pi-info-circle text-sm text-blue-500"></i>
            Ketentuan Presensi GPS Asy-Syuuraa:
          </div>
          <ul class="list-disc list-inside space-y-1 pl-1">
            <li>Pastikan izin lokasi (GPS) pada browser smartphone atau laptop Anda selalu dalam status <b>Izinkan (Allow)</b>.</li>
            <li>Radius check-in maksimal adalah <b>{{ geofence.radius_meters }} meter</b> dari titik gerbang/gedung komplek sekolah.</li>
            <li>Batas jam masuk tepat waktu adalah pukul <b>{{ geofence.work_start_time || '07:30' }} WIB</b>. Lewat dari waktu tersebut sistem otomatis mencatat status <b>Terlambat</b>.</li>
            <li>Jika ada kendala GPS saat berada di sekolah, silakan lapor kepada petugas Tata Usaha (TU) untuk input manual.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()

const loadingInit = ref(true)
const submitting = ref(false)
const detectingGPS = ref(false)
const attendanceNotes = ref('')
const isDutyOutside = ref(false)
const dutyReason = ref('')
const selectedCategory = ref('')

const isSunday = computed(() => {
  return new Date().getDay() === 0
})

const categoryList = [
  { label: '🏆 Lomba / Ekskul', value: '[LOMBA]' },
  { label: '🕌 Mabit / Keagamaan', value: '[MABIT]' },
  { label: '🏛️ Rapat Dinas / Yayasan', value: '[RAPAT]' },
  { label: '📝 Akreditasi / Asesmen', value: '[AKREDITASI]' },
  { label: '🏢 Piket Sekolah / SPMB', value: '[PIKET]' },
]

function toggleCategory(val: string) {
  if (selectedCategory.value === val) {
    selectedCategory.value = ''
  } else {
    selectedCategory.value = val
  }
}

const currentTime = ref('00:00:00')
const currentDate = ref('')
let timerInterval: any = null

const userCoords = reactive({
  lat: null as number | null,
  lng: null as number | null,
  accuracy: null as number | null
})

const geofence = reactive({
  is_enabled: true,
  latitude: 1.123456,
  longitude: 104.012345,
  radius_meters: 30,
  location_name: 'Komplek Sekolah Asy-Syuuraa Batam',
  work_start_time: '06:45',
  work_end_time: '16:00',
  schedule_ra_mon_thu: '14:00',
  schedule_sdit_mon_thu: '15:00',
  schedule_smpit_mon_thu: '15:30',
  schedule_friday: '11:30',
  schedule_saturday: '12:00',
  schedule_default_mon_thu: '16:00'
})

const todayData = reactive({
  today: '',
  has_employee_profile: true,
  employee: null as any,
  attendance: null as any
})

const todayAttendance = computed(() => todayData.attendance)
const isFullyCompleted = computed(() => !!(todayAttendance.value?.check_in && todayAttendance.value?.check_out))

const expectedCheckOutTime = computed(() => {
  const now = new Date()
  const day = now.getDay() // 0 = Sunday, 1 = Monday, ..., 5 = Friday, 6 = Saturday
  const cfg = geofence as any
  if (day === 5) {
    return cfg.schedule_friday || '11:30'
  }
  if (day === 6) {
    return cfg.schedule_saturday || '12:00'
  }
  if (day === 0) {
    return 'Libur (Ahad)'
  }
  // Senin - Kamis
  const unit = (todayData.employee?.unit?.name || '').toUpperCase()
  if (unit.includes('RA')) {
    return cfg.schedule_ra_mon_thu || '14:00'
  }
  if (unit.includes('SDIT') || unit.includes('SD')) {
    return cfg.schedule_sdit_mon_thu || '15:00'
  }
  if (unit.includes('SMPIT') || unit.includes('SMP')) {
    return cfg.schedule_smpit_mon_thu || '15:30'
  }
  return cfg.schedule_default_mon_thu || cfg.work_end_time || '16:00'
})

// Haversine formula on client
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371000 // Earth's radius in meters
  const dLat = (lat2 - lat1) * (Math.PI / 180)
  const dLon = (lon2 - lon1) * (Math.PI / 180)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return Math.round(R * c)
}

const currentDistance = computed(() => {
  if (userCoords.lat == null || userCoords.lng == null) return null
  return calculateDistance(userCoords.lat, userCoords.lng, geofence.latitude, geofence.longitude)
})

const gpsErrorMessage = ref('')
const gpsStatus = computed(() => {
  if (detectingGPS.value) return 'loading'
  if (gpsErrorMessage.value) return 'error'
  if (currentDistance.value == null) return 'prompt'
  if (!geofence.is_enabled) return 'in_radius'
  return currentDistance.value <= geofence.radius_meters ? 'in_radius' : 'out_radius'
})

const canCheckIn = computed(() => {
  if (!todayData.has_employee_profile) return false
  if (todayAttendance.value?.check_in) return false
  if (isDutyOutside.value) {
    return !!(userCoords.lat && userCoords.lng && dutyReason.value.trim())
  }
  if (!geofence.is_enabled) return true
  return gpsStatus.value === 'in_radius'
})

const canCheckOut = computed(() => {
  if (!todayData.has_employee_profile) return false
  if (!todayAttendance.value?.check_in) return false
  if (todayAttendance.value?.check_out) return false
  if (isDutyOutside.value || (todayAttendance.value?.notes || '').includes('Tugas Luar')) {
    return !!(userCoords.lat && userCoords.lng)
  }
  if (!geofence.is_enabled) return true
  return gpsStatus.value === 'in_radius'
})

function updateLiveClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('id-ID', { hour12: false })
  currentDate.value = now.toLocaleDateString('id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function getLiveLocation() {
  if (typeof window === 'undefined' || !navigator.geolocation) {
    gpsErrorMessage.value = 'Browser Anda tidak mendukung geolokasi GPS'
    return
  }
  detectingGPS.value = true
  gpsErrorMessage.value = ''

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      detectingGPS.value = false
      userCoords.lat = pos.coords.latitude
      userCoords.lng = pos.coords.longitude
      userCoords.accuracy = pos.coords.accuracy
      gpsErrorMessage.value = ''
    },
    (err) => {
      detectingGPS.value = false
      if (err.code === 1) gpsErrorMessage.value = 'Izin lokasi ditolak'
      else if (err.code === 2) gpsErrorMessage.value = 'Posisi tidak dapat diperoleh'
      else if (err.code === 3) gpsErrorMessage.value = 'Waktu sinyal GPS habis'
      else gpsErrorMessage.value = 'Gagal membaca GPS'
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 5000 }
  )
}

async function fetchTodayData() {
  loadingInit.value = true
  try {
    const res = await api.get<any>('/sdm/attendance/today')
    if (res) {
      todayData.today = res.today
      todayData.has_employee_profile = res.has_employee_profile
      todayData.employee = res.employee
      todayData.attendance = res.attendance
      if (res.geofence) {
        Object.assign(geofence, res.geofence)
      }
    }
  } catch (e) {
    console.error('Failed to load today attendance', e)
  } finally {
    loadingInit.value = false
  }
}

async function handleCheckIn() {
  if (!userCoords.lat || !userCoords.lng) {
    toast.add({ severity: 'warn', summary: 'GPS Belum Siap', detail: 'Mohon tunggu atau perbarui posisi GPS Anda.', life: 4000 })
    getLiveLocation()
    return
  }

  if (isDutyOutside.value && !dutyReason.value.trim()) {
    toast.add({ severity: 'warn', summary: 'Isi Keperluan Dinas', detail: 'Mohon isi nama agenda dinas / lokasi lomba.', life: 4000 })
    return
  }

  submitting.value = true
  try {
    let finalDuty = dutyReason.value.trim()
    let finalNote = attendanceNotes.value.trim()

    if (selectedCategory.value) {
      if (isDutyOutside.value && finalDuty) {
        if (!finalDuty.startsWith(selectedCategory.value)) {
          finalDuty = `${selectedCategory.value} ${finalDuty}`
        }
      } else if (finalNote) {
        if (!finalNote.startsWith(selectedCategory.value)) {
          finalNote = `${selectedCategory.value} ${finalNote}`
        }
      } else {
        finalNote = selectedCategory.value
      }
    }

    const res = await api.post<any>('/sdm/attendance/check-in', {
      latitude: userCoords.lat,
      longitude: userCoords.lng,
      device_info: typeof navigator !== 'undefined' ? navigator.userAgent : 'Web Browser',
      notes: finalNote || undefined,
      is_duty_outside: isDutyOutside.value,
      duty_reason: finalDuty || undefined
    })
    toast.add({
      severity: 'success',
      summary: 'Presensi Berhasil',
      detail: res.message || 'Check-in berhasil dicatat.',
      life: 5000
    })
    attendanceNotes.value = ''
    dutyReason.value = ''
    selectedCategory.value = ''
    isDutyOutside.value = false
    await fetchTodayData()
  } catch (e: any) {
    const msg = e?.data?.detail || 'Gagal melakukan check-in'
    toast.add({ severity: 'error', summary: 'Check-in Gagal', detail: msg, life: 6000 })
  } finally {
    submitting.value = false
  }
}

async function handleCheckOut() {
  if (!userCoords.lat || !userCoords.lng) {
    toast.add({ severity: 'warn', summary: 'GPS Belum Siap', detail: 'Mohon tunggu atau perbarui posisi GPS Anda.', life: 4000 })
    getLiveLocation()
    return
  }

  submitting.value = true
  try {
    let finalDuty = dutyReason.value.trim()
    let finalNote = attendanceNotes.value.trim()

    if (selectedCategory.value) {
      if (isDutyOutside.value && finalDuty) {
        if (!finalDuty.startsWith(selectedCategory.value)) {
          finalDuty = `${selectedCategory.value} ${finalDuty}`
        }
      } else if (finalNote) {
        if (!finalNote.startsWith(selectedCategory.value)) {
          finalNote = `${selectedCategory.value} ${finalNote}`
        }
      } else {
        finalNote = selectedCategory.value
      }
    }

    const res = await api.post<any>('/sdm/attendance/check-out', {
      latitude: userCoords.lat,
      longitude: userCoords.lng,
      device_info: typeof navigator !== 'undefined' ? navigator.userAgent : 'Web Browser',
      notes: finalNote || undefined,
      is_duty_outside: isDutyOutside.value,
      duty_reason: finalDuty || undefined
    })
    toast.add({
      severity: 'success',
      summary: 'Presensi Berhasil',
      detail: res.message || 'Check-out berhasil dicatat.',
      life: 5000
    })
    attendanceNotes.value = ''
    dutyReason.value = ''
    selectedCategory.value = ''
    await fetchTodayData()
  } catch (e: any) {
    const msg = e?.data?.detail || 'Gagal melakukan check-out'
    toast.add({ severity: 'error', summary: 'Check-out Gagal', detail: msg, life: 6000 })
  } finally {
    submitting.value = false
  }
}

function formatTimeOnly(isoStr?: string | null) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

function getStatusLabel(status?: string | null) {
  if (!status) return 'Belum Presensi'
  const map: Record<string, string> = {
    PRESENT: 'Hadir Tepat Waktu',
    LATE: 'Hadir Terlambat',
    SICK: 'Sakit',
    PERMIT: 'Izin',
    DISPENSATION: 'Dispensasi',
    LEAVE_ANNUAL: 'Cuti Tahunan',
    LEAVE_MATERNITY: 'Cuti Melahirkan',
    LEAVE_MARRIAGE: 'Cuti Menikah',
    LEAVE_BEREAVEMENT: 'Cuti Berkabung',
    LEAVE_PILGRIMAGE: 'Cuti Ibadah',
    LEAVE_UNPAID: 'Cuti Tanpa Tanggungan',
    ABSENT: 'Alpa'
  }
  return map[status] || status
}

function getStatusBadgeClass(status?: string | null) {
  if (!status) return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
  if (status === 'PRESENT') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
  if (status === 'LATE') return 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
  if (status === 'SICK' || status === 'PERMIT') return 'bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300'
  if (status.startsWith('LEAVE_')) return 'bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300'
  return 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300'
}

onMounted(() => {
  updateLiveClock()
  timerInterval = setInterval(updateLiveClock, 1000)
  fetchTodayData()
  getLiveLocation()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>
