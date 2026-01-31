<template>
  <NuxtLayout name="default">
    <div class="min-h-screen">
      <!-- Hero -->
      <section class="relative bg-gradient-to-br from-secondary via-secondary-dark to-slate-900 py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <div class="inline-flex items-center px-4 py-2 bg-white/20 rounded-full text-sm font-medium mb-6">
            <i class="pi pi-calendar mr-2"></i>
            Tahun Ajaran 2026/2027
          </div>
          <h1 class="text-4xl lg:text-5xl font-bold mb-4">Penerimaan Peserta Didik Baru</h1>
          <p class="text-xl opacity-90 mb-8">Daftarkan putra-putri Anda untuk bergabung bersama kami</p>
          <Button severity="contrast" size="large" @click="scrollToForm">
            <i class="pi pi-arrow-down mr-2"></i>
            Daftar Sekarang
          </Button>
        </div>
      </section>

      <!-- Timeline -->
      <section class="py-16 bg-white dark:bg-slate-900">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-center text-slate-800 dark:text-white mb-12">
            Jadwal PPDB
          </h2>
          <div class="grid md:grid-cols-4 gap-8">
            <div class="text-center">
              <div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-pencil text-2xl text-primary"></i>
              </div>
              <h3 class="font-bold text-slate-800 dark:text-white mb-2">Pendaftaran</h3>
              <p class="text-slate-500">1 Jan - 28 Feb 2026</p>
            </div>
            <div class="text-center">
              <div class="w-16 h-16 bg-secondary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-file text-2xl text-secondary"></i>
              </div>
              <h3 class="font-bold text-slate-800 dark:text-white mb-2">Seleksi Berkas</h3>
              <p class="text-slate-500">1 - 7 Mar 2026</p>
            </div>
            <div class="text-center">
              <div class="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-users text-2xl text-purple-600"></i>
              </div>
              <h3 class="font-bold text-slate-800 dark:text-white mb-2">Tes & Wawancara</h3>
              <p class="text-slate-500">10 - 15 Mar 2026</p>
            </div>
            <div class="text-center">
              <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-check-circle text-2xl text-green-600"></i>
              </div>
              <h3 class="font-bold text-slate-800 dark:text-white mb-2">Pengumuman</h3>
              <p class="text-slate-500">20 Mar 2026</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Registration Form -->
      <section id="form-section" class="py-16 bg-slate-50 dark:bg-slate-800">
        <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-lg p-8">
            <h2 class="text-2xl font-bold text-slate-800 dark:text-white mb-6 text-center">
              Formulir Pendaftaran
            </h2>

            <Message v-if="success" severity="success" class="mb-6">
              Pendaftaran berhasil! Silakan cek email untuk informasi selanjutnya.
            </Message>

            <form @submit.prevent="submitForm" class="space-y-6">
              <!-- Unit Selection -->
              <div class="flex flex-col gap-2">
                <label class="font-medium text-slate-700 dark:text-slate-300">Pilih Unit Pendidikan *</label>
                <div class="grid grid-cols-3 gap-4">
                  <div
                    v-for="unit in units"
                    :key="unit.value"
                    class="border-2 rounded-lg p-4 text-center cursor-pointer transition-all"
                    :class="form.unit === unit.value ? 'border-primary bg-primary/10' : 'border-slate-200 dark:border-slate-700 hover:border-primary/50'"
                    @click="form.unit = unit.value"
                  >
                    <i :class="unit.icon" class="text-2xl mb-2" :style="{ color: unit.color }"></i>
                    <p class="font-medium text-sm">{{ unit.label }}</p>
                  </div>
                </div>
              </div>

              <!-- Child Name -->
              <div class="flex flex-col gap-2">
                <label for="child_name" class="font-medium text-slate-700 dark:text-slate-300">Nama Lengkap Calon Siswa *</label>
                <InputText id="child_name" v-model="form.child_name" placeholder="Nama lengkap sesuai akta kelahiran" class="w-full" />
              </div>

              <!-- Birth Date & Gender -->
              <div class="grid grid-cols-2 gap-4">
                <div class="flex flex-col gap-2">
                  <label for="birth_date" class="font-medium text-slate-700 dark:text-slate-300">Tanggal Lahir *</label>
                  <Calendar id="birth_date" v-model="form.birth_date" dateFormat="dd/mm/yy" showIcon placeholder="Pilih tanggal" class="w-full" />
                </div>
                <div class="flex flex-col gap-2">
                  <label for="gender" class="font-medium text-slate-700 dark:text-slate-300">Jenis Kelamin *</label>
                  <Select id="gender" v-model="form.gender" :options="genderOptions" optionLabel="label" optionValue="value" placeholder="Pilih" class="w-full" />
                </div>
              </div>

              <!-- Parent Info -->
              <div class="pt-4 border-t">
                <h3 class="font-bold text-slate-800 dark:text-white mb-4">Data Orang Tua / Wali</h3>
                <div class="grid md:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-2">
                    <label for="parent_name" class="font-medium text-slate-700 dark:text-slate-300">Nama Orang Tua *</label>
                    <InputText id="parent_name" v-model="form.parent_name" placeholder="Nama ayah/ibu" class="w-full" />
                  </div>
                  <div class="flex flex-col gap-2">
                    <label for="phone" class="font-medium text-slate-700 dark:text-slate-300">No. WhatsApp *</label>
                    <InputText id="phone" v-model="form.phone" placeholder="08xxxxxxxxxx" class="w-full" />
                  </div>
                </div>
              </div>

              <!-- Email -->
              <div class="flex flex-col gap-2">
                <label for="email" class="font-medium text-slate-700 dark:text-slate-300">Email *</label>
                <InputText id="email" v-model="form.email" type="email" placeholder="email@example.com" class="w-full" />
              </div>

              <!-- Address -->
              <div class="flex flex-col gap-2">
                <label for="address" class="font-medium text-slate-700 dark:text-slate-300">Alamat Lengkap</label>
                <Textarea id="address" v-model="form.address" rows="3" placeholder="Alamat tempat tinggal" class="w-full" />
              </div>

              <!-- Submit -->
              <Button type="submit" class="w-full" size="large" :loading="submitting">
                <i class="pi pi-send mr-2"></i>
                Kirim Pendaftaran
              </Button>
            </form>
          </div>
        </div>
      </section>

      <!-- Info -->
      <section class="py-16 bg-white dark:bg-slate-900">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 class="text-3xl font-bold text-center text-slate-800 dark:text-white mb-12">
            Informasi Pendaftaran
          </h2>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="text-center p-6">
              <div class="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-file text-2xl text-blue-600"></i>
              </div>
              <h3 class="font-bold text-slate-800 dark:text-white mb-2">Persyaratan</h3>
              <ul class="text-sm text-slate-600 dark:text-slate-400 space-y-1">
                <li>Fotokopi akta kelahiran</li>
                <li>Fotokopi KK</li>
                <li>Pas foto 3x4 (3 lembar)</li>
                <li>Rapor terakhir (SD/SMP)</li>
              </ul>
            </div>
            <div class="text-center p-6">
              <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-wallet text-2xl text-green-600"></i>
              </div>
              <h3 class="font-bold text-slate-800 dark:text-white mb-2">Biaya Pendaftaran</h3>
              <p class="text-slate-600 dark:text-slate-400 text-sm mb-2">Biaya formulir pendaftaran:</p>
              <p class="text-2xl font-bold text-primary">Rp 200.000</p>
            </div>
            <div class="text-center p-6">
              <div class="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="pi pi-phone text-2xl text-purple-600"></i>
              </div>
              <h3 class="font-bold text-slate-800 dark:text-white mb-2">Kontak</h3>
              <p class="text-slate-600 dark:text-slate-400 text-sm">
                WhatsApp: 0812-3456-7890<br />
                Email: ppdb@asy-syuuraa.sch.id
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: false })

const toast = useToast()

const units = [
  { value: 'RA', label: 'RA (TK)', icon: 'pi pi-star', color: '#3b82f6' },
  { value: 'SDIT', label: 'SDIT', icon: 'pi pi-book', color: '#22c55e' },
  { value: 'SMPIT', label: 'SMPIT', icon: 'pi pi-graduation-cap', color: '#a855f7' },
]

const genderOptions = [
  { label: 'Laki-laki', value: 'L' },
  { label: 'Perempuan', value: 'P' },
]

const form = reactive({
  unit: 'SDIT',
  child_name: '',
  birth_date: null,
  gender: 'L',
  parent_name: '',
  phone: '',
  email: '',
  address: '',
})

const submitting = ref(false)
const success = ref(false)

function scrollToForm() {
  document.getElementById('form-section')?.scrollIntoView({ behavior: 'smooth' })
}

async function submitForm() {
  // Basic validation
  if (!form.child_name || !form.parent_name || !form.phone || !form.email) {
    toast.add({ severity: 'warn', summary: 'Perhatian', detail: 'Mohon lengkapi data yang wajib diisi.', life: 3000 })
    return
  }

  submitting.value = true
  try {
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1500))
    success.value = true
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pendaftaran dikirim!', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Terjadi kesalahan', life: 3000 })
  } finally {
    submitting.value = false
  }
}
</script>
