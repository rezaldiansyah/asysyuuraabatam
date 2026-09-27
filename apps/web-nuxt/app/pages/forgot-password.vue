<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary via-primary-dark to-slate-900 px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-8 space-y-6">
        <!-- Logo -->
        <div class="text-center">
          <div class="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4 text-primary text-3xl">
            <i class="pi pi-lock"></i>
          </div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Bantuan Lupa Password</h1>
          <p class="text-slate-500 dark:text-slate-400 text-sm mt-1">Sistem Informasi Sekolah Terpadu Asy-Syuuraa Batam</p>
        </div>

        <!-- Info Box -->
        <div class="bg-slate-50 dark:bg-slate-700/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3 text-sm text-slate-600 dark:text-slate-300">
          <p>
            Untuk menjaga keamanan data sekolah, reset kata sandi akun Guru dan Pegawai dikelola langsung oleh <strong>Administrator / Tim IT Yayasan</strong>.
          </p>
          <div class="space-y-1 text-xs text-slate-500 dark:text-slate-400">
            <div>1. Siapkan <strong>NIK Pegawai</strong> atau <strong>Nama Lengkap</strong> Anda.</div>
            <div>2. Hubungi Admin TU / IT Yayasan melalui WhatsApp untuk verifikasi dan penerbitan password sementara.</div>
          </div>
        </div>

        <!-- WhatsApp Action Button -->
        <Button 
          as="a" 
          :href="waAdminUrl" 
          target="_blank"
          label="Hubungi Admin via WhatsApp" 
          icon="pi pi-whatsapp" 
          severity="success" 
          class="w-full justify-center !py-3 font-bold text-base shadow-lg"
        />

        <!-- Back to Login -->
        <div class="text-center pt-2">
          <NuxtLink to="/login" class="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
            <i class="pi pi-arrow-left text-xs"></i> Kembali ke Halaman Login
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const waAdminUrl = computed(() => {
  const text = encodeURIComponent('Assalamu\'alaikum Admin SIST Asy-Syuuraa, saya ingin meminta bantuan reset password akun pegawai saya.')
  return `https://wa.me/6281234567890?text=${text}`
})
</script>
