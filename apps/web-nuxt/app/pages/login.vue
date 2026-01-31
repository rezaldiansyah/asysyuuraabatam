<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary via-primary-dark to-slate-900 px-4">
    <div class="w-full max-w-md">
      <!-- Login Card -->
      <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-8">
        <!-- Logo -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mx-auto mb-4">
            <span class="text-white font-bold text-2xl">AS</span>
          </div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">SIST Asy-Syuuraa</h1>
          <p class="text-slate-500 dark:text-slate-400 mt-1">Sistem Informasi Sekolah Terpadu</p>
        </div>

        <!-- Error Message -->
        <Message v-if="errorMessage" severity="error" class="mb-4">{{ errorMessage }}</Message>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- NIK Field -->
          <div class="flex flex-col gap-2">
            <label for="nik" class="font-medium text-slate-700 dark:text-slate-300">NIK / Username</label>
            <InputText
              id="nik"
              v-model="form.nik"
              placeholder="Masukkan NIK"
              class="w-full"
              :disabled="loading"
            />
          </div>

          <!-- Password Field -->
          <div class="flex flex-col gap-2">
            <label for="password" class="font-medium text-slate-700 dark:text-slate-300">Password</label>
            <Password
              id="password"
              v-model="form.password"
              placeholder="Masukkan password"
              :feedback="false"
              toggleMask
              class="w-full"
              inputClass="w-full"
              :disabled="loading"
            />
          </div>

          <!-- Forgot Password -->
          <div class="text-right">
            <NuxtLink to="/forgot-password" class="text-sm text-primary hover:underline">
              Lupa password?
            </NuxtLink>
          </div>

          <!-- Submit Button -->
          <Button
            type="submit"
            label="Masuk"
            class="w-full"
            :loading="loading"
            severity="success"
          />
        </form>

        <!-- Back to Home -->
        <div class="text-center mt-6">
          <NuxtLink to="/" class="text-slate-500 hover:text-primary text-sm">
            ← Kembali ke Beranda
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
})

const authStore = useAuthStore()
const api = useApi()
const router = useRouter()

const form = reactive({
  nik: '',
  password: '',
})

const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (!form.nik || !form.password) {
    errorMessage.value = 'NIK dan password harus diisi'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const config = useRuntimeConfig()
    const formData = new URLSearchParams()
    formData.append('username', form.nik)
    formData.append('password', form.password)

    const response = await $fetch<{ access_token: string; token_type: string }>(
      `${config.public.apiBase}/auth/login`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      }
    )

    // Use username from form as basic user info (API doesn't have /auth/me endpoint)
    const user = { nik: form.nik, full_name: 'Admin' }

    authStore.setAuth(response.access_token, user)
    router.push('/dashboard')
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || 'NIK atau password salah'
  } finally {
    loading.value = false
  }
}
</script>
