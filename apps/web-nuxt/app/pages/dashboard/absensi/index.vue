<template>
    <div class="space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Absensi Siswa</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola data kehadiran siswa.</p>
      </div>
      <Card>
        <template #content>
          <div class="text-center py-16">
            <i class="pi pi-calendar-clock text-6xl text-slate-300 mb-4"></i>
            <h2 class="text-xl font-semibold text-slate-600 dark:text-slate-300 mb-2">Coming Soon</h2>
            <p class="text-slate-500 dark:text-slate-400 max-w-md mx-auto">
              Fitur ini sedang dalam tahap pengembangan.
            </p>
          </div>
        </template>
      </Card>
    </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
</script>
