<template>
  <NuxtLayout name="dashboard">
    <div class="space-y-6">
      <!-- Page Header -->
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Manajemen Akademik</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola jadwal pelajaran, mata pelajaran, dan kelas.</p>
      </div>

      <!-- Tabs -->
      <TabView>
        <!-- Tab: Jadwal Pelajaran -->
        <TabPanel>
          <template #header>
            <div class="flex items-center gap-2">
              <i class="pi pi-calendar"></i>
              <span>Jadwal Pelajaran</span>
            </div>
          </template>

          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">Jadwal Aktif</h3>
              <Button severity="success" size="small" @click="showScheduleDialog = true">
                <i class="pi pi-plus mr-2"></i>Tambah Jadwal
              </Button>
            </div>

            <DataTable :value="schedules" :loading="loadingSchedules" stripedRows class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada jadwal.</div>
              </template>
              <Column field="day" header="Hari" />
              <Column header="Jam">
                <template #body="{ data }">{{ data.start_time }} - {{ data.end_time }}</template>
              </Column>
              <Column header="Kelas">
                <template #body="{ data }">{{ data.classroom?.name || data.classroom_id }}</template>
              </Column>
              <Column header="Mapel">
                <template #body="{ data }">{{ data.subject?.name || data.subject_id }}</template>
              </Column>
              <Column header="Guru">
                <template #body="{ data }">{{ data.teacher?.full_name || data.teacher_id }}</template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>

        <!-- Tab: Data Kelas -->
        <TabPanel>
          <template #header>
            <div class="flex items-center gap-2">
              <i class="pi pi-building"></i>
              <span>Data Kelas</span>
            </div>
          </template>

          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">Daftar Kelas</h3>
              <Button severity="success" size="small" @click="showClassroomDialog = true">
                <i class="pi pi-plus mr-2"></i>Tambah Kelas
              </Button>
            </div>

            <DataTable :value="classrooms" :loading="loadingClassrooms" stripedRows class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada data kelas.</div>
              </template>
              <Column field="name" header="Nama Kelas" />
              <Column field="level" header="Level" />
              <Column header="Unit">
                <template #body="{ data }">{{ getUnitName(data.unit_id) }}</template>
              </Column>
              <Column header="Aksi" style="width: 100px">
                <template #body="{ data }">
                  <Button icon="pi pi-trash" severity="danger" size="small" text rounded @click="deleteClassroom(data)" />
                </template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>

        <!-- Tab: Mata Pelajaran -->
        <TabPanel>
          <template #header>
            <div class="flex items-center gap-2">
              <i class="pi pi-book"></i>
              <span>Mata Pelajaran</span>
            </div>
          </template>

          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">Daftar Mata Pelajaran</h3>
              <Button severity="success" size="small" @click="showSubjectDialog = true">
                <i class="pi pi-plus mr-2"></i>Tambah Mapel
              </Button>
            </div>

            <DataTable :value="subjects" :loading="loadingSubjects" stripedRows class="p-datatable-sm">
              <template #empty>
                <div class="text-center py-8 text-slate-500">Belum ada mapel.</div>
              </template>
              <Column field="code" header="Kode">
                <template #body="{ data }">{{ data.code || '-' }}</template>
              </Column>
              <Column field="name" header="Mata Pelajaran" />
              <Column header="Unit">
                <template #body="{ data }">{{ getUnitName(data.unit_id) }}</template>
              </Column>
              <Column header="Aksi" style="width: 100px">
                <template #body="{ data }">
                  <Button icon="pi pi-trash" severity="danger" size="small" text rounded @click="deleteSubject(data)" />
                </template>
              </Column>
            </DataTable>
          </div>
        </TabPanel>
      </TabView>

      <!-- Schedule Dialog -->
      <Dialog v-model:visible="showScheduleDialog" header="Tambah Jadwal" :style="{ width: '500px' }" modal>
        <form @submit.prevent="submitSchedule" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label class="font-medium">Hari</label>
              <Select v-model="scheduleForm.day" :options="dayOptions" placeholder="Pilih hari" class="w-full" />
            </div>
            <div class="flex flex-col gap-2">
              <label class="font-medium">Kelas</label>
              <Select v-model="scheduleForm.classroom_id" :options="classrooms" optionLabel="name" optionValue="id" placeholder="Pilih kelas" class="w-full" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label class="font-medium">Jam Mulai</label>
              <InputText v-model="scheduleForm.start_time" placeholder="08:00" class="w-full" />
            </div>
            <div class="flex flex-col gap-2">
              <label class="font-medium">Jam Selesai</label>
              <InputText v-model="scheduleForm.end_time" placeholder="09:30" class="w-full" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col gap-2">
              <label class="font-medium">Mata Pelajaran</label>
              <Select v-model="scheduleForm.subject_id" :options="subjects" optionLabel="name" optionValue="id" placeholder="Pilih mapel" class="w-full" />
            </div>
            <div class="flex flex-col gap-2">
              <label class="font-medium">Guru</label>
              <Select v-model="scheduleForm.teacher_id" :options="teachers" optionLabel="full_name" optionValue="id" placeholder="Pilih guru" class="w-full" />
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showScheduleDialog = false" />
            <Button type="submit" label="Simpan" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Classroom Dialog -->
      <Dialog v-model:visible="showClassroomDialog" header="Tambah Kelas" :style="{ width: '400px' }" modal>
        <form @submit.prevent="submitClassroom" class="space-y-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nama Kelas</label>
            <InputText v-model="classroomForm.name" placeholder="Contoh: 1A" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Level / Tingkat</label>
            <InputText v-model="classroomForm.level" placeholder="1" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Unit</label>
            <Select v-model="classroomForm.unit_id" :options="units" optionLabel="name" optionValue="id" placeholder="Pilih unit" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showClassroomDialog = false" />
            <Button type="submit" label="Simpan" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Subject Dialog -->
      <Dialog v-model:visible="showSubjectDialog" header="Tambah Mata Pelajaran" :style="{ width: '400px' }" modal>
        <form @submit.prevent="submitSubject" class="space-y-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Nama Mata Pelajaran</label>
            <InputText v-model="subjectForm.name" placeholder="Matematika" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Kode</label>
            <InputText v-model="subjectForm.code" placeholder="MTK" class="w-full" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Unit</label>
            <Select v-model="subjectForm.unit_id" :options="units" optionLabel="name" optionValue="id" placeholder="Pilih unit" class="w-full" />
          </div>
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showSubjectDialog = false" />
            <Button type="submit" label="Simpan" :loading="submitting" />
          </div>
        </form>
      </Dialog>

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

// Data
const schedules = ref<any[]>([])
const classrooms = ref<any[]>([])
const subjects = ref<any[]>([])
const teachers = ref<any[]>([])
const units = ref<any[]>([])

// Loading states
const loadingSchedules = ref(false)
const loadingClassrooms = ref(false)
const loadingSubjects = ref(false)
const submitting = ref(false)

// Dialogs
const showScheduleDialog = ref(false)
const showClassroomDialog = ref(false)
const showSubjectDialog = ref(false)

// Form states
const scheduleForm = reactive({
  day: 'Senin',
  start_time: '',
  end_time: '',
  classroom_id: null,
  subject_id: null,
  teacher_id: null,
})

const classroomForm = reactive({
  name: '',
  level: '',
  unit_id: null,
})

const subjectForm = reactive({
  name: '',
  code: '',
  unit_id: null,
})

const dayOptions = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']

// Fetch functions
async function fetchSchedules() {
  loadingSchedules.value = true
  try {
    schedules.value = await api.get('/academic/schedules')
  } catch (e) {
    console.error(e)
  } finally {
    loadingSchedules.value = false
  }
}

async function fetchClassrooms() {
  loadingClassrooms.value = true
  try {
    classrooms.value = await api.get('/academic/classrooms')
  } catch (e) {
    console.error(e)
  } finally {
    loadingClassrooms.value = false
  }
}

async function fetchSubjects() {
  loadingSubjects.value = true
  try {
    subjects.value = await api.get('/academic/subjects')
  } catch (e) {
    console.error(e)
  } finally {
    loadingSubjects.value = false
  }
}

async function fetchTeachers() {
  try {
    teachers.value = await api.get('/academic/teachers')
  } catch (e) {
    console.error(e)
  }
}

async function fetchUnits() {
  try {
    units.value = await api.get('/units')
  } catch (e) {
    console.error(e)
  }
}

function getUnitName(unitId: number): string {
  const unit = units.value.find((u) => u.id === unitId)
  return unit?.name || `Unit ${unitId}`
}

// Submit functions
async function submitSchedule() {
  submitting.value = true
  try {
    await api.post('/academic/schedules', scheduleForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Jadwal berhasil ditambahkan', life: 3000 })
    showScheduleDialog.value = false
    fetchSchedules()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menambah jadwal', life: 3000 })
  } finally {
    submitting.value = false
  }
}

async function submitClassroom() {
  submitting.value = true
  try {
    await api.post('/academic/classrooms', classroomForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Kelas berhasil ditambahkan', life: 3000 })
    showClassroomDialog.value = false
    classroomForm.name = ''
    classroomForm.level = ''
    classroomForm.unit_id = null
    fetchClassrooms()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menambah kelas', life: 3000 })
  } finally {
    submitting.value = false
  }
}

async function submitSubject() {
  submitting.value = true
  try {
    await api.post('/academic/subjects', subjectForm)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Mapel berhasil ditambahkan', life: 3000 })
    showSubjectDialog.value = false
    subjectForm.name = ''
    subjectForm.code = ''
    subjectForm.unit_id = null
    fetchSubjects()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menambah mapel', life: 3000 })
  } finally {
    submitting.value = false
  }
}

// Delete functions
function deleteClassroom(item: any) {
  confirm.require({
    message: `Hapus kelas "${item.name}"?`,
    header: 'Konfirmasi',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await api.delete(`/academic/classrooms/${item.id}`)
      toast.add({ severity: 'success', summary: 'Dihapus', detail: 'Kelas berhasil dihapus', life: 3000 })
      fetchClassrooms()
    },
  })
}

function deleteSubject(item: any) {
  confirm.require({
    message: `Hapus mapel "${item.name}"?`,
    header: 'Konfirmasi',
    acceptClass: 'p-button-danger',
    accept: async () => {
      await api.delete(`/academic/subjects/${item.id}`)
      toast.add({ severity: 'success', summary: 'Dihapus', detail: 'Mapel berhasil dihapus', life: 3000 })
      fetchSubjects()
    },
  })
}

onMounted(() => {
  fetchSchedules()
  fetchClassrooms()
  fetchSubjects()
  fetchTeachers()
  fetchUnits()
})
</script>
