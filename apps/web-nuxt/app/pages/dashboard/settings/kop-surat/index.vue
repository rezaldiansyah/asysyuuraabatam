<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <i class="pi pi-file-pdf text-emerald-600 text-2xl"></i>
          Pengaturan Kop Surat & Dokumen
        </h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Konfigurasi terpusat untuk kop surat resmi institusi. Seluruh fitur cetak dan ekspor PDF (Notulen Rapat, Kalender Pendidikan, Rapor, Surat Keputusan) otomatis menggunakan identitas ini.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button 
          label="Reset Default" 
          icon="pi pi-refresh" 
          severity="secondary" 
          outlined 
          size="small" 
          @click="resetToDefault" 
        />
        <Button 
          label="Simpan Kop Surat" 
          icon="pi pi-save" 
          severity="primary" 
          size="small" 
          :loading="saving" 
          @click="saveData" 
        />
      </div>
    </div>

    <!-- Alert / Banner Standarisasi -->
    <div class="p-4 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/20 text-xs text-emerald-800 dark:text-emerald-300 flex items-start gap-3">
      <i class="pi pi-shield-check text-emerald-600 text-lg mt-0.5 shrink-0"></i>
      <div>
        <p class="font-bold mb-0.5">Standarisasi Format Dokumen Resmi Yayasan Asy-Syuuraa</p>
        <p class="text-emerald-700 dark:text-emerald-400 leading-relaxed">
          Setiap perubahan logo, alamat, atau nomor kontak di halaman ini akan langsung disinkronkan ke seluruh file PDF resmi yang di-generate dari sistem tanpa perlu mengubah kode program.
        </p>
      </div>
    </div>

    <!-- Main Grid: Form + Live Preview -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <!-- Left Column: Form Settings (7 Cols) -->
      <div class="lg:col-span-7 space-y-5">
        <!-- Logo Lembaga -->
        <div class="card p-5 space-y-4">
          <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-500 border-b border-slate-100 dark:border-slate-800 pb-2 flex items-center gap-2">
            <i class="pi pi-image text-primary"></i> 1. Logo Resmi Kop Surat
          </h2>
          <div>
            <CmsImageUploader 
              v-model="form.logo_url" 
              folder="branding/logo"
              label="Logo Lembaga / Yayasan" 
              placeholder="https://... atau upload file PNG berlatar transparan"
            />
            <p class="text-[11px] text-slate-400 mt-1.5">
              Disarankan menggunakan gambar PNG berlatar transparan atau persegi (minimal 200x200 px). Jika logo dikosongkan, kop surat otomatis ditampilkan dalam format teks terpusat (*centered*).
            </p>

            <!-- Status Lokasi Penyimpanan di R2 / Test Migrasi -->
            <div 
              v-if="form.logo_url && form.logo_url.includes('/uploads/')" 
              class="mt-3 p-3 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 text-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 shadow-xs"
            >
              <div class="flex items-center gap-2">
                <i class="pi pi-info-circle text-amber-600 text-base shrink-0"></i>
                <div>
                  <div class="font-bold">File logo saat ini berada di folder umum (<code>uploads/</code>)</div>
                  <div class="text-[11px] text-amber-700 dark:text-amber-300">Uji coba pindahkan ke folder rapi <code>branding/logo/</code> secara aman.</div>
                </div>
              </div>
              <Button 
                label="Pindahkan ke branding/logo/" 
                icon="pi pi-arrow-right" 
                size="small" 
                severity="warn" 
                class="!text-xs font-semibold shrink-0"
                :loading="migratingLogo"
                @click="migrateLogo"
              />
            </div>
            <div 
              v-else-if="form.logo_url && form.logo_url.includes('branding/logo')" 
              class="mt-3 p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs flex items-center gap-2"
            >
              <i class="pi pi-check-circle text-emerald-600"></i>
              <span>File logo telah tersimpan rapi di folder khusus: <b>branding/logo/</b></span>
            </div>
          </div>
        </div>

        <!-- Nama Instansi & Satuan Pendidikan -->
        <div class="card p-5 space-y-4">
          <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-500 border-b border-slate-100 dark:border-slate-800 pb-2 flex items-center gap-2">
            <i class="pi pi-building text-primary"></i> 2. Nama Lembaga & Legalitas
          </h2>
          <div class="space-y-3 text-xs">
            <div class="flex flex-col gap-1.5">
              <label class="font-semibold text-slate-700 dark:text-slate-300">
                Nama Badan Penyelenggara / Yayasan (Baris Utama 1) <span class="text-red-500">*</span>
              </label>
              <InputText v-model="form.nama_yayasan" placeholder="YAYASAN ASY-SYUURAA BATAM" fluid />
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="font-semibold text-slate-700 dark:text-slate-300">
                Nama Satuan Pendidikan / Sub-Instansi (Baris Utama 2) <span class="text-red-500">*</span>
              </label>
              <InputText v-model="form.nama_unit" placeholder="SEKOLAH ISLAM TERPADU ASY-SYUURAA" fluid />
              <span class="text-[11px] text-slate-400">
                *Catatan: Pada dokumen khusus unit (misal Rapat Unit SMPIT), sistem secara otomatis dapat menyesuaikan baris ini dengan nama unit terkait.
              </span>
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="font-semibold text-slate-700 dark:text-slate-300">
                Legalitas & Status Akreditasi (Baris Tambahan)
              </label>
              <InputText v-model="form.keterangan_legal" placeholder="NPSN: - • Akreditasi A • Berdiri Sejak 2005" fluid />
            </div>
          </div>
        </div>

        <!-- Alamat & Kontak -->
        <div class="card p-5 space-y-4">
          <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-500 border-b border-slate-100 dark:border-slate-800 pb-2 flex items-center gap-2">
            <i class="pi pi-map-marker text-primary"></i> 3. Alamat & Saluran Komunikasi
          </h2>
          <div class="space-y-3 text-xs">
            <div class="flex flex-col gap-1.5">
              <label class="font-semibold text-slate-700 dark:text-slate-300">
                Alamat Lengkap Institusi <span class="text-red-500">*</span>
              </label>
              <Textarea v-model="form.alamat" rows="2" placeholder="Komplek Asy-Syuuraa, Sungai Langkai, Kec. Sagulung, Batam..." fluid />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">No. Telepon Kantor</label>
                <InputText v-model="form.telepon" placeholder="(0778) 391234" fluid />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">WhatsApp / Layanan Cepat</label>
                <InputText v-model="form.whatsapp" placeholder="0812-xxxx-xxxx" fluid />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">Email Resmi</label>
                <InputText v-model="form.email" placeholder="sekretariat@asy-syuuraabatam.or.id" fluid />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-semibold text-slate-700 dark:text-slate-300">Website Resmi</label>
                <InputText v-model="form.website" placeholder="https://asy-syuuraabatam.or.id" fluid />
              </div>
            </div>
          </div>
        </div>

        <!-- Desain & Aksen Garis -->
        <div class="card p-5 space-y-4">
          <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-500 border-b border-slate-100 dark:border-slate-800 pb-2 flex items-center gap-2">
            <i class="pi pi-palette text-primary"></i> 4. Desain Garis Pembatas (Separator)
          </h2>
          <div class="flex flex-wrap items-center gap-4 text-xs">
            <div class="flex items-center gap-2">
              <label class="font-semibold text-slate-700 dark:text-slate-300">Warna Aksen:</label>
              <div class="flex items-center gap-1.5">
                <button
                  v-for="color in presetColors"
                  :key="color.value"
                  type="button"
                  class="w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 flex items-center justify-center text-white text-[10px]"
                  :style="{ backgroundColor: color.value }"
                  :class="form.line_color === color.value ? 'border-slate-800 dark:border-white ring-2 ring-primary/40' : 'border-transparent'"
                  :title="color.label"
                  @click="form.line_color = color.value"
                >
                  <i v-if="form.line_color === color.value" class="pi pi-check text-[10px]"></i>
                </button>
              </div>
            </div>

            <div class="flex items-center gap-2 ml-auto">
              <span class="text-slate-400">Kode Hex:</span>
              <InputText v-model="form.line_color" class="!w-28 !py-1 text-xs font-mono uppercase" placeholder="#059669" />
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Live Document Preview (5 Cols Sticky) -->
      <div class="lg:col-span-5 space-y-4 sticky top-20">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
            <i class="pi pi-eye text-emerald-600"></i> Pratinjau Kop Surat (Live Preview)
          </span>
          <span class="text-[11px] text-slate-400">Ukuran A4 Standar</span>
        </div>

        <!-- Simulation Paper A4 Card -->
        <div class="bg-white rounded-xl shadow-xl border border-slate-200/80 p-6 text-slate-800 font-sans relative overflow-hidden transition-all">
          <div class="absolute top-0 right-0 px-2 py-0.5 bg-slate-100 border-b border-l border-slate-200 text-[10px] text-slate-400 font-mono">
            Preview PDF
          </div>

          <!-- Letterhead Box -->
          <div class="pt-2">
            <div class="flex items-center gap-4">
              <!-- Logo Container -->
              <div v-if="form.logo_url" class="shrink-0 w-16 h-16 rounded-lg flex items-center justify-center p-1 bg-slate-50 border border-slate-100 overflow-hidden">
                <img :src="form.logo_url" alt="Logo" class="max-w-full max-h-full object-contain" />
              </div>
              <div v-else class="shrink-0 w-14 h-14 rounded-lg border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-[10px] text-slate-400">
                <i class="pi pi-image mb-0.5"></i>
                <span>No Logo</span>
              </div>

              <!-- Institution Titles -->
              <div class="flex-1 text-center" :class="{ 'pl-2': form.logo_url }">
                <h3 class="font-extrabold text-sm sm:text-base leading-tight tracking-wide text-slate-900 uppercase">
                  {{ form.nama_yayasan || 'YAYASAN ASY-SYUURAA BATAM' }}
                </h3>
                <h4 class="font-bold text-xs sm:text-sm leading-tight uppercase mt-0.5" :style="{ color: form.line_color || '#059669' }">
                  {{ form.nama_unit || 'SEKOLAH ISLAM TERPADU ASY-SYUURAA' }}
                </h4>
                <p v-if="form.keterangan_legal" class="text-[9.5px] italic text-slate-500 leading-snug mt-0.5">
                  {{ form.keterangan_legal }}
                </p>
                <p class="text-[9.5px] text-slate-600 leading-snug mt-0.5">
                  {{ form.alamat || 'Komplek Asy-Syuuraa, Batam, Kepulauan Riau' }}
                </p>
                <p class="text-[9px] text-slate-500 leading-snug mt-0.5 font-medium">
                  {{ previewContacts }}
                </p>
              </div>
            </div>

            <!-- Double Line Separator -->
            <div class="mt-3.5 space-y-0.5">
              <div class="w-full h-[2.5px]" :style="{ backgroundColor: form.line_color || '#059669' }"></div>
              <div class="w-full h-[0.8px]" :style="{ backgroundColor: form.line_color || '#059669' }"></div>
            </div>
          </div>

          <!-- Document Mock Body -->
          <div class="mt-6 space-y-3 opacity-60 pointer-events-none select-none text-[10px] text-slate-400">
            <div class="text-center font-bold text-slate-700 text-xs uppercase underline">
              SURAT KEPUTUSAN / NOTULEN RAPAT
            </div>
            <div class="text-center text-[9px] text-slate-500 -mt-2">
              Nomor: 012/YYS-AS/SK/2026
            </div>
            <div class="space-y-1.5 pt-2">
              <div class="h-2 bg-slate-200 rounded w-full"></div>
              <div class="h-2 bg-slate-200 rounded w-11/12"></div>
              <div class="h-2 bg-slate-200 rounded w-4/5"></div>
            </div>
            <div class="grid grid-cols-2 gap-4 pt-4">
              <div class="h-10 border border-dashed border-slate-200 rounded"></div>
              <div class="h-10 border border-dashed border-slate-200 rounded"></div>
            </div>
          </div>
        </div>

        <div class="card p-4 space-y-2 text-xs text-slate-500 dark:text-slate-400 bg-slate-50/50 dark:bg-slate-800/40">
          <p class="font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
            <i class="pi pi-info-circle text-primary"></i> Modul Terintegrasi
          </p>
          <ul class="list-disc list-inside space-y-1 text-[11px]">
            <li><strong>Notulen Rapat:</strong> Header otomatis sinkron dengan logo & nomor izin.</li>
            <li><strong>Kalender Pendidikan:</strong> Cetak browser & PDF memakai kop terpusat.</li>
            <li><strong>Kepegawaian & SK:</strong> Surat resmi & data pegawai memakai kop standar.</li>
            <li><strong>PPDB Online:</strong> Formulir & bukti pendaftaran resmi siswa.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const saving = ref(false)

const DEFAULT_SETTINGS = {
  nama_yayasan: 'YAYASAN ASY-SYUURAA BATAM',
  nama_unit: 'SEKOLAH ISLAM TERPADU ASY-SYUURAA',
  keterangan_legal: 'NPSN: - • Akreditasi A • Berdiri Sejak 2005',
  alamat: 'Komplek Asy-Syuuraa, Sungai Langkai, Kec. Sagulung, Kota Batam, Kepulauan Riau 29437',
  telepon: '(0778) 391234',
  whatsapp: '0812-7000-0000',
  email: 'sekretariat@asy-syuuraabatam.or.id',
  website: 'https://asy-syuuraabatam.or.id',
  logo_url: '',
  line_color: '#059669'
}

const form = reactive({ ...DEFAULT_SETTINGS })

const presetColors = [
  { label: 'Emerald (Khas Yayasan)', value: '#059669' },
  { label: 'Navy Blue (Formal)', value: '#1E3A8A' },
  { label: 'Teal (Modern)', value: '#0D9488' },
  { label: 'Charcoal Slate', value: '#334155' },
  { label: 'Dark Maroon', value: '#831843' }
]

const previewContacts = computed(() => {
  const parts = []
  if (form.telepon) parts.push(`Telp: ${form.telepon}`)
  if (form.whatsapp) parts.push(`WA: ${form.whatsapp}`)
  if (form.email) parts.push(`Email: ${form.email}`)
  if (form.website) parts.push(`Web: ${form.website.replace('https://', '')}`)
  return parts.join(' • ')
})

async function fetchData() {
  try {
    const res = await api.get<any>('/public/content/settings_letterhead')
    if (res && res.content_json) {
      const data = JSON.parse(res.content_json)
      Object.assign(form, data)
    }
    if (res && res.image_url && !form.logo_url) {
      form.logo_url = res.image_url
    }
  } catch (e: any) {
    if (e?.statusCode !== 404 && e?.status !== 404) {
      console.error('Failed to load letterhead settings:', e)
    }
  }
}

async function saveData() {
  if (!form.nama_yayasan.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama Yayasan wajib diisi', life: 3000 })
    return
  }

  saving.value = true
  try {
    const payload = {
      section_key: 'settings_letterhead',
      title: form.nama_yayasan,
      subtitle: form.nama_unit,
      body: form.alamat,
      image_url: form.logo_url,
      content_json: JSON.stringify(form)
    }

    await api.put('/cms/content/settings_letterhead', payload)
    toast.add({
      severity: 'success',
      summary: 'Berhasil Disimpan',
      detail: 'Konfigurasi kop surat resmi berhasil diperbarui dan aktif di seluruh dokumen.',
      life: 3500
    })
  } catch (e: any) {
    console.error('Error saving letterhead:', e)
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: e?.data?.detail || 'Terjadi kesalahan saat menyimpan pengaturan kop surat.',
      life: 4000
    })
  } finally {
    saving.value = false
  }
}

function resetToDefault() {
  Object.assign(form, DEFAULT_SETTINGS)
  toast.add({
    severity: 'info',
    summary: 'Form Direset',
    detail: 'Konfigurasi dikembalikan ke default. Klik Simpan untuk mempermanenkan.',
    life: 3000
  })
}

const migratingLogo = ref(false)
async function migrateLogo() {
  migratingLogo.value = true
  try {
    const res = await api.post<any>('/cms/migrate-letterhead-logo')
    if (res?.new_url) {
      form.logo_url = res.new_url
    }
    toast.add({
      severity: 'success',
      summary: 'Migrasi Berhasil',
      detail: res?.message || 'Logo berhasil dipindahkan ke folder branding/logo/!',
      life: 4000
    })
  } catch (e: any) {
    console.error('Migrasi logo gagal:', e)
    toast.add({
      severity: 'error',
      summary: 'Gagal Migrasi',
      detail: e?.data?.detail || e?.message || 'Terjadi kesalahan saat memindahkan logo.',
      life: 5000
    })
  } finally {
    migratingLogo.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>
