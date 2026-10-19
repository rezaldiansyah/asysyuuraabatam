<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary via-primary-dark to-slate-900 px-4 py-8">
    <div class="w-full max-w-md">
      <!-- Reset Password Card -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-7 sm:p-8 space-y-6">
        <!-- Logo & Header -->
        <div class="text-center">
          <div class="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mx-auto mb-4 shadow-md">
            <span class="text-white font-bold text-2xl">AS</span>
          </div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Atur Ulang Kata Sandi</h1>
          <p class="text-slate-500 dark:text-slate-400 text-xs sm:text-sm mt-1">
            Buat kata sandi baru yang kuat untuk akun Anda
          </p>
        </div>

        <!-- SCENARIO 1: TOKEN TIDAK ADA / KOSONG -->
        <div v-if="!token" class="space-y-4 text-center">
          <div class="w-14 h-14 bg-rose-50 dark:bg-rose-950/40 text-rose-500 rounded-full flex items-center justify-center mx-auto border border-rose-200 dark:border-rose-800">
            <i class="pi pi-exclamation-triangle text-2xl"></i>
          </div>
          <div class="space-y-1">
            <h2 class="text-base font-semibold text-slate-800 dark:text-white">Tautan Tidak Valid</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400">
              Tautan ini tidak menyertakan token verifikasi yang sah. Silakan minta tautan baru melalui halaman Lupa Password.
            </p>
          </div>
          <Button
            as="router-link"
            to="/forgot-password"
            label="Minta Tautan Baru"
            icon="pi pi-arrow-left"
            severity="secondary"
            class="w-full !py-2.5 text-xs sm:text-sm"
          />
        </div>

        <!-- SCENARIO 2: SUCCESS RESET -->
        <div v-else-if="isSuccess" class="space-y-5 text-center">
          <div class="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto border-2 border-emerald-200 dark:border-emerald-800 shadow-inner">
            <i class="pi pi-check-circle text-3xl"></i>
          </div>
          <div class="space-y-1.5">
            <h2 class="text-lg font-bold text-slate-800 dark:text-white">Kata Sandi Berhasil Diperbarui!</h2>
            <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300">
              Kata sandi akun Anda telah berhasil diubah. Mengalihkan ke halaman login dalam <b>{{ countdown }}</b> detik...
            </p>
          </div>
          <Button
            label="Masuk Sekarang"
            icon="pi pi-sign-in"
            severity="success"
            class="w-full !py-2.5 font-semibold text-xs sm:text-sm shadow-md"
            @click="navigateTo('/login')"
          />
        </div>

        <!-- SCENARIO 3: FORM RESET PASSWORD -->
        <div v-else class="space-y-4">
          <Message v-if="errorMessage" severity="error" :closable="true" @close="errorMessage = ''" class="text-xs">
            {{ errorMessage }}
          </Message>

          <form @submit.prevent="handleReset" class="space-y-4">
            <!-- Password Baru -->
            <div class="flex flex-col gap-1.5">
              <label for="password" class="text-xs font-medium text-slate-700 dark:text-slate-300">
                Kata Sandi Baru <span class="text-rose-500">*</span>
              </label>
              <Password
                id="password"
                v-model="password"
                placeholder="Minimal 6 karakter"
                toggleMask
                :feedback="true"
                class="w-full"
                inputClass="w-full text-xs sm:text-sm"
                :disabled="loading"
                required
              />
            </div>

            <!-- Konfirmasi Password -->
            <div class="flex flex-col gap-1.5">
              <label for="confirm-password" class="text-xs font-medium text-slate-700 dark:text-slate-300">
                Konfirmasi Kata Sandi Baru <span class="text-rose-500">*</span>
              </label>
              <Password
                id="confirm-password"
                v-model="confirmPassword"
                placeholder="Ulangi kata sandi baru"
                toggleMask
                :feedback="false"
                class="w-full"
                inputClass="w-full text-xs sm:text-sm"
                :disabled="loading"
                required
              />
            </div>

            <Button
              type="submit"
              label="Simpan Kata Sandi Baru"
              icon="pi pi-check"
              severity="success"
              class="w-full !py-2.5 font-semibold text-xs sm:text-sm shadow-md"
              :loading="loading"
            />
          </form>

          <div class="text-center pt-2 border-t border-slate-100 dark:border-slate-800">
            <NuxtLink to="/login" class="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline">
              <i class="pi pi-arrow-left text-[11px]"></i> Kembali ke Halaman Login
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: false })

const route = useRoute()
const api = useApi()
const toast = useToast()
const authStore = useAuthStore()

const token = computed(() => (route.query.token as string) || '')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const isSuccess = ref(false)
const errorMessage = ref('')
const countdown = ref(3)

let timer: any = null

onMounted(() => {
  // Clear any existing active session to prevent conflict with password recovery
  if (authStore.isAuthenticated) {
    authStore.logout()
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

async function handleReset() {
  errorMessage.value = ''

  if (!password.value || password.value.length < 6) {
    errorMessage.value = 'Kata sandi baru minimal terdiri dari 6 karakter.'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Konfirmasi kata sandi tidak cocok. Pastikan kedua input sama.'
    return
  }

  loading.value = true
  try {
    await api.post('/auth/reset-password', {
      token: token.value,
      new_password: password.value
    })

    isSuccess.value = true
    toast.add({
      severity: 'success',
      summary: 'Sukses',
      detail: 'Kata sandi berhasil diperbarui!',
      life: 3000
    })

    // Auto redirect countdown
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
        navigateTo('/login')
      }
    }, 1000)
  } catch (err: any) {
    console.error('Reset password error:', err)
    const detail = err?.data?.detail || err?.message || ''
    if (detail.toLowerCase().includes('token') || detail.toLowerCase().includes('expired') || detail.toLowerCase().includes('invalid')) {
      errorMessage.value = 'Tautan reset kata sandi ini sudah kedaluwarsa atau tidak valid. Silakan ajukan permintaan reset baru.'
    } else {
      errorMessage.value = detail || 'Gagal mengatur ulang kata sandi. Silakan coba kembali.'
    }
  } finally {
    loading.value = false
  }
}
</script>
