<template>
  <div class="flex items-center justify-center min-h-screen bg-slate-50 dark:bg-slate-900 p-4">
    <div class="max-w-md w-full">
      <Card class="shadow-xl">
        <template #title>
          <div class="text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-500 mb-4 shadow-inner">
              <i class="pi pi-lock text-3xl"></i>
            </div>
            <h2 class="text-2xl font-bold text-slate-800 dark:text-white">Ganti Password Wajib</h2>
          </div>
        </template>
        <template #content>
          <p class="text-slate-600 dark:text-slate-400 text-center text-xs sm:text-sm mb-6 leading-relaxed">
            Demi keamanan akun Anda, silakan ubah password sementara / default Anda sebelum dapat mengakses menu dashboard.
          </p>

          <form @submit.prevent="submitForm" class="space-y-4">
            <!-- Password Lama -->
            <div>
              <div class="flex justify-between items-center mb-1">
                <label class="block text-xs font-medium text-slate-700 dark:text-slate-300">
                  Password Lama (Default) <span class="text-rose-500">*</span>
                </label>
                <NuxtLink to="/forgot-password" class="text-[11px] text-primary hover:underline font-medium">
                  Lupa password lama?
                </NuxtLink>
              </div>
              <Password 
                v-model="form.old_password" 
                :feedback="false" 
                toggleMask 
                placeholder="Masukkan password lama / tanggal lahir"
                class="w-full" 
                inputClass="w-full text-xs sm:text-sm" 
                :class="{ 'p-invalid': submitted && !form.old_password }" 
              />
              <small class="text-rose-500 text-[11px] block mt-1" v-if="submitted && !form.old_password">
                Password lama wajib diisi. Jika Anda lupa, klik tautan "Lupa password lama?" di atas.
              </small>
            </div>

            <!-- Password Baru -->
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Password Baru <span class="text-rose-500">*</span>
              </label>
              <Password 
                v-model="form.new_password" 
                toggleMask 
                placeholder="Minimal 6 karakter"
                class="w-full" 
                inputClass="w-full text-xs sm:text-sm" 
                :class="{ 'p-invalid': submitted && (!form.new_password || form.new_password.length < 6) }"
              >
                <template #header>
                  <div class="font-semibold text-xs mb-2">Kriteria Password</div>
                </template>
                <template #footer>
                  <Divider />
                  <p class="mt-2 text-[11px] text-slate-500">Saran: Gunakan kombinasi huruf besar, huruf kecil, angka, dan simbol.</p>
                </template>
              </Password>
              <small class="text-rose-500 text-[11px] block mt-1" v-if="submitted && (!form.new_password || form.new_password.length < 6)">
                Password baru minimal 6 karakter.
              </small>
            </div>

            <!-- Konfirmasi Password Baru -->
            <div>
              <label class="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Konfirmasi Password Baru <span class="text-rose-500">*</span>
              </label>
              <Password 
                v-model="form.confirm_password" 
                :feedback="false" 
                toggleMask 
                placeholder="Ulangi password baru"
                class="w-full" 
                inputClass="w-full text-xs sm:text-sm" 
                :class="{ 'p-invalid': submitted && (!form.confirm_password || form.new_password !== form.confirm_password) }" 
              />
              <small class="text-rose-500 text-[11px] block mt-1" v-if="submitted && form.new_password !== form.confirm_password">
                Konfirmasi password tidak cocok.
              </small>
            </div>

            <!-- Submit Button -->
            <Button 
              type="submit" 
              label="Ubah Password & Masuk" 
              icon="pi pi-check" 
              class="w-full mt-6 text-xs sm:text-sm font-semibold !py-2.5 shadow-md" 
              severity="success"
              :loading="loading" 
            />
          </form>

          <!-- Alternative Options -->
          <div class="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col items-center gap-2 text-xs">
            <button 
              type="button" 
              @click="handleLogout" 
              class="text-slate-500 hover:text-rose-600 transition-colors flex items-center gap-1 font-medium"
            >
              <i class="pi pi-sign-out text-xs"></i> Keluar / Ganti Akun
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'empty' })

const router = useRouter()
const toast = useToast()
const api = useApi()
const authStore = useAuthStore()

const loading = ref(false)
const submitted = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

async function submitForm() {
  submitted.value = true

  // Validation
  if (!form.old_password) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Password lama wajib diisi. Jika lupa, gunakan menu Lupa Password.',
      life: 4000
    })
    return
  }

  if (!form.new_password || form.new_password.length < 6) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Password baru minimal 6 karakter.',
      life: 4000
    })
    return
  }

  if (form.new_password !== form.confirm_password) {
    toast.add({
      severity: 'warn',
      summary: 'Perhatian',
      detail: 'Konfirmasi password baru tidak cocok.',
      life: 4000
    })
    return
  }

  loading.value = true
  try {
    await api.post('/auth/change-password', {
      old_password: form.old_password,
      new_password: form.new_password
    })

    // Update store state
    if (authStore.user) {
      authStore.user.must_change_password = false
      authStore.setAuth(authStore.token || '', authStore.user)
    }

    toast.add({
      severity: 'success',
      summary: 'Berhasil',
      detail: 'Password Anda telah berhasil diperbarui. Selamat datang!',
      life: 3000
    })
    router.push('/dashboard')
  } catch (error: any) {
    console.error('Change password error:', error)
    const msg = error?.data?.detail || error?.message || 'Gagal mengubah password. Pastikan password lama Anda benar.'
    toast.add({
      severity: 'error',
      summary: 'Gagal',
      detail: msg,
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  authStore.logout()
  navigateTo('/login')
}
</script>
