<template>
  <NuxtLayout name="default">
    <div class="min-h-screen">
      <!-- Hero -->
      <section class="relative bg-gradient-to-br from-primary via-primary-dark to-slate-900 py-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h1 class="text-4xl lg:text-5xl font-bold mb-4">Unit Pendidikan</h1>
          <p class="text-xl opacity-90">Tiga jenjang pendidikan Islam terpadu</p>
        </div>
      </section>

      <!-- Units -->
      <section class="py-16 bg-white dark:bg-slate-900">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-16">
          <!-- RA -->
          <div class="grid lg:grid-cols-2 gap-12 items-center">
            <div class="bg-gradient-to-br from-blue-100 to-blue-50 dark:from-blue-900/30 dark:to-slate-800 rounded-2xl p-8 aspect-video flex items-center justify-center">
              <i class="pi pi-star text-8xl text-blue-500 opacity-50"></i>
            </div>
            <div>
              <div class="inline-flex items-center px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm font-medium mb-4">
                Usia 4-6 Tahun
              </div>
              <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">RA (TK Islam)</h2>
              <p class="text-lg text-slate-600 dark:text-slate-400 mb-6">
                Raudhatul Athfal menyediakan pendidikan anak usia dini dengan kurikulum bermain dan belajar
                berbasis Islam. Menumbuhkan kecintaan terhadap Al-Qur'an sejak dini melalui metode yang menyenangkan.
              </p>
              <ul class="space-y-3 mb-6">
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Kurikulum bermain sambil belajar
                </li>
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Pengenalan huruf hijaiyah
                </li>
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Hafalan surat pendek
                </li>
              </ul>
            </div>
          </div>

          <!-- SDIT -->
          <div class="grid lg:grid-cols-2 gap-12 items-center">
            <div class="order-2 lg:order-1">
              <div class="inline-flex items-center px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-sm font-medium mb-4">
                Kelas 1-6
              </div>
              <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">SDIT (SD Islam Terpadu)</h2>
              <p class="text-lg text-slate-600 dark:text-slate-400 mb-6">
                Sekolah Dasar Islam Terpadu dengan kurikulum nasional plus tahfidz Al-Qur'an.
                Memadukan ilmu pengetahuan umum dengan nilai-nilai keislaman.
              </p>
              <ul class="space-y-3 mb-6">
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Kurikulum nasional + tahfidz
                </li>
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Target hafalan 3 juz
                </li>
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Program ekstrakurikuler lengkap
                </li>
              </ul>
            </div>
            <div class="order-1 lg:order-2 bg-gradient-to-br from-green-100 to-green-50 dark:from-green-900/30 dark:to-slate-800 rounded-2xl p-8 aspect-video flex items-center justify-center">
              <i class="pi pi-book text-8xl text-green-500 opacity-50"></i>
            </div>
          </div>

          <!-- SMPIT -->
          <div class="grid lg:grid-cols-2 gap-12 items-center">
            <div class="bg-gradient-to-br from-purple-100 to-purple-50 dark:from-purple-900/30 dark:to-slate-800 rounded-2xl p-8 aspect-video flex items-center justify-center">
              <i class="pi pi-graduation-cap text-8xl text-purple-500 opacity-50"></i>
            </div>
            <div>
              <div class="inline-flex items-center px-4 py-2 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-full text-sm font-medium mb-4">
                Kelas 7-9
              </div>
              <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-4">SMPIT (SMP Islam Terpadu)</h2>
              <p class="text-lg text-slate-600 dark:text-slate-400 mb-6">
                SMP Islam Terpadu dengan program boarding untuk pembinaan karakter intensif.
                Menghasilkan lulusan yang siap melanjutkan ke jenjang pendidikan menengah atas terbaik.
              </p>
              <ul class="space-y-3 mb-6">
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Program boarding school
                </li>
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Kurikulum karakter Islami
                </li>
                <li class="flex items-center gap-3 text-slate-700 dark:text-slate-300">
                  <i class="pi pi-check text-green-500"></i>
                  Persiapan masuk SMA/MA favorit
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="py-16 bg-secondary">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 class="text-3xl font-bold text-white mb-4">Tertarik Bergabung?</h2>
          <p class="text-lg text-white/90 mb-8">Daftarkan putra-putri Anda sekarang melalui PPDB Online</p>
          <NuxtLink
            to="/ppdb"
            class="inline-flex items-center px-8 py-4 bg-white text-secondary font-semibold rounded-lg hover:bg-slate-100 transition-colors"
          >
            <i class="pi pi-arrow-right mr-2"></i>
            Daftar PPDB
          </NuxtLink>
        </div>
      </section>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })
</script>
