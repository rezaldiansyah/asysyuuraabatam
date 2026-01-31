<template>
  <Dialog 
    :visible="visible" 
    :header="isEdit ? 'Edit User' : 'Tambah User Baru'" 
    modal 
    @update:visible="$emit('update:visible', $event)"
    class="w-full max-w-lg"
  >
    <div class="space-y-4">
      <!-- Full Name -->
      <div class="flex flex-col gap-2">
        <label class="font-medium text-slate-700 dark:text-slate-300">Nama Lengkap</label>
        <InputText v-model="form.full_name" placeholder="John Doe" />
        <small v-if="errors.full_name" class="text-red-500">{{ errors.full_name }}</small>
      </div>

      <!-- Email -->
      <div class="flex flex-col gap-2">
        <label class="font-medium text-slate-700 dark:text-slate-300">Email</label>
        <InputText v-model="form.email" placeholder="john@example.com" />
        <small v-if="errors.email" class="text-red-500">{{ errors.email }}</small>
      </div>

       <!-- NIK -->
      <div class="flex flex-col gap-2">
        <label class="font-medium text-slate-700 dark:text-slate-300">NIK / Username</label>
        <InputText v-model="form.nik" placeholder="12345678" />
        <small v-if="errors.nik" class="text-red-500">{{ errors.nik }}</small>
      </div>

      <!-- Role -->
      <div class="flex flex-col gap-2">
        <label class="font-medium text-slate-700 dark:text-slate-300">Role</label>
        <Select 
          v-model="form.role_id" 
          :options="roleOptions" 
          optionLabel="name" 
          optionValue="id" 
          placeholder="Pilih Role" 
          class="w-full"
        />
        <small v-if="errors.role_id" class="text-red-500">{{ errors.role_id }}</small>
      </div>

       <!-- Password -->
      <div class="flex flex-col gap-2">
        <label class="font-medium text-slate-700 dark:text-slate-300">
           {{ isEdit ? 'Password Baru (Kosongkan jika tidak diubah)' : 'Password' }}
        </label>
        <Password 
           v-model="form.password" 
           toggleMask 
           :feedback="!isEdit" 
           inputClass="w-full"
           placeholder="******"
        />
        <small v-if="errors.password" class="text-red-500">{{ errors.password }}</small>
      </div>
      
       <!-- Status -->
      <div class="flex items-center gap-2">
        <Checkbox v-model="form.is_active" :binary="true" inputId="status" />
        <label for="status" class="font-medium text-slate-700 dark:text-slate-300">Aktif</label>
      </div>

    </div>

    <template #footer>
      <Button label="Batal" icon="pi pi-times" text @click="$emit('close')" />
      <Button label="Simpan" icon="pi pi-check" :loading="loading" @click="save" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { useForm } from 'vee-validate'
import * as yup from 'yup'

const props = defineProps({
  visible: Boolean,
  user: { type: Object, default: null },
  roles: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:visible', 'close', 'saved'])
const api = useApi()
const loading = ref(false)

const isEdit = computed(() => !!props.user)
const roleOptions = computed(() => props.roles)

const schema = yup.object({
  full_name: yup.string().required('Nama wajib diisi'),
  email: yup.string().email('Email tidak valid').required('Email wajib diisi'),
  nik: yup.string().required('NIK wajib diisi'),
  role_id: yup.number().required('Role wajib dipilih'),
  password: yup.string().test('password-required', 'Password wajib diisi untuk user baru', function(val) {
    if (!isEdit.value && !val) return false
    return true
  })
})

const { defineField, handleSubmit, errors, resetForm, setValues } = useForm({
  validationSchema: schema,
  initialValues: {
     is_active: true
  }
})

const [full_name] = defineField('full_name') // Wait, using v-model directly on form object is easier for PrimeVue checks? 
// Actually standard is using v-model="value" and binding error.
// I will use simplified reactive form object + manual validate or verify api
// But VeeValidate with `defineField` returns [value, props].
// I'll stick to a simple reactive form for integration speed with PrimeVue components.

const form = reactive({
    full_name: '',
    email: '',
    nik: '',
    role_id: null as number | null,
    password: '',
    is_active: true
})

// Validation State
const validate = () => {
    errors.value = {}
    let isValid = true
    if (!form.full_name) { errors.value.full_name = 'Nama wajib diisi'; isValid = false }
    if (!form.email) { errors.value.email = 'Email wajib diisi'; isValid = false }
    if (!form.nik) { errors.value.nik = 'NIK wajib diisi'; isValid = false }
    if (!form.role_id) { errors.value.role_id = 'Role wajib dipilih'; isValid = false }
    if (!isEdit.value && !form.password) { errors.value.password = 'Password wajib diisi'; isValid = false }
    return isValid
}

watch(() => props.user, (newVal) => {
    if (newVal) {
        form.full_name = newVal.full_name
        form.email = newVal.email
        form.nik = newVal.nik
        form.role_id = newVal.role_id
        form.is_active = newVal.is_active
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

const save = async () => {
    if (!validate()) return

    loading.value = true
    try {
        if (isEdit.value) {
            await api.put(`/users/${props.user.id}`, form)
        } else {
            await api.post('/users', form)
        }
        emit('saved')
        emit('close')
    } catch (e: any) {
        console.error(e)
        // Handle backend validation errors?
        if (e.message.includes('Email already registered')) {
            errors.value.email = 'Email sudah terdaftar'
        }
    } finally {
        loading.value = false
    }
}

</script>
