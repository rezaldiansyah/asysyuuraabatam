<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Rombel (Rombongan Belajar)</h1>
          <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
            <i class="pi pi-check-circle text-[10px]"></i> Manajemen Kelas
          </span>
        </div>
        <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
          Kelola data kelas, penugasan Wali Kelas, dan distribusi siswa per tingkat & unit sekolah.
        </p>
      </div>
      <div class="flex items-center gap-2 self-stretch sm:self-auto">
        <NuxtLink to="/dashboard/jadwal">
          <Button severity="secondary" outlined size="small" class="text-xs">
            <i class="pi pi-calendar mr-1.5 text-xs"></i>
            Jadwal Pelajaran
          </Button>
        </NuxtLink>
        <Button severity="success" size="small" class="text-xs font-medium" @click="openCreateDialog">
          <i class="pi pi-plus mr-1.5 text-xs"></i>
          Tambah Rombel
        </Button>
      </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <!-- Total Rombel -->
      <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-lg font-bold">
          <i class="pi pi-th-large"></i>
        </div>
        <div>
          <div class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">{{ classrooms.length }}</div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400">Total Rombel (Kelas)</div>
        </div>
      </div>

      <!-- Total Siswa -->
      <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center text-lg font-bold">
          <i class="pi pi-users"></i>
        </div>
        <div>
          <div class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">{{ totalStudentsInClasses }}</div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400">Siswa Terdaftar</div>
        </div>
      </div>

      <!-- Wali Kelas Status -->
      <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
        <div 
          class="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-bold"
          :class="unassignedHomeroomCount === 0 
            ? 'bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400' 
            : 'bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400'"
        >
          <i :class="unassignedHomeroomCount === 0 ? 'pi pi-user-check' : 'pi pi-exclamation-triangle'"></i>
        </div>
        <div>
          <div class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">
            {{ assignedHomeroomCount }} <span class="text-xs font-normal text-slate-400">/ {{ classrooms.length }}</span>
          </div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400">
            {{ unassignedHomeroomCount === 0 ? 'Semua Ada Wali Kelas' : `${unassignedHomeroomCount} Belum Ada Wali` }}
          </div>
        </div>
      </div>

      <!-- Tahun Ajaran -->
      <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-teal-50 dark:bg-teal-950/40 text-teal-600 dark:text-teal-400 flex items-center justify-center text-lg font-bold">
          <i class="pi pi-calendar"></i>
        </div>
        <div class="min-w-0">
          <div class="text-sm font-bold text-slate-800 dark:text-white truncate">
            {{ activeAcademicYear?.name || '2025/2026' }}
          </div>
          <div class="text-[11px] text-slate-500 dark:text-slate-400 truncate">
            Semester {{ activeAcademicYear?.semester || 'Ganjil' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="bg-white dark:bg-slate-800 p-3 sm:p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Search -->
        <div class="relative w-full">
          <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
          <InputText
            v-model="filters.search"
            placeholder="Cari nama rombel atau wali kelas..."
            class="w-full !pl-9 text-xs sm:text-sm"
            size="small"
          />
        </div>

        <!-- Tahun Ajaran Filter -->
        <Select
          v-model="filters.academic_year_id"
          :options="academicYears"
          optionLabel="label"
          optionValue="id"
          placeholder="Pilih Tahun Ajaran"
          size="small"
          class="w-full text-xs sm:text-sm"
          @change="fetchClassrooms"
        >
          <template #option="{ option }">
            <div class="flex items-center justify-between w-full">
              <span>{{ option.name }} - {{ option.semester }}</span>
              <span v-if="option.is_active" class="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-semibold">Aktif</span>
            </div>
          </template>
        </Select>

        <!-- Unit Filter -->
        <Select
          v-model="filters.unit_id"
          :options="units"
          optionLabel="name"
          optionValue="id"
          placeholder="Semua Unit"
          showClear
          size="small"
          class="w-full text-xs sm:text-sm"
          @change="fetchClassrooms"
        />

        <!-- Level / Tingkat Filter -->
        <Select
          v-model="filters.level"
          :options="levelOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Semua Tingkat"
          showClear
          size="small"
          class="w-full text-xs sm:text-sm"
          @change="fetchClassrooms"
        />
      </div>
    </div>

    <!-- Data Table -->
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
      <DataTable
        :value="filteredClassrooms"
        :loading="loading"
        paginator
        :rows="10"
        :rowsPerPageOptions="[10, 20, 50]"
        stripedRows
        removableSort
        class="p-datatable-sm text-xs sm:text-sm"
        responsiveLayout="scroll"
      >
        <template #empty>
          <div class="text-center py-12 text-slate-500">
            <i class="pi pi-th-large text-4xl text-slate-300 dark:text-slate-600 mb-2 block"></i>
            Tidak ada rombel yang terdaftar pada filter ini.
          </div>
        </template>

        <template #loading>
          <div class="flex justify-center items-center py-12 text-slate-500">
            <i class="pi pi-spin pi-spinner text-2xl mr-2 text-emerald-500"></i>
            Memuat data rombel...
          </div>
        </template>

        <!-- Nama Rombel & Tingkat -->
        <Column field="name" header="Nama Rombel (Kelas)" sortable>
          <template #body="{ data }">
            <div class="flex items-center gap-2.5 py-1">
              <div class="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center font-bold text-xs text-slate-700 dark:text-slate-200 shrink-0">
                {{ data.level }}
              </div>
              <div>
                <div class="font-bold text-slate-800 dark:text-white text-sm">
                  {{ data.name }}
                </div>
                <div class="text-[11px] text-slate-400">
                  Tingkat / Grade {{ data.level }}
                </div>
              </div>
            </div>
          </template>
        </Column>

        <!-- Unit Sekolah -->
        <Column field="unit.name" header="Unit Sekolah" sortable>
          <template #body="{ data }">
            <span
              class="px-2 py-0.5 rounded text-[11px] font-semibold"
              :class="getUnitBadgeClass(data.unit?.name)"
            >
              {{ data.unit?.name || '-' }}
            </span>
          </template>
        </Column>

        <!-- Wali Kelas (Homeroom Teacher) -->
        <Column header="Wali Kelas" sortable>
          <template #body="{ data }">
            <div v-if="data.homeroom_teacher" class="flex items-center gap-2.5">
              <Avatar
                :image="data.homeroom_teacher.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.homeroom_teacher.full_name)}&background=059669&color=fff&size=80`"
                shape="circle"
                class="shrink-0 shadow-sm"
              />
              <div class="min-w-0">
                <div class="font-semibold text-slate-800 dark:text-white truncate max-w-[180px]">
                  {{ data.homeroom_teacher.full_name }}
                </div>
                <div class="text-[11px] text-slate-400 flex items-center gap-1">
                  <span v-if="data.homeroom_teacher.nuptk">NUPTK: {{ data.homeroom_teacher.nuptk }}</span>
                  <span v-else>NIK: {{ data.homeroom_teacher.nik || '-' }}</span>
                </div>
              </div>
            </div>
            <div v-else>
              <button
                type="button"
                @click="openAssignHomeroom(data)"
                class="inline-flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400 hover:underline font-medium bg-amber-50 dark:bg-amber-950/40 px-2 py-1 rounded-lg border border-amber-200 dark:border-amber-900/50"
              >
                <i class="pi pi-user-plus text-[10px]"></i>
                Tugaskan Wali Kelas
              </button>
            </div>
          </template>
        </Column>

        <!-- Jumlah Siswa -->
        <Column field="student_count" header="Siswa Terdaftar" sortable style="width: 140px">
          <template #body="{ data }">
            <button
              type="button"
              @click="viewClassroomStudents(data)"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 transition"
              title="Klik untuk melihat daftar siswa di kelas ini"
            >
              <i class="pi pi-users text-xs text-slate-400"></i>
              <span>{{ data.student_count || 0 }} Siswa</span>
            </button>
          </template>
        </Column>

        <!-- Tahun Ajaran -->
        <Column header="Tahun Ajaran" style="width: 150px">
          <template #body="{ data }">
            <div class="text-xs text-slate-600 dark:text-slate-300">
              <span class="font-medium">{{ data.academic_year?.name || '-' }}</span>
              <span class="text-slate-400 block text-[11px]">{{ data.academic_year?.semester || '' }}</span>
            </div>
          </template>
        </Column>

        <!-- Aksi -->
        <Column header="Aksi" style="width: 120px" :exportable="false">
          <template #body="{ data }">
            <div class="flex items-center gap-1">
              <Button icon="pi pi-users" severity="info" size="small" text rounded class="!w-8 !h-8" title="Lihat Siswa" @click="viewClassroomStudents(data)" />
              <Button icon="pi pi-pencil" severity="secondary" size="small" text rounded class="!w-8 !h-8" title="Edit Rombel" @click="openEditDialog(data)" />
              <Button icon="pi pi-trash" severity="danger" size="small" text rounded class="!w-8 !h-8" title="Hapus Rombel" @click="confirmDelete(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Create / Edit Dialog -->
    <Dialog
      v-model:visible="showFormDialog"
      :header="editingClassroom ? 'Edit Rombel (Kelas)' : 'Tambah Rombel Baru'"
      :style="{ width: '500px' }"
      modal
      @hide="resetForm"
    >
      <form @submit.prevent="submitForm" class="space-y-4 pt-2">
        <!-- Unit Sekolah -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">
            Unit Sekolah <span class="text-rose-500">*</span>
          </label>
          <Select
            v-model="form.unit_id"
            :options="units"
            optionLabel="name"
            optionValue="id"
            placeholder="Pilih Unit Sekolah"
            class="w-full text-xs sm:text-sm"
            :class="{ 'p-invalid': errors.unit_id }"
            @change="onUnitChange"
          />
          <small v-if="errors.unit_id" class="text-rose-500 text-[11px]">{{ errors.unit_id }}</small>
        </div>

        <!-- Tingkat & Nama Kelas -->
        <div class="grid grid-cols-2 gap-3">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Tingkat / Level <span class="text-rose-500">*</span>
            </label>
            <Select
              v-model="form.level"
              :options="availableLevelsForUnit"
              optionLabel="label"
              optionValue="value"
              placeholder="Tingkat"
              class="w-full text-xs sm:text-sm"
              :class="{ 'p-invalid': errors.level }"
            />
            <small v-if="errors.level" class="text-rose-500 text-[11px]">{{ errors.level }}</small>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Nama Kelas <span class="text-rose-500">*</span>
            </label>
            <InputText
              v-model="form.name"
              placeholder="Contoh: 1 Abu Bakar"
              class="w-full text-xs sm:text-sm"
              :class="{ 'p-invalid': errors.name }"
            />
            <small v-if="errors.name" class="text-rose-500 text-[11px]">{{ errors.name }}</small>
          </div>
        </div>

        <!-- Tahun Ajaran -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">
            Tahun Ajaran <span class="text-rose-500">*</span>
          </label>
          <Select
            v-model="form.academic_year_id"
            :options="academicYears"
            optionLabel="label"
            optionValue="id"
            placeholder="Pilih Tahun Ajaran"
            class="w-full text-xs sm:text-sm"
          />
        </div>

        <!-- Wali Kelas (Dropdown Guru dari Langkah 1) -->
        <div class="flex flex-col gap-1.5">
          <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">
            Wali Kelas (Homeroom Teacher)
          </label>
          <Select
            v-model="form.homeroom_teacher_id"
            :options="filteredTeachersForUnit"
            optionLabel="full_name"
            optionValue="id"
            placeholder="-- Pilih Guru sebagai Wali Kelas --"
            filter
            showClear
            class="w-full text-xs sm:text-sm"
          >
            <template #option="{ option }">
              <div class="flex justify-between items-center w-full py-1">
                <div>
                  <div class="font-semibold text-xs">{{ option.full_name }}</div>
                  <div class="text-[11px] text-slate-400">
                    {{ option.nuptk ? `NUPTK: ${option.nuptk}` : `NIK: ${option.nik || '-'}` }} • {{ option.position || 'Guru' }}
                  </div>
                </div>
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">{{ option.unit_name || '-' }}</span>
              </div>
            </template>
          </Select>
          <p class="text-[11px] text-slate-400">
            Daftar guru diambil langsung dari master Data Guru & Kepegawaian (SDM).
          </p>
        </div>

        <!-- Footer -->
        <div class="flex justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
          <Button type="button" label="Batal" severity="secondary" size="small" @click="showFormDialog = false" />
          <Button
            type="submit"
            :label="editingClassroom ? 'Perbarui Rombel' : 'Simpan Rombel'"
            icon="pi pi-check"
            size="small"
            severity="success"
            :loading="submitting"
          />
        </div>
      </form>
    </Dialog>

    <!-- Students in Classroom Modal -->
    <Dialog
      v-model:visible="showStudentsDialog"
      :header="`Daftar Siswa - ${selectedClassroomForStudents?.name || 'Rombel'}`"
      :style="{ width: '680px' }"
      modal
    >
      <div class="space-y-4 pt-2">
        <div class="flex items-center justify-between bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700 text-xs">
          <div>
            <span class="text-slate-500">Unit:</span> <strong class="ml-1 text-slate-700 dark:text-slate-200">{{ selectedClassroomForStudents?.unit?.name }}</strong>
            <span class="mx-2 text-slate-300">•</span>
            <span class="text-slate-500">Wali Kelas:</span> <strong class="ml-1 text-slate-700 dark:text-slate-200">{{ selectedClassroomForStudents?.homeroom_teacher?.full_name || 'Belum Ditugaskan' }}</strong>
          </div>
          <NuxtLink to="/dashboard/siswa">
            <span class="text-emerald-600 dark:text-emerald-400 hover:underline font-semibold flex items-center gap-1">
              <i class="pi pi-arrow-up-right text-[10px]"></i> Buka Data Siswa
            </span>
          </NuxtLink>
        </div>

        <DataTable
          :value="classroomStudents"
          :loading="loadingStudents"
          stripedRows
          class="p-datatable-sm text-xs sm:text-sm"
          responsiveLayout="scroll"
        >
          <template #empty>
            <div class="text-center py-8 text-slate-500">
              Belum ada siswa yang ditempatkan pada kelas ini.
            </div>
          </template>

          <Column header="No." style="width: 50px">
            <template #body="{ index }">
              {{ index + 1 }}
            </template>
          </Column>

          <Column field="nis" header="NIS / NISN">
            <template #body="{ data }">
              <div>
                <span class="font-mono font-medium">{{ data.nis || '-' }}</span>
                <span v-if="data.nisn" class="text-[11px] text-slate-400 block">NISN: {{ data.nisn }}</span>
              </div>
            </template>
          </Column>

          <Column field="full_name" header="Nama Siswa">
            <template #body="{ data }">
              <span class="font-semibold text-slate-800 dark:text-white">{{ data.full_name }}</span>
            </template>
          </Column>

          <Column field="gender" header="L/P" style="width: 70px">
            <template #body="{ data }">
              <span
                class="px-2 py-0.5 rounded text-[11px] font-bold"
                :class="data.gender === 'L' ? 'bg-blue-100 text-blue-700' : 'bg-pink-100 text-pink-700'"
              >
                {{ data.gender || '-' }}
              </span>
            </template>
          </Column>

          <Column field="status" header="Status" style="width: 90px">
            <template #body="{ data }">
              <Tag :value="data.status" severity="success" class="text-[10px]" />
            </template>
          </Column>
        </DataTable>

        <div class="flex justify-end pt-3 border-t border-slate-100 dark:border-slate-800">
          <Button label="Tutup" severity="secondary" size="small" @click="showStudentsDialog = false" />
        </div>
      </div>
    </Dialog>

    <!-- Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const confirm = useConfirm()
const toast = useToast()

// States
const classrooms = ref<any[]>([])
const units = ref<any[]>([])
const academicYears = ref<any[]>([])
const teachers = ref<any[]>([])
const loading = ref(true)
const submitting = ref(false)

// Modals
const showFormDialog = ref(false)
const editingClassroom = ref<any>(null)
const showStudentsDialog = ref(false)
const selectedClassroomForStudents = ref<any>(null)
const classroomStudents = ref<any[]>([])
const loadingStudents = ref(false)

// Filters
const filters = reactive({
  search: '',
  academic_year_id: null as number | null,
  unit_id: null as number | null,
  level: null as number | null
})

// Form
const form = reactive({
  name: '',
  level: null as number | null,
  unit_id: null as number | null,
  academic_year_id: null as number | null,
  homeroom_teacher_id: null as number | null
})

const errors = reactive({
  name: '',
  level: '',
  unit_id: ''
})

const levelOptions = [
  { label: 'Tingkat 1', value: 1 },
  { label: 'Tingkat 2', value: 2 },
  { label: 'Tingkat 3', value: 3 },
  { label: 'Tingkat 4', value: 4 },
  { label: 'Tingkat 5', value: 5 },
  { label: 'Tingkat 6', value: 6 },
  { label: 'Tingkat 7', value: 7 },
  { label: 'Tingkat 8', value: 8 },
  { label: 'Tingkat 9', value: 9 },
]

// Computeds
const activeAcademicYear = computed(() => {
  return academicYears.value.find(y => y.is_active) || academicYears.value[0]
})

const totalStudentsInClasses = computed(() => {
  return classrooms.value.reduce((acc, c) => acc + (c.student_count || 0), 0)
})

const assignedHomeroomCount = computed(() => {
  return classrooms.value.filter(c => c.homeroom_teacher_id).length
})

const unassignedHomeroomCount = computed(() => {
  return classrooms.value.filter(c => !c.homeroom_teacher_id).length
})

const availableLevelsForUnit = computed(() => {
  if (!form.unit_id) return levelOptions
  const unit = units.value.find(u => u.id === form.unit_id)
  const code = (unit?.code || unit?.name || '').toUpperCase()

  if (code.includes('RA') || code.includes('PAUD')) {
    return [
      { label: 'Kelompok A', value: 1 },
      { label: 'Kelompok B', value: 2 }
    ]
  } else if (code.includes('SMP')) {
    return [
      { label: 'Kelas 7', value: 7 },
      { label: 'Kelas 8', value: 8 },
      { label: 'Kelas 9', value: 9 }
    ]
  } else {
    // Default SDIT (1 - 6)
    return [
      { label: 'Kelas 1', value: 1 },
      { label: 'Kelas 2', value: 2 },
      { label: 'Kelas 3', value: 3 },
      { label: 'Kelas 4', value: 4 },
      { label: 'Kelas 5', value: 5 },
      { label: 'Kelas 6', value: 6 }
    ]
  }
})

const filteredTeachersForUnit = computed(() => {
  if (!form.unit_id) return teachers.value
  // Prioritize teachers of the same unit, but still allow selecting any active teacher
  return [...teachers.value].sort((a, b) => {
    if (a.unit_id === form.unit_id && b.unit_id !== form.unit_id) return -1
    if (a.unit_id !== form.unit_id && b.unit_id === form.unit_id) return 1
    return (a.full_name || '').localeCompare(b.full_name || '')
  })
})

const filteredClassrooms = computed(() => {
  return classrooms.value.filter(c => {
    if (filters.search) {
      const q = filters.search.toLowerCase().trim()
      const matchName = (c.name || '').toLowerCase().includes(q)
      const matchTeacher = (c.homeroom_teacher?.full_name || '').toLowerCase().includes(q)
      if (!matchName && !matchTeacher) return false
    }
    if (filters.unit_id && c.unit_id !== filters.unit_id) return false
    if (filters.level && c.level !== filters.level) return false
    return true
  })
})

function getUnitBadgeClass(unitName?: string) {
  if (!unitName) return 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
  const u = unitName.toUpperCase()
  if (u.includes('RA')) return 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
  if (u.includes('SDIT') || u.includes('SD')) return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
  if (u.includes('SMPIT') || u.includes('SMP')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
  return 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300'
}

// Fetch Classrooms
async function fetchClassrooms() {
  loading.value = true
  try {
    const params: any = {}
    if (filters.academic_year_id) params.academic_year_id = filters.academic_year_id
    if (filters.unit_id) params.unit_id = filters.unit_id
    if (filters.level) params.level = filters.level

    const data = await api.get<any[]>('/academic/classrooms', { params })
    classrooms.value = data || []
  } catch (error) {
    console.error('Failed to fetch classrooms:', error)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal memuat data rombel', life: 3000 })
  } finally {
    loading.value = false
  }
}

// Fetch Units
async function fetchUnits() {
  try {
    units.value = await api.get<any[]>('/units')
  } catch (error) {
    console.error('Failed to fetch units:', error)
  }
}

// Fetch Academic Years
async function fetchAcademicYears() {
  try {
    const data = await api.get<any[]>('/academic/years')
    academicYears.value = (data || []).map(y => ({
      ...y,
      label: `${y.name} - ${y.semester}${y.is_active ? ' (Aktif)' : ''}`
    }))

    // Auto set filter to active academic year
    const active = academicYears.value.find(y => y.is_active)
    if (active && !filters.academic_year_id) {
      filters.academic_year_id = active.id
    }
  } catch (error) {
    console.error('Failed to fetch academic years:', error)
  }
}

// Fetch Teachers
async function fetchTeachers() {
  try {
    teachers.value = await api.get<any[]>('/academic/teachers')
  } catch (error) {
    console.error('Failed to fetch teachers:', error)
  }
}

function onUnitChange() {
  // Reset level if outside valid levels for unit
  const validLevels = availableLevelsForUnit.value.map(l => l.value)
  if (form.level && !validLevels.includes(form.level)) {
    form.level = validLevels[0] || null
  }
}

function openCreateDialog() {
  editingClassroom.value = null
  resetForm()
  form.academic_year_id = filters.academic_year_id || activeAcademicYear.value?.id || null
  if (units.value.length > 0) {
    form.unit_id = units.value[0].id
    form.level = availableLevelsForUnit.value[0]?.value || 1
  }
  showFormDialog.value = true
}

function openEditDialog(classroom: any) {
  editingClassroom.value = classroom
  form.name = classroom.name
  form.level = classroom.level
  form.unit_id = classroom.unit_id
  form.academic_year_id = classroom.academic_year_id
  form.homeroom_teacher_id = classroom.homeroom_teacher_id
  showFormDialog.value = true
}

function openAssignHomeroom(classroom: any) {
  openEditDialog(classroom)
}

function resetForm() {
  form.name = ''
  form.level = null
  form.unit_id = null
  form.academic_year_id = null
  form.homeroom_teacher_id = null
  errors.name = ''
  errors.level = ''
  errors.unit_id = ''
}

// Submit Create / Edit
async function submitForm() {
  errors.name = ''
  errors.level = ''
  errors.unit_id = ''

  let valid = true
  if (!form.name || form.name.trim().length < 2) {
    errors.name = 'Nama kelas minimal 2 karakter.'
    valid = false
  }
  if (!form.level) {
    errors.level = 'Tingkat wajib dipilih.'
    valid = false
  }
  if (!form.unit_id) {
    errors.unit_id = 'Unit sekolah wajib dipilih.'
    valid = false
  }

  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(),
      level: form.level,
      unit_id: form.unit_id,
      academic_year_id: form.academic_year_id,
      homeroom_teacher_id: form.homeroom_teacher_id || null
    }

    if (editingClassroom.value) {
      await api.put(`/academic/classrooms/${editingClassroom.value.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Rombel berhasil diperbarui!', life: 3000 })
    } else {
      await api.post('/academic/classrooms', payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Rombel berhasil dibuat!', life: 3000 })
    }

    showFormDialog.value = false
    fetchClassrooms()
  } catch (error: any) {
    const msg = error?.data?.detail || 'Gagal menyimpan rombel'
    toast.add({ severity: 'error', summary: 'Gagal', detail: msg, life: 5000 })
  } finally {
    submitting.value = false
  }
}

// View Students in Classroom
async function viewClassroomStudents(classroom: any) {
  selectedClassroomForStudents.value = classroom
  showStudentsDialog.value = true
  loadingStudents.value = true
  classroomStudents.value = []
  try {
    const detail = await api.get<any>(`/academic/classrooms/${classroom.id}`)
    classroomStudents.value = detail.students || []
  } catch (error) {
    console.error('Failed to load students in classroom:', error)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal memuat daftar siswa', life: 3000 })
  } finally {
    loadingStudents.value = false
  }
}

// Confirm Delete
function confirmDelete(classroom: any) {
  confirm.require({
    message: `Apakah Anda yakin ingin menghapus rombel "${classroom.name}"? Pastikan tidak ada siswa atau jadwal yang terikat.`,
    header: 'Konfirmasi Hapus Rombel',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Ya, Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        const res = await api.delete<any>(`/academic/classrooms/${classroom.id}`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: res?.message || 'Rombel berhasil dihapus', life: 3000 })
        fetchClassrooms()
      } catch (error: any) {
        const msg = error?.data?.detail || 'Gagal menghapus rombel'
        toast.add({ severity: 'error', summary: 'Perhatian', detail: msg, life: 5000 })
      }
    }
  })
}

onMounted(async () => {
  await Promise.all([
    fetchAcademicYears(),
    fetchUnits(),
    fetchTeachers()
  ])
  fetchClassrooms()
})
</script>
