<template>
  <div class="space-y-8">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Identitas & Lokasi Sekolah</h1>
      <p class="text-slate-500 dark:text-slate-400">Kelola kontak profil sekolah dan konfigurasi titik lokasi GPS untuk presensi pegawai.</p>
    </div>

    <!-- Geofencing & Presensi Section -->
    <div class="card bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700 space-y-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-100 dark:border-slate-700 pb-4">
        <div>
          <div class="flex items-center gap-2">
            <span class="p-2 bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400 rounded-lg">
              <i class="pi pi-map-marker text-lg"></i>
            </span>
            <h2 class="text-lg font-bold text-slate-800 dark:text-white">Titik Lokasi & Geofence Presensi Pegawai</h2>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Pegawai hanya dapat melakukan check-in mandiri bila berada di dalam radius titik koordinat yang ditentukan.
          </p>
        </div>

        <div class="flex items-center gap-3 bg-slate-50 dark:bg-slate-900/50 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700">
          <label for="geofence-switch" class="text-xs font-semibold text-slate-700 dark:text-slate-300 cursor-pointer">
            Status Validasi Lokasi:
          </label>
          <div class="flex items-center gap-2">
            <input 
              id="geofence-switch"
              type="checkbox" 
              v-model="geofenceForm.is_enabled" 
              class="w-4 h-4 text-emerald-600 rounded focus:ring-emerald-500 cursor-pointer"
            />
            <span class="text-xs font-bold" :class="geofenceForm.is_enabled ? 'text-emerald-600' : 'text-slate-400'">
              {{ geofenceForm.is_enabled ? 'Aktif (Dibatasi Radius)' : 'Nonaktif (Bebas)' }}
            </span>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="flex flex-col gap-1.5 md:col-span-2">
          <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Nama Lokasi / Area Pusat</label>
          <InputText v-model="geofenceForm.location_name" placeholder="Misal: Komplek Sekolah Islam Terpadu Asy-Syuuraa Batam" class="w-full" />
        </div>

        <div class="flex flex-col gap-1.5">
          <div class="flex justify-between items-center">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Latitude (Garis Lintang)</label>
            <span class="text-[11px] text-slate-400">Contoh: 1.123456</span>
          </div>
          <InputNumber v-model="geofenceForm.latitude" :minFractionDigits="4" :maxFractionDigits="8" class="w-full" />
        </div>

        <div class="flex flex-col gap-1.5">
          <div class="flex justify-between items-center">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Longitude (Garis Bujur)</label>
            <span class="text-[11px] text-slate-400">Contoh: 104.012345</span>
          </div>
          <InputNumber v-model="geofenceForm.longitude" :minFractionDigits="4" :maxFractionDigits="8" class="w-full" />
        </div>

        <div class="flex flex-col gap-1.5">
          <div class="flex justify-between items-center">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Radius Toleransi Presensi (Meter)</label>
            <span class="text-[11px] text-emerald-600 font-semibold">{{ geofenceForm.radius_meters }} meter</span>
          </div>
          <InputNumber v-model="geofenceForm.radius_meters" :min="10" :max="500" suffix=" meter" class="w-full" />
          <p class="text-[11px] text-slate-400">
            *Rekomendasi: 30 - 50 meter untuk memperhitungkan deviasi GPS ponsel saat di dalam ruangan kelas.
          </p>
        </div>

        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Jam Masuk & Pulang Sekolah</label>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <span class="text-[11px] text-slate-500 block mb-1">Masuk (Batas Terlambat)</span>
              <InputText v-model="geofenceForm.work_start_time" placeholder="07:30" class="w-full" />
            </div>
            <div>
              <span class="text-[11px] text-slate-500 block mb-1">Pulang Kerja</span>
              <InputText v-model="geofenceForm.work_end_time" placeholder="16:00" class="w-full" />
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions / GPS Helpers -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-700">
        <div class="flex flex-wrap gap-2">
          <Button 
            label="Ambil Titik GPS Saya Saat Ini" 
            icon="pi pi-compass" 
            severity="secondary" 
            outlined 
            size="small"
            :loading="detectingGPS"
            @click="getCurrentGPS"
          />
          <a 
            :href="`https://www.google.com/maps?q=${geofenceForm.latitude},${geofenceForm.longitude}`" 
            target="_blank" 
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-700/60 hover:bg-slate-200 rounded-lg transition"
          >
            <i class="pi pi-external-link text-xs"></i>
            Buka di Google Maps
          </a>
        </div>

        <Button 
          label="Simpan Pengaturan Lokasi" 
          icon="pi pi-save" 
          severity="success"
          :loading="savingGeofence" 
          @click="saveGeofenceData" 
        />
      </div>
    </div>

    <!-- Identitas Kontak & Profil Sekolah -->
    <div class="card bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700 space-y-4">
      <div class="flex items-center gap-2 border-b border-slate-100 dark:border-slate-700 pb-3">
        <span class="p-2 bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 rounded-lg">
          <i class="pi pi-info-circle text-lg"></i>
        </span>
        <div>
          <h2 class="text-lg font-bold text-slate-800 dark:text-white">Kontak & Profil Footer Website</h2>
          <p class="text-xs text-slate-500 dark:text-slate-400">Informasi publik yang ditampilkan pada footer portal website resmi.</p>
        </div>
      </div>

      <div class="flex flex-col gap-2">
        <label class="font-medium text-sm">Tentang Kami (Footer)</label>
        <Textarea v-model="form.about" rows="3" placeholder="Sekolah Islam Terpadu yang berkarakter Qur'ani..." />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Alamat Sekolah</label>
          <InputText v-model="form.address" placeholder="Batam, Kepulauan Riau" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">No. Telepon</label>
          <InputText v-model="form.phone" placeholder="(0778) xxx-xxxx" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Email Resmi</label>
          <InputText v-model="form.email" placeholder="info@asy-syuuraa.sch.id" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">No. WhatsApp (format: 628xxx)</label>
          <InputText v-model="form.whatsapp" placeholder="628123456789" />
        </div>
      </div>

      <h3 class="font-bold text-sm text-slate-700 dark:text-slate-300 mt-4 mb-1">Tautan Media Sosial</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium text-xs">Link Facebook</label>
          <InputText v-model="form.facebook" placeholder="https://facebook.com/..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-xs">Link Instagram</label>
          <InputText v-model="form.instagram" placeholder="https://instagram.com/..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-xs">Link YouTube</label>
          <InputText v-model="form.youtube" placeholder="https://youtube.com/@..." />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium text-xs">Link TikTok</label>
          <InputText v-model="form.tiktok" placeholder="https://tiktok.com/@..." />
        </div>
      </div>

      <div class="pt-4 border-t border-slate-100 dark:border-slate-700">
        <Button label="Simpan Profil Footer" icon="pi pi-save" :loading="loading" @click="saveData" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const loading = ref(false)
const savingGeofence = ref(false)
const detectingGPS = ref(false)

const form = reactive({
  about: '',
  address: '',
  phone: '',
  email: '',
  instagram: '',
  facebook: '',
  youtube: '',
  tiktok: '',
  whatsapp: ''
})

const geofenceForm = reactive({
  is_enabled: true,
  location_name: 'Komplek Sekolah Asy-Syuuraa Batam',
  latitude: 1.123456,
  longitude: 104.012345,
  radius_meters: 30,
  work_start_time: '07:30',
  work_end_time: '16:00'
})

async function fetchData() {
  try {
    const res = await api.get<any>('/public/content/settings_footer')
    if (res && res.content_json) {
      const data = JSON.parse(res.content_json)
      Object.assign(form, data)
    }
  } catch (e: any) {
    if (e?.statusCode !== 404 && e?.status !== 404) {
      console.error('Failed to load footer settings', e)
    }
  }
}

async function fetchGeofenceData() {
  try {
    const res = await api.get<any>('/sdm/settings/geofence')
    if (res) {
      Object.assign(geofenceForm, res)
    }
  } catch (e) {
    console.error('Failed to load geofence settings', e)
  }
}

function getCurrentGPS() {
  if (typeof window === 'undefined' || !navigator.geolocation) {
    toast.add({ severity: 'warn', summary: 'GPS Tidak Didukung', detail: 'Browser Anda tidak mendukung deteksi lokasi.', life: 4000 })
    return
  }
  detectingGPS.value = true
  navigator.geolocation.getCurrentPosition(
    (position) => {
      detectingGPS.value = false
      geofenceForm.latitude = Number(position.coords.latitude.toFixed(6))
      geofenceForm.longitude = Number(position.coords.longitude.toFixed(6))
      toast.add({
        severity: 'success',
        summary: 'Lokasi Terdeteksi',
        detail: `Titik GPS berhasil disetel (${geofenceForm.latitude}, ${geofenceForm.longitude}) Akurasi: ±${Math.round(position.coords.accuracy)}m`,
        life: 5000
      })
    },
    (error) => {
      detectingGPS.value = false
      let msg = 'Gagal mendeteksi lokasi GPS.'
      if (error.code === 1) msg = 'Akses lokasi ditolak oleh browser. Mohon izinkan izin akses lokasi.'
      else if (error.code === 2) msg = 'Posisi tidak tersedia / sinyal GPS lemah.'
      else if (error.code === 3) msg = 'Waktu permintaan lokasi habis (timeout).'
      toast.add({ severity: 'error', summary: 'Gagal Deteksi GPS', detail: msg, life: 5000 })
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 }
  )
}

async function saveGeofenceData() {
  savingGeofence.value = true
  try {
    await api.put('/sdm/settings/geofence', geofenceForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pengaturan lokasi & geofence presensi berhasil disimpan', life: 3000 })
  } catch (e: any) {
    const detail = e?.data?.detail || 'Gagal menyimpan pengaturan lokasi presensi'
    toast.add({ severity: 'error', summary: 'Gagal', detail, life: 4000 })
  } finally {
    savingGeofence.value = false
  }
}

async function saveData() {
  loading.value = true
  try {
    await api.put('/cms/content/settings_footer', {
      section_key: 'settings_footer',
      title: 'Pengaturan Footer',
      content_json: JSON.stringify(form)
    })
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pengaturan kontak berhasil disimpan', life: 3000 })
  } catch (e) {
    console.error('Failed to save settings', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan pengaturan', life: 3000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchGeofenceData()
})
</script>
