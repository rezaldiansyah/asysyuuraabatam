<template>
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Pengumuman / Mading</h1>
          <p class="text-slate-500 dark:text-slate-400">Kelola pengumuman dan mading digital sekolah.</p>
        </div>
      </div>
      <Card>
        <template #content>
          <div class="text-center py-16">
            <i class="pi pi-megaphone text-6xl text-slate-300 mb-4"></i>
            <h2 class="text-xl font-semibold text-slate-600 dark:text-slate-300 mb-2">Coming Soon</h2>
            <p class="text-slate-500 dark:text-slate-400 max-w-md mx-auto">
              Fitur Pengumuman / Mading sedang dalam tahap pengembangan. Sementara gunakan fitur Berita & Artikel untuk menampilkan informasi.
            </p>
          </div>
        </template>
      </Card>
    </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'dashboard' })
</script>
