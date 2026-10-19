<template>
  <NuxtLayout name="dashboard">
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Data Guru & Pendidik</h1>
            <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300">
              <i class="pi pi-link text-[10px]"></i> Terintegrasi SDM
            </span>
          </div>
          <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Data master guru pengajar yang terhubung langsung dengan Kepegawaian (SDM), Wali Kelas, dan Jadwal Pelajaran.
          </p>
        </div>
        <div class="flex items-center gap-2 self-stretch sm:self-auto">
          <NuxtLink to="/dashboard/sdm/pegawai">
            <Button severity="secondary" outlined size="small" class="text-xs">
              <i class="pi pi-users mr-1.5 text-xs"></i>
              Buka Data Pegawai SDM
            </Button>
          </NuxtLink>
          <Button severity="success" size="small" class="text-xs font-medium" @click="openAddDialog">
            <i class="pi pi-plus mr-1.5 text-xs"></i>
            Tambah / Tugaskan Guru
          </Button>
        </div>
      </div>

      <!-- Quick Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-lg font-bold">
            <i class="pi pi-user"></i>
          </div>
          <div>
            <div class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">{{ activeTeachersCount }}</div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">Guru Aktif</div>
          </div>
        </div>

        <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center text-lg font-bold">
            <i class="pi pi-id-card"></i>
          </div>
          <div>
            <div class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">{{ nuptkCount }}</div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">Memiliki NUPTK</div>
          </div>
        </div>

        <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 flex items-center justify-center text-lg font-bold">
            <i class="pi pi-briefcase"></i>
          </div>
          <div>
            <div class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">{{ gtyCount }}</div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">Guru Tetap (GTY)</div>
          </div>
        </div>

        <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 flex items-center justify-center text-lg font-bold">
            <i class="pi pi-building"></i>
          </div>
          <div>
            <div class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white">{{ units.length }}</div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">Unit Sekolah</div>
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
              placeholder="Cari nama, NIK, NUPTK, mapel..."
              class="w-full !pl-9 text-xs sm:text-sm"
              size="small"
              @input="onSearchChange"
            />
          </div>

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
            @change="fetchTeachers"
          />

          <!-- Employee Type Filter -->
          <Select
            v-model="filters.employee_type"
            :options="[
              { label: 'Semua Status Pegawai', value: '' },
              { label: 'Tetap (GTY)', value: 'tetap' },
              { label: 'Kontrak', value: 'kontrak' },
              { label: 'Honorer', value: 'honorer' }
            ]"
            optionLabel="label"
            optionValue="value"
            placeholder="Status Pegawai"
            size="small"
            class="w-full text-xs sm:text-sm"
            @change="fetchTeachers"
          />

          <!-- Status Filter -->
          <Select
            v-model="filters.is_active"
            :options="[
              { label: 'Semua Status', value: null },
              { label: 'Aktif', value: true },
              { label: 'Nonaktif', value: false }
            ]"
            optionLabel="label"
            optionValue="value"
            placeholder="Status Aktif"
            size="small"
            class="w-full text-xs sm:text-sm"
            @change="fetchTeachers"
          />
        </div>
      </div>

      <!-- Data Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <DataTable
          :value="filteredTeachers"
          :loading="loading"
          paginator
          :rows="rowsPerPage"
          :rowsPerPageOptions="[10, 20, 50, 100]"
          stripedRows
          removableSort
          class="p-datatable-sm text-xs sm:text-sm"
          responsiveLayout="scroll"
        >
          <template #empty>
            <div class="text-center py-12 text-slate-500">
              <i class="pi pi-users text-4xl text-slate-300 dark:text-slate-600 mb-2 block"></i>
              Tidak ada data guru yang ditemukan.
            </div>
          </template>

          <template #loading>
            <div class="flex justify-center items-center py-12 text-slate-500">
              <i class="pi pi-spin pi-spinner text-2xl mr-2 text-emerald-500"></i>
              Memuat data guru...
            </div>
          </template>

          <!-- Profil Guru -->
          <Column field="full_name" header="Nama Guru" sortable>
            <template #body="{ data }">
              <div class="flex items-center gap-3 py-1">
                <Avatar
                  :image="data.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.full_name)}&background=059669&color=fff&size=80`"
                  shape="circle"
                  class="shrink-0 shadow-sm"
                />
                <div class="min-w-0">
                  <div class="font-semibold text-slate-800 dark:text-white flex items-center gap-1.5 flex-wrap">
                    <span>{{ data.full_name }}</span>
                    <span v-if="data.nuptk" class="text-[10px] bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 px-1.5 py-0.2 rounded font-mono font-medium">
                      NUPTK: {{ data.nuptk }}
                    </span>
                  </div>
                  <div class="text-[11px] text-slate-500 flex items-center gap-2 mt-0.5">
                    <span>NIK: {{ data.nik || '-' }}</span>
                    <span v-if="data.nip">• NIP: {{ data.nip }}</span>
                  </div>
                </div>
              </div>
            </template>
          </Column>

          <!-- Unit & Jabatan -->
          <Column field="unit_name" header="Unit & Jabatan" sortable>
            <template #body="{ data }">
              <div class="space-y-1">
                <div class="flex items-center gap-1.5">
                  <span
                    class="px-2 py-0.5 rounded text-[11px] font-semibold"
                    :class="getUnitBadgeClass(data.unit_name)"
                  >
                    {{ data.unit_name || 'Yayasan' }}
                  </span>
                </div>
                <div class="text-xs font-medium text-slate-700 dark:text-slate-300">
                  {{ data.position || 'Guru' }}
                </div>
              </div>
            </template>
          </Column>

          <!-- Kontak & Akun -->
          <Column header="Kontak & Akun">
            <template #body="{ data }">
              <div class="space-y-1 text-xs">
                <div class="flex items-center gap-1.5 text-slate-600 dark:text-slate-300">
                  <i class="pi pi-envelope text-[11px] text-slate-400"></i>
                  <span class="truncate max-w-[160px]">{{ data.email || '-' }}</span>
                </div>
                <div v-if="data.no_hp" class="flex items-center gap-1.5">
                  <i class="pi pi-whatsapp text-[11px] text-emerald-500"></i>
                  <a :href="`https://wa.me/${cleanPhone(data.no_hp)}`" target="_blank" class="text-emerald-600 dark:text-emerald-400 hover:underline">
                    {{ data.no_hp }}
                  </a>
                </div>
              </div>
            </template>
          </Column>

          <!-- Jenis & Status -->
          <Column field="employee_type" header="Status" sortable style="width: 130px">
            <template #body="{ data }">
              <div class="flex flex-col gap-1 items-start">
                <Tag
                  :value="data.is_active ? 'Aktif' : 'Nonaktif'"
                  :severity="data.is_active ? 'success' : 'danger'"
                  class="text-[10px] !px-2 !py-0.5"
                />
                <span class="text-[11px] uppercase tracking-wider font-medium text-slate-400">
                  {{ data.employee_type || 'tetap' }}
                </span>
              </div>
            </template>
          </Column>

          <!-- Aksi -->
          <Column header="Aksi" style="width: 130px" :exportable="false">
            <template #body="{ data }">
              <div class="flex items-center gap-1">
                <!-- View Profile in SDM if employee_id exists -->
                <NuxtLink v-if="data.employee_id" :to="`/dashboard/sdm/pegawai/${data.employee_id}`" title="Buka Detail Profil Pegawai">
                  <Button icon="pi pi-id-card" severity="info" size="small" text rounded class="!w-8 !h-8" />
                </NuxtLink>
                <!-- Edit -->
                <Button icon="pi pi-pencil" severity="secondary" size="small" text rounded class="!w-8 !h-8" title="Edit Guru" @click="editTeacher(data)" />
                <!-- Delete / Unassign -->
                <Button icon="pi pi-trash" severity="danger" size="small" text rounded class="!w-8 !h-8" title="Cabut Penugasan Guru" @click="confirmDelete(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Add Teacher Dialog -->
      <Dialog
        v-model:visible="showAddDialog"
        header="Tambah / Tugaskan Guru"
        :style="{ width: '620px' }"
        modal
        @hide="resetAddForm"
      >
        <div class="space-y-4 pt-2">
          <!-- Selection Mode Tabs -->
          <div class="grid grid-cols-2 gap-2 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
            <button
              type="button"
              class="py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
              :class="addMode === 'from_sdm' 
                ? 'bg-white dark:bg-slate-700 text-primary shadow-sm' 
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
              @click="addMode = 'from_sdm'"
            >
              <i class="pi pi-users text-xs"></i>
              1. Pilih Pegawai SDM
            </button>
            <button
              type="button"
              class="py-2 text-xs font-semibold rounded-lg transition-all flex items-center justify-center gap-2"
              :class="addMode === 'new_entry' 
                ? 'bg-white dark:bg-slate-700 text-primary shadow-sm' 
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'"
              @click="addMode = 'new_entry'"
            >
              <i class="pi pi-user-plus text-xs"></i>
              2. Input Guru Baru
            </button>
          </div>

          <!-- MODE 1: PILIH DARI SDM PEGAWAI -->
          <div v-if="addMode === 'from_sdm'" class="space-y-4">
            <div class="bg-blue-50 dark:bg-blue-950/30 p-3 rounded-xl border border-blue-200 dark:border-blue-900/50 text-xs text-blue-700 dark:text-blue-300">
              <i class="pi pi-info-circle mr-1"></i>
              Pilih pegawai yang sudah terdaftar di menu <strong>Kepegawaian (SDM)</strong> untuk dijadikan Guru. Sistem otomatis memberikan role Guru dan menghubungkan akunnya.
            </div>

            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">
                Pilih Pegawai <span class="text-rose-500">*</span>
              </label>
              <Select
                v-model="selectedCandidateId"
                :options="candidates"
                optionLabel="nama_lengkap"
                optionValue="id"
                placeholder="-- Pilih Nama Pegawai SDM --"
                filter
                class="w-full text-xs sm:text-sm"
                :loading="loadingCandidates"
                @change="onCandidateSelected"
              >
                <template #option="{ option }">
                  <div class="flex justify-between items-center w-full py-1">
                    <div>
                      <div class="font-semibold text-xs">{{ option.nama_lengkap }}</div>
                      <div class="text-[11px] text-slate-400">NIK: {{ option.nik_kepegawaian }} • {{ option.position || 'Staf' }}</div>
                    </div>
                    <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">{{ option.unit_name || '-' }}</span>
                  </div>
                </template>
              </Select>
            </div>

            <div v-if="selectedCandidate" class="space-y-3 pt-2 border-t border-slate-100 dark:border-slate-800">
              <div class="grid grid-cols-2 gap-3">
                <div class="flex flex-col gap-1.5">
                  <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Unit Penempatan *</label>
                  <Select
                    v-model="candidateForm.unit_id"
                    :options="units"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Pilih Unit"
                    class="w-full text-xs sm:text-sm"
                  />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Jabatan / Penugasan *</label>
                  <InputText
                    v-model="candidateForm.position"
                    placeholder="Contoh: Guru Kelas 1 Abu Bakar"
                    class="w-full text-xs sm:text-sm"
                  />
                </div>
              </div>

              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Email Akun (Opsional)</label>
                <InputText
                  v-model="candidateForm.email"
                  placeholder="guru@asysyuura.sch.id"
                  class="w-full text-xs sm:text-sm"
                />
              </div>
            </div>

            <div class="flex justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
              <Button type="button" label="Batal" severity="secondary" size="small" @click="showAddDialog = false" />
              <Button
                type="button"
                label="Jadikan Guru"
                icon="pi pi-check"
                size="small"
                severity="success"
                :disabled="!selectedCandidateId"
                :loading="submitting"
                @click="submitCandidateAsTeacher"
              />
            </div>
          </div>

          <!-- MODE 2: INPUT GURU BARU LENGKAP -->
          <form v-if="addMode === 'new_entry'" @submit.prevent="submitNewTeacher" class="space-y-3.5">
            <div class="bg-emerald-50 dark:bg-emerald-950/30 p-3 rounded-xl border border-emerald-200 dark:border-emerald-900/50 text-xs text-emerald-800 dark:text-emerald-300">
              <i class="pi pi-check-circle mr-1"></i>
              Guru baru yang diinput di sini akan <strong>otomatis terdaftar di Data Pegawai (SDM)</strong> dan dibuatkan akun login.
            </div>

            <!-- Nama Lengkap -->
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Nama Lengkap *</label>
              <InputText
                v-model="form.full_name"
                placeholder="Contoh: Ustadzah Fatimah, S.Pd."
                class="w-full text-xs sm:text-sm"
                :class="{ 'p-invalid': errors.full_name }"
              />
              <small v-if="errors.full_name" class="text-rose-500 text-[11px]">{{ errors.full_name }}</small>
            </div>

            <!-- NIK & NUPTK -->
            <div class="grid grid-cols-2 gap-3">
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">NIK Kepegawaian *</label>
                <InputText
                  v-model="form.nik"
                  placeholder="Nomor Induk Pegawai"
                  class="w-full text-xs sm:text-sm"
                  :class="{ 'p-invalid': errors.nik }"
                />
                <small v-if="errors.nik" class="text-rose-500 text-[11px]">{{ errors.nik }}</small>
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">NUPTK (Jika Ada)</label>
                <InputText
                  v-model="form.nuptk"
                  placeholder="16 Digit NUPTK"
                  class="w-full text-xs sm:text-sm"
                />
              </div>
            </div>

            <!-- Unit & Jabatan -->
            <div class="grid grid-cols-2 gap-3">
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Unit Sekolah *</label>
                <Select
                  v-model="form.unit_id"
                  :options="units"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Pilih Unit"
                  class="w-full text-xs sm:text-sm"
                  :class="{ 'p-invalid': errors.unit_id }"
                />
                <small v-if="errors.unit_id" class="text-rose-500 text-[11px]">{{ errors.unit_id }}</small>
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Jabatan Pengampu *</label>
                <InputText
                  v-model="form.position"
                  placeholder="Contoh: Guru Kelas 2"
                  class="w-full text-xs sm:text-sm"
                />
              </div>
            </div>

            <!-- Jenis Pegawai & No HP -->
            <div class="grid grid-cols-2 gap-3">
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Status Pegawai</label>
                <Select
                  v-model="form.employee_type"
                  :options="[
                    { label: 'Tetap (GTY)', value: 'tetap' },
                    { label: 'Kontrak', value: 'kontrak' },
                    { label: 'Honorer', value: 'honorer' }
                  ]"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full text-xs sm:text-sm"
                />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">No. WhatsApp / HP</label>
                <InputText
                  v-model="form.no_hp"
                  placeholder="0812xxxxxxxx"
                  class="w-full text-xs sm:text-sm"
                />
              </div>
            </div>

            <!-- Email & Password -->
            <div class="grid grid-cols-2 gap-3">
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Email Login</label>
                <InputText
                  v-model="form.email"
                  placeholder="guru@sekolah.id"
                  class="w-full text-xs sm:text-sm"
                />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Password Awal</label>
                <Password
                  v-model="form.password"
                  placeholder="Default: password123"
                  class="w-full"
                  inputClass="w-full text-xs sm:text-sm"
                  :feedback="false"
                  toggleMask
                />
              </div>
            </div>

            <!-- Footer -->
            <div class="flex justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
              <Button type="button" label="Batal" severity="secondary" size="small" @click="showAddDialog = false" />
              <Button type="submit" label="Simpan Guru Baru" icon="pi pi-check" size="small" severity="success" :loading="submitting" />
            </div>
          </form>
        </div>
      </Dialog>

      <!-- Edit Teacher Dialog -->
      <Dialog
        v-model:visible="showEditDialog"
        header="Edit Data Guru"
        :style="{ width: '560px' }"
        modal
      >
        <form @submit.prevent="submitEditTeacher" class="space-y-3.5 pt-2">
          <!-- Nama Lengkap -->
          <div class="flex flex-col gap-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Nama Lengkap *</label>
            <InputText v-model="editForm.full_name" class="w-full text-xs sm:text-sm" />
          </div>

          <!-- NIK & NUPTK -->
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">NIK Kepegawaian *</label>
              <InputText v-model="editForm.nik" class="w-full text-xs sm:text-sm" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">NUPTK</label>
              <InputText v-model="editForm.nuptk" placeholder="16 Digit NUPTK" class="w-full text-xs sm:text-sm" />
            </div>
          </div>

          <!-- Unit & Jabatan -->
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Unit Sekolah *</label>
              <Select
                v-model="editForm.unit_id"
                :options="units"
                optionLabel="name"
                optionValue="id"
                class="w-full text-xs sm:text-sm"
              />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Jabatan Pengampu *</label>
              <InputText v-model="editForm.position" placeholder="Guru Kelas" class="w-full text-xs sm:text-sm" />
            </div>
          </div>

          <!-- Status Pegawai & No HP -->
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Status Pegawai</label>
              <Select
                v-model="editForm.employee_type"
                :options="[
                  { label: 'Tetap (GTY)', value: 'tetap' },
                  { label: 'Kontrak', value: 'kontrak' },
                  { label: 'Honorer', value: 'honorer' }
                ]"
                optionLabel="label"
                optionValue="value"
                class="w-full text-xs sm:text-sm"
              />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">No. WhatsApp / HP</label>
              <InputText v-model="editForm.no_hp" placeholder="0812xxxxxxxx" class="w-full text-xs sm:text-sm" />
            </div>
          </div>

          <!-- Email & Reset Password -->
          <div class="grid grid-cols-2 gap-3">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Email Akun</label>
              <InputText v-model="editForm.email" class="w-full text-xs sm:text-sm" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Ganti Password (Opsional)</label>
              <Password
                v-model="editForm.password"
                placeholder="Kosongkan bila tetap"
                class="w-full"
                inputClass="w-full text-xs sm:text-sm"
                :feedback="false"
                toggleMask
              />
            </div>
          </div>

          <!-- Status Aktif Toggle -->
          <div class="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="is_active_toggle"
              v-model="editForm.is_active"
              class="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 w-4 h-4"
            />
            <label for="is_active_toggle" class="text-xs font-medium text-slate-700 dark:text-slate-300 cursor-pointer">
              Guru Berstatus Aktif Mengajar
            </label>
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-2 pt-4 border-t border-slate-100 dark:border-slate-800">
            <Button type="button" label="Batal" severity="secondary" size="small" @click="showEditDialog = false" />
            <Button type="submit" label="Simpan Perubahan" icon="pi pi-check" size="small" severity="success" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <!-- Confirmation Dialog -->
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

// State
const teachers = ref<any[]>([])
const units = ref<any[]>([])
const candidates = ref<any[]>([])
const loading = ref(true)
const loadingCandidates = ref(false)
const submitting = ref(false)
const rowsPerPage = ref(10)

// Filters
const filters = reactive({
  search: '',
  unit_id: null as number | null,
  employee_type: '',
  is_active: null as boolean | null
})

// Dialogs
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addMode = ref<'from_sdm' | 'new_entry'>('from_sdm')
const selectedCandidateId = ref<number | null>(null)
const editingTeacher = ref<any>(null)

// Candidate Form (Mode 1)
const candidateForm = reactive({
  unit_id: null as number | null,
  position: 'Guru',
  email: ''
})

// New Teacher Form (Mode 2)
const form = reactive({
  full_name: '',
  nik: '',
  nuptk: '',
  nip: '',
  unit_id: null as number | null,
  position: 'Guru',
  employee_type: 'tetap',
  no_hp: '',
  email: '',
  password: ''
})

const errors = reactive({
  full_name: '',
  nik: '',
  unit_id: ''
})

// Edit Form
const editForm = reactive({
  id: null as number | null,
  full_name: '',
  nik: '',
  nuptk: '',
  nip: '',
  unit_id: null as number | null,
  position: '',
  employee_type: 'tetap',
  no_hp: '',
  email: '',
  password: '',
  is_active: true
})

// Computeds
const activeTeachersCount = computed(() => {
  return teachers.value.filter(t => t.is_active).length
})

const nuptkCount = computed(() => {
  return teachers.value.filter(t => t.nuptk && t.nuptk.trim().length > 0).length
})

const gtyCount = computed(() => {
  return teachers.value.filter(t => (t.employee_type || '').toLowerCase() === 'tetap').length
})

const selectedCandidate = computed(() => {
  return candidates.value.find(c => c.id === selectedCandidateId.value)
})

const filteredTeachers = computed(() => {
  return teachers.value.filter(t => {
    // Search
    if (filters.search) {
      const q = filters.search.toLowerCase().trim()
      const matchName = (t.full_name || '').toLowerCase().includes(q)
      const matchNik = (t.nik || '').toLowerCase().includes(q)
      const matchNuptk = (t.nuptk || '').toLowerCase().includes(q)
      const matchPos = (t.position || '').toLowerCase().includes(q)
      if (!matchName && !matchNik && !matchNuptk && !matchPos) return false
    }

    // Unit
    if (filters.unit_id && t.unit_id !== filters.unit_id) {
      return false
    }

    // Employee Type
    if (filters.employee_type && (t.employee_type || '').toLowerCase() !== filters.employee_type.toLowerCase()) {
      return false
    }

    // Active
    if (filters.is_active !== null && t.is_active !== filters.is_active) {
      return false
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

function cleanPhone(phone?: string) {
  if (!phone) return ''
  let cleaned = phone.replace(/[^0-9]/g, '')
  if (cleaned.startsWith('0')) {
    cleaned = '62' + cleaned.substring(1)
  }
  return cleaned
}

// Fetch Teachers
async function fetchTeachers() {
  loading.value = true
  try {
    const data = await api.get<any[]>('/academic/teachers')
    teachers.value = data || []
  } catch (error) {
    console.error('Failed to fetch teachers:', error)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal memuat data guru', life: 3000 })
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

// Fetch Candidates from SDM
async function fetchCandidates() {
  loadingCandidates.value = true
  try {
    candidates.value = await api.get<any[]>('/academic/teachers/candidates')
  } catch (error) {
    console.error('Failed to fetch candidates:', error)
  } finally {
    loadingCandidates.value = false
  }
}

function onSearchChange() {
  // Handled reactively by computed filteredTeachers
}

function openAddDialog() {
  showAddDialog.value = true
  addMode.value = 'from_sdm'
  fetchCandidates()
}

function onCandidateSelected() {
  const cand = selectedCandidate.value
  if (cand) {
    candidateForm.unit_id = cand.unit_id || null
    candidateForm.position = cand.position && cand.position !== 'Staf' ? `Guru / ${cand.position}` : 'Guru'
    candidateForm.email = ''
  }
}

function resetAddForm() {
  selectedCandidateId.value = null
  candidateForm.unit_id = null
  candidateForm.position = 'Guru'
  candidateForm.email = ''

  form.full_name = ''
  form.nik = ''
  form.nuptk = ''
  form.nip = ''
  form.unit_id = null
  form.position = 'Guru'
  form.employee_type = 'tetap'
  form.no_hp = ''
  form.email = ''
  form.password = ''

  errors.full_name = ''
  errors.nik = ''
  errors.unit_id = ''
}

// Submit Mode 1: From SDM
async function submitCandidateAsTeacher() {
  if (!selectedCandidateId.value) return

  submitting.value = true
  try {
    await api.post('/academic/teachers', {
      employee_id: selectedCandidateId.value,
      unit_id: candidateForm.unit_id,
      position: candidateForm.position || 'Guru',
      email: candidateForm.email || undefined
    })

    toast.add({
      severity: 'success',
      summary: 'Berhasil',
      detail: 'Pegawai berhasil ditugaskan sebagai Guru!',
      life: 3000
    })

    showAddDialog.value = false
    resetAddForm()
    fetchTeachers()
  } catch (error: any) {
    const msg = error?.data?.detail || 'Gagal menugaskan pegawai sebagai guru'
    toast.add({ severity: 'error', summary: 'Gagal', detail: msg, life: 5000 })
  } finally {
    submitting.value = false
  }
}

// Submit Mode 2: New Entry
async function submitNewTeacher() {
  errors.full_name = ''
  errors.nik = ''
  errors.unit_id = ''

  let valid = true
  if (!form.full_name || form.full_name.trim().length < 2) {
    errors.full_name = 'Nama lengkap minimal 2 karakter.'
    valid = false
  }
  if (!form.nik || form.nik.trim().length < 3) {
    errors.nik = 'NIK minimal 3 karakter.'
    valid = false
  }
  if (!form.unit_id) {
    errors.unit_id = 'Pilih salah satu unit sekolah.'
    valid = false
  }

  if (!valid) return

  submitting.value = true
  try {
    await api.post('/academic/teachers', {
      full_name: form.full_name,
      nik: form.nik,
      nuptk: form.nuptk || undefined,
      nip: form.nip || undefined,
      unit_id: form.unit_id,
      position: form.position || 'Guru',
      employee_type: form.employee_type,
      no_hp: form.no_hp || undefined,
      email: form.email || undefined,
      password: form.password || undefined
    })

    toast.add({
      severity: 'success',
      summary: 'Berhasil',
      detail: 'Guru baru berhasil ditambahkan dan tersinkronisasi ke SDM!',
      life: 3000
    })

    showAddDialog.value = false
    resetAddForm()
    fetchTeachers()
  } catch (error: any) {
    const msg = error?.data?.detail || 'Gagal menambahkan guru'
    toast.add({ severity: 'error', summary: 'Gagal', detail: msg, life: 5000 })
  } finally {
    submitting.value = false
  }
}

// Edit Teacher
function editTeacher(teacher: any) {
  editingTeacher.value = teacher
  editForm.id = teacher.id
  editForm.full_name = teacher.full_name
  editForm.nik = teacher.nik || ''
  editForm.nuptk = teacher.nuptk || ''
  editForm.nip = teacher.nip || ''
  editForm.unit_id = teacher.unit_id || null
  editForm.position = teacher.position || 'Guru'
  editForm.employee_type = teacher.employee_type || 'tetap'
  editForm.no_hp = teacher.no_hp || ''
  editForm.email = teacher.email || ''
  editForm.password = ''
  editForm.is_active = teacher.is_active ?? true

  showEditDialog.value = true
}

async function submitEditTeacher() {
  if (!editForm.id) return

  submitting.value = true
  try {
    const payload: any = {
      full_name: editForm.full_name,
      nik: editForm.nik,
      nuptk: editForm.nuptk || undefined,
      nip: editForm.nip || undefined,
      unit_id: editForm.unit_id,
      position: editForm.position,
      employee_type: editForm.employee_type,
      no_hp: editForm.no_hp || undefined,
      email: editForm.email || undefined,
      is_active: editForm.is_active
    }
    if (editForm.password && editForm.password.trim()) {
      payload.password = editForm.password.trim()
    }

    await api.put(`/academic/teachers/${editForm.id}`, payload)

    toast.add({
      severity: 'success',
      summary: 'Berhasil',
      detail: 'Data guru berhasil diperbarui!',
      life: 3000
    })

    showEditDialog.value = false
    fetchTeachers()
  } catch (error: any) {
    const msg = error?.data?.detail || 'Gagal memperbarui data guru'
    toast.add({ severity: 'error', summary: 'Gagal', detail: msg, life: 5000 })
  } finally {
    submitting.value = false
  }
}

// Confirm Delete / Unassign
function confirmDelete(teacher: any) {
  confirm.require({
    message: `Apakah Anda yakin ingin mencabut penugasan guru untuk "${teacher.full_name}"? Data di SDM Kepegawaian tetap aman dan tidak akan terhapus.`,
    header: 'Konfirmasi Cabut Penugasan Guru',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Ya, Cabut Penugasan',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        const res = await api.delete<any>(`/academic/teachers/${teacher.id}`)
        toast.add({
          severity: 'success',
          summary: 'Berhasil',
          detail: res?.message || 'Penugasan guru berhasil dicabut',
          life: 3000
        })
        fetchTeachers()
      } catch (error: any) {
        const msg = error?.data?.detail || 'Gagal menghapus penugasan guru'
        toast.add({
          severity: 'error',
          summary: 'Perhatian',
          detail: msg,
          life: 5000
        })
      }
    }
  })
}

onMounted(() => {
  fetchTeachers()
  fetchUnits()
})
</script>
