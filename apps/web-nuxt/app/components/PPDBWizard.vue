<template>
  <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-lg p-6 md:p-10">
    <Message v-if="success" severity="success" class="mb-6">
      Pendaftaran berhasil! Akun orangtua telah dibuat. Silakan login menggunakan NIK Ayah dan Password nomor WhatsApp untuk mengecek status pendaftaran.
    </Message>

    <div v-else>
      <!-- Stepper Header -->
      <div class="flex items-center justify-between mb-8 overflow-x-auto pb-4">
        <div v-for="(step, index) in steps" :key="index" class="flex flex-col items-center min-w-[80px] cursor-pointer" @click="goToStep(index)">
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm mb-2 transition-colors', currentStep === index ? 'bg-primary text-white' : currentStep > index ? 'bg-green-500 text-white' : 'bg-slate-100 text-slate-400']">
            <i v-if="currentStep > index" class="pi pi-check"></i>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span :class="['text-xs text-center font-medium', currentStep === index ? 'text-primary' : 'text-slate-500']">{{ step.title }}</span>
        </div>
      </div>

      <form @submit.prevent="nextStep">
        <!-- Step 1: Unit & Anak -->
        <div v-if="currentStep === 0" class="space-y-6">
          <h3 class="text-xl font-bold border-b pb-2">Identitas Calon Siswa</h3>
          
          <div class="flex flex-col gap-2">
            <label class="font-medium">Pilih Unit Pendidikan *</label>
            <div class="grid grid-cols-3 gap-4">
              <div v-for="unit in ['RA', 'SDIT', 'SMPIT']" :key="unit"
                class="border-2 rounded-lg p-3 text-center cursor-pointer"
                :class="form.unit === unit ? 'border-primary bg-primary/10' : 'border-slate-200'"
                @click="form.unit = unit">
                <p class="font-bold">{{ unit }}</p>
              </div>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label>Nama Lengkap *</label>
              <InputText v-model="form.student_data.full_name" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>NIK Siswa *</label>
              <InputText v-model="form.student_data.nik" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>NISN</label>
              <InputText v-model="form.student_data.nisn" />
            </div>
            <div class="flex flex-col gap-2">
              <label>Jenis Kelamin</label>
              <Select v-model="form.student_data.gender" :options="[{l:'Laki-laki',v:'L'},{l:'Perempuan',v:'P'}]" optionLabel="l" optionValue="v" />
            </div>
          </div>
        </div>

        <!-- Step 2: Data Ayah -->
        <div v-if="currentStep === 1" class="space-y-6">
          <h3 class="text-xl font-bold border-b pb-2">Data Ayah Kandung</h3>
          <div class="bg-blue-50 text-blue-800 p-3 rounded-md text-sm mb-4">
            <i class="pi pi-info-circle mr-2"></i> Data NIK Ayah akan digunakan sebagai Username untuk login ke sistem sekolah.
          </div>
          
          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label>Nama Ayah *</label>
              <InputText v-model="form.father_data.name" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>NIK Ayah *</label>
              <InputText v-model="form.father_data.nik" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>No. WhatsApp *</label>
              <InputText v-model="form.father_data.phone" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>Email *</label>
              <InputText v-model="form.father_data.email" type="email" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>Pekerjaan</label>
              <InputText v-model="form.father_data.pekerjaan" />
            </div>
            <div class="flex flex-col gap-2">
              <label>Penghasilan</label>
              <InputText v-model="form.father_data.penghasilan" />
            </div>
          </div>
        </div>

        <!-- Step 3: Data Ibu -->
        <div v-if="currentStep === 2" class="space-y-6">
          <h3 class="text-xl font-bold border-b pb-2">Data Ibu Kandung</h3>
          
          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label>Nama Ibu *</label>
              <InputText v-model="form.mother_data.name" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>NIK Ibu *</label>
              <InputText v-model="form.mother_data.nik" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>No. WhatsApp *</label>
              <InputText v-model="form.mother_data.phone" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>Email *</label>
              <InputText v-model="form.mother_data.email" type="email" required />
            </div>
            <div class="flex flex-col gap-2">
              <label>Pekerjaan</label>
              <InputText v-model="form.mother_data.pekerjaan" />
            </div>
            <div class="flex flex-col gap-2">
              <label>Penghasilan</label>
              <InputText v-model="form.mother_data.penghasilan" />
            </div>
          </div>
        </div>

        <!-- Step 4: Data Fisik & Lainnya -->
        <div v-if="currentStep === 3" class="space-y-6">
          <h3 class="text-xl font-bold border-b pb-2">Data Periodik & Fisik</h3>
          
          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label>Tinggi Badan (cm)</label>
              <InputText v-model="form.periodic_data.tinggi" type="number" />
            </div>
            <div class="flex flex-col gap-2">
              <label>Berat Badan (kg)</label>
              <InputText v-model="form.periodic_data.berat" type="number" />
            </div>
            <div class="flex flex-col gap-2">
              <label>Jarak ke Sekolah (km)</label>
              <InputText v-model="form.periodic_data.jarak" type="number" />
            </div>
            <div class="flex flex-col gap-2">
              <label>Anak Ke-</label>
              <InputText v-model="form.periodic_data.anak_ke" type="number" />
            </div>
          </div>

          <h3 class="text-xl font-bold border-b pb-2 pt-4">Unggah Berkas Pendukung</h3>
          <div class="bg-blue-50 text-blue-800 p-3 rounded-md text-sm">
            <i class="pi pi-info-circle mr-2"></i> Harap unggah foto atau scan dokumen asli (Format: JPG, PNG, atau PDF).
          </div>
          
          <div class="grid md:grid-cols-2 gap-6">
            <CmsImageUploader 
              v-model="form.file_kk_url" 
              label="Kartu Keluarga (KK) *" 
              placeholder="Klik untuk upload KK"
              accept="image/*,application/pdf"
            />
            <CmsImageUploader 
              v-model="form.file_akta_url" 
              label="Akta Kelahiran *" 
              placeholder="Klik untuk upload Akta"
              accept="image/*,application/pdf"
            />
          </div>
        </div>

        <!-- Step 5: Review -->
        <div v-if="currentStep === 4" class="space-y-6">
          <h3 class="text-xl font-bold border-b pb-2">Konfirmasi Data</h3>
          <p class="text-slate-600">Dengan ini saya menyatakan bahwa data yang saya isikan adalah benar dan dapat dipertanggungjawabkan.</p>
          <div class="bg-yellow-50 p-4 border border-yellow-200 rounded-lg">
            <strong>Catatan:</strong> Akun orangtua akan dibuatkan secara otomatis dengan <strong>Username: {{ form.father_data.nik || 'NIK Ayah' }}</strong> dan <strong>Password: {{ form.father_data.phone || 'No WA' }}</strong>.
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex justify-between mt-8 pt-4 border-t">
          <Button v-if="currentStep > 0" type="button" severity="secondary" @click="currentStep--">Kembali</Button>
          <div v-else></div> <!-- Spacer -->
          
          <Button v-if="currentStep < steps.length - 1" type="submit" severity="primary">Selanjutnya</Button>
          <Button v-else type="button" severity="success" @click="submitForm" :loading="loading">
            <i class="pi pi-check mr-2"></i> Kirim Pendaftaran
          </Button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const config = useRuntimeConfig()

const currentStep = ref(0)
const success = ref(false)
const loading = ref(false)

const steps = [
  { title: 'Data Anak' },
  { title: 'Data Ayah' },
  { title: 'Data Ibu' },
  { title: 'Data Fisik' },
  { title: 'Selesai' }
]

const form = reactive({
  unit: 'SDIT',
  student_data: { full_name: '', nik: '', nisn: '', gender: 'L' },
  father_data: { name: '', nik: '', phone: '', email: '', pekerjaan: '', penghasilan: '' },
  mother_data: { name: '', nik: '', phone: '', email: '', pekerjaan: '', penghasilan: '' },
  periodic_data: { tinggi: '', berat: '', jarak: '', anak_ke: '' },
  file_kk_url: '',
  file_akta_url: ''
})

function nextStep() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function goToStep(index) {
  if (index < currentStep.value) {
    currentStep.value = index
  }
}

async function submitForm() {
  if (!form.file_kk_url || !form.file_akta_url) {
    toast.add({ severity: 'warn', summary: 'Berkas Belum Lengkap', detail: 'Harap unggah Kartu Keluarga dan Akta Kelahiran.', life: 3000 })
    currentStep.value = 3 // Go back to files step
    return
  }
  
  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/ppdb/register`, {
      method: 'POST',
      body: form
    })
    success.value = true
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pendaftaran berhasil dikirim', life: 5000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: error.data?.detail || 'Terjadi kesalahan sistem', life: 3000 })
  } finally {
    loading.value = false
  }
}
</script>
