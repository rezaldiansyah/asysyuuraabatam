<template>
  <NuxtLayout name="dashboard">
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Data Siswa</h1>
          <p class="text-slate-500 dark:text-slate-400">Manajemen data siswa aktif.</p>
        </div>
        <Button severity="success" @click="showAddDialog = true">
          <i class="pi pi-plus mr-2"></i>
          Tambah Siswa
        </Button>
      </div>

      <!-- Data Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
        <DataTable
          :value="students"
          :loading="loading"
          paginator
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          stripedRows
          removableSort
          class="p-datatable-sm"
        >
          <template #empty>
            <div class="text-center py-8 text-slate-500">Belum ada data siswa.</div>
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

          <Column header="NIS / NISN">
            <template #body="{ data }">
              <div class="flex flex-col text-sm">
                <span class="text-slate-500">NIS: {{ data.nis || '-' }}</span>
                <span>NISN: {{ data.nisn || '-' }}</span>
              </div>
            </template>
          </Column>

          <Column field="gender" header="L/P" style="width: 80px">
            <template #body="{ data }">
              <Tag :value="data.gender" :severity="data.gender === 'L' ? 'info' : 'danger'" />
            </template>
          </Column>

          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag
                :value="data.status"
                :severity="data.status === 'ACTIVE' ? 'success' : 'secondary'"
              />
            </template>
          </Column>

          <Column field="unit_name" header="Unit" />

          <Column header="Aksi" style="width: 120px">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" severity="secondary" size="small" text rounded @click="editStudent(data)" />
                <Button icon="pi pi-trash" severity="danger" size="small" text rounded @click="confirmDelete(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Add/Edit Dialog -->
      <Dialog
        v-model:visible="showAddDialog"
        :header="editingStudent ? 'Edit Siswa' : 'Tambah Siswa Baru'"
        :style="{ width: '450px' }"
        modal
        @hide="resetForm"
      >
        <form @submit.prevent="submitForm" class="space-y-4">
          <!-- Nama Lengkap -->
          <div class="flex flex-col gap-2">
            <label for="full_name" class="font-medium">Nama Lengkap *</label>
            <InputText
              id="full_name"
              v-model="form.full_name"
              placeholder="Nama Siswa"
              class="w-full"
              :class="{ 'p-invalid': errors.full_name }"
            />
            <small v-if="errors.full_name" class="text-red-500">{{ errors.full_name }}</small>
          </div>

          <!-- NIS & NISN -->
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label for="nis" class="font-medium">NIS</label>
              <InputText id="nis" v-model="form.nis" placeholder="NIS" class="w-full" />
            </div>
            <div class="flex flex-col gap-2">
              <label for="nisn" class="font-medium">NISN</label>
              <InputText id="nisn" v-model="form.nisn" placeholder="NISN" class="w-full" />
            </div>
          </div>

          <!-- Gender -->
          <div class="flex flex-col gap-2">
            <label for="gender" class="font-medium">Jenis Kelamin *</label>
            <Select
              id="gender"
              v-model="form.gender"
              :options="genderOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Pilih jenis kelamin"
              class="w-full"
            />
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
            <Button type="submit" :label="editingStudent ? 'Update' : 'Simpan'" :loading="submitting" />
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
const students = ref<any[]>([])
const units = ref<any[]>([])
const loading = ref(true)
const loadingUnits = ref(false)
const submitting = ref(false)
const showAddDialog = ref(false)
const editingStudent = ref<any>(null)

const genderOptions = [
  { label: 'Laki-laki', value: 'L' },
  { label: 'Perempuan', value: 'P' },
]

const form = reactive({
  full_name: '',
  nis: '',
  nisn: '',
  gender: 'L',
  unit_id: null as number | null,
})

const errors = reactive({
  full_name: '',
})

// Fetch students
async function fetchStudents() {
  loading.value = true
  try {
    const data = await api.get<any[]>('/academic/students')
    students.value = data
  } catch (error) {
    console.error('Failed to fetch students:', error)
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

// Edit student
function editStudent(student: any) {
  editingStudent.value = student
  form.full_name = student.full_name
  form.nis = student.nis || ''
  form.nisn = student.nisn || ''
  form.gender = student.gender
  form.unit_id = student.unit_id
  showAddDialog.value = true
}

// Reset form
function resetForm() {
  editingStudent.value = null
  form.full_name = ''
  form.nis = ''
  form.nisn = ''
  form.gender = 'L'
  form.unit_id = null
  errors.full_name = ''
}

// Validate form
function validateForm() {
  errors.full_name = ''
  if (!form.full_name || form.full_name.length < 2) {
    errors.full_name = 'Nama lengkap minimal 2 karakter.'
    return false
  }
  return true
}

// Submit form
async function submitForm() {
  if (!validateForm()) return

  submitting.value = true
  try {
    if (editingStudent.value) {
      await api.put(`/academic/students/${editingStudent.value.id}`, form)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data siswa berhasil diupdate', life: 3000 })
    } else {
      await api.post('/academic/students', form)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data siswa berhasil ditambahkan', life: 3000 })
    }
    showAddDialog.value = false
    resetForm()
    fetchStudents()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan data siswa', life: 3000 })
  } finally {
    submitting.value = false
  }
}

// Confirm delete
function confirmDelete(student: any) {
  confirm.require({
    message: `Yakin ingin menghapus siswa "${student.full_name}"?`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete(`/academic/students/${student.id}`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Siswa berhasil dihapus', life: 3000 })
        fetchStudents()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus siswa', life: 3000 })
      }
    },
  })
}

// On mount
onMounted(() => {
  fetchStudents()
  fetchUnits()
})

// Watch dialog open to refresh units
watch(showAddDialog, (val) => {
  if (val && units.value.length === 0) {
    fetchUnits()
  }
})
</script>
