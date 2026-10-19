<template>
  <NuxtLayout name="dashboard">
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Jadwal & Mata Pelajaran</h1>
            <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
              <i class="pi pi-calendar text-[10px]"></i> Tahun Ajaran {{ activeAcademicYear?.name || '2025/2026' }}
            </span>
          </div>
          <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Susun jadwal pelajaran mingguan per kelas atau guru pengajar, serta kelola master mata pelajaran.
          </p>
        </div>
        <div class="flex items-center gap-2 self-stretch sm:self-auto flex-wrap">
          <NuxtLink to="/dashboard/rombel">
            <Button severity="secondary" outlined size="small" class="text-xs">
              <i class="pi pi-th-large mr-1.5 text-xs"></i>
              Kelola Rombel (Kelas)
            </Button>
          </NuxtLink>
          <NuxtLink to="/dashboard/jadwal/upload">
            <Button severity="secondary" size="small" class="text-xs">
              <i class="pi pi-file-excel mr-1.5 text-xs text-emerald-600"></i>
              Import dari Excel
            </Button>
          </NuxtLink>
          <Button 
            v-if="activeTab === 'jadwal'" 
            severity="success" 
            size="small" 
            class="text-xs font-medium" 
            @click="openAddScheduleDialog"
          >
            <i class="pi pi-plus mr-1.5 text-xs"></i>
            Tambah Jadwal
          </Button>
          <Button 
            v-else 
            severity="success" 
            size="small" 
            class="text-xs font-medium" 
            @click="openAddSubjectDialog"
          >
            <i class="pi pi-plus mr-1.5 text-xs"></i>
            Tambah Mapel
          </Button>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex border-b border-slate-200 dark:border-slate-700 gap-4 text-sm font-medium">
        <button
          type="button"
          class="pb-3 px-1 flex items-center gap-2 border-b-2 transition-all"
          :class="activeTab === 'jadwal'
            ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400 font-bold'
            : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
          @click="activeTab = 'jadwal'"
        >
          <i class="pi pi-calendar"></i>
          <span>Jadwal Pelajaran</span>
          <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold">
            {{ schedules.length }}
          </span>
        </button>

        <button
          type="button"
          class="pb-3 px-1 flex items-center gap-2 border-b-2 transition-all"
          :class="activeTab === 'mapel'
            ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400 font-bold'
            : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'"
          @click="activeTab = 'mapel'"
        >
          <i class="pi pi-book"></i>
          <span>Mata Pelajaran (Mapel)</span>
          <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-semibold">
            {{ subjects.length }}
          </span>
        </button>
      </div>

      <!-- TAB 1: JADWAL PELAJARAN -->
      <div v-if="activeTab === 'jadwal'" class="space-y-4">
        <!-- Filter Bar -->
        <div class="bg-white dark:bg-slate-800 p-3 sm:p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            <!-- Tahun Ajaran -->
            <Select
              v-model="filters.academic_year_id"
              :options="academicYears"
              optionLabel="label"
              optionValue="id"
              placeholder="Tahun Ajaran"
              size="small"
              class="w-full text-xs sm:text-sm"
              @change="fetchSchedules"
            />

            <!-- Unit -->
            <Select
              v-model="filters.unit_id"
              :options="units"
              optionLabel="name"
              optionValue="id"
              placeholder="Semua Unit"
              showClear
              size="small"
              class="w-full text-xs sm:text-sm"
              @change="onUnitFilterChange"
            />

            <!-- Rombel (Kelas) -->
            <Select
              v-model="filters.classroom_id"
              :options="filteredClassrooms"
              optionLabel="name"
              optionValue="id"
              placeholder="Semua Kelas"
              showClear
              filter
              size="small"
              class="w-full text-xs sm:text-sm"
              @change="fetchSchedules"
            />

            <!-- Guru Pengajar -->
            <Select
              v-model="filters.teacher_id"
              :options="teachers"
              optionLabel="full_name"
              optionValue="id"
              placeholder="Semua Guru"
              showClear
              filter
              size="small"
              class="w-full text-xs sm:text-sm"
              @change="fetchSchedules"
            />

            <!-- Hari -->
            <Select
              v-model="filters.day"
              :options="[
                { label: 'Semua Hari', value: '' },
                { label: 'Senin', value: 'SENIN' },
                { label: 'Selasa', value: 'SELASA' },
                { label: 'Rabu', value: 'RABU' },
                { label: 'Kamis', value: 'KAMIS' },
                { label: 'Jumat', value: 'JUMAT' },
                { label: 'Sabtu', value: 'SABTU' }
              ]"
              optionLabel="label"
              optionValue="value"
              placeholder="Pilih Hari"
              size="small"
              class="w-full text-xs sm:text-sm"
              @change="fetchSchedules"
            />
          </div>

          <!-- View Switcher & Counter -->
          <div class="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-xs text-slate-500">
            <div>
              Menampilkan <strong class="text-slate-800 dark:text-white">{{ filteredSchedules.length }}</strong> jadwal pelajaran
              <span v-if="filters.teacher_id" class="text-emerald-600 font-medium ml-1">
                (Khusus guru terpilih)
              </span>
              <span v-else-if="filters.classroom_id" class="text-emerald-600 font-medium ml-1">
                (Khusus kelas terpilih)
              </span>
            </div>
            <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-700/60 p-0.5 rounded-lg">
              <button
                type="button"
                class="px-2.5 py-1 rounded text-xs font-semibold flex items-center gap-1.5 transition"
                :class="viewMode === 'table' ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                @click="viewMode = 'table'"
              >
                <i class="pi pi-list text-xs"></i>
                Tabel
              </button>
              <button
                type="button"
                class="px-2.5 py-1 rounded text-xs font-semibold flex items-center gap-1.5 transition"
                :class="viewMode === 'matrix' ? 'bg-white dark:bg-slate-800 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                @click="viewMode = 'matrix'"
              >
                <i class="pi pi-calendar-plus text-xs"></i>
                Matriks Mingguan
              </button>
            </div>
          </div>
        </div>

        <!-- VIEW MODE: TABLE -->
        <div v-if="viewMode === 'table'" class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
          <DataTable
            :value="filteredSchedules"
            :loading="loadingSchedules"
            paginator
            :rows="15"
            :rowsPerPageOptions="[10, 15, 30, 50]"
            stripedRows
            removableSort
            class="p-datatable-sm text-xs sm:text-sm"
            responsiveLayout="scroll"
          >
            <template #empty>
              <div class="text-center py-12 text-slate-500">
                <i class="pi pi-calendar text-4xl text-slate-300 dark:text-slate-600 mb-2 block"></i>
                Tidak ada jadwal pelajaran yang sesuai dengan filter.
              </div>
            </template>

            <!-- Hari -->
            <Column field="day" header="Hari" sortable style="width: 100px">
              <template #body="{ data }">
                <span class="font-bold text-slate-800 dark:text-white uppercase tracking-wider text-xs">
                  {{ data.day }}
                </span>
              </template>
            </Column>

            <!-- Jam Pelajaran -->
            <Column header="Waktu" sortable style="width: 130px">
              <template #body="{ data }">
                <div class="font-mono text-xs font-semibold text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded inline-block">
                  {{ data.start_time }} - {{ data.end_time }}
                </div>
              </template>
            </Column>

            <!-- Rombel (Kelas) -->
            <Column field="classroom.name" header="Rombel (Kelas)" sortable style="width: 160px">
              <template #body="{ data }">
                <div class="flex items-center gap-1.5">
                  <span class="font-bold text-slate-800 dark:text-white">{{ data.classroom?.name || data.classroom_id }}</span>
                  <span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-700 text-slate-500">
                    Tingkat {{ data.classroom?.level }}
                  </span>
                </div>
                <div class="text-[11px] text-slate-400">
                  {{ data.classroom?.unit?.name || '' }}
                </div>
              </template>
            </Column>

            <!-- Mata Pelajaran -->
            <Column field="subject.name" header="Mata Pelajaran" sortable>
              <template #body="{ data }">
                <div class="font-semibold text-slate-800 dark:text-white flex items-center gap-1.5">
                  <span>{{ data.subject?.name || '-' }}</span>
                  <span v-if="data.subject?.code" class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 font-mono">
                    {{ data.subject.code }}
                  </span>
                </div>
              </template>
            </Column>

            <!-- Guru Pengajar -->
            <Column field="teacher.full_name" header="Guru Pengajar" sortable>
              <template #body="{ data }">
                <div class="flex items-center gap-2">
                  <Avatar
                    :image="data.teacher?.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.teacher?.full_name || 'Guru')}&background=059669&color=fff&size=80`"
                    shape="circle"
                    class="shrink-0 shadow-sm"
                  />
                  <div class="min-w-0">
                    <div class="font-semibold text-slate-800 dark:text-white truncate max-w-[200px]">
                      {{ data.teacher?.full_name || '-' }}
                    </div>
                    <div class="text-[11px] text-slate-400">
                      {{ data.teacher?.nuptk ? `NUPTK: ${data.teacher.nuptk}` : `NIK: ${data.teacher?.nik || '-'}` }}
                    </div>
                  </div>
                </div>
              </template>
            </Column>

            <!-- Aksi -->
            <Column header="Aksi" style="width: 100px" :exportable="false">
              <template #body="{ data }">
                <div class="flex items-center gap-1">
                  <Button icon="pi pi-pencil" severity="secondary" size="small" text rounded class="!w-8 !h-8" title="Edit Jadwal" @click="openEditSchedule(data)" />
                  <Button icon="pi pi-trash" severity="danger" size="small" text rounded class="!w-8 !h-8" title="Hapus Jadwal" @click="confirmDeleteSchedule(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </div>

        <!-- VIEW MODE: MATRIKS MINGGUAN -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="dayName in ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']"
            :key="dayName"
            class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden flex flex-col"
          >
            <!-- Day Header -->
            <div class="px-4 py-2.5 bg-slate-50 dark:bg-slate-700/50 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center">
              <span class="font-bold text-xs uppercase tracking-wider text-slate-800 dark:text-white">
                {{ dayName }}
              </span>
              <span class="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
                {{ getSchedulesByDay(dayName).length }} Sesi
              </span>
            </div>

            <!-- Day Items -->
            <div class="p-3 space-y-2 flex-1">
              <div v-if="getSchedulesByDay(dayName).length === 0" class="text-center py-8 text-xs text-slate-400">
                Tidak ada jadwal di hari ini
              </div>
              <div
                v-for="sc in getSchedulesByDay(dayName)"
                :key="sc.id"
                class="p-2.5 rounded-lg border border-slate-100 dark:border-slate-700 hover:border-emerald-300 dark:hover:border-emerald-700 bg-white dark:bg-slate-800 shadow-xs transition group"
              >
                <div class="flex justify-between items-start gap-2">
                  <div>
                    <span class="text-[10px] font-mono font-bold bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 px-1.5 py-0.5 rounded">
                      {{ sc.start_time }} - {{ sc.end_time }}
                    </span>
                    <span class="ml-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-400">
                      {{ sc.classroom?.name }}
                    </span>
                  </div>
                  <div class="opacity-0 group-hover:opacity-100 transition flex items-center gap-0.5">
                    <button type="button" @click="openEditSchedule(sc)" class="text-slate-400 hover:text-slate-700 dark:hover:text-white p-1">
                      <i class="pi pi-pencil text-xs"></i>
                    </button>
                    <button type="button" @click="confirmDeleteSchedule(sc)" class="text-slate-400 hover:text-rose-600 p-1">
                      <i class="pi pi-trash text-xs"></i>
                    </button>
                  </div>
                </div>

                <div class="text-xs font-semibold text-slate-800 dark:text-white mt-1">
                  {{ sc.subject?.name }}
                </div>

                <div class="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-1">
                  <i class="pi pi-user text-[10px]"></i>
                  <span class="truncate">{{ sc.teacher?.full_name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: MATA PELAJARAN (MAPEL) -->
      <div v-if="activeTab === 'mapel'" class="space-y-4">
        <!-- Filter Bar -->
        <div class="bg-white dark:bg-slate-800 p-3 sm:p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col sm:flex-row justify-between gap-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 flex-1 max-w-lg">
            <!-- Search -->
            <div class="relative w-full">
              <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
              <InputText
                v-model="subjectSearch"
                placeholder="Cari mata pelajaran atau kode..."
                class="w-full !pl-9 text-xs sm:text-sm"
                size="small"
              />
            </div>

            <!-- Unit Filter -->
            <Select
              v-model="subjectUnitFilter"
              :options="units"
              optionLabel="name"
              optionValue="id"
              placeholder="Semua Unit"
              showClear
              size="small"
              class="w-full text-xs sm:text-sm"
            />
          </div>
        </div>

        <!-- Table Subjects -->
        <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
          <DataTable
            :value="filteredSubjects"
            :loading="loadingSubjects"
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
                <i class="pi pi-book text-4xl text-slate-300 dark:text-slate-600 mb-2 block"></i>
                Tidak ada mata pelajaran yang ditemukan.
              </div>
            </template>

            <Column field="code" header="Kode" sortable style="width: 120px">
              <template #body="{ data }">
                <span class="font-mono font-bold text-xs bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded text-slate-700 dark:text-slate-200">
                  {{ data.code || '-' }}
                </span>
              </template>
            </Column>

            <Column field="name" header="Nama Mata Pelajaran" sortable>
              <template #body="{ data }">
                <span class="font-bold text-slate-800 dark:text-white">{{ data.name }}</span>
              </template>
            </Column>

            <Column field="unit.name" header="Unit Sekolah" sortable style="width: 180px">
              <template #body="{ data }">
                <span
                  class="px-2 py-0.5 rounded text-[11px] font-semibold"
                  :class="getUnitBadgeClass(data.unit?.name)"
                >
                  {{ data.unit?.name || '-' }}
                </span>
              </template>
            </Column>

            <Column header="Aksi" style="width: 120px" :exportable="false">
              <template #body="{ data }">
                <div class="flex items-center gap-1">
                  <Button icon="pi pi-pencil" severity="secondary" size="small" text rounded class="!w-8 !h-8" title="Edit Mapel" @click="openEditSubject(data)" />
                  <Button icon="pi pi-trash" severity="danger" size="small" text rounded class="!w-8 !h-8" title="Hapus Mapel" @click="confirmDeleteSubject(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>

      <!-- Dialog Tambah / Edit Jadwal -->
      <Dialog
        v-model:visible="showScheduleDialog"
        :header="editingSchedule ? 'Edit Jadwal Pelajaran' : 'Tambah Jadwal Pelajaran'"
        :style="{ width: '520px' }"
        modal
      >
        <form @submit.prevent="submitScheduleForm" class="space-y-4 pt-2">
          <!-- Hari & Tahun Ajaran -->
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Hari *</label>
              <Select
                v-model="scheduleForm.day"
                :options="['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']"
                placeholder="Pilih Hari"
                class="w-full text-xs sm:text-sm"
              />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Tahun Ajaran *</label>
              <Select
                v-model="scheduleForm.academic_year_id"
                :options="academicYears"
                optionLabel="label"
                optionValue="id"
                placeholder="Pilih Tahun Ajaran"
                class="w-full text-xs sm:text-sm"
              />
            </div>
          </div>

          <!-- Jam Mulai & Jam Selesai -->
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Jam Mulai (HH:MM) *</label>
              <InputText v-model="scheduleForm.start_time" placeholder="07:30" class="w-full text-xs sm:text-sm" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Jam Selesai (HH:MM) *</label>
              <InputText v-model="scheduleForm.end_time" placeholder="09:00" class="w-full text-xs sm:text-sm" />
            </div>
          </div>

          <!-- Rombel (Kelas) -->
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Rombel (Kelas) *</label>
            <Select
              v-model="scheduleForm.classroom_id"
              :options="classrooms"
              optionLabel="name"
              optionValue="id"
              placeholder="-- Pilih Kelas --"
              filter
              class="w-full text-xs sm:text-sm"
              @change="onScheduleClassroomChange"
            >
              <template #option="{ option }">
                <div class="flex justify-between items-center w-full py-1">
                  <span class="font-semibold text-xs">{{ option.name }}</span>
                  <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">{{ option.unit?.name || '-' }}</span>
                </div>
              </template>
            </Select>
          </div>

          <!-- Mata Pelajaran -->
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Mata Pelajaran *</label>
            <Select
              v-model="scheduleForm.subject_id"
              :options="subjectsForSelectedClassroom"
              optionLabel="name"
              optionValue="id"
              placeholder="-- Pilih Mata Pelajaran --"
              filter
              class="w-full text-xs sm:text-sm"
            >
              <template #option="{ option }">
                <div class="flex justify-between items-center w-full py-1">
                  <span class="font-semibold text-xs">{{ option.name }}</span>
                  <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">{{ option.code || '-' }}</span>
                </div>
              </template>
            </Select>
          </div>

          <!-- Guru Pengajar -->
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Guru Pengajar *</label>
            <Select
              v-model="scheduleForm.teacher_id"
              :options="teachers"
              optionLabel="full_name"
              optionValue="id"
              placeholder="-- Pilih Guru Pengajar --"
              filter
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
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
            <Button type="button" label="Batal" severity="secondary" size="small" @click="showScheduleDialog = false" />
            <Button
              type="submit"
              :label="editingSchedule ? 'Perbarui Jadwal' : 'Simpan Jadwal'"
              icon="pi pi-check"
              size="small"
              severity="success"
              :loading="submitting"
            />
          </div>
        </form>
      </Dialog>

      <!-- Dialog Tambah / Edit Mapel -->
      <Dialog
        v-model:visible="showSubjectDialog"
        :header="editingSubject ? 'Edit Mata Pelajaran' : 'Tambah Mata Pelajaran'"
        :style="{ width: '450px' }"
        modal
      >
        <form @submit.prevent="submitSubjectForm" class="space-y-4 pt-2">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Nama Mata Pelajaran *</label>
            <InputText v-model="subjectForm.name" placeholder="Contoh: Matematika" class="w-full text-xs sm:text-sm" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Kode Singkatan *</label>
            <InputText v-model="subjectForm.code" placeholder="Contoh: MTK" class="w-full text-xs sm:text-sm" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Unit Sekolah *</label>
            <Select
              v-model="subjectForm.unit_id"
              :options="units"
              optionLabel="name"
              optionValue="id"
              placeholder="Pilih Unit"
              class="w-full text-xs sm:text-sm"
            />
          </div>

          <div class="flex justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
            <Button type="button" label="Batal" severity="secondary" size="small" @click="showSubjectDialog = false" />
            <Button
              type="submit"
              :label="editingSubject ? 'Perbarui' : 'Simpan'"
              icon="pi pi-check"
              size="small"
              severity="success"
              :loading="submitting"
            />
          </div>
        </form>
      </Dialog>

      <ConfirmDialog />
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: false })

const api = useApi()
const confirm = useConfirm()
const toast = useToast()

// Active Tab
const activeTab = ref<'jadwal' | 'mapel'>('jadwal')
const viewMode = ref<'table' | 'matrix'>('table')

// States
const schedules = ref<any[]>([])
const subjects = ref<any[]>([])
const classrooms = ref<any[]>([])
const teachers = ref<any[]>([])
const units = ref<any[]>([])
const academicYears = ref<any[]>([])

const loadingSchedules = ref(false)
const loadingSubjects = ref(false)
const submitting = ref(false)

// Dialog States
const showScheduleDialog = ref(false)
const editingSchedule = ref<any>(null)
const showSubjectDialog = ref(false)
const editingSubject = ref<any>(null)

// Filters for Schedule
const filters = reactive({
  academic_year_id: null as number | null,
  unit_id: null as number | null,
  classroom_id: null as number | null,
  teacher_id: null as number | null,
  day: ''
})

// Filters for Subject
const subjectSearch = ref('')
const subjectUnitFilter = ref<number | null>(null)

// Forms
const scheduleForm = reactive({
  day: 'SENIN',
  start_time: '07:30',
  end_time: '09:00',
  classroom_id: null as number | null,
  subject_id: null as number | null,
  teacher_id: null as number | null,
  academic_year_id: null as number | null
})

const subjectForm = reactive({
  name: '',
  code: '',
  unit_id: null as number | null
})

// Computeds
const activeAcademicYear = computed(() => {
  return academicYears.value.find(y => y.is_active) || academicYears.value[0]
})

const filteredClassrooms = computed(() => {
  if (!filters.unit_id) return classrooms.value
  return classrooms.value.filter(c => c.unit_id === filters.unit_id)
})

const subjectsForSelectedClassroom = computed(() => {
  if (!scheduleForm.classroom_id) return subjects.value
  const cr = classrooms.value.find(c => c.id === scheduleForm.classroom_id)
  if (!cr || !cr.unit_id) return subjects.value
  return subjects.value.filter(s => s.unit_id === cr.unit_id)
})

const filteredSchedules = computed(() => {
  return schedules.value.filter(s => {
    if (filters.day && (s.day || '').toUpperCase() !== filters.day.toUpperCase()) return false
    return true
  })
})

const filteredSubjects = computed(() => {
  return subjects.value.filter(s => {
    if (subjectUnitFilter.value && s.unit_id !== subjectUnitFilter.value) return false
    if (subjectSearch.value) {
      const q = subjectSearch.value.toLowerCase().trim()
      const matchName = (s.name || '').toLowerCase().includes(q)
      const matchCode = (s.code || '').toLowerCase().includes(q)
      if (!matchName && !matchCode) return false
    }
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

function getSchedulesByDay(day: string) {
  return filteredSchedules.value.filter(s => (s.day || '').toUpperCase() === day.toUpperCase())
}

function onUnitFilterChange() {
  filters.classroom_id = null
  fetchSchedules()
}

function onScheduleClassroomChange() {
  // If subject outside unit, reset subject
  if (scheduleForm.subject_id) {
    const valid = subjectsForSelectedClassroom.value.some(s => s.id === scheduleForm.subject_id)
    if (!valid) scheduleForm.subject_id = null
  }
}

// Fetch Functions
async function fetchSchedules() {
  loadingSchedules.value = true
  try {
    const params: any = {}
    if (filters.academic_year_id) params.academic_year_id = filters.academic_year_id
    if (filters.unit_id) params.unit_id = filters.unit_id
    if (filters.classroom_id) params.classroom_id = filters.classroom_id
    if (filters.teacher_id) params.teacher_id = filters.teacher_id
    if (filters.day) params.day = filters.day

    schedules.value = await api.get<any[]>('/academic/schedules', { params }) || []
  } catch (e) {
    console.error('Failed to fetch schedules:', e)
  } finally {
    loadingSchedules.value = false
  }
}

async function fetchSubjects() {
  loadingSubjects.value = true
  try {
    subjects.value = await api.get<any[]>('/academic/subjects') || []
  } catch (e) {
    console.error('Failed to fetch subjects:', e)
  } finally {
    loadingSubjects.value = false
  }
}

async function fetchClassrooms() {
  try {
    classrooms.value = await api.get<any[]>('/academic/classrooms') || []
  } catch (e) {
    console.error('Failed to fetch classrooms:', e)
  }
}

async function fetchTeachers() {
  try {
    teachers.value = await api.get<any[]>('/academic/teachers') || []
  } catch (e) {
    console.error('Failed to fetch teachers:', e)
  }
}

async function fetchUnits() {
  try {
    units.value = await api.get<any[]>('/units') || []
  } catch (e) {
    console.error('Failed to fetch units:', e)
  }
}

async function fetchAcademicYears() {
  try {
    const data = await api.get<any[]>('/academic/years')
    academicYears.value = (data || []).map(y => ({
      ...y,
      label: `${y.name} - ${y.semester}${y.is_active ? ' (Aktif)' : ''}`
    }))
    const active = academicYears.value.find(y => y.is_active)
    if (active && !filters.academic_year_id) {
      filters.academic_year_id = active.id
    }
  } catch (e) {
    console.error('Failed to fetch academic years:', e)
  }
}

// Schedule CRUD
function openAddScheduleDialog() {
  editingSchedule.value = null
  scheduleForm.day = filters.day || 'SENIN'
  scheduleForm.start_time = '07:30'
  scheduleForm.end_time = '09:00'
  scheduleForm.classroom_id = filters.classroom_id || (classrooms.value[0]?.id || null)
  scheduleForm.subject_id = null
  scheduleForm.teacher_id = filters.teacher_id || null
  scheduleForm.academic_year_id = filters.academic_year_id || activeAcademicYear.value?.id || null
  showScheduleDialog.value = true
}

function openEditSchedule(sc: any) {
  editingSchedule.value = sc
  scheduleForm.day = sc.day
  scheduleForm.start_time = sc.start_time
  scheduleForm.end_time = sc.end_time
  scheduleForm.classroom_id = sc.classroom_id
  scheduleForm.subject_id = sc.subject_id
  scheduleForm.teacher_id = sc.teacher_id
  scheduleForm.academic_year_id = sc.academic_year_id
  showScheduleDialog.value = true
}

async function submitScheduleForm() {
  if (!scheduleForm.classroom_id || !scheduleForm.subject_id || !scheduleForm.teacher_id) {
    toast.add({ severity: 'warn', summary: 'Perhatian', detail: 'Kelas, mata pelajaran, dan guru pengajar wajib dipilih', life: 4000 })
    return
  }

  submitting.value = true
  try {
    if (editingSchedule.value) {
      await api.put(`/academic/schedules/${editingSchedule.value.id}`, scheduleForm)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Jadwal pelajaran berhasil diperbarui!', life: 3000 })
    } else {
      await api.post('/academic/schedules', scheduleForm)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Jadwal pelajaran berhasil ditambahkan!', life: 3000 })
    }
    showScheduleDialog.value = false
    fetchSchedules()
  } catch (e: any) {
    const msg = e?.data?.detail || e?.message || 'Gagal menyimpan jadwal'
    toast.add({ severity: 'error', summary: 'Gagal', detail: msg, life: 5000 })
  } finally {
    submitting.value = false
  }
}

function confirmDeleteSchedule(sc: any) {
  confirm.require({
    message: `Hapus jadwal "${sc.subject?.name}" di ${sc.classroom?.name} (${sc.day} ${sc.start_time}-${sc.end_time})?`,
    header: 'Konfirmasi Hapus Jadwal',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Ya, Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/academic/schedules/${sc.id}`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Jadwal berhasil dihapus', life: 3000 })
        fetchSchedules()
      } catch (e: any) {
        toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus jadwal', life: 3000 })
      }
    }
  })
}

// Subject CRUD
function openAddSubjectDialog() {
  editingSubject.value = null
  subjectForm.name = ''
  subjectForm.code = ''
  subjectForm.unit_id = units.value[0]?.id || null
  showSubjectDialog.value = true
}

function openEditSubject(sb: any) {
  editingSubject.value = sb
  subjectForm.name = sb.name
  subjectForm.code = sb.code || ''
  subjectForm.unit_id = sb.unit_id
  showSubjectDialog.value = true
}

async function submitSubjectForm() {
  if (!subjectForm.name || !subjectForm.unit_id) {
    toast.add({ severity: 'warn', summary: 'Perhatian', detail: 'Nama mata pelajaran dan unit wajib diisi', life: 4000 })
    return
  }

  submitting.value = true
  try {
    if (editingSubject.value) {
      await api.put(`/academic/subjects/${editingSubject.value.id}`, subjectForm)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Mata pelajaran berhasil diperbarui!', life: 3000 })
    } else {
      await api.post('/academic/subjects', subjectForm)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Mata pelajaran berhasil ditambahkan!', life: 3000 })
    }
    showSubjectDialog.value = false
    fetchSubjects()
  } catch (e: any) {
    const msg = e?.data?.detail || e?.message || 'Gagal menyimpan mata pelajaran'
    toast.add({ severity: 'error', summary: 'Gagal', detail: msg, life: 5000 })
  } finally {
    submitting.value = false
  }
}

function confirmDeleteSubject(sb: any) {
  confirm.require({
    message: `Hapus mata pelajaran "${sb.name}"? Pastikan tidak ada jadwal yang menggunakan mapel ini.`,
    header: 'Konfirmasi Hapus Mapel',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Ya, Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/academic/subjects/${sb.id}`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Mata pelajaran berhasil dihapus', life: 3000 })
        fetchSubjects()
      } catch (e: any) {
        const msg = e?.data?.detail || 'Gagal menghapus mata pelajaran'
        toast.add({ severity: 'error', summary: 'Perhatian', detail: msg, life: 5000 })
      }
    }
  })
}

onMounted(async () => {
  await Promise.all([
    fetchAcademicYears(),
    fetchUnits(),
    fetchClassrooms(),
    fetchTeachers(),
    fetchSubjects()
  ])
  fetchSchedules()
})
</script>
