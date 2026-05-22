<template>
  <div class="flex flex-1 flex-col gap-4 pt-8">

      <!-- PPDB Card for Orangtua -->
      <div v-if="ppdbReg" class="rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg p-6 text-white">
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div class="space-y-2">
            <h3 class="text-lg font-bold flex items-center gap-2">
              <i class="pi pi-file-edit"></i> Pendaftaran PPDB
            </h3>
            <p class="text-indigo-100 text-sm">No. Registrasi: <strong>{{ ppdbReg.registration_number }}</strong></p>
            <div class="flex items-center gap-2">
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                :class="ppdbReg.status === 'DRAFT' ? 'bg-yellow-400 text-yellow-900' : ppdbReg.status === 'PENDING' ? 'bg-blue-400 text-blue-900' : ppdbReg.status === 'ACCEPTED' ? 'bg-emerald-400 text-emerald-900' : 'bg-red-400 text-red-900'">
                {{ ppdbReg.status }}
              </span>
              <span class="text-xs text-indigo-200">Step {{ ppdbReg.last_completed_step || 0 }} / 8</span>
            </div>
            <!-- Progress bar -->
            <div class="h-2 w-48 bg-white/20 rounded-full mt-2">
              <div class="h-2 bg-white rounded-full transition-all" :style="{ width: ((ppdbReg.last_completed_step || 0) / 8 * 100) + '%' }"></div>
            </div>
          </div>
          <NuxtLink v-if="ppdbReg.status === 'DRAFT'" to="/ppdb"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-indigo-600 font-bold rounded-xl shadow hover:shadow-lg hover:bg-indigo-50 transition">
            <i class="pi pi-arrow-right"></i> Lanjutkan Pengisian
          </NuxtLink>
          <span v-else-if="ppdbReg.status === 'PENDING'" class="text-sm text-indigo-200 italic">Menunggu review panitia...</span>
        </div>
      </div>

      <!-- Stats Grid - 3 cards like Next.js -->
      <div class="grid auto-rows-min gap-4 md:grid-cols-3">
        <!-- Total Siswa Card -->
        <div class="aspect-video rounded-xl bg-white dark:bg-slate-800 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <h3 class="text-lg font-medium text-slate-900 dark:text-slate-100">Total Siswa</h3>
            <p class="text-3xl font-bold text-primary mt-2">{{ stats.totalSiswa.toLocaleString('id-ID') }}</p>
          </div>
          <p class="text-sm text-slate-500">+12% dari bulan lalu</p>
        </div>

        <!-- Tagihan Lunas Card with Progress Bar -->
        <div class="aspect-video rounded-xl bg-white dark:bg-slate-800 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <h3 class="text-lg font-medium text-slate-900 dark:text-slate-100">Tagihan Lunas</h3>
            <p class="text-3xl font-bold text-emerald-600 mt-2">{{ stats.tagihanLunasPercent }}%</p>
          </div>
          <div class="h-2 w-full bg-slate-100 dark:bg-slate-700 rounded-full mt-2">
            <div class="h-2 bg-emerald-500 rounded-full transition-all" :style="{ width: stats.tagihanLunasPercent + '%' }"></div>
          </div>
        </div>

        <!-- Hadir Hari Ini Card -->
        <div class="aspect-video rounded-xl bg-white dark:bg-slate-800 shadow-sm p-6 flex flex-col justify-between">
          <div>
            <h3 class="text-lg font-medium text-slate-900 dark:text-slate-100">Hadir Hari Ini</h3>
            <p class="text-3xl font-bold text-blue-600 mt-2">{{ stats.hadirPercent }}%</p>
          </div>
          <p class="text-sm text-slate-500">Guru & Karyawan</p>
        </div>
      </div>

      <!-- Welcome Section -->
      <div class="min-h-[50vh] flex-1 rounded-xl bg-white dark:bg-slate-800 shadow-sm p-6">
        <h2 class="text-xl font-bold text-primary mb-4">Selamat Datang di Dashboard Asy-Syuuraa</h2>
        <p class="text-slate-600 dark:text-slate-400 mb-6">
          Anda telah berhasil masuk ke sistem. Gunakan menu di samping kiri untuk mengelola data akademik, keuangan, dan pengaturan sekolah.
        </p>

        <!-- Quick Actions Grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
          <NuxtLink
            to="/dashboard/siswa"
            class="flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-50 dark:bg-slate-700 hover:bg-primary/10 transition"
          >
            <i class="pi pi-users text-2xl text-primary"></i>
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Data Siswa</span>
          </NuxtLink>
          <NuxtLink
            to="/dashboard/guru"
            class="flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-50 dark:bg-slate-700 hover:bg-primary/10 transition"
          >
            <i class="pi pi-user text-2xl text-primary"></i>
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Data Guru</span>
          </NuxtLink>
          <NuxtLink
            to="/dashboard/jadwal"
            class="flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-50 dark:bg-slate-700 hover:bg-primary/10 transition"
          >
            <i class="pi pi-calendar text-2xl text-primary"></i>
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Jadwal</span>
          </NuxtLink>
          <NuxtLink
            to="/dashboard/keuangan"
            class="flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-50 dark:bg-slate-700 hover:bg-primary/10 transition"
          >
            <i class="pi pi-wallet text-2xl text-primary"></i>
            <span class="text-sm font-medium text-slate-700 dark:text-slate-300">Keuangan</span>
          </NuxtLink>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
})

const api = useApi()
const authStore = useAuthStore()

const stats = reactive({
  totalSiswa: 0,
  totalGuru: 0,
  totalKelas: 0,
  tagihanLunasPercent: 85,
  hadirPercent: 98,
})

const ppdbReg = ref<any>(null)

onMounted(async () => {
  try {
    const [students, teachers, classrooms] = await Promise.all([
      api.get<any[]>('/academic/students').catch(() => []),
      api.get<any[]>('/academic/teachers').catch(() => []),
      api.get<any[]>('/academic/classrooms').catch(() => []),
    ])

    stats.totalSiswa = students.length || 1240
    stats.totalGuru = teachers.length
    stats.totalKelas = classrooms.length
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error)
    stats.totalSiswa = 1240 // Fallback like Next.js
  }

  // Fetch PPDB registration for orangtua
  const roleCode = authStore.user?.role?.code || ''
  if (roleCode === 'orangtua' || roleCode === 'wali_murid') {
    try {
      const regs = await api.get<any[]>('/ppdb/register/my')
      if (regs && regs.length > 0) {
        ppdbReg.value = regs[0] // Show the most recent registration
      }
    } catch (e) {
      console.log('PPDB registration not found')
    }
  }
})
</script>

