<template>
  <div class="flex flex-1 flex-col gap-4 pt-8">
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

const stats = reactive({
  totalSiswa: 0,
  totalGuru: 0,
  totalKelas: 0,
  tagihanLunasPercent: 85,
  hadirPercent: 98,
})

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
})
</script>
