<template>
  <NuxtLayout name="dashboard">
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Data Guru</h1>
          <p class="text-slate-500 dark:text-slate-400">Manajemen data guru dan staf pengajar.</p>
        </div>
        <Button severity="success" @click="showAddDialog = true">
          <i class="pi pi-plus mr-2"></i>
          Tambah Guru
        </Button>
      </div>

      <!-- Data Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
        <DataTable
          :value="teachers"
          :loading="loading"
          paginator
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          stripedRows
          removableSort
          class="p-datatable-sm"
        >
          <template #empty>
            <div class="text-center py-8 text-slate-500">Belum ada data guru.</div>
          </template>
          <template #loading>
            <div class="flex justify-center items-center py-8">
              <i class="pi pi-spin pi-spinner text-2xl mr-2"></i>
              Loading...
            </div>
          </template>

          <Column field="full_name" header="Nama Lengkap" sortable>
            <template #body="{ data }">
              <span class="font-medium">{{ data.full_name }}</span>
            </template>
          </Column>

          <Column field="nik" header="NIK">
            <template #body="{ data }">
              {{ data.nik || '-' }}
            </template>
          </Column>

          <Column field="email" header="Email" sortable />

          <Column field="is_active" header="Status" style="width: 100px">
            <template #body="{ data }">
              <Tag
                :value="data.is_active ? 'Aktif' : 'Nonaktif'"
                :severity="data.is_active ? 'success' : 'danger'"
              />
            </template>
          </Column>

          <Column header="Aksi" style="width: 120px">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" severity="secondary" size="small" text rounded @click="editTeacher(data)" />
                <Button icon="pi pi-trash" severity="danger" size="small" text rounded @click="confirmDelete(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Add/Edit Dialog -->
      <Dialog
        v-model:visible="showAddDialog"
        :header="editingTeacher ? 'Edit Guru' : 'Tambah Guru Baru'"
        :style="{ width: '500px' }"
        modal
        @hide="resetForm"
      >
        <p class="text-slate-500 mb-4">User baru dengan role 'GURU' akan dibuat.</p>

        <form @submit.prevent="submitForm" class="space-y-4">
          <!-- Nama Lengkap -->
          <div class="flex flex-col gap-2">
            <label for="full_name" class="font-medium">Nama Lengkap *</label>
            <InputText
              id="full_name"
              v-model="form.full_name"
              placeholder="Nama Guru"
              class="w-full"
              :class="{ 'p-invalid': errors.full_name }"
            />
            <small v-if="errors.full_name" class="text-red-500">{{ errors.full_name }}</small>
          </div>

          <!-- NIK & Email -->
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label for="nik" class="font-medium">NIK *</label>
              <InputText
                id="nik"
                v-model="form.nik"
                placeholder="Nomor Induk"
                class="w-full"
                :class="{ 'p-invalid': errors.nik }"
              />
              <small v-if="errors.nik" class="text-red-500">{{ errors.nik }}</small>
            </div>
            <div class="flex flex-col gap-2">
              <label for="email" class="font-medium">Email *</label>
              <InputText
                id="email"
                v-model="form.email"
                placeholder="email@sekolah.id"
                class="w-full"
                :class="{ 'p-invalid': errors.email }"
              />
              <small v-if="errors.email" class="text-red-500">{{ errors.email }}</small>
            </div>
          </div>

          <!-- Password (only for new teacher) -->
          <div v-if="!editingTeacher" class="flex flex-col gap-2">
            <label for="password" class="font-medium">Password Login *</label>
            <Password
              id="password"
              v-model="form.password"
              placeholder="Minimal 6 karakter"
              class="w-full"
              inputClass="w-full"
              :feedback="false"
              toggleMask
              :class="{ 'p-invalid': errors.password }"
            />
            <small v-if="errors.password" class="text-red-500">{{ errors.password }}</small>
          </div>

          <!-- Unit -->
          <div class="flex flex-col gap-2">
            <label for="unit_id" class="font-medium">Unit Sekolah *</label>
            <Select
              id="unit_id"
              v-model="form.unit_id"
              :options="units"
              optionLabel="name"
              optionValue="id"
              placeholder="Pilih unit"
              class="w-full"
              :loading="loadingUnits"
            />
          </div>

          <!-- Dialog Footer -->
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showAddDialog = false" />
            <Button type="submit" :label="editingTeacher ? 'Update' : 'Simpan'" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Delete Confirmation -->
      <ConfirmDialog />
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: false })

const api = useApi()
const confirm = useConfirm()
const toast = useToast()

// State
const teachers = ref<any[]>([])
const units = ref<any[]>([])
const loading = ref(true)
const loadingUnits = ref(false)
const submitting = ref(false)
const showAddDialog = ref(false)
const editingTeacher = ref<any>(null)

const form = reactive({
  full_name: '',
  nik: '',
  email: '',
  password: '',
  unit_id: null as number | null,
})

const errors = reactive({
  full_name: '',
  nik: '',
  email: '',
  password: '',
})

// Fetch teachers
async function fetchTeachers() {
  loading.value = true
  try {
    const data = await api.get<any[]>('/academic/teachers')
    teachers.value = data
  } catch (error) {
    console.error('Failed to fetch teachers:', error)
  } finally {
    loading.value = false
  }
}

// Fetch units
async function fetchUnits() {
  loadingUnits.value = true
  try {
    const data = await api.get<any[]>('/units')
    units.value = data
  } catch (error) {
    console.error('Failed to fetch units:', error)
  } finally {
    loadingUnits.value = false
  }
}

// Edit teacher
function editTeacher(teacher: any) {
  editingTeacher.value = teacher
  form.full_name = teacher.full_name
  form.nik = teacher.nik || ''
  form.email = teacher.email
  form.password = ''
  form.unit_id = teacher.unit_id
  showAddDialog.value = true
}

// Reset form
function resetForm() {
  editingTeacher.value = null
  form.full_name = ''
  form.nik = ''
  form.email = ''
  form.password = ''
  form.unit_id = null
  Object.keys(errors).forEach((key) => (errors[key as keyof typeof errors] = ''))
}

// Validate form
function validateForm(): boolean {
  let valid = true
  Object.keys(errors).forEach((key) => (errors[key as keyof typeof errors] = ''))

  if (!form.full_name || form.full_name.length < 2) {
    errors.full_name = 'Nama lengkap minimal 2 karakter.'
    valid = false
  }
  if (!form.nik || form.nik.length < 5) {
    errors.nik = 'NIK minimal 5 karakter.'
    valid = false
  }
  if (!form.email || !form.email.includes('@')) {
    errors.email = 'Email tidak valid.'
    valid = false
  }
  if (!editingTeacher.value && (!form.password || form.password.length < 6)) {
    errors.password = 'Password minimal 6 karakter.'
    valid = false
  }

  return valid
}

// Submit form
async function submitForm() {
  if (!validateForm()) return

  submitting.value = true
  try {
    const payload = { ...form }
    if (editingTeacher.value) {
      delete (payload as any).password // Don't send password on edit
      await api.put(`/academic/teachers/${editingTeacher.value.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data guru berhasil diupdate', life: 3000 })
    } else {
      await api.post('/academic/teachers', payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data guru berhasil ditambahkan', life: 3000 })
    }
    showAddDialog.value = false
    resetForm()
    fetchTeachers()
  } catch (error: any) {
    const msg = error?.data?.detail || 'Gagal menyimpan data guru'
    toast.add({ severity: 'error', summary: 'Gagal', detail: msg, life: 5000 })
  } finally {
    submitting.value = false
  }
}

// Confirm delete
function confirmDelete(teacher: any) {
  confirm.require({
    message: `Yakin ingin menghapus guru "${teacher.full_name}"?`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete(`/academic/teachers/${teacher.id}`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Guru berhasil dihapus', life: 3000 })
        fetchTeachers()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus guru', life: 3000 })
      }
    },
  })
}

// On mount
onMounted(() => {
  fetchTeachers()
  fetchUnits()
})

watch(showAddDialog, (val) => {
  if (val && units.value.length === 0) {
    fetchUnits()
  }
})
</script>
