<template>
  <NuxtLayout name="dashboard">
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Data Siswa</h1>
          <p class="text-slate-500 dark:text-slate-400">Manajemen data siswa aktif.</p>
        </div>
        <Button severity="success" @click="openAddDialog">
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
                :value="statusLabel(data.status)"
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

      <!-- Add/Edit Dialog - Multi Step -->
      <Dialog
        v-model:visible="showAddDialog"
        :header="editingStudent ? 'Edit Siswa' : 'Tambah Siswa Baru'"
        :style="{ width: '90vw', maxWidth: '650px' }"
        modal
        @hide="resetForm"
      >
        <!-- Step indicators -->
        <div class="flex items-center justify-center gap-2 mb-6">
          <button
            v-for="(stepLabel, idx) in stepLabels"
            :key="idx"
            class="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition"
            :class="currentStep === idx
              ? 'bg-primary/10 text-primary'
              : idx < currentStep
                ? 'text-green-600'
                : 'text-slate-400'"
            @click="currentStep = idx"
          >
            <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
              :class="currentStep === idx
                ? 'bg-primary text-white'
                : idx < currentStep
                  ? 'bg-green-500 text-white'
                  : 'bg-slate-200 text-slate-500'"
            >
              <i v-if="idx < currentStep" class="pi pi-check text-xs"></i>
              <span v-else>{{ idx + 1 }}</span>
            </span>
            <span class="hidden sm:inline">{{ stepLabel }}</span>
          </button>
        </div>

        <form @submit.prevent="submitForm">
          <!-- Step 1: Identitas -->
          <div v-show="currentStep === 0" class="space-y-4">
            <div class="flex flex-col gap-2">
              <label for="full_name" class="font-medium">Nama Lengkap *</label>
              <InputText
                id="full_name"
                v-model="form.full_name"
                placeholder="Nama lengkap siswa"
                class="w-full"
                :class="{ 'p-invalid': errors.full_name }"
              />
              <small v-if="errors.full_name" class="text-red-500">{{ errors.full_name }}</small>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-2">
                <label for="nis" class="font-medium">NIS</label>
                <InputText id="nis" v-model="form.nis" placeholder="No. Induk Sekolah" class="w-full" />
              </div>
              <div class="flex flex-col gap-2">
                <label for="nisn" class="font-medium">NISN</label>
                <InputText id="nisn" v-model="form.nisn" placeholder="No. Induk Siswa Nasional" class="w-full" />
              </div>
            </div>

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
          </div>

          <!-- Step 2: Data Pribadi -->
          <div v-show="currentStep === 1" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="flex flex-col gap-2">
                <label for="birth_place" class="font-medium">Tempat Lahir</label>
                <InputText id="birth_place" v-model="form.birth_place" placeholder="Kota lahir" class="w-full" />
              </div>
              <div class="flex flex-col gap-2">
                <label for="birth_date" class="font-medium">Tanggal Lahir</label>
                <DatePicker
                  id="birth_date"
                  v-model="form.birth_date"
                  dateFormat="dd/mm/yy"
                  placeholder="dd/mm/yyyy"
                  class="w-full"
                  showIcon
                  iconDisplay="input"
                />
              </div>
            </div>

            <div class="flex flex-col gap-2">
              <label for="address" class="font-medium">Alamat</label>
              <Textarea id="address" v-model="form.address" rows="3" placeholder="Alamat lengkap siswa" class="w-full" />
            </div>
          </div>

          <!-- Step 3: Penempatan -->
          <div v-show="currentStep === 2" class="space-y-4">
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

            <div class="flex flex-col gap-2">
              <label for="classroom_id" class="font-medium">Kelas</label>
              <Select
                id="classroom_id"
                v-model="form.current_classroom_id"
                :options="classrooms"
                optionLabel="name"
                optionValue="id"
                placeholder="Pilih kelas"
                class="w-full"
                :loading="loadingClassrooms"
                showClear
              />
            </div>

            <div class="flex flex-col gap-2">
              <label for="status" class="font-medium">Status</label>
              <Select
                id="status"
                v-model="form.status"
                :options="statusOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Status siswa"
                class="w-full"
              />
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex justify-between pt-6 border-t mt-6">
            <Button
              v-if="currentStep > 0"
              type="button"
              label="Sebelumnya"
              severity="secondary"
              icon="pi pi-arrow-left"
              @click="currentStep--"
            />
            <span v-else></span>

            <div class="flex gap-2">
              <Button type="button" label="Batal" severity="secondary" text @click="showAddDialog = false" />
              <Button
                v-if="currentStep < stepLabels.length - 1"
                type="button"
                label="Selanjutnya"
                icon="pi pi-arrow-right"
                iconPos="right"
                @click="nextStep"
              />
              <Button
                v-else
                type="submit"
                :label="editingStudent ? 'Update' : 'Simpan'"
                icon="pi pi-check"
                :loading="submitting"
              />
            </div>
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

// Step labels
const stepLabels = ['Identitas', 'Data Pribadi', 'Penempatan']
const currentStep = ref(0)

// State
const students = ref<any[]>([])
const units = ref<any[]>([])
const classrooms = ref<any[]>([])
const loading = ref(true)
const loadingUnits = ref(false)
const loadingClassrooms = ref(false)
const submitting = ref(false)
const showAddDialog = ref(false)
const editingStudent = ref<any>(null)

const genderOptions = [
  { label: 'Laki-laki', value: 'L' },
  { label: 'Perempuan', value: 'P' },
]

const statusOptions = [
  { label: 'Aktif', value: 'ACTIVE' },
  { label: 'Lulus', value: 'GRADUATED' },
  { label: 'Pindah', value: 'MOVED' },
  { label: 'Keluar', value: 'DROPPED' },
]

function statusLabel(status: string) {
  return statusOptions.find(s => s.value === status)?.label || status
}

const form = reactive({
  full_name: '',
  nis: '',
  nisn: '',
  gender: 'L',
  birth_place: '',
  birth_date: null as Date | null,
  address: '',
  unit_id: null as number | null,
  current_classroom_id: null as number | null,
  status: 'ACTIVE',
})

const errors = reactive({
  full_name: '',
})

// Fetch
async function fetchStudents() {
  loading.value = true
  try {
    students.value = await api.get<any[]>('/academic/students')
  } catch (error) {
    console.error('Failed to fetch students:', error)
  } finally {
    loading.value = false
  }
}

async function fetchUnits() {
  loadingUnits.value = true
  try {
    units.value = await api.get<any[]>('/units')
  } catch (error) {
    console.error('Failed to fetch units:', error)
  } finally {
    loadingUnits.value = false
  }
}

async function fetchClassrooms() {
  loadingClassrooms.value = true
  try {
    classrooms.value = await api.get<any[]>('/academic/classrooms')
  } catch (error) {
    console.error('Failed to fetch classrooms:', error)
  } finally {
    loadingClassrooms.value = false
  }
}

// Open add dialog
function openAddDialog() {
  resetForm()
  showAddDialog.value = true
}

// Edit student
function editStudent(student: any) {
  editingStudent.value = student
  form.full_name = student.full_name
  form.nis = student.nis || ''
  form.nisn = student.nisn || ''
  form.gender = student.gender
  form.birth_place = student.birth_place || ''
  form.birth_date = student.birth_date ? new Date(student.birth_date) : null
  form.address = student.address || ''
  form.unit_id = student.unit_id
  form.current_classroom_id = student.current_classroom_id
  form.status = student.status || 'ACTIVE'
  currentStep.value = 0
  showAddDialog.value = true
}

// Reset form
function resetForm() {
  editingStudent.value = null
  currentStep.value = 0
  form.full_name = ''
  form.nis = ''
  form.nisn = ''
  form.gender = 'L'
  form.birth_place = ''
  form.birth_date = null
  form.address = ''
  form.unit_id = null
  form.current_classroom_id = null
  form.status = 'ACTIVE'
  errors.full_name = ''
}

// Validate per step
function validateStep(step: number): boolean {
  errors.full_name = ''
  if (step === 0) {
    if (!form.full_name || form.full_name.length < 2) {
      errors.full_name = 'Nama lengkap minimal 2 karakter.'
      return false
    }
  }
  return true
}

function nextStep() {
  if (validateStep(currentStep.value)) {
    currentStep.value++
  }
}

// Submit form
async function submitForm() {
  if (!validateStep(0)) {
    currentStep.value = 0
    return
  }

  submitting.value = true
  try {
    // Format birth_date to ISO string for API
    const payload: any = { ...form }
    if (payload.birth_date) {
      payload.birth_date = payload.birth_date.toISOString().split('T')[0]
    }
    // Remove null values for optional fields
    if (!payload.current_classroom_id) delete payload.current_classroom_id
    if (!payload.birth_place) delete payload.birth_place
    if (!payload.birth_date) delete payload.birth_date
    if (!payload.address) delete payload.address

    if (editingStudent.value) {
      await api.put(`/academic/students/${editingStudent.value.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data siswa berhasil diupdate', life: 3000 })
    } else {
      await api.post('/academic/students', payload)
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
  fetchClassrooms()
})
</script>
