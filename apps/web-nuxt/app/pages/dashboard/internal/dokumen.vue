<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Pusat Unduhan & Dokumen</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola dokumen SK, SOP, Juknis, Lampiran Formulir, serta Riwayat Karir Pegawai.</p>
      </div>
      <div class="flex items-center gap-2 flex-wrap">
        <Button label="Upload Dokumen" icon="pi pi-upload" @click="openDialog()" />
        <Button label="+ SK Karir Pegawai" severity="secondary" icon="pi pi-user-plus" @click="openCareerSkDialog()" />
      </div>
    </div>

    <!-- Tab Navigasi Utama -->
    <div class="flex items-center gap-2 border-b border-slate-200 dark:border-slate-700 pb-3 flex-wrap">
      <button
        type="button"
        @click="activeViewTab = 'documents'"
        class="px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition inline-flex items-center gap-2"
        :class="activeViewTab === 'documents' ? 'bg-primary text-white shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'"
      >
        <i class="pi pi-folder-open text-xs"></i>
        <span>Semua Dokumen & SOP</span>
        <span class="px-1.5 py-0.5 rounded-full text-[10px]" :class="activeViewTab === 'documents' ? 'bg-white/20 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'">
          {{ documents.length }}
        </span>
      </button>

      <button
        type="button"
        @click="switchTab('career')"
        class="px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition inline-flex items-center gap-2"
        :class="activeViewTab === 'career' ? 'bg-primary text-white shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700'"
      >
        <i class="pi pi-id-card text-xs"></i>
        <span>Riwayat SK & Karir Pegawai</span>
        <span class="px-1.5 py-0.5 rounded-full text-[10px]" :class="activeViewTab === 'career' ? 'bg-white/20 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'">
          {{ careerList.length }}
        </span>
      </button>
    </div>

    <!-- TAB 1: SEMUA DOKUMEN & SOP -->
    <div v-show="activeViewTab === 'documents'" class="space-y-6">
      <!-- Quick Stats Cards (5 Indikator Kunci) -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
        <div class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold">
            <i class="pi pi-folder text-lg"></i>
          </div>
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Total Dokumen</div>
            <div class="text-xl font-bold text-slate-800 dark:text-white">{{ documents.length }}</div>
          </div>
        </div>

        <div class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
            <i class="pi pi-check-circle text-lg"></i>
          </div>
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Aktif & Tetap</div>
            <div class="text-xl font-bold text-emerald-600 dark:text-emerald-400">{{ activeDocCount }}</div>
          </div>
        </div>

        <div class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center font-bold">
            <i class="pi pi-clock text-lg"></i>
          </div>
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Segera Berakhir</div>
            <div class="text-xl font-bold text-amber-600 dark:text-amber-400">{{ expiringDocCount }}</div>
          </div>
        </div>

        <div class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 flex items-center justify-center font-bold">
            <i class="pi pi-exclamation-triangle text-lg"></i>
          </div>
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Kedaluwarsa</div>
            <div class="text-xl font-bold text-red-600 dark:text-red-400">{{ expiredDocCount }}</div>
          </div>
        </div>

        <!-- Card Potensi Duplikasi (Interaktif) -->
        <div 
          @click="openDuplicateDialog"
          class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border shadow-sm flex items-center gap-3 cursor-pointer transition group"
          :class="duplicateCount > 0 ? 'border-purple-300 dark:border-purple-700 bg-purple-50/30 dark:bg-purple-950/20 hover:border-purple-400' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300'"
        >
          <div 
            class="w-10 h-10 rounded-lg flex items-center justify-center font-bold transition"
            :class="duplicateCount > 0 ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/50 dark:text-purple-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400'"
          >
            <i class="pi pi-copy text-lg"></i>
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center justify-between">
              <span>Potensi Duplikat</span>
              <span v-if="duplicateCount > 0" class="text-[10px] text-purple-600 dark:text-purple-400 font-bold group-hover:underline">Tinjau &rarr;</span>
            </div>
            <div class="text-xl font-bold" :class="duplicateCount > 0 ? 'text-purple-600 dark:text-purple-400' : 'text-slate-700 dark:text-slate-300'">
              {{ duplicateCount }}
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="card">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <InputText v-model="searchQuery" placeholder="Cari nomor surat, judul, kata kunci, atau nama pegawai..." class="w-full" @input="fetchDocuments" />
          </div>
          <Select v-model="filterCategory" :options="allCategoryOptions" optionLabel="label" optionValue="value" placeholder="Semua Kategori" class="w-full md:w-48" @change="fetchDocuments" />
          <Select v-model="filterVisibility" :options="visibilityOptions" optionLabel="label" optionValue="value" placeholder="Semua Akses" class="w-full md:w-48" @change="fetchDocuments" />
        </div>
      </div>

      <!-- Documents Table -->
      <div class="card !p-0 overflow-hidden border border-slate-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 shadow-sm">
        <DataTable 
          :value="documents" 
          :loading="loading" 
          stripedRows 
          :rowHover="true" 
          responsiveLayout="scroll" 
          class="text-sm"
          sortMode="single"
          removableSort
        >
          <!-- Kolom Dokumen (Judul, Nomor, Versi, Lampiran, Pegawai, dan Tombol Keterangan) -->
          <Column field="title" header="Dokumen" sortable style="min-width: 310px">
            <template #body="{ data }">
              <div class="flex items-start gap-3 py-1.5">
                <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5" :class="getCategoryColor(data.category)">
                  <i :class="getCategoryIcon(data.category)" class="text-base"></i>
                </div>
                <div class="min-w-0 flex-1">
                  <!-- Baris 1: Judul Dokumen (Bisa diklik untuk preview) -->
                  <div class="flex items-center gap-1.5 flex-wrap">
                    <span 
                      @click="openPreviewDialog(data)" 
                      class="font-semibold text-slate-800 dark:text-white hover:text-primary cursor-pointer transition text-sm leading-snug" 
                      :title="'Klik untuk lihat pratinjau: ' + data.title"
                    >
                      {{ data.title }}
                    </span>
                    
                    <Tag :value="'v' + (data.version || '1.0')" severity="secondary" class="text-[10px] px-1 py-0" />

                    <!-- Badge Lampiran Formulir Pendukung -->
                    <button
                      v-if="data.attachments && data.attachments.length > 0"
                      type="button"
                      @click.stop="openPreviewDialog(data)"
                      class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 transition cursor-pointer"
                      :title="'Ada ' + data.attachments.length + ' berkas formulir pendukung'"
                    >
                      <i class="pi pi-paperclip text-[9px]"></i>
                      <span>{{ data.attachments.length }} Formulir</span>
                    </button>

                    <!-- Badge Kaitan Pegawai jika SK Karir -->
                    <span
                      v-if="data.employee_name"
                      class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-50 dark:bg-purple-950/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800"
                    >
                      <i class="pi pi-user text-[9px]"></i>
                      <span>{{ data.employee_name }}<span v-if="data.position_title"> ({{ data.position_title }})</span></span>
                    </span>
                  </div>

                  <!-- Baris 2: Nomor Surat, Info File, dan Tombol Keterangan Popover -->
                  <div class="flex items-center gap-2 text-xs text-slate-400 mt-1 flex-wrap">
                    <span v-if="data.document_number" class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-mono font-medium bg-slate-100 dark:bg-slate-700/60 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600">
                      <i class="pi pi-hashtag text-[9px] text-slate-400"></i>{{ data.document_number }}
                    </span>
                    
                    <span v-if="isGdriveLink(data.file_url)" class="text-blue-600 dark:text-blue-400 font-semibold inline-flex items-center gap-1 bg-blue-50 dark:bg-blue-950/40 px-1.5 py-0.5 rounded text-[11px]">
                      <i class="pi pi-external-link text-[10px]"></i> Google Drive
                    </span>
                    <span v-else class="text-[11px] text-slate-400 truncate max-w-[180px]" :title="data.file_name">
                      {{ data.file_name }} · {{ formatSize(data.file_size) }}
                    </span>

                    <!-- Tombol Popover Deskripsi/Keterangan -->
                    <button 
                      v-if="data.description"
                      type="button" 
                      @click="toggleDescPopover($event, data)"
                      @mouseenter="showDescPopover($event, data)"
                      @mouseleave="scheduleHideDescPopover"
                      class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-medium bg-slate-100 hover:bg-slate-200 dark:bg-slate-700/60 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition cursor-pointer"
                      title="Klik atau arahkan kursor untuk melihat deskripsi"
                    >
                      <i class="pi pi-info-circle text-[10px] text-primary"></i>
                      <span>Keterangan</span>
                    </button>
                  </div>
                </div>
              </div>
            </template>
          </Column>

          <!-- Kolom Kategori -->
          <Column field="category" header="Kategori" sortable style="min-width: 140px">
            <template #body="{ data }">
              <Tag :value="getCategoryLabel(data.category)" :severity="getCategorySeverity(data.category)" class="text-xs font-medium" />
            </template>
          </Column>

          <!-- Kolom Masa Berlaku, Umur Dokumen, dan Status Kadaluarsa -->
          <Column field="effective_timestamp" header="Masa Berlaku & Umur" sortable style="min-width: 200px">
            <template #body="{ data }">
              <div class="space-y-1 py-1">
                <div>
                  <span 
                    class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold"
                    :class="data.expiry_info.badgeClass"
                  >
                    <i :class="data.expiry_info.icon" class="text-[10px]"></i>
                    {{ data.expiry_info.label }}
                  </span>
                </div>

                <div class="flex items-center gap-1 text-xs text-slate-600 dark:text-slate-300 font-medium">
                  <i class="pi pi-hourglass text-[10px] text-primary"></i>
                  <span>Umur: <strong>{{ data.age_info.text }}</strong></span>
                </div>

                <div class="text-[11px] text-slate-400">
                  {{ data.expiry_info.subtext }}
                </div>
              </div>
            </template>
          </Column>

          <!-- Kolom Akses & Visibilitas -->
          <Column field="visibility" header="Akses" sortable style="min-width: 130px">
            <template #body="{ data }">
              <div class="space-y-1 py-1">
                <Tag 
                  :value="data.visibility === 'public' ? 'Publik' : formatTargetUnits(data.target_units)" 
                  :severity="data.visibility === 'public' ? 'success' : 'info'" 
                  class="text-xs font-semibold"
                />
                <div v-if="data.is_confidential" class="text-[10px] text-red-600 dark:text-red-400 font-bold flex items-center gap-1">
                  <i class="pi pi-lock text-[9px]"></i> Pimpinan & TU
                </div>
              </div>
            </template>
          </Column>

          <!-- Kolom Diupload -->
          <Column field="created_timestamp" header="Diupload" sortable style="min-width: 140px">
            <template #body="{ data }">
              <div class="py-1">
                <p class="text-xs text-slate-600 dark:text-slate-300 font-medium truncate max-w-[130px]" :title="data.uploader_name || '-'">
                  {{ data.uploader_name || '-' }}
                </p>
                <p class="text-xs text-slate-400">{{ formatDate(data.created_at) }}</p>
              </div>
            </template>
          </Column>

          <!-- Kolom Aksi -->
          <Column header="Aksi" style="min-width: 190px">
            <template #body="{ data }">
              <div class="flex items-center gap-1">
                <button @click="openPreviewDialog(data)" class="p-1.5 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 rounded-lg transition" title="Lihat Pratinjau">
                  <i class="pi pi-eye text-sm"></i>
                </button>
                <a :href="data.file_url" target="_blank" download class="p-1.5 text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition" title="Unduh File">
                  <i class="pi pi-download text-sm"></i>
                </a>
                <button @click="openHistoryDialog(data)" class="p-1.5 text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-lg transition" title="Riwayat Versi">
                  <i class="pi pi-history text-sm"></i>
                </button>
                <button @click="openDialog(data)" class="p-1.5 text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/30 rounded-lg transition" title="Edit">
                  <i class="pi pi-pencil text-sm"></i>
                </button>
                <button @click="deleteDoc(data)" class="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition" title="Hapus">
                  <i class="pi pi-trash text-sm"></i>
                </button>
              </div>
            </template>
          </Column>

          <template #empty>
            <div class="text-center py-12 text-slate-400">
              <i class="pi pi-folder-open text-4xl mb-3 block opacity-50"></i>
              <p class="font-medium">Belum ada dokumen yang sesuai kriteria.</p>
              <p class="text-xs text-slate-400 mt-1">Klik tombol "Upload Dokumen" untuk menambahkan berkas baru.</p>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- TAB 2: RIWAYAT SK & KARIR PEGAWAI -->
    <div v-show="activeViewTab === 'career'" class="space-y-6">
      <!-- Career Summary Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        <div class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center font-bold">
            <i class="pi pi-users text-lg"></i>
          </div>
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Pegawai Terdata SK</div>
            <div class="text-xl font-bold text-slate-800 dark:text-white">{{ careerList.length }} Orang</div>
          </div>
        </div>

        <div class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold">
            <i class="pi pi-check-circle text-lg"></i>
          </div>
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Aktif Menjabat</div>
            <div class="text-xl font-bold text-emerald-600 dark:text-emerald-400">{{ activeCareerCount }} Orang</div>
          </div>
        </div>

        <div class="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold">
            <i class="pi pi-file-o text-lg"></i>
          </div>
          <div>
            <div class="text-xs text-slate-500 dark:text-slate-400 font-medium">Total SK Karir Terbit</div>
            <div class="text-xl font-bold text-blue-600 dark:text-blue-400">{{ totalCareerSkCount }} Berkas SK</div>
          </div>
        </div>
      </div>

      <!-- Filters & Search for Career -->
      <div class="card">
        <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div class="flex-1 w-full">
            <InputText v-model="careerSearch" placeholder="Cari nama pegawai/guru, NIK, jabatan, atau nomor SK..." class="w-full" @input="fetchCareerHistory" />
          </div>
          <div class="flex items-center gap-2 w-full md:w-auto">
            <Select v-model="careerSkTypeFilter" :options="allSkTypeFilterOptions" optionLabel="label" optionValue="value" placeholder="Semua Jenis SK" class="w-full md:w-56" @change="fetchCareerHistory" />
            <Button label="+ SK Pegawai" icon="pi pi-plus" @click="openCareerSkDialog()" />
          </div>
        </div>
      </div>

      <!-- Career Dossiers List -->
      <div v-if="loadingCareer" class="text-center py-16 text-slate-400">
        <i class="pi pi-spin pi-spinner text-3xl mb-3 text-primary"></i>
        <p class="font-medium">Memuat berkas riwayat SK & karir pegawai...</p>
      </div>

      <div v-else-if="careerList.length === 0" class="card text-center py-16 text-slate-400">
        <div class="w-14 h-14 bg-slate-100 dark:bg-slate-800 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-3">
          <i class="pi pi-id-card text-2xl"></i>
        </div>
        <h3 class="text-base font-bold text-slate-700 dark:text-white">Tidak Ada Riwayat SK Pegawai Ditemukan</h3>
        <p class="text-xs text-slate-400 mt-1 max-w-md mx-auto">
          Belum ada SK pengangkatan/promosi/mutasi yang ditautkan ke nama pegawai yang dicari.
        </p>
        <div class="mt-4">
          <Button label="Buat SK Pegawai Baru" icon="pi pi-plus" @click="openCareerSkDialog()" />
        </div>
      </div>

      <div v-else class="space-y-6">
        <div
          v-for="emp in careerList"
          :key="emp.employee_name"
          class="border border-slate-200 dark:border-slate-700 rounded-2xl bg-white dark:bg-slate-800 shadow-sm overflow-hidden"
        >
          <!-- Employee Dossier Header -->
          <div class="p-4 sm:p-5 bg-gradient-to-r from-slate-50 to-white dark:from-slate-800/90 dark:to-slate-800 border-b border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div class="flex items-center gap-3.5">
              <!-- Avatar Initials -->
              <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-primary to-indigo-500 text-white flex items-center justify-center font-bold text-base shadow-sm shrink-0">
                {{ getInitials(emp.employee_name) }}
              </div>
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <h3 class="text-base font-bold text-slate-800 dark:text-white">{{ emp.employee_name }}</h3>
                  <Tag
                    :value="emp.is_currently_active ? 'Aktif Menjabat' : 'Non-Aktif / Pensiun'"
                    :severity="emp.is_currently_active ? 'success' : 'secondary'"
                    class="text-[11px]"
                  />
                  <Tag v-if="emp.unit" :value="emp.unit" severity="info" class="text-[11px]" />
                </div>
                <div class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-2 flex-wrap">
                  <span v-if="emp.current_position">
                    Jabatan Saat Ini: <strong class="text-slate-700 dark:text-slate-200">{{ emp.current_position }}</strong>
                  </span>
                  <span v-if="emp.first_appointment_date">
                    &bull; Mulai Bekerja: {{ formatDate(emp.first_appointment_date) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Right Side: Total Tenure Badge & Quick Add SK Button -->
            <div class="flex items-center gap-2 flex-wrap self-end sm:self-center">
              <div class="px-3 py-1.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300 text-xs font-semibold flex items-center gap-1.5 shadow-xs">
                <i class="pi pi-hourglass text-emerald-600"></i>
                <span>Masa Pengabdian: <strong>{{ emp.total_tenure || '-' }}</strong></span>
              </div>

              <Button
                label="+ Tambah SK"
                icon="pi pi-plus"
                size="small"
                severity="secondary"
                @click="openCareerSkDialog(emp)"
                title="Tambah SK baru untuk pegawai ini"
              />
            </div>
          </div>

          <!-- Chronological Career Timeline -->
          <div class="p-4 sm:p-6 bg-slate-50/40 dark:bg-slate-900/20">
            <div class="relative pl-6 sm:pl-8 border-l-2 border-indigo-200 dark:border-indigo-900/60 space-y-6">
              <div
                v-for="(item, idx) in emp.items"
                :key="item.id"
                class="relative group"
              >
                <!-- Timeline Node Dot -->
                <div
                  class="absolute -left-[31px] sm:-left-[39px] top-1.5 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shadow-xs border-2 border-white dark:border-slate-800"
                  :class="getSkTypeBadge(item.sk_type).badgeClass"
                >
                  <i :class="getSkTypeBadge(item.sk_type).icon" class="text-[11px]"></i>
                </div>

                <!-- Timeline Content Card -->
                <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-800/90 shadow-2xs hover:shadow-sm transition">
                  <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-700/60 pb-2.5 mb-2.5">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span
                        class="px-2 py-0.5 rounded text-[11px] font-bold border"
                        :class="getSkTypeBadge(item.sk_type).badgeClass"
                      >
                        {{ getSkTypeBadge(item.sk_type).label }}
                      </span>
                      <h4 class="font-bold text-sm text-slate-800 dark:text-white">
                        {{ item.position_title || 'Penetapan SK' }}
                      </h4>
                      <Tag
                        v-if="idx === 0 && emp.is_currently_active"
                        value="Jabatan Terakhir / Saat Ini"
                        severity="success"
                        class="text-[10px]"
                      />
                    </div>

                    <!-- Periode & Durasi -->
                    <div class="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2 flex-wrap">
                      <span class="inline-flex items-center gap-1 font-medium text-slate-700 dark:text-slate-300">
                        <i class="pi pi-calendar text-[10px] text-primary"></i>
                        {{ formatDate(item.term_start_date) }}
                        &rarr;
                        {{ item.term_end_date ? formatDate(item.term_end_date) : 'Sekarang / Tetap' }}
                      </span>
                      <span class="text-slate-400">
                        ({{ calculateTenure(item.term_start_date, item.term_end_date) }})
                      </span>
                    </div>
                  </div>

                  <!-- Document Reference & Description -->
                  <div class="text-xs text-slate-600 dark:text-slate-300 space-y-1.5">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span v-if="item.document_number" class="font-mono text-[11px] font-semibold bg-slate-100 dark:bg-slate-700/60 px-1.5 py-0.5 rounded text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600">
                        #{{ item.document_number }}
                      </span>
                      <span class="font-semibold text-slate-800 dark:text-white">{{ item.title }}</span>
                      <Tag :value="'v' + (item.version || '1.0')" severity="secondary" class="text-[10px]" />
                    </div>
                    <p v-if="item.description" class="text-slate-500 dark:text-slate-400 italic text-[11px]">
                      "{{ item.description }}"
                    </p>
                  </div>

                  <!-- Supporting Forms / Attachments (Lampiran Formulir) -->
                  <div v-if="item.attachments && item.attachments.length > 0" class="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-700/60">
                    <div class="text-[11px] font-bold text-slate-500 dark:text-slate-400 mb-1.5 flex items-center gap-1">
                      <i class="pi pi-paperclip text-[10px] text-emerald-600"></i>
                      <span>Berkas Lampiran & Formulir ({{ item.attachments.length }}):</span>
                    </div>
                    <div class="flex items-center gap-2 flex-wrap">
                      <a
                        v-for="(att, aIdx) in item.attachments"
                        :key="aIdx"
                        :href="att.file_url"
                        target="_blank"
                        download
                        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 font-medium transition border border-slate-200 dark:border-slate-600"
                        :title="'Unduh: ' + (att.title || att.file_name)"
                      >
                        <i :class="getAttachmentIcon(att.file_url)" class="text-xs"></i>
                        <span>{{ att.title || att.file_name }}</span>
                        <span v-if="att.file_size" class="text-[10px] text-slate-400">({{ formatSize(att.file_size) }})</span>
                      </a>
                    </div>
                  </div>

                  <!-- Action Buttons -->
                  <div class="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between flex-wrap gap-2">
                    <span class="text-[11px] text-slate-400">
                      Diupload: {{ formatDate(item.created_at) }}
                    </span>
                    <div class="flex items-center gap-1.5">
                      <button
                        type="button"
                        @click="openPreviewDialog(item)"
                        class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-50 hover:bg-emerald-100 dark:bg-emerald-950/40 dark:hover:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 transition inline-flex items-center gap-1"
                      >
                        <i class="pi pi-eye text-[11px]"></i> Pratinjau SK
                      </button>
                      <a
                        :href="item.file_url"
                        target="_blank"
                        download
                        class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/40 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 transition inline-flex items-center gap-1"
                      >
                        <i class="pi pi-download text-[11px]"></i> Unduh
                      </a>
                      <button
                        type="button"
                        @click="openDialog(item)"
                        class="px-2 py-1 rounded-lg text-xs font-semibold text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-950/40 transition inline-flex items-center gap-1"
                      >
                        <i class="pi pi-pencil text-[11px]"></i> Edit
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Dynamic Floating Popover untuk Deskripsi Dokumen -->
    <Popover ref="descPopover" class="!shadow-2xl !rounded-xl !border !border-slate-200 dark:!border-slate-700 !bg-white dark:!bg-slate-900" @mouseenter="cancelHideDescPopover" @mouseleave="hideDescPopover">
      <div v-if="hoveredDoc" class="p-3.5 max-w-sm">
        <div class="flex items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-2 mb-2">
          <div class="flex items-center gap-1.5 font-bold text-xs text-slate-800 dark:text-slate-100">
            <i class="pi pi-align-left text-primary"></i>
            <span>Deskripsi / Keterangan</span>
          </div>
          <Tag :value="'v' + (hoveredDoc.version || '1.0')" severity="secondary" class="text-[10px]" />
        </div>

        <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
          {{ hoveredDoc.description }}
        </p>

        <div v-if="hoveredDoc.document_number || hoveredDoc.effective_date" class="mt-2.5 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
          <span v-if="hoveredDoc.document_number" class="font-mono font-medium text-slate-600 dark:text-slate-400">#{{ hoveredDoc.document_number }}</span>
          <span v-if="hoveredDoc.effective_date">Berlaku: {{ formatDate(hoveredDoc.effective_date) }}</span>
        </div>
      </div>
    </Popover>

    <!-- Upload/Edit Dialog -->
    <Dialog v-model:visible="dialogVisible" :header="editingDoc ? 'Edit Dokumen' : 'Upload Dokumen Baru'" modal class="w-full max-w-2xl" :breakpoints="{ '960px': '90vw', '640px': '98vw' }">
      <div class="space-y-4 pt-2 max-h-[75vh] overflow-y-auto pr-1">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium text-sm">Nomor Surat / SK (opsional)</label>
            <InputText v-model="form.document_number" placeholder="Contoh: 18/SK/Y-AS/V/2025" @input="onTitleOrNumberInput" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium text-sm">Kategori *</label>
            <Select v-model="form.category" :options="categoryOptions" optionLabel="label" optionValue="value" placeholder="Pilih kategori" class="w-full" @change="onCategoryChange" />
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Judul Dokumen *</label>
          <InputText v-model="form.title" placeholder="Contoh: Ketentuan Jumlah Jam Pelajaran (JP)" @input="onTitleOrNumberInput" />
        </div>

        <!-- Banner Deteksi Kemiripan Real-time saat Upload -->
        <div v-if="duplicateWarning" class="p-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-300 dark:border-amber-700 rounded-xl text-xs space-y-2">
          <div class="flex items-start gap-2 text-amber-800 dark:text-amber-200">
            <i class="pi pi-exclamation-triangle text-base text-amber-500 mt-0.5 shrink-0"></i>
            <div>
              <strong class="font-bold">Perhatian — Terdeteksi Dokumen Serupa:</strong>
              <div class="mt-0.5 font-medium">
                "{{ duplicateWarning.match.title }}"
                <span v-if="duplicateWarning.match.document_number">({{ duplicateWarning.match.document_number }})</span>
                — Versi {{ duplicateWarning.match.version }}
              </div>
              <div class="text-[11px] text-amber-600 dark:text-amber-400 mt-0.5">
                Pemicu: {{ duplicateWarning.match.reason }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 pt-1 border-t border-amber-200 dark:border-amber-800">
            <button 
              type="button" 
              @click="applyAsRevision(duplicateWarning.match)"
              class="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-md text-xs font-semibold inline-flex items-center gap-1 transition"
            >
              <i class="pi pi-history"></i> Jadikan Revisi dari Dokumen Ini
            </button>
            <button 
              type="button" 
              @click="duplicateWarning = null"
              class="text-amber-700 dark:text-amber-300 hover:underline text-xs"
            >
              Bukan, ini dokumen baru
            </button>
          </div>
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-medium text-sm">Deskripsi / Keterangan Singkat (opsional)</label>
          <Textarea v-model="form.description" rows="2" placeholder="Keterangan singkat tentang dokumen ini (akan tampil sebagai popover saat kursor diarahkan ke dokumen)..." />
        </div>

        <!-- SEKSI 1: KAITAN KARIR PEGAWAI & SK JABATAN -->
        <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/50 space-y-3">
          <div class="flex items-center gap-2">
            <Checkbox v-model="form.is_career_sk" :binary="true" inputId="is-career-check" />
            <label for="is-career-check" class="cursor-pointer text-xs font-bold text-slate-700 dark:text-slate-200 select-none flex items-center gap-1.5">
              <i class="pi pi-id-card text-purple-500"></i> Tautkan ke Riwayat Karir & Jabatan Pegawai
            </label>
          </div>
          <p class="text-[11px] text-slate-500 dark:text-slate-400 pl-6">
            Centang jika dokumen ini merupakan SK Pengangkatan, Mutasi, Promosi, Pemberhentian, atau Tugas Tambahan untuk staf/guru tertentu.
          </p>

          <div v-if="form.is_career_sk" class="pt-2 border-t border-slate-200 dark:border-slate-700 space-y-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <!-- Dropdown Pegawai Terdaftar -->
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-xs">Pilih Pegawai dari Sistem (opsional)</label>
                <Select
                  v-model="selectedUserObj"
                  :options="usersBrief"
                  optionLabel="full_name"
                  filter
                  placeholder="Cari nama pegawai/guru..."
                  class="w-full text-xs"
                  @change="onUserSelected"
                  showClear
                >
                  <template #option="{ option }">
                    <div class="flex items-center justify-between text-xs w-full">
                      <span class="font-medium">{{ option.full_name }}</span>
                      <span class="text-[10px] text-slate-400">({{ option.unit || option.role || '-' }})</span>
                    </div>
                  </template>
                </Select>
              </div>

              <!-- Input Nama Lengkap Pegawai -->
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-xs">Nama Lengkap Pegawai *</label>
                <InputText v-model="form.employee_name" placeholder="Contoh: Siti Yeni, S.Pd" class="w-full text-sm" />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <!-- Jenis SK Karir -->
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-xs">Jenis Penetapan SK *</label>
                <Select
                  v-model="form.sk_type"
                  :options="skTypeOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Pilih jenis SK"
                  class="w-full text-xs"
                />
              </div>

              <!-- Nama Posisi / Jabatan -->
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-xs">Nama Jabatan / Posisi *</label>
                <InputText v-model="form.position_title" placeholder="Contoh: Wakil Kurikulum / Kepala Sekolah" class="w-full text-sm" />
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <!-- TMT Mulai Menjabat -->
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-xs">TMT Mulai Menjabat (Berlaku SK) *</label>
                <InputText v-model="form.term_start_date" type="date" class="w-full text-sm" />
              </div>

              <!-- Selesai Menjabat -->
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-xs">Selesai Menjabat (opsional)</label>
                <InputText v-model="form.term_end_date" type="date" class="w-full text-sm" />
                <span class="text-[10px] text-slate-400">Kosongkan jika aktif sampai sekarang / masa jabatan tetap.</span>
              </div>
            </div>
          </div>
        </div>

        <!-- SEKSI 2: BERKAS LAMPIRAN & FORMULIR PENDUKUNG -->
        <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/50 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                <i class="pi pi-paperclip text-emerald-600"></i>
                <span>Berkas Lampiran & Formulir Pendukung</span>
                <Tag v-if="form.attachments.length > 0" :value="form.attachments.length + ' Berkas'" severity="success" class="text-[10px]" />
              </div>
              <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                Lampirkan formulir yang harus diisi atau berkas turunan (contoh: Form Pengajuan Spanduk, Form Exit Clearance, dll).
              </p>
            </div>
            <Button
              type="button"
              label="+ Tambah Formulir"
              icon="pi pi-plus"
              size="small"
              severity="secondary"
              @click="addAttachmentRow"
            />
          </div>

          <!-- Hidden File Input for Attachment -->
          <input
            ref="attachmentFileInputRef"
            type="file"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar,.jpg,.jpeg,.png"
            class="hidden"
            @change="handleAttachmentFileSelect"
          />

          <div v-if="form.attachments.length === 0" class="text-center py-3 text-xs text-slate-400 border border-dashed border-slate-200 dark:border-slate-700 rounded-lg">
            Belum ada berkas formulir dilampirkan. Klik <strong>"+ Tambah Formulir"</strong> jika SOP/SK ini membutuhkan lampiran form.
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="(att, idx) in form.attachments"
              :key="idx"
              class="p-2.5 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2"
            >
              <div class="flex-1 flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                <InputText
                  v-model="att.title"
                  placeholder="Judul Formulir (contoh: Form Exit Clearance)"
                  class="w-full sm:w-1/2 text-xs"
                />

                <div v-if="att.file_url" class="flex-1 flex items-center gap-2 text-xs bg-slate-50 dark:bg-slate-700/60 p-1.5 rounded border border-slate-200 dark:border-slate-600 min-w-0">
                  <i :class="getAttachmentIcon(att.file_url)" class="text-sm shrink-0"></i>
                  <span class="truncate text-slate-700 dark:text-slate-200 text-xs">{{ att.file_name }}</span>
                  <span v-if="att.file_size" class="text-[10px] text-slate-400 shrink-0">({{ formatSize(att.file_size) }})</span>
                </div>

                <div v-else class="flex-1 flex items-center gap-2">
                  <button
                    type="button"
                    :disabled="att.uploading"
                    @click="triggerAttachmentUpload(idx)"
                    class="px-2.5 py-1.5 rounded bg-emerald-50 hover:bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 text-xs font-semibold inline-flex items-center gap-1 transition shrink-0"
                  >
                    <i :class="att.uploading ? 'pi pi-spin pi-spinner' : 'pi pi-upload'"></i>
                    <span>{{ att.uploading ? 'Mengupload...' : 'Pilih File Formulir' }}</span>
                  </button>
                  <InputText
                    v-model="att.file_url"
                    placeholder="Atau tautan URL / Google Drive..."
                    class="flex-1 text-xs"
                  />
                </div>
              </div>

              <button
                type="button"
                @click="removeAttachmentRow(idx)"
                class="text-red-500 hover:text-red-700 p-1 self-end sm:self-center"
                title="Hapus Lampiran"
              >
                <i class="pi pi-trash text-sm"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- 2-Level Visibility & Target Unit Controls -->
        <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 space-y-3">
          <label class="font-bold text-sm text-slate-800 dark:text-white block">Tingkat Akses & Visibilitas Dokumen *</label>
          
          <div class="grid grid-cols-2 gap-3">
            <div 
              @click="form.visibility = 'public'"
              class="p-3 rounded-lg border cursor-pointer transition-all flex items-center gap-2"
              :class="form.visibility === 'public' ? 'border-green-500 bg-green-50 dark:bg-green-950/20 ring-1 ring-green-500 text-green-700 dark:text-green-300 font-medium' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 text-slate-600 dark:text-slate-300'"
            >
              <i class="pi pi-globe text-base text-green-500"></i>
              <div>
                <div class="text-xs font-bold">Publik (Terbuka)</div>
                <div class="text-[10px] opacity-75">Bisa diakses publik & ortu</div>
              </div>
            </div>

            <div 
              @click="form.visibility = 'internal'"
              class="p-3 rounded-lg border cursor-pointer transition-all flex items-center gap-2"
              :class="form.visibility === 'internal' ? 'border-primary bg-primary/5 ring-1 ring-primary text-primary font-medium' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 text-slate-600 dark:text-slate-300'"
            >
              <i class="pi pi-shield text-base text-primary"></i>
              <div>
                <div class="text-xs font-bold">Internal Yayasan</div>
                <div class="text-[10px] opacity-75">Hanya staf & guru login</div>
              </div>
            </div>
          </div>

          <div v-if="form.visibility === 'internal'" class="pt-2 border-t border-slate-200 dark:border-slate-700 space-y-3">
            <div>
              <div class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">Cakupan Unit Target:</div>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                <div class="flex items-center gap-2">
                  <Checkbox v-model="allUnitsSelected" :binary="true" inputId="unit-all" @change="toggleAllUnits" />
                  <label for="unit-all" class="cursor-pointer font-medium">Semua Unit (Global)</label>
                </div>
                <div v-for="u in unitCheckboxOptions" :key="u.code" class="flex items-center gap-2">
                  <Checkbox v-model="selectedUnits" :value="u.code" :inputId="'unit-' + u.code" :disabled="allUnitsSelected" />
                  <label :for="'unit-' + u.code" class="cursor-pointer text-slate-600 dark:text-slate-300" :class="{ 'opacity-50': allUnitsSelected }">
                    {{ u.name }}
                  </label>
                </div>
              </div>
            </div>

            <div class="pt-2 border-t border-slate-200/60 dark:border-slate-700/60">
              <div class="flex items-start gap-2">
                <Checkbox v-model="form.is_confidential" :binary="true" inputId="confidential-check" />
                <label for="confidential-check" class="cursor-pointer">
                  <div class="text-xs font-bold text-red-600 dark:text-red-400 flex items-center gap-1">
                    <i class="pi pi-lock text-[10px]"></i> Dokumen Rahasia (Hanya Pimpinan & TU)
                  </div>
                  <div class="text-[10px] text-slate-400 mt-0.5">
                    Guru dan staf biasa di unit terkait tidak akan dapat melihat atau mengunduh dokumen ini.
                  </div>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Versi & Masa Berlaku -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium text-sm">Versi Dokumen</label>
            <InputText v-model="form.version" placeholder="Contoh: 1.0 atau 2026.1" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium text-sm">Tanggal Mulai Berlaku (opsional)</label>
            <InputText v-model="form.effective_date" type="date" class="w-full text-sm" />
          </div>
        </div>

        <!-- Opsi Checkbox Masa Berlaku / Tanggal Berakhir SK/SOP -->
        <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/50 space-y-3">
          <div class="flex items-center gap-2">
            <Checkbox v-model="form.has_expired_date" :binary="true" inputId="has-expired-check" @change="onExpiredCheckboxChange" />
            <label for="has-expired-check" class="cursor-pointer text-xs font-semibold text-slate-700 dark:text-slate-200 select-none flex items-center gap-1.5">
              <i class="pi pi-calendar-times text-amber-500"></i> Dokumen memiliki masa berlaku / tanggal berakhir
            </label>
          </div>

          <div v-if="form.has_expired_date" class="pt-2 border-t border-slate-200 dark:border-slate-700 space-y-2">
            <label class="font-medium text-xs text-slate-700 dark:text-slate-300">
              Pilih Tanggal, Bulan, dan Tahun Berakhirnya SOP/SK/Juknis *
            </label>
            <InputText v-model="form.expired_date" type="date" class="w-full text-sm" />
            <p class="text-[11px] text-slate-500 dark:text-slate-400">
              Sistem akan memantau umur dokumen dan menampilkan indikator peringatan otomatis saat masa berlaku mendekati habis atau sudah kedaluwarsa.
            </p>
          </div>
        </div>

        <div class="flex flex-col gap-2" v-if="!editingDoc && documents.length > 0">
          <label class="font-medium text-sm">Revisi dari Dokumen Sebelumnya (opsional)</label>
          <Select v-model="form.replaces_id" :options="replacesOptions" optionLabel="title" optionValue="id" placeholder="Pilih jika merupakan revisi/update dokumen lama" showClear class="w-full" />
          <p class="text-xs text-slate-400">Pilih dokumen lama jika upload ini adalah revisi atau versi baru.</p>
        </div>

        <!-- File Source Switcher: Upload Berkas vs Link Google Drive -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <label class="font-medium text-sm">Sumber Dokumen Utama *</label>
            <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg text-xs">
              <button
                type="button"
                @click="fileSourceMode = 'upload'"
                class="px-2.5 py-1 rounded-md transition font-medium"
                :class="fileSourceMode === 'upload' ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-800'"
              >
                <i class="pi pi-upload mr-1"></i> Upload File
              </button>
              <button
                type="button"
                @click="fileSourceMode = 'gdrive'"
                class="px-2.5 py-1 rounded-md transition font-medium"
                :class="fileSourceMode === 'gdrive' ? 'bg-white dark:bg-slate-700 text-primary shadow-sm' : 'text-slate-500 hover:text-slate-800'"
              >
                <i class="pi pi-external-link mr-1"></i> Link GDrive
              </button>
            </div>
          </div>

          <!-- Mode 1: Upload File Fisik -->
          <div v-if="fileSourceMode === 'upload'">
            <div v-if="form.file_url && !isGdriveLink(form.file_url)" class="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <i class="pi pi-file text-green-500 text-xl"></i>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-green-700 dark:text-green-400 truncate">{{ form.file_name }}</p>
                <p class="text-xs text-green-500">{{ formatSize(form.file_size) }}</p>
              </div>
              <button @click="clearFile" class="text-red-500 hover:text-red-700 p-1">
                <i class="pi pi-times"></i>
              </button>
            </div>

            <div v-else class="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-6 text-center hover:border-primary transition cursor-pointer" @click="triggerFileInput" @drop.prevent="handleDrop" @dragover.prevent>
              <i class="pi pi-cloud-upload text-3xl text-slate-400 mb-2"></i>
              <p class="text-sm text-slate-500">Klik untuk upload atau drag & drop</p>
              <p class="text-xs text-slate-400 mt-1">PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, ZIP (maks 10MB)</p>
            </div>
            <input ref="fileInputRef" type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar,.jpg,.jpeg,.png" class="hidden" @change="handleFileSelect" />
          </div>

          <!-- Mode 2: Link Google Drive -->
          <div v-else class="space-y-2">
            <div class="relative w-full">
              <i class="pi pi-link absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
              <InputText 
                v-model="gdriveInputUrl" 
                placeholder="https://drive.google.com/file/d/.../view" 
                class="w-full !pl-9"
                @input="handleGdriveInput"
              />
            </div>
            <div class="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800 text-xs text-blue-700 dark:text-blue-300 flex items-start gap-2">
              <i class="pi pi-info-circle text-blue-500 mt-0.5 shrink-0"></i>
              <div>
                <strong>Hemat Storage:</strong> Dokumen tidak diunggah ke server, melainkan langsung ditautkan ke Google Drive Yayasan. Pastikan setelan berbagi di Drive adalah <em>"Siapa saja yang memiliki link dapat melihat"</em>.
              </div>
            </div>
          </div>
        </div>

        <div v-if="uploadProgress > 0 && uploadProgress < 100" class="w-full bg-slate-200 rounded-full h-2">
          <div class="bg-primary h-2 rounded-full transition-all" :style="{ width: uploadProgress + '%' }"></div>
        </div>
      </div>

      <template #footer>
        <Button label="Batal" severity="secondary" @click="dialogVisible = false" />
        <Button :label="editingDoc ? 'Simpan' : 'Upload'" icon="pi pi-save" :loading="saving" @click="saveDocument" :disabled="!form.title || !form.file_url || !form.category" />
      </template>
    </Dialog>

    <!-- History Dialog -->
    <Dialog v-model:visible="historyDialogVisible" header="Riwayat Versi Dokumen" modal class="w-full max-w-lg">
      <div v-if="loadingHistory" class="text-center py-6 text-slate-400">
        <i class="pi pi-spin pi-spinner text-2xl mb-2"></i>
        <p>Memuat riwayat versi...</p>
      </div>
      <div v-else-if="documentHistory.length === 0" class="text-center py-6 text-slate-400">
        Belum ada riwayat versi untuk dokumen ini.
      </div>
      <div v-else class="space-y-3 py-2 max-h-96 overflow-y-auto">
        <div v-for="item in documentHistory" :key="item.id" class="p-3 rounded-lg border flex items-center justify-between"
          :class="item.is_current ? 'border-primary bg-primary/5 dark:bg-primary/10' : 'border-slate-200 dark:border-slate-700'">
          <div class="flex-1 pr-3">
            <div class="flex items-center gap-2 flex-wrap">
              <span v-if="item.document_number" class="text-[11px] font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                #{{ item.document_number }}
              </span>
              <span class="font-bold text-sm text-slate-800 dark:text-white">{{ item.title }}</span>
              <Tag :value="'v' + item.version" :severity="item.is_current ? 'success' : 'secondary'" class="text-xs" />
              <span v-if="item.is_current" class="text-[10px] text-primary font-semibold">(Versi Ini)</span>
            </div>
            <div class="text-xs text-slate-400 mt-1 flex flex-wrap gap-2">
              <span v-if="item.effective_date">Berlaku: {{ formatDate(item.effective_date) }}</span>
              <span v-if="item.expired_date" class="text-amber-600 dark:text-amber-400">Berakhir: {{ formatDate(item.expired_date) }}</span>
              <span>Diupload: {{ formatDate(item.created_at) }}</span>
              <span v-if="item.uploader_name">Oleh: {{ item.uploader_name }}</span>
            </div>
          </div>
          <div class="flex items-center gap-1 flex-shrink-0">
            <button @click="openPreviewDialog(item)" class="p-2 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/30 rounded-lg transition" title="Lihat Versi Ini">
              <i class="pi pi-eye"></i>
            </button>
            <a :href="item.file_url" target="_blank" download class="p-2 text-primary hover:bg-primary/10 rounded-lg" title="Unduh Versi Ini">
              <i class="pi pi-download"></i>
            </a>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Preview Document Dialog -->
    <Dialog v-model:visible="previewDialogVisible" :header="previewDoc?.title || 'Pratinjau Dokumen'" modal class="w-full max-w-5xl" :breakpoints="{ '960px': '90vw', '640px': '98vw' }">
      <div v-if="previewDoc" class="space-y-3">
        <!-- Info Bar -->
        <div class="flex items-center justify-between flex-wrap gap-2 p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-700 text-xs">
          <div class="flex items-center gap-2 flex-wrap">
            <span v-if="previewDoc.document_number" class="font-mono font-bold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-700 px-2 py-1 rounded border border-slate-200 dark:border-slate-600">
              #{{ previewDoc.document_number }}
            </span>
            <Tag :value="'v' + (previewDoc.version || '1.0')" severity="secondary" />
            <Tag :value="getCategoryLabel(previewDoc.category)" :severity="getCategorySeverity(previewDoc.category)" />
            
            <span v-if="previewDoc.effective_date" class="text-slate-600 dark:text-slate-300">
              Mulai: {{ formatDate(previewDoc.effective_date) }}
            </span>
            <span v-if="previewDoc.age_info" class="text-primary font-medium">
              (Umur: {{ previewDoc.age_info.text }})
            </span>
            <span v-if="previewDoc.expired_date" class="text-amber-600 dark:text-amber-400 font-semibold">
              · s/d {{ formatDate(previewDoc.expired_date) }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <a :href="previewDoc.file_url" target="_blank" class="px-2.5 py-1 text-xs rounded-md bg-white dark:bg-slate-700 hover:bg-slate-100 dark:hover:bg-slate-600 border border-slate-200 dark:border-slate-600 text-primary font-medium inline-flex items-center gap-1.5 transition">
              <i class="pi pi-external-link"></i> Buka di Tab Baru
            </a>
          </div>
        </div>

        <!-- Career SK Info Banner jika dokumen ditautkan ke Karir Pegawai -->
        <div v-if="previewDoc.employee_name" class="p-3 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-xl flex items-center justify-between text-xs">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/60 text-purple-700 dark:text-purple-300 flex items-center justify-center font-bold">
              <i class="pi pi-id-card"></i>
            </div>
            <div>
              <div class="font-bold text-slate-800 dark:text-white">SK Terkait Pegawai: {{ previewDoc.employee_name }}</div>
              <div class="text-slate-500 dark:text-slate-400">
                {{ getSkTypeBadge(previewDoc.sk_type).label }} &bull; Jabatan: <strong>{{ previewDoc.position_title || '-' }}</strong>
                <span v-if="previewDoc.term_start_date"> &bull; Periode: {{ formatDate(previewDoc.term_start_date) }} s/d {{ previewDoc.term_end_date ? formatDate(previewDoc.term_end_date) : 'Sekarang / Tetap' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Berkas Lampiran & Formulir Pendukung (Jika Ada) -->
        <div v-if="previewDoc.attachments && previewDoc.attachments.length > 0" class="p-3 bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 rounded-xl space-y-2">
          <div class="flex items-center justify-between">
            <div class="font-bold text-xs text-emerald-800 dark:text-emerald-300 flex items-center gap-1.5">
              <i class="pi pi-paperclip text-sm"></i>
              <span>Berkas Lampiran & Formulir Pendukung ({{ previewDoc.attachments.length }})</span>
            </div>
            <span class="text-[11px] text-slate-400">Dapat diunduh terpisah untuk pengisian formulir</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div
              v-for="(att, idx) in previewDoc.attachments"
              :key="idx"
              class="p-2.5 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 flex items-center justify-between gap-2"
            >
              <div class="flex items-center gap-2 min-w-0">
                <i :class="getAttachmentIcon(att.file_url)" class="text-lg shrink-0"></i>
                <div class="min-w-0">
                  <p class="text-xs font-semibold text-slate-800 dark:text-white truncate">{{ att.title || att.file_name }}</p>
                  <p class="text-[10px] text-slate-400 truncate">{{ att.file_name }} <span v-if="att.file_size">· {{ formatSize(att.file_size) }}</span></p>
                </div>
              </div>
              <a
                :href="att.file_url"
                target="_blank"
                download
                class="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold inline-flex items-center gap-1 shrink-0 transition"
              >
                <i class="pi pi-download text-[10px]"></i> Unduh
              </a>
            </div>
          </div>
        </div>

        <!-- Embedded Viewer Container -->
        <div class="bg-slate-100 dark:bg-slate-900 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 min-h-[60vh] flex items-center justify-center">
          <!-- Mode 1: Google Drive Link -->
          <iframe 
            v-if="isGdriveLink(previewDoc.file_url)" 
            :src="getGdrivePreviewUrl(previewDoc.file_url)" 
            class="w-full h-[68vh] border-0" 
            allow="autoplay"
          ></iframe>

          <!-- Mode 2: Image File -->
          <div v-else-if="isImageFile(previewDoc.file_url)" class="p-4 text-center max-h-[68vh] overflow-auto w-full">
            <img :src="previewDoc.file_url" :alt="previewDoc.title" class="max-h-[66vh] max-w-full mx-auto object-contain rounded-lg shadow-sm" />
          </div>

          <!-- Mode 3: PDF File -->
          <iframe 
            v-else-if="isPdfFile(previewDoc.file_url)" 
            :src="previewDoc.file_url" 
            class="w-full h-[68vh] border-0"
          ></iframe>

          <!-- Mode 4: Other Docs (Word/Excel/dll) via Google Docs Viewer -->
          <iframe 
            v-else 
            :src="'https://docs.google.com/viewer?url=' + encodeURIComponent(previewDoc.file_url) + '&embedded=true'" 
            class="w-full h-[68vh] border-0"
          ></iframe>
        </div>
      </div>
      <template #footer>
        <div class="flex items-center justify-between w-full">
          <p class="text-xs text-slate-400">Tekan ESC atau tombol Tutup untuk kembali.</p>
          <div class="flex items-center gap-2">
            <Button label="Tutup" severity="secondary" @click="previewDialogVisible = false" />
            <a v-if="previewDoc?.file_url" :href="previewDoc.file_url" target="_blank" download class="p-button p-component p-button-primary inline-flex items-center gap-1 text-sm px-3 py-2 rounded-lg">
              <i class="pi pi-download"></i> Unduh File Utama
            </a>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Dialog Audit & Resolusi Potensi Duplikasi Dokumen -->
    <Dialog v-model:visible="duplicateDialogVisible" header="Audit & Resolusi Potensi Duplikasi Dokumen" modal class="w-full max-w-4xl" :breakpoints="{ '960px': '90vw', '640px': '98vw' }">
      <div v-if="loadingDuplicates" class="text-center py-12 text-slate-400">
        <i class="pi pi-spin pi-spinner text-3xl mb-3 text-primary"></i>
        <p class="font-medium">Memindai dan menganalisis kemiripan seluruh dokumen...</p>
      </div>

      <div v-else-if="duplicatePairs.length === 0" class="text-center py-12 text-slate-500 dark:text-slate-400">
        <div class="w-14 h-14 bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-3">
          <i class="pi pi-check text-2xl"></i>
        </div>
        <h3 class="text-base font-bold text-slate-800 dark:text-white">Tidak Ada Potensi Duplikasi</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-md mx-auto">
          Seluruh SK, SOP, dan Juknis tertata rapi. Tidak ditemukan dokumen dengan nomor surat ganda atau kemiripan judul yang mencurigakan.
        </p>
      </div>

      <div v-else class="space-y-6 py-2 max-h-[72vh] overflow-y-auto pr-1">
        <div class="p-3.5 bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-xl text-xs text-purple-900 dark:text-purple-200 flex items-start gap-2.5">
          <i class="pi pi-info-circle text-purple-600 text-base mt-0.5 shrink-0"></i>
          <div class="leading-relaxed">
            <strong>Terdeteksi {{ duplicatePairs.length }} pasangan dokumen yang memiliki kemiripan tinggi.</strong><br/>
            Anda dapat menautkan salah satu dokumen sebagai <em>riwayat versi (revisi)</em>, menghapus dokumen yang keliru/ganda, atau menandainya sah sebagai dokumen terpisah.
          </div>
        </div>

        <div v-for="(pair, idx) in duplicatePairs" :key="pair.pair_id" class="border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden bg-white dark:bg-slate-800 shadow-sm">
          <div class="bg-slate-50 dark:bg-slate-800/80 p-3 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-purple-600 text-white text-xs font-bold flex items-center justify-center">
                {{ idx + 1 }}
              </span>
              <span class="text-xs font-bold text-slate-800 dark:text-white">Pemicu: {{ pair.reason }}</span>
            </div>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300">
              Skor: {{ pair.score }}%
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200 dark:divide-slate-700 p-4 gap-4">
            <!-- Dokumen A -->
            <div class="space-y-2 pr-0 md:pr-2">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Dokumen A (ID: #{{ pair.doc_a.id }})</span>
                <Tag :value="'v' + (pair.doc_a.version || '1.0')" severity="secondary" class="text-[10px]" />
              </div>
              <h4 class="font-bold text-sm text-slate-800 dark:text-white leading-snug">{{ pair.doc_a.title }}</h4>
              
              <div class="space-y-1 text-xs text-slate-600 dark:text-slate-300">
                <div v-if="pair.doc_a.document_number" class="font-mono text-[11px] text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-700/60 px-1.5 py-0.5 rounded inline-block">
                  #{{ pair.doc_a.document_number }}
                </div>
                <div><span class="text-slate-400">Kategori:</span> {{ getCategoryLabel(pair.doc_a.category) }}</div>
                <div v-if="pair.doc_a.effective_date"><span class="text-slate-400">Berlaku:</span> {{ formatDate(pair.doc_a.effective_date) }}</div>
                <div><span class="text-slate-400">Berkas:</span> {{ pair.doc_a.file_name }}</div>
                <div><span class="text-slate-400">Diupload:</span> {{ pair.doc_a.uploader_name || '-' }} ({{ formatDate(pair.doc_a.created_at) }})</div>
              </div>

              <div class="pt-2">
                <button @click="openPreviewDialog(pair.doc_a)" type="button" class="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 font-medium inline-flex items-center gap-1.5 transition">
                  <i class="pi pi-eye text-emerald-600"></i> Pratinjau Berkas A
                </button>
              </div>
            </div>

            <!-- Dokumen B -->
            <div class="space-y-2 pt-4 md:pt-0 pl-0 md:pl-2">
              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Dokumen B (ID: #{{ pair.doc_b.id }})</span>
                <Tag :value="'v' + (pair.doc_b.version || '1.0')" severity="secondary" class="text-[10px]" />
              </div>
              <h4 class="font-bold text-sm text-slate-800 dark:text-white leading-snug">{{ pair.doc_b.title }}</h4>
              
              <div class="space-y-1 text-xs text-slate-600 dark:text-slate-300">
                <div v-if="pair.doc_b.document_number" class="font-mono text-[11px] text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-700/60 px-1.5 py-0.5 rounded inline-block">
                  #{{ pair.doc_b.document_number }}
                </div>
                <div><span class="text-slate-400">Kategori:</span> {{ getCategoryLabel(pair.doc_b.category) }}</div>
                <div v-if="pair.doc_b.effective_date"><span class="text-slate-400">Berlaku:</span> {{ formatDate(pair.doc_b.effective_date) }}</div>
                <div><span class="text-slate-400">Berkas:</span> {{ pair.doc_b.file_name }}</div>
                <div><span class="text-slate-400">Diupload:</span> {{ pair.doc_b.uploader_name || '-' }} ({{ formatDate(pair.doc_b.created_at) }})</div>
              </div>

              <div class="pt-2">
                <button @click="openPreviewDialog(pair.doc_b)" type="button" class="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 font-medium inline-flex items-center gap-1.5 transition">
                  <i class="pi pi-eye text-emerald-600"></i> Pratinjau Berkas B
                </button>
              </div>
            </div>
          </div>

          <div class="bg-slate-50 dark:bg-slate-800/60 p-3 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between flex-wrap gap-2">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-semibold text-slate-600 dark:text-slate-400">Rantai Versi:</span>
              <button 
                @click="resolveDuplicate(pair, 'merge_as_revision', pair.doc_a.id, pair.doc_b.id)" 
                class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded-lg text-xs font-medium transition inline-flex items-center gap-1"
                title="Jadikan Dokumen B sebagai versi pembaruan dari Dokumen A"
              >
                <i class="pi pi-sync text-[11px]"></i> Jadikan B Revisi dari A
              </button>
              <button 
                @click="resolveDuplicate(pair, 'merge_as_revision', pair.doc_b.id, pair.doc_a.id)" 
                class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded-lg text-xs font-medium transition inline-flex items-center gap-1"
                title="Jadikan Dokumen A sebagai versi pembaruan dari Dokumen B"
              >
                <i class="pi pi-sync text-[11px]"></i> Jadikan A Revisi dari B
              </button>
            </div>

            <div class="flex items-center gap-1.5 flex-wrap">
              <button 
                @click="resolveDuplicate(pair, 'delete_doc', undefined, undefined, pair.doc_a.id)"
                class="px-2 py-1 bg-red-50 hover:bg-red-100 dark:bg-red-950/40 dark:hover:bg-red-900/50 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg text-xs font-medium transition inline-flex items-center gap-1"
                title="Hapus Dokumen A"
              >
                <i class="pi pi-trash text-[11px]"></i> Hapus A
              </button>
              <button 
                @click="resolveDuplicate(pair, 'delete_doc', undefined, undefined, pair.doc_b.id)"
                class="px-2 py-1 bg-red-50 hover:bg-red-100 dark:bg-red-950/40 dark:hover:bg-red-900/50 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg text-xs font-medium transition inline-flex items-center gap-1"
                title="Hapus Dokumen B"
              >
                <i class="pi pi-trash text-[11px]"></i> Hapus B
              </button>
              <button 
                @click="resolveDuplicate(pair, 'mark_distinct')" 
                class="px-2.5 py-1 bg-slate-200 hover:bg-slate-300 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-medium transition inline-flex items-center gap-1"
                title="Kedua dokumen ini sah dan sengaja dibuat terpisah"
              >
                <i class="pi pi-shield text-[11px]"></i> Dokumen Terpisah (Abaikan)
              </button>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-between w-full">
          <span class="text-xs text-slate-400">Keputusan resolusi akan langsung tersimpan di database.</span>
          <Button label="Tutup" severity="secondary" @click="duplicateDialogVisible = false" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const historyDialogVisible = ref(false)
const documentHistory = ref<any[]>([])
const loadingHistory = ref(false)
const editingDoc = ref<any>(null)
const previewDialogVisible = ref(false)
const previewDoc = ref<any>(null)

// Tab Aktif: 'documents' | 'career'
const activeViewTab = ref<'documents' | 'career'>('documents')

// User list for dropdown
const usersBrief = ref<any[]>([])
const selectedUserObj = ref<any>(null)

// Popover Deskripsi Dokumen
const descPopover = ref<any>(null)
const hoveredDoc = ref<any>(null)
let hidePopoverTimer: any = null

function showDescPopover(event: Event, doc: any) {
  if (hidePopoverTimer) {
    clearTimeout(hidePopoverTimer)
    hidePopoverTimer = null
  }
  hoveredDoc.value = doc
  descPopover.value?.show(event)
}

function toggleDescPopover(event: Event, doc: any) {
  if (hidePopoverTimer) {
    clearTimeout(hidePopoverTimer)
    hidePopoverTimer = null
  }
  hoveredDoc.value = doc
  descPopover.value?.toggle(event)
}

function scheduleHideDescPopover() {
  hidePopoverTimer = setTimeout(() => {
    descPopover.value?.hide()
  }, 250)
}

function cancelHideDescPopover() {
  if (hidePopoverTimer) {
    clearTimeout(hidePopoverTimer)
    hidePopoverTimer = null
  }
}

function hideDescPopover() {
  if (hidePopoverTimer) {
    clearTimeout(hidePopoverTimer)
    hidePopoverTimer = null
  }
  descPopover.value?.hide()
}

function openPreviewDialog(doc: any) {
  previewDoc.value = doc
  previewDialogVisible.value = true
}

function getGdrivePreviewUrl(url?: string): string {
  if (!url) return ''
  if (url.includes('/view')) {
    return url.replace(/\/view.*/, '/preview')
  }
  if (url.includes('drive.google.com/file/d/')) {
    return url.replace(/\/?$/, '/preview')
  }
  return url
}

function isImageFile(url?: string): boolean {
  if (!url) return false
  const cleanUrl = url.split('?')[0].split('#')[0]
  const ext = cleanUrl.split('.').pop()?.toLowerCase() || ''
  return ['jpg', 'jpeg', 'png', 'webp', 'gif', 'svg', 'bmp'].includes(ext)
}

function isPdfFile(url?: string): boolean {
  if (!url) return false
  const cleanUrl = url.split('?')[0].split('#')[0]
  const ext = cleanUrl.split('.').pop()?.toLowerCase() || ''
  return ext === 'pdf'
}

const documents = ref<any[]>([])
const searchQuery = ref('')
const filterCategory = ref('')
const filterVisibility = ref('')
const uploadProgress = ref(0)
const fileInputRef = ref<HTMLInputElement>()

// Attachment upload reference & state
const attachmentFileInputRef = ref<HTMLInputElement>()
const currentAttIndexToUpload = ref<number | null>(null)

// KPI summary counters
const activeDocCount = computed(() => {
  return documents.value.filter(d => d.expiry_info?.status === 'active' || d.expiry_info?.status === 'permanent').length
})
const expiringDocCount = computed(() => {
  return documents.value.filter(d => d.expiry_info?.status === 'expiring_soon').length
})
const expiredDocCount = computed(() => {
  return documents.value.filter(d => d.expiry_info?.status === 'expired').length
})

const replacesOptions = computed(() => {
  return documents.value.map(d => ({
    id: d.id,
    title: `${d.title} (v${d.version || '1.0'})`
  }))
})

const categoryOptions = [
  { value: 'sk_yayasan', label: 'SK Yayasan' },
  { value: 'sop', label: 'SOP' },
  { value: 'kalender_akademik', label: 'Kalender Akademik' },
  { value: 'juknis', label: 'Juknis' },
  { value: 'surat_edaran', label: 'Surat Edaran' },
  { value: 'lainnya', label: 'Lainnya' },
]

const allCategoryOptions = [{ value: '', label: 'Semua Kategori' }, ...categoryOptions]

const visibilityOptions = [
  { value: 'internal', label: 'Internal' },
  { value: 'public', label: 'Publik' },
]

// SK Career Type Options
const skTypeOptions = [
  { value: 'PENGANGKATAN', label: 'Pengangkatan Pegawai/Guru', icon: 'pi pi-check-circle', badgeClass: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-300' },
  { value: 'PROMOSI', label: 'Promosi Jabatan', icon: 'pi pi-arrow-up-circle', badgeClass: 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-300' },
  { value: 'MUTASI', label: 'Mutasi / Rotasi Posisi', icon: 'pi pi-sync', badgeClass: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-300' },
  { value: 'TUGAS_TAMBAHAN', label: 'Tugas Tambahan (Wakakur, dll)', icon: 'pi pi-star', badgeClass: 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-300' },
  { value: 'PEMBERHENTIAN', label: 'Pemberhentian / Selesai Masa Bakti', icon: 'pi pi-ban', badgeClass: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300 border-red-300' },
  { value: 'PENGUNDURAN_DIRI', label: 'Pengunduran Diri (Resign)', icon: 'pi pi-sign-out', badgeClass: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-300' },
]

const allSkTypeFilterOptions = [
  { value: '', label: 'Semua Jenis SK' },
  ...skTypeOptions
]

function getSkTypeBadge(val?: string) {
  const found = skTypeOptions.find(o => o.value === val)
  if (found) return found
  return {
    value: val || 'SK_UMUM',
    label: val ? val.replace(/_/g, ' ') : 'SK Umum',
    icon: 'pi pi-file',
    badgeClass: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-300'
  }
}

const fileSourceMode = ref<'upload' | 'gdrive'>('upload')
const gdriveInputUrl = ref('')

const allUnitsSelected = ref(true)
const selectedUnits = ref<string[]>(['YYS', 'RA', 'SDIT', 'SMPIT'])

const unitCheckboxOptions = [
  { code: 'YYS', name: 'Yayasan (Pusat)' },
  { code: 'RA', name: 'RA Asy-Syuuraa' },
  { code: 'SDIT', name: 'SDIT Asy-Syuuraa' },
  { code: 'SMPIT', name: 'SMPIT Asy-Syuuraa' },
]

function toggleAllUnits() {
  if (allUnitsSelected.value) {
    selectedUnits.value = ['YYS', 'RA', 'SDIT', 'SMPIT']
  } else {
    selectedUnits.value = []
  }
}

function formatTargetUnits(val?: string): string {
  if (!val || val === 'ALL') return 'Semua Unit'
  try {
    const parsed = val.startsWith('[') ? JSON.parse(val) : [val]
    return parsed.join(', ')
  } catch (e) {
    return val
  }
}

function isGdriveLink(url?: string): boolean {
  if (!url) return false
  return url.includes('drive.google.com') || url.includes('docs.google.com')
}

function handleGdriveInput() {
  const url = gdriveInputUrl.value.trim()
  if (url) {
    form.file_url = url
    form.file_name = 'Google Drive Document'
    form.file_size = 0
    if (!form.title) {
      form.title = 'Dokumen Google Drive'
    }
  } else {
    form.file_url = ''
    form.file_name = ''
    form.file_size = 0
  }
}

function calculateDocumentAge(effectiveDateStr?: string, createdAtStr?: string) {
  const refDateStr = effectiveDateStr || createdAtStr
  if (!refDateStr) return { text: '-', days: 0 }
  
  const refDate = new Date(refDateStr)
  const now = new Date()
  
  const diffTime = now.getTime() - refDate.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    const daysUntil = Math.abs(diffDays)
    return { text: `Mulai dlm ${daysUntil} hr`, days: diffDays }
  }
  
  if (diffDays === 0) {
    return { text: 'Hari ini', days: 0 }
  }
  
  if (diffDays < 30) {
    return { text: `${diffDays} hari`, days: diffDays }
  }
  
  const months = Math.floor(diffDays / 30.4375)
  if (months < 12) {
    const remDays = Math.floor(diffDays % 30.4375)
    return {
      text: remDays > 0 ? `${months} bln ${remDays} hr` : `${months} bln`,
      days: diffDays
    }
  }
  
  const years = Math.floor(months / 12)
  const remMonths = months % 12
  return {
    text: remMonths > 0 ? `${years} thn ${remMonths} bln` : `${years} thn`,
    days: diffDays
  }
}

function getExpiryInfo(effectiveDateStr?: string, expiredDateStr?: string) {
  if (!expiredDateStr) {
    return {
      status: 'permanent',
      label: 'Berlaku Tetap',
      severity: 'info',
      badgeClass: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800',
      icon: 'pi pi-check-circle',
      subtext: effectiveDateStr ? `Mulai ${formatDate(effectiveDateStr)}` : 'Tanpa batas waktu'
    }
  }

  const expDate = new Date(expiredDateStr)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  expDate.setHours(0, 0, 0, 0)
  
  const diffTime = expDate.getTime() - now.getTime()
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    const overdueDays = Math.abs(diffDays)
    return {
      status: 'expired',
      label: 'Kedaluwarsa',
      severity: 'danger',
      badgeClass: 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300 border border-red-200 dark:border-red-800',
      icon: 'pi pi-exclamation-triangle',
      subtext: `Habis: ${formatDate(expiredDateStr)} (lewat ${overdueDays} hr)`
    }
  }

  if (diffDays <= 30) {
    return {
      status: 'expiring_soon',
      label: `Sisa ${diffDays} hari`,
      severity: 'warn',
      badgeClass: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300 border border-amber-200 dark:border-amber-800',
      icon: 'pi pi-clock',
      subtext: `s/d ${formatDate(expiredDateStr)}`
    }
  }

  return {
    status: 'active',
    label: 'Aktif',
    severity: 'success',
    badgeClass: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800',
    icon: 'pi pi-check',
    subtext: `s/d ${formatDate(expiredDateStr)}`
  }
}

// Tenure helper between two dates
function calculateTenure(startDateStr?: string, endDateStr?: string): string {
  if (!startDateStr) return '-'
  const start = new Date(startDateStr)
  const end = endDateStr ? new Date(endDateStr) : new Date()
  if (isNaN(start.getTime()) || isNaN(end.getTime()) || end < start) return '-'
  
  let years = end.getFullYear() - start.getFullYear()
  let months = end.getMonth() - start.getMonth()
  let days = end.getDate() - start.getDate()
  
  if (days < 0) {
    months -= 1
  }
  if (months < 0) {
    years -= 1
    months += 12
  }
  
  const parts: string[] = []
  if (years > 0) parts.push(`${years} Tahun`)
  if (months > 0) parts.push(`${months} Bulan`)
  if (parts.length === 0) return 'Kurang dari 1 Bulan'
  return parts.join(' ')
}

function getInitials(name?: string): string {
  if (!name) return 'PG'
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase()
  return (parts[0][0] + parts[1][0]).toUpperCase()
}

function getAttachmentIcon(urlOrName?: string): string {
  if (!urlOrName) return 'pi pi-file text-slate-500'
  const ext = urlOrName.split('?')[0].split('.').pop()?.toLowerCase() || ''
  if (['doc', 'docx'].includes(ext)) return 'pi pi-file-word text-blue-600'
  if (['xls', 'xlsx', 'csv'].includes(ext)) return 'pi pi-file-excel text-emerald-600'
  if (ext === 'pdf') return 'pi pi-file-pdf text-red-600'
  if (['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext)) return 'pi pi-image text-purple-600'
  if (['zip', 'rar'].includes(ext)) return 'pi pi-box text-amber-600'
  return 'pi pi-file text-slate-600'
}

const form = reactive({
  document_number: '',
  title: '',
  description: '',
  category: 'lainnya',
  visibility: 'internal',
  file_url: '',
  file_name: '',
  file_size: 0,
  version: '1.0',
  replaces_id: null as number | null,
  effective_date: '',
  has_expired_date: false,
  expired_date: '',
  target_units: 'ALL',
  is_confidential: false,
  // Feature A: Attachments
  attachments: [] as Array<{
    title: string
    file_url: string
    file_name: string
    file_size?: number
    uploading?: boolean
  }>,
  // Feature B: Career Metadata
  is_career_sk: false,
  employee_id: null as number | null,
  employee_name: '',
  sk_type: 'PENGANGKATAN',
  position_title: '',
  term_start_date: '',
  term_end_date: '',
})

function onCategoryChange() {
  onTitleOrNumberInput()
  if (form.category === 'sk_yayasan' && !editingDoc.value) {
    form.is_career_sk = true
  }
}

function onUserSelected(e: any) {
  if (e?.value) {
    form.employee_id = e.value.id
    form.employee_name = e.value.full_name
  }
}

function onExpiredCheckboxChange() {
  if (!form.has_expired_date) {
    form.expired_date = ''
  }
}

function resetForm() {
  form.document_number = ''
  form.title = ''
  form.description = ''
  form.category = 'lainnya'
  form.visibility = 'internal'
  form.file_url = ''
  form.file_name = ''
  form.file_size = 0
  form.version = '1.0'
  form.replaces_id = null
  form.effective_date = ''
  form.has_expired_date = false
  form.expired_date = ''
  form.target_units = 'ALL'
  form.is_confidential = false
  form.attachments = []
  form.is_career_sk = false
  form.employee_id = null
  form.employee_name = ''
  form.sk_type = 'PENGANGKATAN'
  form.position_title = ''
  form.term_start_date = ''
  form.term_end_date = ''
  selectedUserObj.value = null
  allUnitsSelected.value = true
  selectedUnits.value = ['YYS', 'RA', 'SDIT', 'SMPIT']
  fileSourceMode.value = 'upload'
  gdriveInputUrl.value = ''
  uploadProgress.value = 0
}

function openDialog(doc?: any) {
  if (doc) {
    editingDoc.value = doc
    Object.assign(form, {
      document_number: doc.document_number || '',
      title: doc.title,
      description: doc.description || '',
      category: doc.category,
      visibility: doc.visibility || 'internal',
      file_url: doc.file_url,
      file_name: doc.file_name,
      file_size: doc.file_size,
      version: doc.version || '1.0',
      replaces_id: doc.replaces_id || null,
      effective_date: doc.effective_date ? doc.effective_date.substring(0, 10) : '',
      has_expired_date: !!doc.expired_date,
      expired_date: doc.expired_date ? doc.expired_date.substring(0, 10) : '',
      target_units: doc.target_units || 'ALL',
      is_confidential: !!doc.is_confidential,
      employee_id: doc.employee_id || null,
      employee_name: doc.employee_name || '',
      sk_type: doc.sk_type || 'PENGANGKATAN',
      position_title: doc.position_title || '',
      term_start_date: doc.term_start_date ? doc.term_start_date.substring(0, 10) : '',
      term_end_date: doc.term_end_date ? doc.term_end_date.substring(0, 10) : '',
      is_career_sk: !!(doc.employee_name || doc.employee_id || doc.position_title || doc.category === 'sk_yayasan'),
    })

    form.attachments = doc.attachments && Array.isArray(doc.attachments)
      ? doc.attachments.map((a: any) => ({ ...a, uploading: false }))
      : []

    if (doc.employee_id && usersBrief.value.length > 0) {
      selectedUserObj.value = usersBrief.value.find(u => u.id === doc.employee_id) || null
    } else {
      selectedUserObj.value = null
    }

    if (!doc.target_units || doc.target_units === 'ALL') {
      allUnitsSelected.value = true
      selectedUnits.value = ['YYS', 'RA', 'SDIT', 'SMPIT']
    } else {
      allUnitsSelected.value = false
      try {
        selectedUnits.value = doc.target_units.startsWith('[') ? JSON.parse(doc.target_units) : [doc.target_units]
      } catch (e) {
        selectedUnits.value = [doc.target_units]
      }
    }

    if (isGdriveLink(doc.file_url)) {
      fileSourceMode.value = 'gdrive'
      gdriveInputUrl.value = doc.file_url
    } else {
      fileSourceMode.value = 'upload'
      gdriveInputUrl.value = ''
    }
  } else {
    editingDoc.value = null
    resetForm()
  }
  dialogVisible.value = true
}

function openCareerSkDialog(employee?: any) {
  openDialog()
  form.category = 'sk_yayasan'
  form.is_career_sk = true
  if (employee) {
    form.employee_id = employee.employee_id || null
    form.employee_name = employee.employee_name || ''
    if (employee.employee_id && usersBrief.value.length > 0) {
      selectedUserObj.value = usersBrief.value.find(u => u.id === employee.employee_id) || null
    }
  }
}

// Attachment Management
function addAttachmentRow() {
  form.attachments.push({
    title: '',
    file_url: '',
    file_name: '',
    file_size: 0,
    uploading: false,
  })
}

function removeAttachmentRow(index: number) {
  form.attachments.splice(index, 1)
}

function triggerAttachmentUpload(index: number) {
  currentAttIndexToUpload.value = index
  attachmentFileInputRef.value?.click()
}

async function handleAttachmentFileSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || currentAttIndexToUpload.value === null) return
  
  const targetIndex = currentAttIndexToUpload.value
  const targetAtt = form.attachments[targetIndex]
  if (!targetAtt) return
  
  if (file.size > 15 * 1024 * 1024) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'File lampiran maksimal 15MB', life: 3000 })
    return
  }
  
  targetAtt.uploading = true
  try {
    const result = await api.upload('/cms/upload', file)
    targetAtt.file_url = result.url
    targetAtt.file_name = file.name
    targetAtt.file_size = file.size
    if (!targetAtt.title) {
      targetAtt.title = file.name.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' ')
    }
    toast.add({ severity: 'success', summary: 'Lampiran Diupload', detail: `Berkas ${file.name} siap disimpan`, life: 2500 })
  } catch (err) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengupload berkas lampiran', life: 3000 })
  } finally {
    targetAtt.uploading = false
    if (attachmentFileInputRef.value) attachmentFileInputRef.value.value = ''
    currentAttIndexToUpload.value = null
  }
}

async function openHistoryDialog(doc: any) {
  historyDialogVisible.value = true
  loadingHistory.value = true
  try {
    const raw = await api.get<any[]>(`/internal/documents/${doc.id}/history`)
    documentHistory.value = raw.map(d => ({
      ...d,
      age_info: calculateDocumentAge(d.effective_date, d.created_at),
      expiry_info: getExpiryInfo(d.effective_date, d.expired_date),
    }))
  } catch (e) {
    console.error('Failed to fetch document history', e)
    documentHistory.value = []
  } finally {
    loadingHistory.value = false
  }
}

async function fetchDocuments() {
  loading.value = true
  try {
    let url = '/internal/documents?'
    if (filterCategory.value) url += `category=${filterCategory.value}&`
    if (filterVisibility.value) url += `visibility=${filterVisibility.value}&`
    if (searchQuery.value) url += `search=${encodeURIComponent(searchQuery.value)}&`
    const raw = await api.get<any[]>(url)
    
    documents.value = raw.map(doc => {
      const age_info = calculateDocumentAge(doc.effective_date, doc.created_at)
      const expiry_info = getExpiryInfo(doc.effective_date, doc.expired_date)
      return {
        ...doc,
        age_info,
        expiry_info,
        effective_timestamp: doc.effective_date ? new Date(doc.effective_date).getTime() : 0,
        expired_timestamp: doc.expired_date ? new Date(doc.expired_date).getTime() : Infinity,
        created_timestamp: doc.created_at ? new Date(doc.created_at).getTime() : 0,
      }
    })
  } catch (e) {
    console.error('Failed to fetch documents', e)
  } finally {
    loading.value = false
  }
}

// ------------------------------------------------------------
// CAREER TIMELINE & DOSSIER LOGIC
// ------------------------------------------------------------
const careerList = ref<any[]>([])
const loadingCareer = ref(false)
const careerSearch = ref('')
const careerSkTypeFilter = ref('')

const activeCareerCount = computed(() => {
  return careerList.value.filter(e => e.is_currently_active).length
})

const totalCareerSkCount = computed(() => {
  return careerList.value.reduce((acc, emp) => acc + (emp.items ? emp.items.length : 0), 0)
})

const filteredCareerList = computed(() => {
  return careerList.value
})

async function fetchCareerHistory() {
  loadingCareer.value = true
  try {
    let url = '/internal/documents/employee-career'
    const q: string[] = []
    if (careerSearch.value) q.push(`search=${encodeURIComponent(careerSearch.value)}`)
    if (careerSkTypeFilter.value) q.push(`sk_type=${encodeURIComponent(careerSkTypeFilter.value)}`)
    if (q.length > 0) url += `?${q.join('&')}`
    
    careerList.value = await api.get<any[]>(url)
  } catch (e) {
    console.error('Failed to fetch career history', e)
    careerList.value = []
  } finally {
    loadingCareer.value = false
  }
}

function switchTab(tab: 'documents' | 'career') {
  activeViewTab.value = tab
  if (tab === 'career' && careerList.value.length === 0) {
    fetchCareerHistory()
  }
}

async function fetchUsersBrief() {
  try {
    usersBrief.value = await api.get<any[]>('/internal/users-brief')
  } catch (e) {
    console.error('Failed to fetch users brief', e)
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) await uploadFile(file)
}

async function handleDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0]
  if (file) await uploadFile(file)
}

async function uploadFile(file: File) {
  if (file.size > 10 * 1024 * 1024) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'File terlalu besar (maks 10MB)', life: 3000 })
    return
  }
  
  uploadProgress.value = 10
  try {
    const result = await api.upload('/cms/upload', file)
    form.file_url = result.url
    form.file_name = file.name
    form.file_size = file.size
    uploadProgress.value = 100
    
    // Auto-fill title if empty
    if (!form.title) {
      form.title = file.name.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' ')
    }
    
    toast.add({ severity: 'success', summary: 'Upload', detail: 'File berhasil diupload', life: 2000 })
  } catch (e) {
    console.error('Upload failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengupload file', life: 3000 })
    uploadProgress.value = 0
  }
}

function clearFile() {
  form.file_url = ''
  form.file_name = ''
  form.file_size = 0
  uploadProgress.value = 0
}

async function saveDocument() {
  saving.value = true
  try {
    const payload: any = { ...form }
    if (payload.visibility === 'public') {
      payload.target_units = 'ALL'
      payload.is_confidential = false
    } else {
      if (allUnitsSelected.value || selectedUnits.value.length === 4 || selectedUnits.value.length === 0) {
        payload.target_units = 'ALL'
      } else {
        payload.target_units = JSON.stringify(selectedUnits.value)
      }
    }

    if (!payload.has_expired_date) {
      payload.expired_date = null
    }
    delete payload.has_expired_date

    // Clean attachments array
    payload.attachments = (form.attachments || [])
      .filter(a => a.file_url)
      .map(a => ({
        title: a.title || a.file_name || 'Lampiran Berkas',
        file_url: a.file_url,
        file_name: a.file_name || 'Berkas Lampiran',
        file_size: a.file_size || 0,
      }))

    // Career fields normalization
    if (!payload.is_career_sk) {
      payload.employee_id = null
      payload.employee_name = null
      payload.sk_type = null
      payload.position_title = null
      payload.term_start_date = null
      payload.term_end_date = null
    } else {
      if (!payload.term_start_date) payload.term_start_date = null
      if (!payload.term_end_date) payload.term_end_date = null
    }
    delete payload.is_career_sk

    if (editingDoc.value) {
      await api.put(`/internal/documents/${editingDoc.value.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Dokumen berhasil diperbarui', life: 3000 })
    } else {
      await api.post('/internal/documents', payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Dokumen berhasil ditambahkan', life: 3000 })
    }
    dialogVisible.value = false
    await fetchDocuments()
    if (activeViewTab.value === 'career' || payload.employee_name) {
      await fetchCareerHistory()
    }
  } catch (e) {
    console.error('Save failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan dokumen', life: 3000 })
  } finally {
    saving.value = false
  }
}

async function deleteDoc(doc: any) {
  if (!confirm(`Hapus dokumen "${doc.title}"?`)) return
  try {
    await api.delete(`/internal/documents/${doc.id}`)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Dokumen berhasil dihapus', life: 3000 })
    await fetchDocuments()
    if (activeViewTab.value === 'career' || doc.employee_name) {
      await fetchCareerHistory()
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus dokumen', life: 3000 })
  }
}

// Helpers
function getCategoryLabel(cat: string) {
  return categoryOptions.find(c => c.value === cat)?.label || cat
}

function getCategoryIcon(cat: string) {
  const map: Record<string, string> = {
    sk_yayasan: 'pi pi-file-pdf',
    sop: 'pi pi-book',
    kalender_akademik: 'pi pi-calendar',
    juknis: 'pi pi-list',
    surat_edaran: 'pi pi-envelope',
    lainnya: 'pi pi-file',
  }
  return map[cat] || 'pi pi-file'
}

function getCategoryColor(cat: string) {
  const map: Record<string, string> = {
    sk_yayasan: 'bg-red-100 dark:bg-red-900/30 text-red-500',
    sop: 'bg-blue-100 dark:bg-blue-900/30 text-blue-500',
    kalender_akademik: 'bg-green-100 dark:bg-green-900/30 text-green-500',
    juknis: 'bg-purple-100 dark:bg-purple-900/30 text-purple-500',
    surat_edaran: 'bg-amber-100 dark:bg-amber-900/30 text-amber-500',
    lainnya: 'bg-slate-100 dark:bg-slate-700 text-slate-500',
  }
  return map[cat] || 'bg-slate-100 dark:bg-slate-700 text-slate-500'
}

function getCategorySeverity(cat: string) {
  const map: Record<string, string> = {
    sk_yayasan: 'danger', sop: 'info', kalender_akademik: 'success',
    juknis: 'warn', surat_edaran: 'warn', lainnya: 'secondary',
  }
  return map[cat] || 'secondary'
}

function formatSize(bytes: number) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

// ------------------------------------------------------------
// DUPLICATE DETECTION & RESOLUTION
// ------------------------------------------------------------
const duplicateCount = ref(0)
const duplicatePairs = ref<any[]>([])
const duplicateDialogVisible = ref(false)
const loadingDuplicates = ref(false)
const duplicateWarning = ref<any>(null)
let checkDuplicateTimer: any = null

async function fetchDuplicateCount() {
  try {
    const res = await api.get<{ count: number, pairs: any[] }>('/internal/documents/duplicates')
    duplicateCount.value = res.count || 0
    duplicatePairs.value = res.pairs || []
  } catch (e) {
    console.error('Failed to fetch duplicate count', e)
  }
}

async function openDuplicateDialog() {
  duplicateDialogVisible.value = true
  loadingDuplicates.value = true
  try {
    const res = await api.get<{ count: number, pairs: any[] }>('/internal/documents/duplicates')
    duplicateCount.value = res.count || 0
    duplicatePairs.value = res.pairs || []
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal memuat daftar potensi duplikasi', life: 3000 })
  } finally {
    loadingDuplicates.value = false
  }
}

async function resolveDuplicate(pair: any, action: string, parentId?: number, childId?: number, deleteId?: number) {
  try {
    const payload: any = {
      doc_a_id: pair.doc_a.id,
      doc_b_id: pair.doc_b.id,
      action,
    }
    if (action === 'merge_as_revision') {
      payload.parent_doc_id = parentId
      payload.child_doc_id = childId
    } else if (action === 'delete_doc') {
      if (!confirm('Apakah Anda yakin ingin menghapus berkas dokumen ini?')) return
      payload.delete_doc_id = deleteId
    }

    const res = await api.post<{ message: string }>('/internal/documents/resolve-duplicate', payload)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: res.message, life: 3000 })
    
    // Refresh duplicates and documents table
    await fetchDuplicateCount()
    await fetchDocuments()
    if (activeViewTab.value === 'career') {
      await fetchCareerHistory()
    }
    
    if (duplicatePairs.value.length === 0) {
      setTimeout(() => {
        duplicateDialogVisible.value = false
      }, 800)
    }
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.message || 'Gagal mengeksekusi resolusi duplikasi', life: 3000 })
  }
}

function onTitleOrNumberInput() {
  duplicateWarning.value = null
  const titleText = (form.title || '').trim()
  if (titleText.length < 3) return

  if (checkDuplicateTimer) clearTimeout(checkDuplicateTimer)
  checkDuplicateTimer = setTimeout(async () => {
    try {
      let q = `/internal/documents/check-duplicate?title=${encodeURIComponent(titleText)}`
      if (form.document_number) q += `&document_number=${encodeURIComponent(form.document_number)}`
      if (form.category) q += `&category=${encodeURIComponent(form.category)}`
      if (editingDoc.value) q += `&exclude_id=${editingDoc.value.id}`
      
      const res = await api.get<{ has_match: boolean, match: any }>(q)
      if (res.has_match && res.match) {
        duplicateWarning.value = res
      }
    } catch (e) {
      // ignore
    }
  }, 400)
}

function applyAsRevision(matchedDoc: any) {
  form.replaces_id = matchedDoc.id
  try {
    const v = parseFloat(matchedDoc.version || '1.0')
    if (!isNaN(v)) {
      form.version = (v + 1.0).toFixed(1)
    }
  } catch (e) {
    form.version = '2.0'
  }
  toast.add({ 
    severity: 'info', 
    summary: 'Rantai Revisi Ditautkan', 
    detail: `Dokumen ini diatur sebagai revisi versi baru dari "${matchedDoc.title}"`, 
    life: 3000 
  })
  duplicateWarning.value = null
}

onMounted(() => {
  fetchDocuments()
  fetchDuplicateCount()
  fetchUsersBrief()
  fetchCareerHistory()
})
</script>
