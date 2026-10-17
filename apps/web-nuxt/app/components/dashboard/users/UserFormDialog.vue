<template>
  <Dialog 
    :visible="visible" 
    :header="isEdit ? 'Edit Pengguna' : 'Tambah Pengguna Baru'" 
    modal 
    @update:visible="$emit('update:visible', $event)"
    class="w-full max-w-lg text-sm"
    :pt="{
      header: { class: 'pb-2 border-b border-slate-100 dark:border-slate-800' },
      content: { class: 'pt-4' },
      footer: { class: 'pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2' }
    }"
  >
    <form @submit.prevent="save" class="space-y-3.5 text-xs">
      <!-- Full Name -->
      <div class="flex flex-col gap-1.5">
        <label class="font-medium text-slate-700 dark:text-slate-300">
          Nama Lengkap <span class="text-rose-500">*</span>
        </label>
        <InputText 
          v-model="form.full_name" 
          placeholder="Contoh: Ahmad Fauzi, S.Pd." 
          size="small"
          class="w-full"
          :invalid="!!errors.full_name"
        />
        <small v-if="errors.full_name" class="text-rose-500 text-[11px]">{{ errors.full_name }}</small>
      </div>

      <!-- Email & NIK (2 columns) -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <!-- Email -->
        <div class="flex flex-col gap-1.5">
          <label class="font-medium text-slate-700 dark:text-slate-300">
            Email <span class="text-rose-500">*</span>
          </label>
          <InputText 
            v-model="form.email" 
            placeholder="nama@asysyuura.sch.id" 
            size="small"
            class="w-full"
            :invalid="!!errors.email"
          />
          <small v-if="errors.email" class="text-rose-500 text-[11px]">{{ errors.email }}</small>
        </div>

        <!-- NIK / Username -->
        <div class="flex flex-col gap-1.5">
          <label class="font-medium text-slate-700 dark:text-slate-300">
            NIK / Username <span class="text-rose-500">*</span>
          </label>
          <InputText 
            v-model="form.nik" 
            placeholder="Contoh: 19850101" 
            size="small"
            class="w-full"
            :invalid="!!errors.nik"
          />
          <small v-if="errors.nik" class="text-rose-500 text-[11px]">{{ errors.nik }}</small>
        </div>
      </div>

      <!-- Role Selection -->
      <div class="flex flex-col gap-1.5">
        <label class="font-medium text-slate-700 dark:text-slate-300">
          Role / Hak Akses <span class="text-rose-500">*</span>
        </label>
        <Select 
          v-model="form.role_id" 
          :options="roleOptions" 
          optionLabel="name" 
          optionValue="id" 
          placeholder="Pilih Role Pengguna" 
          size="small"
          class="w-full"
          :invalid="!!errors.role_id"
        >
          <template #option="slotProps">
            <div class="flex items-center justify-between w-full text-xs">
              <span>{{ slotProps.option.name }}</span>
              <span class="text-slate-400 uppercase text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800">{{ slotProps.option.code }}</span>
            </div>
          </template>
        </Select>
        <small v-if="errors.role_id" class="text-rose-500 text-[11px]">{{ errors.role_id }}</small>
      </div>

      <!-- Password -->
      <div class="flex flex-col gap-1.5">
        <div class="flex justify-between items-center">
          <label class="font-medium text-slate-700 dark:text-slate-300">
            {{ isEdit ? 'Reset Password (Opsional)' : 'Password' }} 
            <span v-if="!isEdit" class="text-rose-500">*</span>
          </label>
          <span v-if="isEdit" class="text-[10px] text-slate-400">Kosongkan bila tidak diubah</span>
        </div>
        <Password 
          v-model="form.password" 
          toggleMask 
          :feedback="!isEdit" 
          size="small"
          class="w-full"
          inputClass="w-full text-xs"
          :placeholder="isEdit ? 'Masukkan password baru bila ingin mereset' : 'Minimal 6 karakter'"
          :invalid="!!errors.password"
        />
        <small v-if="errors.password" class="text-rose-500 text-[11px]">{{ errors.password }}</small>
      </div>
      
      <!-- Status Aktif Switch/Checkbox -->
      <div class="pt-1">
        <div class="flex items-center gap-2 p-2.5 rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <Checkbox v-model="form.is_active" :binary="true" inputId="user-status-switch" />
          <label for="user-status-switch" class="cursor-pointer font-medium text-slate-700 dark:text-slate-300 select-none">
            Status Akun Aktif
            <span class="block text-[11px] text-slate-400 font-normal">
              Akun yang tidak aktif tidak akan dapat login ke sistem dashboard.
            </span>
          </label>
        </div>
      </div>
    </form>

    <template #footer>
      <Button label="Batal" icon="pi pi-times" text size="small" @click="$emit('close')" />
      <Button 
        :label="isEdit ? 'Simpan Perubahan' : 'Tambah Pengguna'" 
        icon="pi pi-check" 
        size="small" 
        :loading="loading" 
        @click="save" 
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const props = defineProps<{
  visible: boolean
  user?: any
  roles?: any[]
}>()

const emit = defineEmits(['update:visible', 'close', 'saved'])

const api = useApi()
const toast = useToast()
const loading = ref(false)

const isEdit = computed(() => !!props.user?.id)
const roleOptions = computed(() => props.roles || [])

const form = reactive({
  full_name: '',
  email: '',
  nik: '',
  role_id: null as number | null,
  password: '',
  is_active: true
})

const errors = ref<Record<string, string>>({})

watch(() => props.user, (newVal) => {
  errors.value = {}
  if (newVal) {
    form.full_name = newVal.full_name || ''
    form.email = newVal.email || ''
    form.nik = newVal.nik || ''
    form.role_id = newVal.role_id || newVal.role?.id || null
    form.is_active = newVal.is_active !== false
    form.password = ''
  } else {
    form.full_name = ''
    form.email = ''
    form.nik = ''
    form.role_id = null
    form.is_active = true
    form.password = ''
  }
}, { immediate: true })

function validate() {
  errors.value = {}
  let valid = true

  if (!form.full_name || !form.full_name.trim()) {
    errors.value.full_name = 'Nama lengkap wajib diisi'
    valid = false
  }

  if (!form.email || !form.email.trim()) {
    errors.value.email = 'Email wajib diisi'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
    errors.value.email = 'Format email tidak valid'
    valid = false
  }

  if (!form.nik || !form.nik.trim()) {
    errors.value.nik = 'NIK / Username wajib diisi'
    valid = false
  }

  if (!form.role_id) {
    errors.value.role_id = 'Role pengguna wajib dipilih'
    valid = false
  }

  if (!isEdit.value) {
    if (!form.password) {
      errors.value.password = 'Password wajib diisi untuk pengguna baru'
      valid = false
    } else if (form.password.length < 6) {
      errors.value.password = 'Password minimal 6 karakter'
      valid = false
    }
  } else if (form.password && form.password.length < 6) {
    errors.value.password = 'Password baru minimal 6 karakter'
    valid = false
  }

  return valid
}

async function save() {
  if (!validate()) return

  loading.value = true
  try {
    const payload: any = {
      full_name: form.full_name.trim(),
      email: form.email.trim().toLowerCase(),
      nik: form.nik.trim(),
      role_id: form.role_id,
      is_active: form.is_active
    }

    if (form.password && form.password.trim()) {
      payload.password = form.password.trim()
    }

    if (isEdit.value) {
      await api.put(`/users/${props.user.id}`, payload)
      toast.add({
        severity: 'success',
        summary: 'Berhasil',
        detail: `Data pengguna ${payload.full_name} berhasil diperbarui`,
        life: 3000
      })
    } else {
      await api.post('/users', payload)
      toast.add({
        severity: 'success',
        summary: 'Berhasil',
        detail: `Pengguna baru ${payload.full_name} berhasil ditambahkan`,
        life: 3000
      })
    }

    emit('saved')
    emit('close')
  } catch (e: any) {
    console.error('Error saving user:', e)
    const errDetail = e?.data?.detail || e?.message || 'Gagal menyimpan data pengguna'
    
    if (typeof errDetail === 'string') {
      if (errDetail.toLowerCase().includes('email')) {
        errors.value.email = errDetail
      } else if (errDetail.toLowerCase().includes('nik')) {
        errors.value.nik = errDetail
      }
      toast.add({
        severity: 'error',
        summary: 'Gagal Menyimpan',
        detail: errDetail,
        life: 4000
      })
    } else if (Array.isArray(errDetail)) {
      // Pydantic validation errors
      const firstMsg = errDetail[0]?.msg || 'Validasi gagal'
      toast.add({
        severity: 'error',
        summary: 'Validasi Gagal',
        detail: firstMsg,
        life: 4000
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Terjadi Kesalahan',
        detail: 'Gagal menghubungi server untuk menyimpan data',
        life: 4000
      })
    }
  } finally {
    loading.value = false
  }
}
</script>
