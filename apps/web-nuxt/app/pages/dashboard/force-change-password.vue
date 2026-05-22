<template>
  <div class="flex items-center justify-center min-h-screen bg-slate-50 dark:bg-slate-900 p-4">
    <div class="max-w-md w-full">
      <Card class="shadow-xl">
        <template #title>
          <div class="text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/30 text-orange-500 mb-4">
              <i class="pi pi-lock text-3xl"></i>
            </div>
            <h2 class="text-2xl font-bold text-slate-800 dark:text-white">Ganti Password Wajib</h2>
          </div>
        </template>
        <template #content>
          <p class="text-slate-600 dark:text-slate-400 text-center mb-6">
            Demi keamanan, Anda diwajibkan untuk mengganti password default (tanggal lahir) Anda sebelum dapat mengakses sistem.
          </p>

          <form @submit.prevent="submitForm" class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Password Lama (Default)</label>
              <Password v-model="form.old_password" :feedback="false" toggleMask class="w-full" inputClass="w-full" :class="{ 'p-invalid': v$.old_password.$invalid && submitted }" />
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Password Baru</label>
              <Password v-model="form.new_password" toggleMask class="w-full" inputClass="w-full" :class="{ 'p-invalid': v$.new_password.$invalid && submitted }">
                <template #header>
                  <div class="font-semibold text-sm mb-2">Kriteria Password</div>
                </template>
                <template #footer>
                  <Divider />
                  <p class="mt-2 text-xs">Saran: Gunakan kombinasi huruf besar, huruf kecil, angka, dan simbol.</p>
                </template>
              </Password>
            </div>

            <div>
              <label class="block text-sm font-medium mb-1">Konfirmasi Password Baru</label>
              <Password v-model="form.confirm_password" :feedback="false" toggleMask class="w-full" inputClass="w-full" :class="{ 'p-invalid': v$.confirm_password.$invalid && submitted }" />
              <small class="text-red-500 block mt-1" v-if="submitted && form.new_password !== form.confirm_password">Password konfirmasi tidak cocok.</small>
            </div>

            <Button type="submit" label="Ubah Password & Lanjutkan" icon="pi pi-check" class="w-full mt-6" :loading="loading" />
          </form>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useVuelidate } from '@vuelidate/core'
import { required, minLength } from '@vuelidate/validators'

definePageMeta({ layout: 'empty' }) // Or minimal layout

const router = useRouter()
const toast = useToast()
const config = useRuntimeConfig()
const apiToken = useCookie('auth_token')
const authStore = useAuthStore()

const loading = ref(false)
const submitted = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const rules = {
  old_password: { required },
  new_password: { required, minLength: minLength(6) },
  confirm_password: { required }
}

const v$ = useVuelidate(rules, form)

const submitForm = async () => {
  submitted.value = true
  
  if (v$.value.$invalid) return
  if (form.new_password !== form.confirm_password) return
  
  loading.value = true
  try {
    await $fetch(`${config.public.apiBase}/auth/change-password`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiToken.value}` },
      body: {
        old_password: form.old_password,
        new_password: form.new_password
      }
    })
    
    // Update local store to remove force redirect
    if (authStore.user) {
      authStore.user.must_change_password = false
      authStore.setAuth(authStore.token, authStore.user)
    }
    
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Password telah diperbarui. Selamat datang!' })
    router.push('/dashboard')
    
  } catch (error) {
    const msg = error.data?.detail || 'Gagal mengubah password. Periksa password lama Anda.'
    toast.add({ severity: 'error', summary: 'Error', detail: msg })
  } finally {
    loading.value = false
  }
}
</script>
