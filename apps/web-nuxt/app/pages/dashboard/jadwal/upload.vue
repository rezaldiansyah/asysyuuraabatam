<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <NuxtLink to="/dashboard/jadwal" class="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-primary mb-2 transition">
          <i class="pi pi-arrow-left"></i> Kembali ke Manajemen Akademik
        </NuxtLink>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Upload Jadwal Guru via Excel</h1>
        <p class="text-slate-500 dark:text-slate-400">Import jadwal pelajaran dan guru pengajar dari file spreadsheet Excel (.xlsx).</p>
      </div>
      <div class="flex gap-2">
        <Button 
          label="Download Template Excel" 
          icon="pi pi-download" 
          severity="secondary" 
          outlined 
          :loading="downloadingTemplate"
          @click="downloadTemplate" 
        />
      </div>
    </div>

    <!-- Stepper Navigation -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
      <div 
        v-for="(st, idx) in steps" 
        :key="st.id" 
        class="p-3.5 rounded-xl border flex items-center gap-3 transition-all"
        :class="currentStep === idx + 1 
          ? 'border-primary bg-primary/5 dark:bg-primary/10 shadow-sm' 
          : currentStep > idx + 1 
            ? 'border-green-300 dark:border-green-800 bg-green-50/40 dark:bg-green-950/20' 
            : 'border-slate-200 dark:border-slate-800 opacity-60'"
      >
        <div 
          class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
          :class="currentStep === idx + 1 
            ? 'bg-primary text-white' 
            : currentStep > idx + 1 
              ? 'bg-green-500 text-white' 
              : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'"
        >
          <i v-if="currentStep > idx + 1" class="pi pi-check text-xs"></i>
          <span v-else>{{ idx + 1 }}</span>
        </div>
        <div class="min-w-0">
          <div class="text-xs font-semibold truncate">{{ st.title }}</div>
          <div class="text-[10px] text-slate-400 truncate">{{ st.desc }}</div>
        </div>
      </div>
    </div>

    <!-- Step 1: Pilih Tahun Ajaran -->
    <div v-if="currentStep === 1" class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl p-6 space-y-6">
      <div class="max-w-xl space-y-4">
        <h3 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <i class="pi pi-calendar text-primary"></i> 1. Tentukan Tahun Ajaran Target
        </h3>
        <p class="text-sm text-slate-500">
          Pilih tahun ajaran dan semester yang akan diisi jadwal pelajarannya.
        </p>

        <div class="space-y-2 pt-2">
          <label class="text-sm font-medium">Tahun Ajaran *</label>
          <Select 
            v-model="selectedAcademicYearId" 
            :options="academicYears" 
            optionLabel="label" 
            optionValue="id" 
            placeholder="Pilih Tahun Ajaran" 
            class="w-full"
          />
        </div>

        <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-xl border border-blue-200 dark:border-blue-800 text-xs text-blue-700 dark:text-blue-300 space-y-2">
          <div class="font-bold flex items-center gap-1.5 text-sm">
            <i class="pi pi-info-circle"></i> Petunjuk Pengisian Excel:
          </div>
          <ul class="list-disc ml-5 space-y-1">
            <li>Gunakan <strong>Template Excel Resmi</strong> yang di-download dari sistem ini.</li>
            <li>Sheet 1 (Jadwal) berisi kolom hari, jam mulai, jam selesai, kelas, mapel, dan NIK guru.</li>
            <li>Sheet 2 (Data Referensi) memuat daftar nama kelas, kode mapel, dan NIK guru yang valid.</li>
            <li>Format jam harus menggunakan <strong>HH:MM</strong> (misal <code>07:30</code> atau <code>13:15</code>).</li>
          </ul>
        </div>

        <div class="flex items-center gap-3 pt-4">
          <Button 
            label="Download Template Excel" 
            icon="pi pi-file-excel" 
            severity="secondary" 
            outlined 
            @click="downloadTemplate" 
          />
          <Button 
            label="Lanjut ke Upload File" 
            icon="pi pi-arrow-right" 
            iconPos="right"
            :disabled="!selectedAcademicYearId" 
            @click="currentStep = 2" 
          />
        </div>
      </div>
    </div>

    <!-- Step 2: Upload File Excel -->
    <div v-if="currentStep === 2" class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl p-6 space-y-6">
      <div class="max-w-2xl space-y-4">
        <h3 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <i class="pi pi-upload text-primary"></i> 2. Unggah Berkas Jadwal Excel
        </h3>
        <p class="text-sm text-slate-500">
          Tahun Ajaran: <strong class="text-slate-800 dark:text-white">{{ selectedYearLabel }}</strong>
        </p>

        <!-- Dropzone -->
        <div 
          class="border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3"
          :class="file ? 'border-primary bg-primary/5' : 'border-slate-300 dark:border-slate-700 hover:border-primary hover:bg-slate-50 dark:hover:bg-slate-800/50'"
          @click="triggerFileInput"
          @drop.prevent="handleDrop"
          @dragover.prevent
        >
          <input 
            ref="fileInputRef" 
            type="file" 
            accept=".xlsx, .xls" 
            class="hidden" 
            @change="handleFileSelect" 
          />
          
          <div class="w-16 h-16 rounded-2xl bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center text-primary text-3xl">
            <i :class="parsingFile ? 'pi pi-spin pi-spinner' : file ? 'pi pi-file-excel' : 'pi pi-cloud-upload'"></i>
          </div>

          <div v-if="parsingFile" class="text-sm text-primary font-medium">
            Menganalisis dan memvalidasi file Excel...
          </div>
          <div v-else-if="file" class="text-center">
            <p class="font-bold text-slate-800 dark:text-white text-base">{{ file.name }}</p>
            <p class="text-xs text-slate-400 mt-1">{{ formatFileSize(file.size) }} · Klik untuk ganti file</p>
          </div>
          <div v-else class="text-center">
            <p class="font-medium text-slate-700 dark:text-slate-300">
              <span class="text-primary font-semibold">Klik untuk memilih file</span> atau drag & drop file ke sini
            </p>
            <p class="text-xs text-slate-400 mt-1">Mendukung format .xlsx dan .xls (Maksimal 10MB)</p>
          </div>
        </div>

        <div class="flex items-center justify-between pt-4">
          <Button label="Kembali" severity="secondary" text @click="currentStep = 1" />
          <Button 
            label="Proses & Lihat Preview" 
            icon="pi pi-search" 
            iconPos="right" 
            :disabled="!file || parsingFile" 
            :loading="parsingFile"
            @click="processFile" 
          />
        </div>
      </div>
    </div>

    <!-- Step 3: Preview & Validasi -->
    <div v-if="currentStep === 3" class="space-y-6">
      <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl p-6">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h3 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
              <i class="pi pi-table text-primary"></i> 3. Hasil Validasi Jadwal
            </h3>
            <p class="text-sm text-slate-500">
              Periksa baris jadwal berikut sebelum melanjutkan ke proses simpan database.
            </p>
          </div>
          <div class="flex gap-2">
            <Button label="Upload Ulang File" icon="pi pi-refresh" severity="secondary" size="small" outlined @click="currentStep = 2" />
            <Button 
              label="Lanjut ke Konfirmasi" 
              icon="pi pi-arrow-right" 
              iconPos="right" 
              size="small" 
              :disabled="validCount === 0" 
              @click="currentStep = 4" 
            />
          </div>
        </div>

        <!-- ExcelPreviewTable Component -->
        <JadwalExcelPreviewTable 
          :rows="previewData.rows"
          :total-count="previewData.total_rows"
          :valid-count="previewData.valid_count"
          :conflict-count="previewData.conflict_count"
          :error-count="previewData.error_count"
        />
      </div>
    </div>

    <!-- Step 4: Konfirmasi Simpan -->
    <div v-if="currentStep === 4" class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl p-6 max-w-3xl space-y-6">
      <h3 class="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
        <i class="pi pi-check-circle text-primary"></i> 4. Konfirmasi Penyimpanan ke Database
      </h3>

      <!-- Summary box -->
      <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-3">
        <div class="text-sm font-semibold text-slate-700 dark:text-slate-300">Ringkasan Data yang Akan Disimpan:</div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span class="text-slate-400">Tahun Ajaran:</span>
            <div class="font-bold text-slate-800 dark:text-white mt-0.5">{{ selectedYearLabel }}</div>
          </div>
          <div>
            <span class="text-slate-400">Total Baris File:</span>
            <div class="font-bold text-slate-800 dark:text-white mt-0.5">{{ previewData.total_rows }}</div>
          </div>
          <div>
            <span class="text-slate-400">Baris Valid:</span>
            <div class="font-bold text-green-600 mt-0.5">{{ validItemsToImport.length }} baris</div>
          </div>
          <div>
            <span class="text-slate-400">Baris Dilewati (Error):</span>
            <div class="font-bold text-red-500 mt-0.5">{{ previewData.error_count }} baris</div>
          </div>
        </div>
      </div>

      <!-- Mode selection -->
      <div class="space-y-3">
        <label class="text-sm font-bold text-slate-800 dark:text-white">Pilih Metode Impor Data:</label>
        
        <div 
          @click="importMode = 'append'"
          class="p-4 rounded-xl border cursor-pointer transition-all flex items-start gap-3"
          :class="importMode === 'append' ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'"
        >
          <RadioButton v-model="importMode" value="append" class="mt-0.5" />
          <div>
            <div class="font-semibold text-sm text-slate-800 dark:text-white">Tambahkan ke Jadwal yang Ada (Append)</div>
            <div class="text-xs text-slate-500 mt-0.5">Jadwal yang sudah tersimpan sebelumnya di semester ini tidak akan dihapus. Data baru akan ditambahkan.</div>
          </div>
        </div>

        <div 
          @click="importMode = 'replace'"
          class="p-4 rounded-xl border cursor-pointer transition-all flex items-start gap-3"
          :class="importMode === 'replace' ? 'border-amber-500 bg-amber-50/40 dark:bg-amber-950/20 ring-2 ring-amber-500/20' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'"
        >
          <RadioButton v-model="importMode" value="replace" class="mt-0.5" />
          <div>
            <div class="font-semibold text-sm text-amber-700 dark:text-amber-400">Ganti Semua Jadwal Semester Ini (Replace All)</div>
            <div class="text-xs text-slate-500 mt-0.5">Semua jadwal pelajaran pada tahun ajaran ini akan dibersihkan terlebih dahulu, kemudian digantikan dengan data baru dari file Excel ini.</div>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
        <Button label="Kembali ke Preview" severity="secondary" text @click="currentStep = 3" />
        <Button 
          :label="`Impor ${validItemsToImport.length} Jadwal Sekarang`" 
          icon="pi pi-check" 
          :loading="saving"
          :disabled="validItemsToImport.length === 0"
          @click="confirmImport" 
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import type { PreviewRow } from '~/components/jadwal/ExcelPreviewTable.vue'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const config = useRuntimeConfig()

const currentStep = ref(1)
const steps = [
  { id: 1, title: 'Tahun Ajaran', desc: 'Pilih semester' },
  { id: 2, title: 'Upload File', desc: 'Unggah file Excel' },
  { id: 3, title: 'Validasi', desc: 'Preview & bentrok' },
  { id: 4, title: 'Konfirmasi', desc: 'Simpan ke DB' },
]

const academicYears = ref<any[]>([])
const selectedAcademicYearId = ref<number | null>(null)
const downloadingTemplate = ref(false)

const fileInputRef = ref<HTMLInputElement>()
const file = ref<File | null>(null)
const parsingFile = ref(false)
const saving = ref(false)
const importMode = ref<'append' | 'replace'>('append')

const previewData = reactive({
  total_rows: 0,
  valid_count: 0,
  conflict_count: 0,
  error_count: 0,
  rows: [] as PreviewRow[]
})

const selectedYearLabel = computed(() => {
  const y = academicYears.value.find(item => item.id === selectedAcademicYearId.value)
  return y ? y.label : 'Belum dipilih'
})

const validCount = computed(() => previewData.valid_count + previewData.conflict_count)

// Baris yang bisa diimport (valid atau konflik tapi tidak ada format error)
const validItemsToImport = computed(() => {
  return previewData.rows.filter(r => r.status !== 'ERROR' && r.classroom_id && r.subject_id && r.teacher_id)
})

async function fetchAcademicYears() {
  try {
    const data = await api.get<any[]>('/academic/years')
    academicYears.value = (data || []).map(y => ({
      id: y.id,
      label: `${y.name} - Semester ${y.semester} ${y.is_active ? '(Aktif)' : ''}`,
      is_active: y.is_active
    }))
    
    // Auto select active year
    const active = academicYears.value.find(y => y.is_active)
    if (active) {
      selectedAcademicYearId.value = active.id
    } else if (academicYears.value.length > 0) {
      selectedAcademicYearId.value = academicYears.value[0].id
    }
  } catch (e) {
    console.error('Failed to fetch academic years', e)
  }
}

async function downloadTemplate() {
  downloadingTemplate.value = true
  try {
    const url = `${config.public.apiBase}/academic/schedules/template${selectedAcademicYearId.value ? `?academic_year_id=${selectedAcademicYearId.value}` : ''}`
    
    // Direct browser download
    const authStore = useAuthStore()
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) throw new Error('Download failed')
    
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = 'template_jadwal_mengajar.xlsx'
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(downloadUrl)

    toast.add({ severity: 'success', summary: 'Sukses', detail: 'Template Excel berhasil diunduh', life: 3000 })
  } catch (e) {
    console.error('Download error', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengunduh template Excel', life: 3000 })
  } finally {
    downloadingTemplate.value = false
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleFileSelect(e: Event) {
  const selected = (e.target as HTMLInputElement).files?.[0]
  if (selected) {
    file.value = selected
  }
}

function handleDrop(e: DragEvent) {
  const dropped = e.dataTransfer?.files?.[0]
  if (dropped) {
    file.value = dropped
  }
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function processFile() {
  if (!file.value || !selectedAcademicYearId.value) return
  
  parsingFile.value = true
  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('academic_year_id', selectedAcademicYearId.value.toString())
  
  try {
    const authStore = useAuthStore()
    const res = await $fetch<any>(`${config.public.apiBase}/academic/schedules/upload-preview`, {
      method: 'POST',
      body: formData,
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    
    previewData.total_rows = res.total_rows
    previewData.valid_count = res.valid_count
    previewData.conflict_count = res.conflict_count
    previewData.error_count = res.error_count
    previewData.rows = res.rows || []
    
    currentStep.value = 3
    toast.add({ 
      severity: 'info', 
      summary: 'Analisis Selesai', 
      detail: `Terdeteksi ${res.valid_count} baris valid, ${res.conflict_count} bentrok, ${res.error_count} error.`, 
      life: 4000 
    })
  } catch (e: any) {
    console.error('Preview error', e)
    const detail = e.data?.detail || 'Gagal memproses berkas Excel'
    toast.add({ severity: 'error', summary: 'Gagal', detail, life: 4000 })
  } finally {
    parsingFile.value = false
  }
}

async function confirmImport() {
  if (!selectedAcademicYearId.value || validItemsToImport.value.length === 0) return
  
  saving.value = true
  try {
    const payload = {
      academic_year_id: selectedAcademicYearId.value,
      mode: importMode.value,
      items: validItemsToImport.value.map(row => ({
        classroom_id: row.classroom_id,
        subject_id: row.subject_id,
        teacher_id: row.teacher_id,
        day: row.day,
        start_time: row.start_time,
        end_time: row.end_time,
      }))
    }
    
    const res = await api.post<any>('/academic/schedules/upload-confirm', payload)
    
    toast.add({ 
      severity: 'success', 
      summary: 'Import Berhasil!', 
      detail: res.message || `Berhasil mengimpor jadwal.`, 
      life: 4000 
    })
    
    // Redirect to schedules list
    await navigateTo('/dashboard/jadwal')
  } catch (e: any) {
    console.error('Import error', e)
    toast.add({ severity: 'error', summary: 'Gagal Simpan', detail: 'Terjadi kesalahan saat menyimpan jadwal.', life: 4000 })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchAcademicYears()
})
</script>
