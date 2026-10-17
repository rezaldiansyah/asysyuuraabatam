<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary via-primary-dark to-slate-900 px-4 py-8">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-7 sm:p-8 space-y-6">
        <!-- Logo & Header -->
        <div class="text-center">
          <div class="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mx-auto mb-4 shadow-md">
            <span class="text-white font-bold text-2xl">AS</span>
          </div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Lupa Kata Sandi</h1>
          <p class="text-slate-500 dark:text-slate-400 text-xs sm:text-sm mt-1">
            Sistem Informasi Manajemen Terpadu Asy-Syuuraa Batam
          </p>
        </div>

        <!-- STATE 1: FORM INPUT EMAIL -->
        <div v-if="!isSubmitted" class="space-y-4">
          <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 text-center">
            Masukkan alamat email yang terdaftar pada akun Anda. Sistem akan mengirimkan tautan aman untuk mengatur ulang kata sandi.
          </p>

          <Message v-if="errorMessage" severity="error" :closable="true" @close="errorMessage = ''" class="text-xs">
            {{ errorMessage }}
          </Message>

          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div class="flex flex-col gap-1.5">
              <label for="email" class="text-xs font-medium text-slate-700 dark:text-slate-300">
                Alamat Email Terdaftar <span class="text-rose-500">*</span>
              </label>
              <div class="relative">
                <i class="pi pi-envelope absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                <InputText
                  id="email"
                  v-model="email"
                  type="email"
                  placeholder="contoh@asysyuura.sch.id"
                  class="w-full !pl-9 text-xs sm:text-sm"
                  :disabled="loading"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              label="Kirim Tautan Reset Password"
              icon="pi pi-send"
              severity="success"
              class="w-full !py-2.5 font-semibold text-xs sm:text-sm shadow-md"
              :loading="loading"
            />
          </form>

          <!-- Divider -->
          <div class="relative my-4">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-slate-200 dark:border-slate-700"></div>
            </div>
            <div class="relative flex justify-center text-xs uppercase">
              <span class="bg-white dark:bg-slate-800 px-2 text-slate-400">Atau</span>
            </div>
          </div>

          <!-- Bantuan WhatsApp -->
          <div class="bg-slate-50 dark:bg-slate-900/50 p-3 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2 text-xs">
            <p class="text-slate-600 dark:text-slate-400">
              Lupa alamat email atau akun belum tertaut email?
            </p>
            <Button
              as="a"
              :href="waAdminUrl"
              target="_blank"
              label="Bantuan Reset via Admin (WhatsApp)"
              icon="pi pi-whatsapp"
              severity="secondary"
              outlined
              size="small"
              class="w-full justify-center !py-2 text-xs"
            />
          </div>
        </div>

        <!-- STATE 2: SUCCESS EMAIL SENT -->
        <div v-else class="space-y-5 text-center">
          <div class="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto border-2 border-emerald-200 dark:border-emerald-800 shadow-inner">
            <i class="pi pi-check-circle text-3xl"></i>
          </div>

          <div class="space-y-2">
            <h2 class="text-lg font-bold text-slate-800 dark:text-white">Tautan Berhasil Dikirim!</h2>
            <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              Kami telah mengirimkan instruksi dan tautan reset kata sandi ke:
            </p>
            <div class="font-mono text-xs font-semibold text-primary bg-primary/10 py-1.5 px-3 rounded-lg inline-block break-all">
              {{ email }}
            </div>
          </div>

          <div class="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800/60 rounded-xl p-3 text-left text-xs text-amber-800 dark:text-amber-300 space-y-1">
            <div class="font-semibold flex items-center gap-1.5">
              <i class="pi pi-info-circle text-xs"></i> Informasi Penting:
            </div>
            <ul class="list-disc list-inside space-y-0.5 text-[11px] opacity-90 pl-1">
              <li>Tautan reset hanya berlaku selama <b>30 menit</b>.</li>
              <li>Periksa folder <b>Inbox</b> atau folder <b>Spam / Promosi</b>.</li>
              <li>Buka tautan yang dikirimkan untuk membuat kata sandi baru.</li>
            </ul>
          </div>

          <div class="pt-2 flex flex-col gap-2">
            <Button
              label="Kirim Ulang Email"
              icon="pi pi-refresh"
              severity="secondary"
              text
              size="small"
              :loading="loading"
              @click="handleSubmit"
            />
          </div>
        </div>

        <!-- Back to Login -->
        <div class="text-center pt-2 border-t border-slate-100 dark:border-slate-800">
          <NuxtLink to="/login" class="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline">
            <i class="pi pi-arrow-left text-[11px]"></i> Kembali ke Halaman Login
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: false })

const api = useApi()
const toast = useToast()

const email = ref('')
const loading = ref(false)
const isSubmitted = ref(false)
const errorMessage = ref('')

const waAdminUrl = computed(() => {
  const text = encodeURIComponent('Assalamu\'alaikum Admin SIST Asy-Syuuraa, saya ingin meminta bantuan reset kata sandi akun saya.')
  return `https://wa.me/6281234567890?text=${text}`
})

async function handleSubmit() {
  errorMessage.value = ''
  const trimmed = email.value.trim().toLowerCase()

  if (!trimmed) {
    errorMessage.value = 'Silakan masukkan alamat email Anda.'
    return
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
    errorMessage.value = 'Format alamat email tidak valid.'
    return
  }

  loading.value = true
  try {
    await api.post('/auth/forgot-password', { email: trimmed })
    isSubmitted.value = true
    toast.add({
      severity: 'success',
      summary: 'Email Terkirim',
      detail: `Tautan reset kata sandi telah dikirim ke ${trimmed}`,
      life: 4000
    })
  } catch (err: any) {
    console.error('Forgot password error:', err)
    errorMessage.value = err?.data?.detail || err?.message || 'Gagal mengirim email reset kata sandi. Silakan coba lagi nanti.'
  } finally {
    loading.value = false
  }
}
</script>
