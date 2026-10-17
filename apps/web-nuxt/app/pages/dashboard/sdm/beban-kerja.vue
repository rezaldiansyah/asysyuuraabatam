<template>
  <div class="space-y-6 pb-12">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <span class="w-9 h-9 rounded-xl bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center text-lg shadow-sm flex-shrink-0">
            <i class="pi pi-gauge"></i>
          </span>
          <span>Distribusi Beban Kerja & Radar Anti-Burnout</span>
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-xs sm:text-sm mt-1">
          Monitoring holistik multi-dimensi: Jam KBM, Jabatan Struktural, SK Kepanitiaan/Tim Aktif, dan Beban Tugas Kanban.
        </p>
      </div>

      <div class="flex items-center gap-2 flex-wrap flex-shrink-0">
        <Button 
          label="Segarkan" 
          icon="pi pi-refresh" 
          severity="secondary" 
          outlined 
          size="small" 
          :loading="loading" 
          @click="fetchRadarData" 
        />
        <NuxtLink to="/dashboard/internal/dokumen">
          <Button 
            label="Kelola SK Tim" 
            icon="pi pi-file-pdf" 
            severity="secondary" 
            size="small" 
          />
        </NuxtLink>
        <NuxtLink to="/dashboard/internal/tugas">
          <Button 
            label="Papan Tugas" 
            icon="pi pi-check-square" 
            class="p-button-primary" 
            size="small" 
          />
        </NuxtLink>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-3">
      <!-- Total Pegawai -->
      <div 
        class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-slate-400': selectedStatusFilter === '' }"
        @click="filterByStatus('')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Total Pegawai</span>
          <i class="pi pi-users text-slate-400 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-slate-800 dark:text-white mt-1">{{ summary.total }}</p>
        <span class="text-[11px] text-slate-400">Terdaftar di sistem</span>
      </div>

      <!-- Risiko Burnout / Overload -->
      <div 
        class="p-3.5 rounded-xl border border-rose-200 dark:border-rose-900/50 bg-rose-50/40 dark:bg-rose-950/20 shadow-sm transition hover:shadow cursor-pointer relative overflow-hidden"
        :class="{ 'ring-2 ring-rose-500': selectedStatusFilter === 'overload' }"
        @click="filterByStatus('overload')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-rose-700 dark:text-rose-300">🔴 Risiko Burnout</span>
          <i class="pi pi-exclamation-triangle text-rose-500 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-rose-700 dark:text-rose-300 mt-1">{{ summary.overload }}</p>
        <span class="text-[11px] text-rose-600/80 dark:text-rose-400">Indeks &ge; 80% / &ge; 4 tugas</span>
      </div>

      <!-- Beban Padat -->
      <div 
        class="p-3.5 rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50/40 dark:bg-amber-950/20 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-amber-500': selectedStatusFilter === 'padat' }"
        @click="filterByStatus('padat')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-amber-700 dark:text-amber-300">🟡 Beban Padat</span>
          <i class="pi pi-bolt text-amber-500 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-amber-700 dark:text-amber-300 mt-1">{{ summary.padat }}</p>
        <span class="text-[11px] text-amber-600/80 dark:text-amber-400">Indeks 60 - 79%</span>
      </div>

      <!-- Ideal / Seimbang -->
      <div 
        class="p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-900/50 bg-emerald-50/40 dark:bg-emerald-950/20 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-emerald-500': selectedStatusFilter === 'optimal' }"
        @click="filterByStatus('optimal')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-emerald-700 dark:text-emerald-300">🟢 Ideal & Seimbang</span>
          <i class="pi pi-verified text-emerald-500 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-emerald-700 dark:text-emerald-300 mt-1">{{ summary.optimal }}</p>
        <span class="text-[11px] text-emerald-600/80 dark:text-emerald-400">Indeks 35 - 59%</span>
      </div>

      <!-- Pasif / Siap Ditugaskan -->
      <div 
        class="p-3.5 rounded-xl border border-sky-200 dark:border-sky-900/50 bg-sky-50/40 dark:bg-sky-950/20 shadow-sm transition hover:shadow cursor-pointer"
        :class="{ 'ring-2 ring-sky-500': selectedStatusFilter === 'underload' }"
        @click="filterByStatus('underload')"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-sky-700 dark:text-sky-300">⚪ Pasif / Siap Tugas</span>
          <i class="pi pi-user-plus text-sky-500 text-sm"></i>
        </div>
        <p class="text-2xl font-bold text-sky-700 dark:text-sky-300 mt-1">{{ summary.underload }}</p>
        <span class="text-[11px] text-sky-600/80 dark:text-sky-400">Siap diberi amanah baru</span>
      </div>
    </div>

    <!-- Tab Navigasi Halaman -->
    <div class="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800">
      <button 
        type="button"
        @click="activeMainTab = 'radar'"
        class="pb-3 px-3 text-sm font-semibold transition border-b-2 flex items-center gap-2"
        :class="activeMainTab === 'radar' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
      >
        <i class="pi pi-chart-pie"></i>
        <span>Radar Beban Kerja Pegawai ({{ filteredEmployees.length }})</span>
      </button>

      <button 
        type="button"
        @click="activeMainTab = 'teams'"
        class="pb-3 px-3 text-sm font-semibold transition border-b-2 flex items-center gap-2"
        :class="activeMainTab === 'teams' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
      >
        <i class="pi pi-users"></i>
        <span>Katalog Tim & Panitia Aktif ({{ activeTeams.length }})</span>
      </button>
    </div>

    <!-- TAB 1: RADAR BEBAN KERJA PEGAWAI -->
    <div v-if="activeMainTab === 'radar'" class="space-y-4">
      <!-- Search & Filters Bar -->
      <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div class="flex items-center gap-2.5 flex-1 max-w-xl">
          <div class="relative w-full">
            <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
            <InputText 
              v-model="searchQuery" 
              placeholder="Cari nama pegawai, NIK, atau posisi..." 
              size="small" 
              class="w-full !pl-9 text-xs" 
            />
          </div>

          <Select 
            v-model="selectedUnitId" 
            :options="unitOptions" 
            optionLabel="name" 
            optionValue="id" 
            placeholder="Semua Unit" 
            showClear 
            size="small" 
            class="w-44 text-xs" 
          />
        </div>

        <div class="flex items-center gap-2">
          <!-- Filter Status Dropdown -->
          <Select 
            v-model="selectedStatusFilter" 
            :options="statusOptions" 
            optionLabel="label" 
            optionValue="value" 
            placeholder="Semua Status Beban" 
            showClear 
            size="small" 
            class="w-48 text-xs" 
          />

          <!-- View Mode Toggle: Table vs Cards -->
          <div class="flex items-center p-1 bg-slate-100 dark:bg-slate-800 rounded-lg text-xs">
            <button 
              type="button" 
              @click="displayMode = 'table'"
              class="px-2.5 py-1 rounded-md transition"
              :class="displayMode === 'table' ? 'bg-white dark:bg-slate-700 text-primary shadow-sm font-bold' : 'text-slate-500'"
              title="Tampilan Tabel Lengkap"
            >
              <i class="pi pi-table"></i>
            </button>
            <button 
              type="button" 
              @click="displayMode = 'cards'"
              class="px-2.5 py-1 rounded-md transition"
              :class="displayMode === 'cards' ? 'bg-white dark:bg-slate-700 text-primary shadow-sm font-bold' : 'text-slate-500'"
              title="Tampilan Kartu Ringkas"
            >
              <i class="pi pi-th-large"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- TAMPILAN TABEL -->
      <div v-if="displayMode === 'table'" class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden p-1">
        <DataTable 
          :value="filteredEmployees" 
          :loading="loading" 
          dataKey="user_id" 
          class="p-datatable-sm text-xs" 
          stripedRows 
          responsiveLayout="scroll"
          paginator 
          :rows="15" 
          :rowsPerPageOptions="[15, 30, 50, 100]"
          currentPageReportTemplate="Menampilkan {first}–{last} dari {totalRecords} pegawai"
          paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
        >
          <template #empty>
            <div class="text-center py-10 text-slate-400">
              <i class="pi pi-search text-3xl mb-2"></i>
              <p>Tidak ada data pegawai yang sesuai dengan filter.</p>
            </div>
          </template>

          <!-- Pegawai & Unit -->
          <Column field="nama_lengkap" header="Pegawai" sortable style="min-width: 220px">
            <template #body="{ data }">
              <div class="flex items-center gap-3 py-1">
                <Avatar 
                  :image="data.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.nama_lengkap)}&background=random`" 
                  shape="circle" 
                  size="normal"
                  class="flex-shrink-0"
                />
                <div class="min-w-0">
                  <div class="font-bold text-slate-800 dark:text-white truncate hover:text-primary cursor-pointer" @click="openEmployeeDetail(data)">
                    {{ data.nama_lengkap }}
                  </div>
                  <div class="text-[11px] text-slate-400 flex items-center gap-1.5 flex-wrap">
                    <span>{{ data.nik || 'N/A' }}</span>
                    <span>&bull;</span>
                    <span class="font-medium text-slate-600 dark:text-slate-300">{{ data.unit_name }}</span>
                  </div>
                  <div class="text-[11px] text-primary/80 truncate font-medium">
                    {{ data.position }}
                  </div>
                </div>
              </div>
            </template>
          </Column>

          <!-- Indeks Beban Kerja & Status -->
          <Column field="workload_score" header="Indeks Beban Kerja" sortable style="min-width: 190px">
            <template #body="{ data }">
              <div class="space-y-1.5 py-1">
                <div class="flex items-center justify-between">
                  <span 
                    class="text-[11px] font-bold px-2 py-0.5 rounded-md inline-flex items-center gap-1"
                    :class="getStatusBadgeClass(data.workload_status)"
                  >
                    {{ data.status_label }}
                  </span>
                  <span class="font-mono font-bold text-xs" :class="getScoreTextClass(data.workload_score)">
                    {{ data.workload_score }}%
                  </span>
                </div>
                <!-- Progress Bar -->
                <div class="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
                  <div 
                    class="h-2 rounded-full transition-all duration-300"
                    :class="getProgressBarClass(data.workload_score)"
                    :style="{ width: `${data.workload_score}%` }"
                  ></div>
                </div>
              </div>
            </template>
          </Column>

          <!-- Jam Mengajar (KBM) -->
          <Column header="Jam KBM" style="min-width: 140px">
            <template #body="{ data }">
              <div v-if="data.breakdown.kbm_slots > 0" class="space-y-1">
                <div class="font-semibold text-slate-700 dark:text-slate-200">
                  {{ data.breakdown.kbm_hours }} Jam <span class="text-slate-400 font-normal">({{ data.breakdown.kbm_slots }} Sesi)</span>
                </div>
                <div class="text-[10px] text-slate-400 flex flex-wrap gap-1">
                  <span v-for="d in data.breakdown.days_teaching" :key="d" class="px-1 bg-slate-100 dark:bg-slate-800 rounded">
                    {{ d }}
                  </span>
                </div>
              </div>
              <div v-else class="text-slate-400 italic text-[11px]">
                Non-Guru / 0 Jam
              </div>
            </template>
          </Column>

          <!-- SK Kepanitiaan & Tim Aktif -->
          <Column header="Kepanitiaan / SK Aktif" style="min-width: 190px">
            <template #body="{ data }">
              <div v-if="data.breakdown.active_committees_count > 0" class="space-y-1">
                <div class="font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                  <i class="pi pi-users text-xs"></i>
                  <span>{{ data.breakdown.active_committees_count }} Tim Aktif</span>
                </div>
                <div class="flex flex-wrap gap-1 max-w-[240px]">
                  <span 
                    v-for="(c, cIdx) in data.breakdown.active_committees.slice(0, 2)" 
                    :key="cIdx" 
                    class="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-100 dark:border-indigo-800 truncate max-w-[180px]"
                    :title="`${c.title} (${c.role})`"
                  >
                    {{ c.title }} ({{ c.role }})
                  </span>
                  <span v-if="data.breakdown.active_committees.length > 2" class="text-[10px] text-slate-400 self-center font-bold">
                    +{{ data.breakdown.active_committees.length - 2 }} lagi
                  </span>
                </div>
              </div>
              <div v-else class="text-slate-400 italic text-[11px]">
                Belum ada SK tim
              </div>
            </template>
          </Column>

          <!-- Tugas Kanban -->
          <Column header="Tugas Kanban" style="min-width: 130px">
            <template #body="{ data }">
              <div class="space-y-0.5">
                <div class="font-medium text-slate-700 dark:text-slate-200">
                  {{ data.breakdown.active_tasks_count }} Aktif
                </div>
                <div v-if="data.breakdown.overdue_tasks_count > 0" class="text-rose-500 font-bold text-[10px] flex items-center gap-1">
                  <i class="pi pi-exclamation-circle text-[9px]"></i>
                  <span>{{ data.breakdown.overdue_tasks_count }} Lewat Deadline!</span>
                </div>
              </div>
            </template>
          </Column>

          <!-- Aksi -->
          <Column header="Aksi" style="min-width: 90px" alignFrozen="right" frozen>
            <template #body="{ data }">
              <Button 
                label="Detail" 
                icon="pi pi-eye" 
                size="small" 
                severity="secondary" 
                outlined 
                class="!text-xs !py-1 !px-2"
                @click="openEmployeeDetail(data)"
              />
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- TAMPILAN CARDS -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div 
          v-for="emp in filteredEmployees" 
          :key="emp.user_id"
          class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm hover:shadow-md transition space-y-3 cursor-pointer"
          @click="openEmployeeDetail(emp)"
        >
          <!-- Card Top -->
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-3">
              <Avatar 
                :image="emp.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(emp.nama_lengkap)}&background=random`" 
                shape="circle" 
                size="large"
              />
              <div>
                <h4 class="font-bold text-slate-800 dark:text-white leading-tight">{{ emp.nama_lengkap }}</h4>
                <div class="text-xs text-slate-400 mt-0.5">{{ emp.nik || 'No NIK' }} &bull; {{ emp.unit_name }}</div>
                <div class="text-xs text-primary font-medium mt-0.5">{{ emp.position }}</div>
              </div>
            </div>

            <!-- Score Badge -->
            <div class="text-right flex-shrink-0">
              <span 
                class="text-xs font-bold px-2 py-0.5 rounded-md inline-block"
                :class="getStatusBadgeClass(emp.workload_status)"
              >
                {{ emp.workload_score }}%
              </span>
              <div class="text-[10px] text-slate-400 mt-0.5 font-medium">{{ emp.status_label }}</div>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="w-full bg-slate-100 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
            <div 
              class="h-2 rounded-full"
              :class="getProgressBarClass(emp.workload_score)"
              :style="{ width: `${emp.workload_score}%` }"
            ></div>
          </div>

          <!-- 3-Pillar Breakdown Chips -->
          <div class="grid grid-cols-3 gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-center text-xs">
            <div class="p-2 rounded-lg bg-slate-50 dark:bg-slate-800">
              <div class="text-slate-400 text-[10px]">KBM</div>
              <div class="font-bold text-slate-700 dark:text-slate-200">{{ emp.breakdown.kbm_hours }}j</div>
              <div class="text-[9px] text-slate-400">{{ emp.breakdown.kbm_slots }} sesi</div>
            </div>

            <div class="p-2 rounded-lg bg-indigo-50/50 dark:bg-indigo-950/30">
              <div class="text-indigo-400 text-[10px]">Tim / SK</div>
              <div class="font-bold text-indigo-700 dark:text-indigo-300">{{ emp.breakdown.active_committees_count }}</div>
              <div class="text-[9px] text-indigo-500">Kepanitiaan</div>
            </div>

            <div class="p-2 rounded-lg bg-emerald-50/50 dark:bg-emerald-950/30">
              <div class="text-emerald-500 text-[10px]">Kanban</div>
              <div class="font-bold text-emerald-700 dark:text-emerald-300">{{ emp.breakdown.active_tasks_count }}</div>
              <div v-if="emp.breakdown.overdue_tasks_count > 0" class="text-[9px] text-rose-500 font-bold">
                {{ emp.breakdown.overdue_tasks_count }} Overdue
              </div>
              <div v-else class="text-[9px] text-slate-400">Tugas aktif</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: KATALOG TIM & PANITIA AKTIF -->
    <div v-else-if="activeMainTab === 'teams'" class="space-y-4">
      <div v-if="activeTeams.length === 0" class="text-center py-12 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-400">
        <i class="pi pi-users text-4xl mb-2 text-slate-300"></i>
        <p class="text-sm font-semibold">Belum ada Tim / Kepanitiaan SK Aktif</p>
        <p class="text-xs text-slate-500 mt-1">Anda dapat menerbitkan SK Tim Multi-Pegawai melalui menu Pusat Unduhan / Dokumen.</p>
        <NuxtLink to="/dashboard/internal/dokumen" class="mt-4 inline-block">
          <Button label="Buat SK Tim Baru" icon="pi pi-plus" size="small" />
        </NuxtLink>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <div 
          v-for="team in activeTeams" 
          :key="team.id"
          class="p-4 rounded-xl border border-indigo-100 dark:border-indigo-950 bg-white dark:bg-slate-900 shadow-sm hover:shadow-md transition space-y-3"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-2.5">
              <div class="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 flex items-center justify-center text-lg font-bold">
                <i class="pi pi-users"></i>
              </div>
              <div>
                <h3 class="font-bold text-slate-800 dark:text-white leading-tight">{{ team.title }}</h3>
                <div v-if="team.document_number" class="text-xs font-mono text-slate-400 mt-0.5">
                  #{{ team.document_number }}
                </div>
              </div>
            </div>
            <span class="text-xs font-bold px-2.5 py-1 rounded-full bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
              {{ team.members_count }} Anggota
            </span>
          </div>

          <!-- Periode Tim -->
          <div class="text-xs text-slate-500 flex items-center gap-1.5 bg-slate-50 dark:bg-slate-800/60 p-2 rounded-lg">
            <i class="pi pi-calendar text-slate-400"></i>
            <span>Masa Tugas: <strong>{{ team.term_start ? formatDate(team.term_start) : 'Aktif' }}</strong> s/d <strong>{{ team.term_end ? formatDate(team.term_end) : 'Selesai Kegiatan' }}</strong></span>
          </div>

          <!-- Daftar Anggota & Peran -->
          <div class="space-y-1.5 pt-1">
            <h5 class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Susunan Panitia / Tim:</h5>
            <div class="space-y-1 max-h-44 overflow-y-auto pr-1">
              <div 
                v-for="(m, mIdx) in team.members" 
                :key="mIdx"
                class="flex items-center justify-between p-1.5 rounded-lg bg-slate-50 dark:bg-slate-800/40 text-xs"
              >
                <span class="font-medium text-slate-700 dark:text-slate-200 truncate">{{ m.name }}</span>
                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-100/70 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 flex-shrink-0">
                  {{ m.role }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- DIALOG DETAIL BEBAN KERJA PEGAWAI -->
    <Dialog 
      v-model:visible="detailModalVisible" 
      :header="selectedEmployee ? `Dossier Beban Kerja: ${selectedEmployee.nama_lengkap}` : 'Detail Pegawai'" 
      modal 
      class="w-full max-w-3xl" 
      :breakpoints="{ '960px': '90vw', '640px': '98vw' }"
    >
      <div v-if="selectedEmployee" class="space-y-4 pt-1 max-h-[75vh] overflow-y-auto pr-1">
        <!-- Profile Banner -->
        <div class="flex items-center justify-between p-3.5 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <div class="flex items-center gap-3">
            <Avatar 
              :image="selectedEmployee.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(selectedEmployee.nama_lengkap)}&background=random`" 
              shape="circle" 
              size="large"
            />
            <div>
              <h3 class="font-bold text-slate-800 dark:text-white text-base">{{ selectedEmployee.nama_lengkap }}</h3>
              <div class="text-xs text-slate-400">NIK: {{ selectedEmployee.nik || '-' }} &bull; Unit: {{ selectedEmployee.unit_name }}</div>
              <div class="text-xs font-semibold text-primary">{{ selectedEmployee.position }}</div>
            </div>
          </div>

          <div class="text-right">
            <div class="text-xs font-bold px-2.5 py-1 rounded-md inline-block" :class="getStatusBadgeClass(selectedEmployee.workload_status)">
              {{ selectedEmployee.status_label }}
            </div>
            <div class="text-lg font-bold font-mono mt-1" :class="getScoreTextClass(selectedEmployee.workload_score)">
              {{ selectedEmployee.workload_score }}% Workload Index
            </div>
          </div>
        </div>

        <!-- Rekomendasi Pimpinan / Insight AI-Engine -->
        <div 
          v-if="selectedEmployee.workload_score >= 80" 
          class="p-3 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 rounded-xl flex items-start gap-2.5 text-xs text-rose-800 dark:text-rose-200"
        >
          <i class="pi pi-exclamation-triangle text-base text-rose-600 flex-shrink-0 mt-0.5"></i>
          <div>
            <span class="font-bold">Peringatan Risiko Overload / Burnout:</span>
            <p class="mt-0.5 leading-relaxed text-rose-700 dark:text-rose-300">
              Pegawai ini memegang beban mengajar yang padat disertai amanah struktural atau lebih dari 3 kepanitiaan/tugas aktif. 
              Disarankan untuk <strong>mendelegasikan penugasan kepanitiaan baru</strong> ke rekan guru/staf lain yang indeks beban kerjanya masih di bawah 40%.
            </p>
          </div>
        </div>

        <div 
          v-else-if="selectedEmployee.workload_score < 35" 
          class="p-3 bg-sky-50 dark:bg-sky-950/30 border border-sky-200 dark:border-sky-900 rounded-xl flex items-start gap-2.5 text-xs text-sky-800 dark:text-sky-200"
        >
          <i class="pi pi-info-circle text-base text-sky-600 flex-shrink-0 mt-0.5"></i>
          <div>
            <span class="font-bold">Potensi Partisipasi (Kapasitas Tersedia):</span>
            <p class="mt-0.5 leading-relaxed text-sky-700 dark:text-sky-300">
              Pegawai ini memiliki kapasitas waktu longgar (jam mengajar tergolong minim dan belum terlibat dalam kepanitiaan aktif yayasan). 
              Sangat direkomendasikan untuk <strong>diberi amanah dalam kepanitiaan baru</strong> (seperti PPDB, HUT RI, atau koordinator program).
            </p>
          </div>
        </div>

        <!-- 3 Breakdown Blocks -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <!-- KBM Schedule -->
          <div class="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
              <span class="font-bold text-xs text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                <i class="pi pi-book text-emerald-600"></i>
                Jadwal KBM ({{ selectedEmployee.breakdown.kbm_hours }} Jam)
              </span>
              <span class="text-[10px] text-slate-400">{{ selectedEmployee.breakdown.kbm_slots }} Sesi</span>
            </div>
            <div v-if="selectedEmployee.breakdown.kbm_schedule_summary.length > 0" class="space-y-1 text-xs">
              <div 
                v-for="(sc, sIdx) in selectedEmployee.breakdown.kbm_schedule_summary" 
                :key="sIdx"
                class="p-1.5 rounded bg-slate-50 dark:bg-slate-800 text-[11px] text-slate-700 dark:text-slate-300"
              >
                {{ sc }}
              </div>
            </div>
            <div v-else class="text-slate-400 italic text-xs py-2 text-center">
              Tidak ada jadwal mengajar di jadwal kelas.
            </div>
          </div>

          <!-- Active Committees -->
          <div class="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
              <span class="font-bold text-xs text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                <i class="pi pi-users text-indigo-600"></i>
                Kepanitiaan / SK ({{ selectedEmployee.breakdown.active_committees_count }})
              </span>
            </div>
            <div v-if="selectedEmployee.breakdown.active_committees.length > 0" class="space-y-1.5 text-xs">
              <div 
                v-for="(cm, cmIdx) in selectedEmployee.breakdown.active_committees" 
                :key="cmIdx"
                class="p-1.5 rounded-lg bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900 text-[11px]"
              >
                <div class="font-bold text-indigo-900 dark:text-indigo-200">{{ cm.title }}</div>
                <div class="text-indigo-600 dark:text-indigo-400 font-semibold mt-0.5">Peran: {{ cm.role }}</div>
                <div v-if="cm.doc_number" class="text-[10px] text-slate-400 mt-0.5 font-mono">#{{ cm.doc_number }}</div>
              </div>
            </div>
            <div v-else class="text-slate-400 italic text-xs py-2 text-center">
              Belum tercatat dalam SK tim / panitia aktif.
            </div>
          </div>

          <!-- Kanban Tasks -->
          <div class="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
            <div class="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-800">
              <span class="font-bold text-xs text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                <i class="pi pi-check-square text-blue-600"></i>
                Beban Kanban ({{ selectedEmployee.breakdown.active_tasks_count }})
              </span>
              <span v-if="selectedEmployee.breakdown.overdue_tasks_count > 0" class="text-[10px] text-rose-500 font-bold">
                {{ selectedEmployee.breakdown.overdue_tasks_count }} Overdue
              </span>
            </div>
            <div class="text-xs text-slate-600 dark:text-slate-400 space-y-2">
              <p class="leading-relaxed">
                Tugas aktif yang sedang dikerjakan atau menunggu approval dalam Kanban Yayasan.
              </p>
              <NuxtLink to="/dashboard/internal/tugas">
                <Button label="Buka Kanban Tugas" icon="pi pi-external-link" size="small" outlined class="w-full !text-xs !py-1" />
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Tutup" severity="secondary" size="small" @click="detailModalVisible = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'dashboard'
})

const api = useApi()

// States
const loading = ref(false)
const activeMainTab = ref<'radar' | 'teams'>('radar')
const displayMode = ref<'table' | 'cards'>('table')
const searchQuery = ref('')
const selectedUnitId = ref<number | null>(null)
const selectedStatusFilter = ref<string>('')
const detailModalVisible = ref(false)
const selectedEmployee = ref<any | null>(null)

const summary = ref({
  total: 0,
  overload: 0,
  padat: 0,
  optimal: 0,
  underload: 0
})

const employees = ref<any[]>([])
const activeTeams = ref<any[]>([])

const unitOptions = ref([
  { id: 1, name: 'Yayasan' },
  { id: 2, name: 'RA' },
  { id: 3, name: 'SDIT' },
  { id: 4, name: 'SMPIT' },
])

const statusOptions = [
  { label: 'Semua Status Beban', value: '' },
  { label: '🔴 Risiko Burnout / Overload', value: 'overload' },
  { label: '🟡 Beban Padat', value: 'padat' },
  { label: '🟢 Ideal & Seimbang', value: 'optimal' },
  { label: '⚪ Pasif / Siap Ditugaskan', value: 'underload' },
]

async function fetchRadarData() {
  loading.value = true
  try {
    const res = await api.get<any>('/sdm/workload-radar')
    if (res) {
      summary.value = res.summary || summary.value
      employees.value = res.employees || []
      activeTeams.value = res.active_teams || []
    }
  } catch (e) {
    console.error('Failed to fetch workload radar data', e)
  } finally {
    loading.value = false
  }
}

const filteredEmployees = computed(() => {
  return employees.value.filter(emp => {
    // Search
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchName = emp.nama_lengkap?.toLowerCase().includes(q)
      const matchNik = emp.nik?.toLowerCase().includes(q)
      const matchPos = emp.position?.toLowerCase().includes(q)
      if (!matchName && !matchNik && !matchPos) return false
    }

    // Unit filter
    if (selectedUnitId.value && emp.unit_id !== selectedUnitId.value) {
      return false
    }

    // Status filter
    if (selectedStatusFilter.value && emp.workload_status !== selectedStatusFilter.value) {
      return false
    }

    return true
  })
})

function filterByStatus(status: string) {
  selectedStatusFilter.value = status
}

function openEmployeeDetail(emp: any) {
  selectedEmployee.value = emp
  detailModalVisible.value = true
}

function getStatusBadgeClass(status: string) {
  switch (status) {
    case 'overload':
      return 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-800'
    case 'padat':
      return 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
    case 'optimal':
      return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
    default:
      return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
  }
}

function getProgressBarClass(score: number) {
  if (score >= 80) return 'bg-rose-500'
  if (score >= 60) return 'bg-amber-500'
  if (score >= 35) return 'bg-emerald-500'
  return 'bg-sky-400'
}

function getScoreTextClass(score: number) {
  if (score >= 80) return 'text-rose-600 dark:text-rose-400'
  if (score >= 60) return 'text-amber-600 dark:text-amber-400'
  if (score >= 35) return 'text-emerald-600 dark:text-emerald-400'
  return 'text-sky-600 dark:text-sky-400'
}

function formatDate(val: string) {
  if (!val) return ''
  try {
    return new Date(val).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return val
  }
}

onMounted(() => {
  fetchRadarData()
})
</script>
