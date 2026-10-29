<template>
  <div class="space-y-6">
    <!-- Header with Quick Action to Presensi Mandiri -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <i class="pi pi-calendar-check text-emerald-600"></i>
          Presensi Harian Pegawai
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
          Verifikasi kehadiran, pantau presensi mandiri GPS, dan kelola absensi harian guru &amp; karyawan.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Info Jam Kerja & Toleransi + Tombol Pengaturan -->
        <button
          type="button"
          class="inline-flex items-center gap-2 px-3 py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-medium border border-slate-200 dark:border-slate-700 transition"
          title="Klik untuk mengatur Jam Masuk, Jam Pulang & Toleransi Keterlambatan"
          @click="showWorkHoursDialog = true"
        >
          <i class="pi pi-clock text-emerald-600"></i>
          <span>Jam Masuk: <b>{{ geofenceConfig.work_start_time || '06:45' }}</b> &bull; Pulang Dinamis</span>
          <span class="px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 text-[10px] font-bold">
            Toleransi {{ geofenceConfig.late_tolerance_minutes || 5 }}m
          </span>
          <i class="pi pi-sliders-h text-[11px] text-slate-400 ml-0.5"></i>
        </button>

        <NuxtLink 
          to="/dashboard/sdm/presensi/mandiri"
          class="inline-flex items-center gap-2 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-semibold text-xs shadow-sm transition"
        >
          <i class="pi pi-map-marker"></i>
          Presensi Mandiri GPS
        </NuxtLink>
        <NuxtLink 
          to="/dashboard/sdm/presensi/rekap"
          class="inline-flex items-center gap-2 px-3.5 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-xl font-semibold text-xs shadow-sm transition"
        >
          <i class="pi pi-chart-bar text-slate-500"></i>
          Rekap Bulanan
        </NuxtLink>
      </div>
    </div>

    <!-- Filter & Date Navigator Bar (Compact Single-Line Layout) -->
    <Card>
      <template #content>
        <div class="flex flex-col xl:flex-row justify-between items-stretch xl:items-center gap-3">
          <!-- Left: Date Navigator + Date Picker -->
          <div class="flex flex-wrap sm:flex-nowrap items-center gap-2">
            <div class="inline-flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 shrink-0">
              <button
                type="button"
                class="w-7 h-7 rounded-lg flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 transition"
                title="Hari Sebelumnya (Kemarin)"
                @click="changeDate(-1)"
              >
                <i class="pi pi-chevron-left text-xs"></i>
              </button>
              <button
                type="button"
                class="px-2.5 py-1 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 transition"
                title="Pindah ke Hari Kemarin"
                @click="changeDate(-1)"
              >
                Kemarin
              </button>
              <button
                type="button"
                class="px-3 py-1 rounded-lg text-xs font-bold transition shadow-xs"
                :class="isTodaySelected ? 'bg-emerald-600 text-white' : 'bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50'"
                title="Kembali ke Hari Ini"
                @click="setToday"
              >
                Hari Ini
              </button>
              <button
                type="button"
                class="px-2.5 py-1 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 transition"
                title="Pindah ke Hari Besok"
                @click="changeDate(1)"
              >
                Besok
              </button>
              <button
                type="button"
                class="w-7 h-7 rounded-lg flex items-center justify-center text-slate-600 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-700 transition"
                title="Hari Berikutnya (Besok)"
                @click="changeDate(1)"
              >
                <i class="pi pi-chevron-right text-xs"></i>
              </button>
            </div>

            <Calendar 
              v-model="filterDate" 
              dateFormat="yy-mm-dd" 
              :showIcon="true" 
              class="w-40 text-xs shrink-0" 
              @date-select="fetchData" 
            />

            <!-- Badge jika Memilih Hari Ahad / Libur -->
            <span 
              v-if="filterDate && filterDate.getDay() === 0" 
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-100 dark:bg-amber-950/70 border border-amber-300 dark:border-amber-800 text-amber-800 dark:text-amber-200 text-xs font-bold shrink-0"
              title="Hari Ahad biasanya libur sekolah, presensi dicatat sebagai penugasan / kegiatan khusus"
            >
              <i class="pi pi-sun text-amber-600"></i>
              Hari Ahad (Kegiatan Khusus)
            </span>
          </div>

          <!-- Right: Unit Selector & Compact Action Buttons with Icon + Tooltip -->
          <div class="flex flex-wrap sm:flex-nowrap items-center gap-2 justify-end">
            <Dropdown 
              v-model="filterUnit" 
              :options="units" 
              optionLabel="name" 
              optionValue="id" 
              placeholder="Semua Unit Sekolah" 
              showClear 
              class="w-full sm:w-48 text-xs" 
              @change="fetchData" 
            />

            <Button 
              icon="pi pi-cloud-download" 
              label="Tarik Tanggal Ini" 
              severity="info" 
              size="small" 
              class="text-xs font-semibold shadow-sm shrink-0 !px-3" 
              :title="`Tarik data presensi dari mesin fingerprint untuk tanggal terpilih (${formattedDate})`"
              :loading="syncingFingerprint" 
              @click="syncFingerprint" 
            />

            <Button 
              icon="pi pi-calendar-plus" 
              label="Tarik Massal (Bulan / Tahun)" 
              severity="warn" 
              size="small" 
              class="text-xs font-semibold shadow-sm shrink-0 !px-3" 
              title="Tarik data presensi 1 bulan penuh, 1 tahun (sejak 1 Jan 2026), atau rentang kustom dari mesin fingerprint"
              @click="openBulkSyncModal" 
            />

            <!-- Icon-only Log Sinkronisasi with Badge & Hint -->
            <div class="relative inline-flex shrink-0">
              <Button 
                icon="pi pi-history" 
                :severity="failedLogsCount > 0 ? 'danger' : 'secondary'" 
                outlined 
                size="small" 
                class="!w-9 !h-9 !p-0 flex items-center justify-center" 
                :title="failedLogsCount > 0 ? `Riwayat & Log Sinkronisasi (${failedLogsCount} Gagal)` : 'Riwayat & Log Sinkronisasi Mesin Presensi'"
                @click="openSyncLogsDialog" 
              />
              <span 
                v-if="failedLogsCount > 0" 
                class="absolute -top-1.5 -right-1.5 min-w-[18px] h-[18px] px-1 rounded-full bg-rose-600 text-white text-[10px] font-bold flex items-center justify-center shadow pointer-events-none"
              >
                {{ failedLogsCount }}
              </span>
            </div>

            <!-- Icon-onlyPengaturan Jam Kerja & Toleransi -->
            <Button 
              icon="pi pi-clock" 
              severity="secondary" 
              outlined 
              size="small" 
              class="!w-9 !h-9 !p-0 shrink-0" 
              title="Atur Jam Masuk, Jam Pulang & Toleransi Keterlambatan"
              @click="showWorkHoursDialog = true" 
            />

            <!-- Icon-only Muat Ulang -->
            <Button 
              icon="pi pi-refresh" 
              severity="secondary"
              outlined 
              size="small" 
              class="!w-9 !h-9 !p-0 shrink-0" 
              title="Muat Ulang Data Presensi"
              :loading="loading" 
              @click="fetchData" 
            />
          </div>
        </div>

        <!-- Step-by-Step Live Progress Panel -->
        <div 
          v-if="syncProgress.active" 
          class="mt-4 p-4 rounded-xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800 space-y-2.5 transition-all"
        >
          <div class="flex items-center justify-between text-xs">
            <div class="font-bold text-sky-900 dark:text-sky-200 flex items-center gap-2">
              <i class="pi pi-spin pi-spinner text-sky-600"></i>
              <span>{{ syncProgress.stageText }}</span>
            </div>
            <span class="font-bold text-sky-700 dark:text-sky-300">
              {{ syncProgress.current }} / {{ syncProgress.total }} Pegawai ({{ syncProgress.percent }}%)
            </span>
          </div>
          <ProgressBar :value="syncProgress.percent" :showValue="false" class="!h-2.5" />
          <div v-if="syncProgress.currentEmployeeName" class="text-[11px] text-sky-700 dark:text-sky-300 flex items-center justify-between">
            <span>Memproses satu per satu: <b>{{ syncProgress.currentEmployeeName }}</b></span>
            <span v-if="syncProgress.failed > 0" class="text-rose-600 font-semibold">{{ syncProgress.failed }} gagal</span>
          </div>
        </div>
      </template>
    </Card>

    <!-- Holiday Banner if selected date is Sunday or Academic Holiday -->
    <div 
      v-if="dateInfo?.is_holiday"
      class="p-3.5 rounded-xl bg-sky-50 dark:bg-sky-950/40 border border-sky-200 dark:border-sky-800 text-sky-900 dark:text-sky-200 text-xs flex items-center justify-between gap-3 shadow-xs"
    >
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-sky-100 dark:bg-sky-900/60 text-sky-600 dark:text-sky-400 flex items-center justify-center text-base shrink-0 shadow-xs">
          <i class="pi pi-sun"></i>
        </div>
        <div>
          <div class="font-bold flex items-center gap-2">
            <span class="text-sm text-sky-950 dark:text-white">{{ dateInfo.holiday_desc }}</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-sky-200/80 dark:bg-sky-800 text-sky-800 dark:text-sky-200 font-bold uppercase tracking-wider">
              Hari Libur
            </span>
          </div>
          <p class="text-[11px] text-sky-700 dark:text-sky-300 mt-0.5">
            Jam kerja reguler diliburkan (tidak ada potongan alpa). Kehadiran guru piket atau pelatih lomba yang hadir tetap dicatat dengan jam longgar/fleksibel.
          </p>
        </div>
      </div>
    </div>

    <!-- Status Banner: Saved in Database vs Draft/Unsaved -->
    <div 
      v-if="attendances.length > 0"
      class="p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-sm transition"
      :class="isSavedInDb 
        ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200' 
        : 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200'"
    >
      <div class="flex items-start sm:items-center gap-3">
        <i 
          class="text-2xl shrink-0 mt-0.5 sm:mt-0" 
          :class="isSavedInDb ? 'pi pi-check-circle text-emerald-600 dark:text-emerald-400' : 'pi pi-exclamation-triangle text-amber-600 dark:text-amber-400'"
        ></i>
        <div>
          <div class="font-bold text-sm flex items-center gap-2">
            <span>{{ isSavedInDb ? 'Data Presensi Telah Tersimpan di Sistem' : 'Presensi Tanggal Ini Belum Tersimpan / Masih Draft' }}</span>
            <span 
              class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
              :class="isSavedInDb ? 'bg-emerald-200/80 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200' : 'bg-amber-200/80 text-amber-800 dark:bg-amber-900 dark:text-amber-200'"
            >
              {{ isSavedInDb ? 'Tersimpan (DB)' : 'Belum Disimpan' }}
            </span>
          </div>
          <p class="text-xs opacity-90 mt-1 leading-relaxed">
            <template v-if="isSavedInDb">
              Kehadiran untuk <b>{{ formattedDate }}</b> sudah tersimpan permanen. Sebanyak <b>{{ summary.hadir }} Hadir</b>, <b>{{ summary.sakit + summary.izin + summary.cuti }} Izin/Sakit/Cuti</b>, dan <b>{{ summary.alpa }} Alpa</b>. Data otomatis terhubung dengan Rekap Bulanan.
            </template>
            <template v-else>
              Belum ada data presensi yang difinalisasi untuk <b>{{ formattedDate }}</b> ({{ summary.belum }} dari {{ attendances.length }} pegawai belum diabsen). Klik <b>"Set Semua Hadir"</b> untuk mengisi cepat, lalu klik <b>"Simpan Perubahan"</b>.
            </template>
          </p>
        </div>
      </div>

      <div class="shrink-0 flex items-center gap-2 pt-2 sm:pt-0 border-t sm:border-t-0 border-amber-200/60 dark:border-amber-800/60">
        <Button 
          label="Set Semua Hadir" 
          icon="pi pi-check" 
          severity="success" 
          size="small" 
          outlined
          class="text-xs font-semibold" 
          @click="setAllPresent" 
        />
        <Button 
          label="Simpan Perubahan" 
          icon="pi pi-save" 
          severity="primary" 
          size="small" 
          class="text-xs font-semibold shadow-sm" 
          :loading="saving" 
          @click="saveAttendance" 
        />
      </div>
    </div>

    <!-- Ringkasan Cards (6 Cards Lengkap + Quick View List Icon di Masing-masing Card) -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3" v-if="attendances.length > 0">
      <!-- 1. Hadir / Tepat & Terlambat -->
      <div 
        class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-emerald-500 shadow-sm flex flex-col justify-between hover:shadow-md transition cursor-pointer group"
        @click="openCategoryModal('HADIR')"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="text-[11px] font-semibold text-slate-500">Hadir / Tepat</div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.hadir }}</div>
          </div>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 hover:bg-emerald-100 flex items-center justify-center transition"
            title="Lihat daftar pegawai yang Hadir hari ini"
            @click.stop="openCategoryModal('HADIR')"
          >
            <i class="pi pi-eye text-xs"></i>
          </button>
        </div>
        <div class="mt-1.5 flex items-center justify-between gap-1">
          <button
            v-if="summary.terlambat > 0"
            type="button"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300 text-[10px] font-bold hover:bg-amber-200 transition"
            title="Klik untuk melihat daftar pegawai yang Terlambat hari ini"
            @click.stop="openCategoryModal('LATE')"
          >
            <i class="pi pi-clock text-[9px]"></i>
            <span>{{ summary.terlambat }} Terlambat (Lihat)</span>
          </button>
          <span v-else class="text-[10px] text-emerald-600 font-medium">Semua tepat waktu</span>
        </div>
      </div>

      <!-- 2. Sakit -->
      <div 
        class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-yellow-500 shadow-sm flex flex-col justify-between hover:shadow-md transition cursor-pointer"
        @click="openCategoryModal('SICK')"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="text-[11px] font-semibold text-slate-500">Sakit</div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.sakit }}</div>
          </div>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-yellow-50 dark:bg-yellow-950/60 text-yellow-600 hover:bg-yellow-100 flex items-center justify-center transition"
            title="Lihat daftar pegawai yang Sakit hari ini"
            @click.stop="openCategoryModal('SICK')"
          >
            <i class="pi pi-eye text-xs"></i>
          </button>
        </div>
        <div class="text-[10px] text-slate-400 mt-1.5">Surat dokter / ket.</div>
      </div>

      <!-- 3. Izin / Tugas Luar -->
      <div 
        class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-blue-500 shadow-sm flex flex-col justify-between hover:shadow-md transition cursor-pointer"
        @click="openCategoryModal('PERMIT')"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="text-[11px] font-semibold text-slate-500">Izin / Tugas Luar</div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.izin }}</div>
          </div>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-blue-600 hover:bg-blue-100 flex items-center justify-center transition"
            title="Lihat daftar pegawai yang Izin / Tugas Luar hari ini"
            @click.stop="openCategoryModal('PERMIT')"
          >
            <i class="pi pi-eye text-xs"></i>
          </button>
        </div>
        <div class="text-[10px] text-slate-400 mt-1.5">Pribadi / Dinas luar</div>
      </div>

      <!-- 4. Cuti Resmi -->
      <div 
        class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-purple-500 shadow-sm flex flex-col justify-between hover:shadow-md transition cursor-pointer"
        @click="openCategoryModal('LEAVE')"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="text-[11px] font-semibold text-slate-500">Cuti Resmi</div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.cuti }}</div>
          </div>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-purple-50 dark:bg-purple-950/60 text-purple-600 hover:bg-purple-100 flex items-center justify-center transition"
            title="Lihat daftar pegawai yang Cuti hari ini"
            @click.stop="openCategoryModal('LEAVE')"
          >
            <i class="pi pi-eye text-xs"></i>
          </button>
        </div>
        <div class="text-[10px] text-slate-400 mt-1.5">Melahirkan, Nikah, Duka</div>
      </div>

      <!-- 5. Alpa -->
      <div 
        class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-rose-500 shadow-sm flex flex-col justify-between hover:shadow-md transition cursor-pointer"
        @click="openCategoryModal('ABSENT')"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="text-[11px] font-semibold text-slate-500">Alpa</div>
            <div class="text-2xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ summary.alpa }}</div>
          </div>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-rose-50 dark:bg-rose-950/60 text-rose-600 hover:bg-rose-100 flex items-center justify-center transition"
            title="Lihat daftar pegawai yang Alpa (Tanpa Keterangan) hari ini"
            @click.stop="openCategoryModal('ABSENT')"
          >
            <i class="pi pi-eye text-xs"></i>
          </button>
        </div>
        <div class="text-[10px] text-slate-400 mt-1.5">Tanpa keterangan</div>
      </div>

      <!-- 6. Belum Presensi -->
      <div 
        class="bg-white dark:bg-slate-800 rounded-xl p-3.5 border-l-4 border-slate-400 dark:border-slate-600 shadow-sm flex flex-col justify-between hover:shadow-md transition cursor-pointer"
        @click="openCategoryModal('UNRECORDED')"
      >
        <div class="flex items-start justify-between gap-2">
          <div>
            <div class="text-[11px] font-semibold text-slate-500">Belum Presensi</div>
            <div class="text-2xl font-extrabold text-slate-700 dark:text-slate-200 mt-0.5">{{ summary.belum }}</div>
          </div>
          <button
            type="button"
            class="w-7 h-7 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 flex items-center justify-center transition"
            title="Lihat daftar pegawai yang Belum Presensi hari ini"
            @click.stop="openCategoryModal('UNRECORDED')"
          >
            <i class="pi pi-eye text-xs"></i>
          </button>
        </div>
        <div class="text-[10px] text-slate-400 font-medium mt-1.5">Dari total {{ attendances.length }} staf</div>
      </div>
    </div>

    <!-- Data Table -->
    <Card>
      <template #content>
        <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3" v-if="attendances.length > 0">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
              <span>Daftar Presensi: {{ formattedDate }}</span>
              <span class="text-xs font-normal px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                {{ summary.totalSudah }} / {{ attendances.length }} Tercatat
              </span>
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">
              Input manual oleh Tata Usaha atau hasil sinkronisasi check-in mandiri GPS oleh pegawai.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <Button 
              label="Set Semua Hadir" 
              icon="pi pi-check" 
              severity="success" 
              outlined 
              size="small" 
              class="text-xs"
              @click="setAllPresent" 
            />
            <Button 
              label="Simpan Perubahan" 
              icon="pi pi-save" 
              size="small" 
              class="text-xs font-semibold"
              :loading="saving" 
              @click="saveAttendance" 
            />
          </div>
        </div>

        <DataTable :value="attendances" :loading="loading" dataKey="employee_id" class="p-datatable-sm" stripedRows responsiveLayout="scroll">
          <Column header="Pegawai" style="min-width: 220px">
            <template #body="{ data }">
              <div class="flex items-center gap-3">
                <Avatar 
                  :image="data.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.nama_lengkap || '')}&background=random`" 
                  shape="circle" 
                  size="normal"
                  class="shrink-0"
                />
                <div class="min-w-0">
                  <div class="font-semibold text-slate-800 dark:text-white truncate">{{ data.nama_lengkap }}</div>
                  <div class="text-xs text-slate-400 truncate">
                    {{ data.position || 'Pegawai' }} - <span class="font-medium text-emerald-600 dark:text-emerald-400">{{ data.unit_name || 'Yayasan' }}</span>
                  </div>
                  <!-- GPS Badge Indicator -->
                  <div v-if="data.check_in_distance != null" class="text-[10px] text-emerald-600 dark:text-emerald-400 flex items-center gap-1 mt-0.5 font-medium">
                    <i class="pi pi-map-marker text-[10px]"></i>
                    <span>GPS Mandiri (Jarak {{ data.check_in_distance }}m)</span>
                  </div>
                </div>
              </div>
            </template>
          </Column>

          <Column header="Status Presensi" style="min-width: 235px">
            <template #body="{ data }">
              <!-- Locked when synced from Fingerprint or GPS Mandiri -->
              <div v-if="isLockedBySystem(data)" class="space-y-1">
                <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold select-none" :class="getStatusBadgeClass(data.status)">
                  <i class="pi pi-lock text-[10px]"></i>
                  <span>{{ getStatusLabel(data.status) }}</span>
                </div>
                <div class="text-[10px] text-slate-400 flex items-center gap-1">
                  <i class="pi pi-verified text-emerald-500 text-[10px]"></i>
                  <span>Terkunci otomatis ({{ data.check_in_distance != null ? 'GPS Mandiri' : 'Mesin Fingerprint' }})</span>
                </div>
              </div>

              <!-- Editable by Admin when NO data in Fingerprint / GPS -->
              <div v-else class="space-y-1">
                <Dropdown 
                  v-model="data.status" 
                  :options="statusOptions" 
                  optionLabel="label" 
                  optionValue="value" 
                  optionGroupLabel="group"
                  optionGroupChildren="items"
                  class="w-full text-xs" 
                >
                  <template #value="slotProps">
                    <span v-if="slotProps.value" class="px-2 py-0.5 rounded text-xs font-semibold" :class="getStatusBadgeClass(slotProps.value)">
                      {{ getStatusLabel(slotProps.value) }}
                    </span>
                    <span v-else class="px-2 py-0.5 rounded text-xs text-slate-400 bg-slate-100 dark:bg-slate-700">
                      Belum Presensi
                    </span>
                  </template>
                  <template #option="slotProps">
                    <div class="flex items-center justify-between text-xs py-0.5">
                      <span>{{ slotProps.option.label }}</span>
                      <span class="text-[10px] px-1.5 py-0.2 rounded" :class="getStatusBadgeClass(slotProps.option.value)">
                        {{ slotProps.option.value }}
                      </span>
                    </div>
                  </template>
                </Dropdown>
                <div class="text-[10px] text-rose-600 dark:text-rose-400 font-medium flex items-center gap-1">
                  <i class="pi pi-info-circle text-[10px]"></i>
                  <span>Tidak ada di Fingerprint — Isi status manual</span>
                </div>
              </div>
            </template>
          </Column>

          <Column header="Jam Masuk" style="width: 135px">
            <template #body="{ data }">
              <Calendar 
                v-model="data.check_in" 
                timeOnly 
                dateFormat=""
                placeholder="--:--" 
                class="w-full text-xs"
                :disabled="isLockedBySystem(data) || !isAttendancePhysical(data.status)"
              />
            </template>
          </Column>

          <Column header="Jam Pulang" style="width: 145px">
            <template #body="{ data }">
              <Calendar 
                v-model="data.check_out" 
                timeOnly 
                dateFormat=""
                placeholder="--:--" 
                class="w-full text-xs"
                :disabled="isLockedBySystem(data) || !isAttendancePhysical(data.status)"
              />
              <div 
                v-if="data.check_out && data.check_out.getHours() >= 18" 
                class="text-[10px] font-bold text-indigo-700 dark:text-indigo-400 mt-1 flex items-center gap-1 bg-indigo-50 dark:bg-indigo-950/60 px-1.5 py-0.5 rounded border border-indigo-200 dark:border-indigo-900"
                title="Pulang larut malam di atas jam 18:00 (Lembur)"
              >
                <i class="pi pi-moon text-[9px]"></i>
                Lembur (>18:00)
              </div>
              <div 
                v-else-if="getEarlyLeaveInfo(data)"
                class="text-[10px] font-bold mt-1 flex items-center gap-1 px-1.5 py-0.5 rounded border"
                :class="getEarlyLeaveInfo(data)?.isDuty 
                  ? 'text-sky-700 dark:text-sky-400 bg-sky-50 dark:bg-sky-950/60 border-sky-200 dark:border-sky-900' 
                  : 'text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-900'"
                :title="`Jadwal pulang seharusnya pukul ${getEarlyLeaveInfo(data)?.expectedTime}. Pulang lebih awal ${getEarlyLeaveInfo(data)?.earlyMinutes} menit.${getEarlyLeaveInfo(data)?.isDuty ? ' (Tugas Luar / Dispensasi)' : ''}`"
              >
                <i :class="getEarlyLeaveInfo(data)?.isDuty ? 'pi pi-briefcase text-[9px]' : 'pi pi-clock text-[9px]'"></i>
                <span>Pulang Cepat (-{{ getEarlyLeaveInfo(data)?.earlyMinutes }}m)</span>
              </div>
            </template>
          </Column>

          <Column header="Catatan / Keterangan" style="min-width: 250px">
            <template #body="{ data }">
              <!-- Read-only locked note for Fingerprint / GPS Mandiri -->
              <div 
                v-if="isLockedBySystem(data)" 
                class="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-300 select-none cursor-not-allowed"
                title="Catatan otomatis dari sistem (Fingerprint / GPS Mandiri) tidak dapat diubah"
              >
                <i class="pi pi-lock text-slate-400 text-xs shrink-0"></i>
                <span class="truncate font-medium">{{ data.notes }}</span>
              </div>

              <!-- Editable manual reason with permanent 'Tidak ada data di Fingerprint' note -->
              <div v-else class="space-y-1">
                <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-800 text-[10px] font-bold text-rose-700 dark:text-rose-300">
                  <i class="pi pi-exclamation-triangle text-[9px]"></i>
                  <span>Tidak ada data di Fingerprint</span>
                </div>
                <InputText 
                  v-model="data.manual_notes" 
                  placeholder="Wajib isi alasan manual (Sakit/Izin/Alpa)..." 
                  class="w-full text-xs p-inputtext-sm" 
                />
              </div>
            </template>
          </Column>

          <template #empty>
            <div class="text-center py-12 text-slate-500">
              <i class="pi pi-users text-3xl text-slate-300 mb-2"></i>
              <p>Tidak ada data pegawai yang ditemukan untuk unit ini.</p>
            </div>
          </template>
        </DataTable>
      </template>
    </Card>

    <!-- Dialog Tarik Data Mesin Fingerprint Massal (1 Bulan / 1 Tahun / Kustom) -->
    <Dialog
      v-model:visible="showBulkSyncModal"
      header="Tarik Data Mesin Fingerprint Massal"
      modal
      :style="{ width: '580px', maxWidth: '95vw' }"
      :closable="!bulkSyncRunning"
    >
      <div class="space-y-4 text-xs">
        <!-- Informasi Mesin & Periode -->
        <div class="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-200 space-y-1">
          <div class="font-bold flex items-center gap-1.5">
            <i class="pi pi-server text-blue-600"></i>
            <span>Mesin Fingerprint (sdit.asysyuuraa.my.id)</span>
          </div>
          <p class="text-[11px] leading-relaxed text-blue-800/80 dark:text-blue-300">
            Tarik riwayat tap kehadiran langsung dari database mesin presensi untuk periode waktu tertentu. Data diproses secara aman per tanggal tanpa membebani server.
          </p>
        </div>

        <!-- Pilihan Opsi Periode Penarikan (Tampil saat tidak sedang running) -->
        <div v-if="!bulkSyncRunning && !bulkSyncFinished" class="space-y-3">
          <div class="font-bold text-slate-700 dark:text-slate-200">Pilih Periode Penarikan:</div>
          
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            <!-- Mode 1: 1 Bulan Penuh -->
            <div 
              class="p-3 rounded-xl border cursor-pointer transition flex flex-col justify-between"
              :class="bulkSyncMode === 'month' 
                ? 'border-emerald-500 bg-emerald-50/60 dark:bg-emerald-950/40 shadow-xs' 
                : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'"
              @click="bulkSyncMode = 'month'"
            >
              <div>
                <div class="font-bold text-slate-800 dark:text-white flex items-center gap-1.5 mb-1">
                  <i class="pi pi-calendar text-emerald-600"></i>
                  <span>1 Bulan Penuh</span>
                </div>
                <div class="text-[11px] text-slate-500">Tarik seluruh tanggal dalam 1 bulan kalender.</div>
              </div>
              <div class="mt-2 text-[10px] font-semibold text-emerald-600">Paling Sering Digunakan</div>
            </div>

            <!-- Mode 2: 1 Tahun 2026 -->
            <div 
              class="p-3 rounded-xl border cursor-pointer transition flex flex-col justify-between"
              :class="bulkSyncMode === 'year' 
                ? 'border-amber-500 bg-amber-50/60 dark:bg-amber-950/40 shadow-xs' 
                : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'"
              @click="bulkSyncMode = 'year'"
            >
              <div>
                <div class="font-bold text-slate-800 dark:text-white flex items-center gap-1.5 mb-1">
                  <i class="pi pi-history text-amber-600"></i>
                  <span>Tahun 2026</span>
                </div>
                <div class="text-[11px] text-slate-500">Dari 01 Januari 2026 s/d Hari ini.</div>
              </div>
              <div class="mt-2 text-[10px] font-semibold text-amber-600">Sinkronisasi Penuh</div>
            </div>

            <!-- Mode 3: Rentang Kustom -->
            <div 
              class="p-3 rounded-xl border cursor-pointer transition flex flex-col justify-between"
              :class="bulkSyncMode === 'custom' 
                ? 'border-blue-500 bg-blue-50/60 dark:bg-blue-950/40 shadow-xs' 
                : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'"
              @click="bulkSyncMode = 'custom'"
            >
              <div>
                <div class="font-bold text-slate-800 dark:text-white flex items-center gap-1.5 mb-1">
                  <i class="pi pi-sliders-h text-blue-600"></i>
                  <span>Rentang Kustom</span>
                </div>
                <div class="text-[11px] text-slate-500">Tentukan tanggal awal dan akhir bebas.</div>
              </div>
              <div class="mt-2 text-[10px] font-semibold text-blue-600">Fleksibel</div>
            </div>
          </div>

          <!-- Parameter Input Detail Sesuai Mode Terpilih -->
          <div class="p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30">
            <!-- Jika Mode Bulan -->
            <div v-if="bulkSyncMode === 'month'" class="flex flex-wrap items-center gap-3">
              <div>
                <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">Pilih Bulan &amp; Tahun:</label>
                <Calendar v-model="bulkSyncSelectedMonth" view="month" dateFormat="mm/yy" class="w-44 text-xs" :showIcon="true" />
              </div>
              <div class="text-slate-500 text-[11px] pt-3">
                Target: <b>{{ getDaysInMonthCount(bulkSyncSelectedMonth) }} hari</b> kalender
              </div>
            </div>

            <!-- Jika Mode Tahun -->
            <div v-else-if="bulkSyncMode === 'year'" class="space-y-1">
              <div class="font-bold text-slate-800 dark:text-white">Periode: 01 Januari 2026 s/d {{ formatDisplayDate(new Date()) }}</div>
              <div class="text-[11px] text-slate-500">
                Sistem akan memproses seluruh hari sejak 1 Januari 2026 secara bertahap dengan progress bar di bawah ini.
              </div>
            </div>

            <!-- Jika Mode Kustom -->
            <div v-else class="flex flex-wrap items-center gap-3">
              <div>
                <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">Dari Tanggal:</label>
                <Calendar v-model="bulkSyncCustomStart" dateFormat="yy-mm-dd" class="w-36 text-xs" :showIcon="true" />
              </div>
              <div>
                <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">Sampai Tanggal:</label>
                <Calendar v-model="bulkSyncCustomEnd" dateFormat="yy-mm-dd" class="w-36 text-xs" :showIcon="true" />
              </div>
            </div>
          </div>
        </div>

        <!-- Bagian Live Progress Saat Sedang Berjalan atau Selesai -->
        <div v-if="bulkSyncRunning || bulkSyncFinished" class="space-y-3 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-900/50">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-slate-800 dark:text-white flex items-center gap-2">
              <i v-if="bulkSyncRunning" class="pi pi-spin pi-spinner text-emerald-600"></i>
              <i v-else class="pi pi-check-circle text-emerald-600"></i>
              <span>{{ bulkSyncStatusText }}</span>
            </span>
            <span class="font-mono font-bold text-emerald-600">{{ bulkSyncPercent }}%</span>
          </div>

          <ProgressBar :value="bulkSyncPercent" :showValue="false" class="!h-2.5" />

          <!-- Statistik Ringkasan -->
          <div class="grid grid-cols-4 gap-2 text-center text-[11px]">
            <div class="p-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-700">
              <div class="text-slate-400 text-[10px]">Total Hari</div>
              <div class="font-bold text-slate-700 dark:text-slate-200">{{ bulkSyncTotalDays }}</div>
            </div>
            <div class="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200/60 text-emerald-800 dark:text-emerald-300">
              <div class="text-[10px]">Ada Data</div>
              <div class="font-bold">{{ bulkSyncSuccessDays }}</div>
            </div>
            <div class="p-2 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200/60 text-amber-800 dark:text-amber-300">
              <div class="text-[10px]">Libur/Kosong</div>
              <div class="font-bold">{{ bulkSyncEmptyDays }}</div>
            </div>
            <div class="p-2 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200/60 text-rose-800 dark:text-rose-300">
              <div class="text-[10px]">Gagal</div>
              <div class="font-bold">{{ bulkSyncFailedDays }}</div>
            </div>
          </div>

          <!-- Log Box Realtime -->
          <div class="max-h-36 overflow-y-auto space-y-1 p-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 font-mono text-[10px]">
            <div 
              v-for="(item, idx) in bulkSyncLogs" 
              :key="idx" 
              class="flex items-center justify-between py-0.5 border-b border-slate-100 dark:border-slate-800 last:border-none"
            >
              <span class="font-bold text-slate-700 dark:text-slate-300">{{ item.date }}</span>
              <span :class="item.status === 'success' ? 'text-emerald-600 dark:text-emerald-400' : item.status === 'empty' ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400'">
                {{ item.msg }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-between w-full">
          <Button 
            v-if="bulkSyncRunning" 
            label="Hentikan Proses" 
            icon="pi pi-stop" 
            severity="danger" 
            size="small" 
            text 
            @click="bulkSyncCancelRequested = true" 
          />
          <div v-else></div>

          <div class="flex items-center gap-2">
            <Button 
              label="Tutup" 
              severity="secondary" 
              size="small" 
              text 
              :disabled="bulkSyncRunning" 
              @click="showBulkSyncModal = false" 
            />
            <Button 
              v-if="!bulkSyncRunning && !bulkSyncFinished" 
              label="Mulai Tarik Data" 
              icon="pi pi-play" 
              severity="warning" 
              size="small" 
              class="font-semibold" 
              @click="startBulkSync" 
            />
            <Button 
              v-if="bulkSyncFinished" 
              label="Selesai &amp; Buka Tanggal Terpilih" 
              icon="pi pi-check" 
              severity="success" 
              size="small" 
              class="font-semibold" 
              @click="finishBulkSync" 
            />
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Dialog Riwayat & Log Kegagalan Sinkronisasi Fingerprint -->
    <Dialog 
      v-model:visible="showSyncLogsDialog" 
      header="Riwayat & Log Sinkronisasi Mesin Presensi (Manual & Cron Job)" 
      modal 
      :style="{ width: '780px', maxWidth: '95vw' }"
    >
      <div class="space-y-4">
        <!-- Toolbar Penarikan Data Massal (Bulk Sync Range) -->
        <div class="bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3 text-xs">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <div class="font-bold text-slate-700 dark:text-slate-200">Penarikan Massal Mesin Fingerprint</div>
              <div class="text-[11px] text-slate-500">
                Tarik data historis dari mesin fingerprint (sdit.asysyuuraa.my.id) untuk rentang waktu tertentu.
              </div>
            </div>
            <Button 
              icon="pi pi-refresh" 
              label="Refresh Log" 
              size="small" 
              text 
              class="!text-xs shrink-0" 
              :loading="loadingSyncLogs" 
              @click="fetchSyncLogs" 
            />
          </div>

          <!-- Quick Presets + Custom Date Range Toggle -->
          <div class="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-200/60 dark:border-slate-700/60">
            <Button 
              icon="pi pi-history" 
              label="Tarik dari 1 Jan 2026 s/d Hari Ini" 
              size="small" 
              severity="warning"
              outlined
              class="!text-xs font-semibold" 
              :loading="syncingRange" 
              @click="syncFromYearStart" 
            />
            <Button 
              icon="pi pi-calendar" 
              label="Tarik Bulan Ini (01 Okt - Hari Ini)" 
              size="small" 
              severity="info"
              outlined
              class="!text-xs font-semibold" 
              :loading="syncingRange" 
              @click="syncMonthToDate" 
            />
            <button
              type="button"
              class="px-2.5 py-1.5 rounded-lg border text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
              @click="showCustomRangeInputs = !showCustomRangeInputs"
            >
              <i class="pi pi-sliders-h mr-1 text-[11px]"></i>
              Pilih Rentang Kustom
            </button>
          </div>

          <!-- Custom Range Inputs (collapsible) -->
          <div v-if="showCustomRangeInputs" class="flex flex-wrap items-end gap-2.5 p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
            <div>
              <label class="block text-[10px] font-bold text-slate-600 dark:text-slate-400 mb-1">Dari Tanggal:</label>
              <Calendar v-model="customSyncStartDate" dateFormat="yy-mm-dd" class="w-36 text-xs" :showIcon="true" />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-slate-600 dark:text-slate-400 mb-1">Sampai Tanggal:</label>
              <Calendar v-model="customSyncEndDate" dateFormat="yy-mm-dd" class="w-36 text-xs" :showIcon="true" />
            </div>
            <Button 
              label="Mulai Tarik Data" 
              icon="pi pi-play" 
              size="small" 
              severity="success" 
              class="!text-xs font-semibold"
              :loading="syncingRange" 
              @click="syncCustomRange" 
            />
          </div>
        </div>

        <div v-if="syncLogs.length === 0" class="text-center py-8 text-slate-400 text-xs">
          Belum ada riwayat log sinkronisasi yang tercatat.
        </div>

        <div v-else class="space-y-3">
          <!-- Filter Tabs -->
          <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-100 dark:border-slate-800">
            <div class="flex flex-wrap items-center gap-1.5">
              <button
                v-for="flt in logFilterOptions"
                :key="flt.value"
                type="button"
                class="px-2.5 py-1 rounded-lg text-xs font-semibold transition cursor-pointer"
                :class="activeLogFilter === flt.value 
                  ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-xs' 
                  : 'bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300'"
                @click="activeLogFilter = flt.value"
              >
                {{ flt.label }} ({{ flt.count }})
              </button>
            </div>
            <span class="text-[11px] text-slate-400">Total: {{ syncLogs.length }} riwayat tersimpan</span>
          </div>

          <div v-if="filteredSyncLogs.length === 0" class="text-center py-8 text-slate-400 text-xs">
            Tidak ada riwayat log yang sesuai dengan filter ini.
          </div>

          <div v-else class="space-y-2.5 max-h-[60vh] overflow-y-auto pr-1">
            <div 
              v-for="log in filteredSyncLogs" 
              :key="log.id" 
              class="p-3.5 rounded-xl border text-xs space-y-1.5"
              :class="log.status === 'failed' 
                ? 'bg-rose-50/70 dark:bg-rose-950/30 border-rose-200 dark:border-rose-800' 
                : log.status === 'holiday'
                  ? 'bg-sky-50/70 dark:bg-sky-950/30 border-sky-200 dark:border-sky-800'
                  : log.status === 'partial' || log.status === 'empty' || log.status === 'likely_holiday'
                    ? 'bg-amber-50/70 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800'
                    : 'bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800'"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="flex items-center gap-2">
                  <span 
                    class="px-2 py-0.5 rounded font-bold uppercase text-[10px]"
                    :class="log.status === 'failed' 
                      ? 'bg-rose-200 text-rose-800 dark:bg-rose-900/60 dark:text-rose-200' 
                      : log.status === 'holiday'
                        ? 'bg-sky-200 text-sky-800 dark:bg-sky-900/60 dark:text-sky-200'
                        : log.status === 'empty' || log.status === 'partial' || log.status === 'likely_holiday'
                          ? 'bg-amber-200 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200'
                          : 'bg-emerald-200 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200'"
                  >
                    {{ log.status === 'failed' ? 'GAGAL' : log.status === 'holiday' ? 'HARI LIBUR' : log.status === 'likely_holiday' ? 'DIDUGA LIBUR' : log.status === 'empty' ? 'DATA KOSONG' : log.status === 'partial' ? 'SEBAGIAN' : 'BERHASIL' }}
                  </span>
                  <span 
                    class="px-2 py-0.5 rounded font-semibold text-[10px] uppercase"
                    :class="log.source === 'cron' 
                      ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300' 
                      : log.source === 'manual_range'
                        ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300'
                        : 'bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300'"
                  >
                    {{ log.source === 'cron' ? 'Cron Otomatis' : log.source === 'manual_range' ? 'Rekap Tarik Massal' : 'Tarik Manual' }}
                  </span>
                  <span class="font-bold text-slate-800 dark:text-white">
                    Target: {{ log.date_target }}
                  </span>
                  <Button 
                    v-if="!log.date_target.includes(' s/d ')"
                    label="Buka Presensi Tanggal Ini" 
                    icon="pi pi-arrow-up-right" 
                    size="small" 
                    text 
                    class="!text-[11px] !py-0 !px-1.5"
                    @click="goToLogDate(log.date_target)"
                  />
                </div>
                <span class="text-[11px] text-slate-500 font-mono">{{ log.timestamp }}</span>
              </div>

            <div class="text-slate-700 dark:text-slate-200 font-medium">
              {{ log.message }}
            </div>

            <div v-if="log.error_detail" class="p-2 rounded bg-rose-100/80 dark:bg-rose-900/40 text-rose-800 dark:text-rose-200 font-mono text-[11px] break-all">
              <b>Detail Kegagalan:</b> {{ log.error_detail }}
            </div>

            <div v-if="log.unmatched_logs && log.unmatched_logs.length > 0" class="text-[11px] text-amber-800 dark:text-amber-300 space-y-1.5 pt-1">
              <div class="font-bold">Log Mesin Belum Cocok NIK/Nama ({{ log.unmatched_logs.length }}) — Klik untuk Hubungkan ke Pegawai:</div>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="rawItem in log.unmatched_logs"
                  :key="rawItem"
                  type="button"
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-100 hover:bg-amber-200 dark:bg-amber-900/50 text-amber-900 dark:text-amber-200 border border-amber-300 dark:border-amber-700 font-semibold transition cursor-pointer"
                  title="Klik untuk menautkan ID Fingerprint ini ke Pegawai SDM"
                  @click="openPinMappingModal(rawItem)"
                >
                  <i class="pi pi-link text-[10px]"></i>
                  <span>{{ rawItem }}</span>
                </button>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Dialog Quick-View Daftar Pegawai per Kategori Card (Hadir, Terlambat, Sakit, Izin, Cuti, Alpa, Belum Presensi) -->
    <Dialog 
      v-model:visible="showCategoryModal" 
      :header="categoryModalTitle" 
      modal 
      :style="{ width: '640px', maxWidth: '95vw' }"
    >
      <div class="space-y-3">
        <!-- Quick Filter Tabs inside Modal so user can switch categories easily -->
        <div class="flex flex-wrap gap-1.5 pb-2 border-b border-slate-100 dark:border-slate-800">
          <button
            v-for="tab in categoryTabs"
            :key="tab.key"
            type="button"
            class="px-2.5 py-1 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
            :class="selectedCategory === tab.key 
              ? 'bg-slate-800 text-white dark:bg-white dark:text-slate-900 shadow-xs' 
              : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'"
            @click="selectedCategory = tab.key"
          >
            <span>{{ tab.label }}</span>
            <span class="px-1.5 py-0.2 rounded-full text-[10px] bg-black/10 dark:bg-white/20 font-bold">{{ tab.count }}</span>
          </button>
        </div>

        <div v-if="categoryModalList.length === 0" class="text-center py-10 text-slate-400 text-xs">
          <i class="pi pi-check-circle text-3xl text-slate-300 mb-2 block"></i>
          Tidak ada pegawai pada kategori <b>{{ categoryModalTitle }}</b> untuk tanggal {{ formattedDate }}.
        </div>

        <div v-else class="space-y-2 max-h-[58vh] overflow-y-auto pr-1">
          <div 
            v-for="emp in categoryModalList" 
            :key="emp.employee_id"
            class="flex items-center justify-between gap-3 p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/50"
          >
            <div class="flex items-center gap-3 min-w-0">
              <Avatar 
                :image="emp.photo_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(emp.nama_lengkap || '')}&background=random`" 
                shape="circle" 
                size="normal"
                class="shrink-0"
              />
              <div class="min-w-0">
                <div class="font-bold text-sm text-slate-800 dark:text-white truncate">{{ emp.nama_lengkap }}</div>
                <div class="text-xs text-slate-400 truncate">
                  {{ emp.position || 'Pegawai' }} • <span class="text-emerald-600 dark:text-emerald-400 font-medium">{{ emp.unit_name || 'Yayasan' }}</span>
                </div>
                <div v-if="emp.notes" class="text-[11px] text-slate-500 mt-0.5 italic truncate">
                  "{{ emp.notes }}"
                </div>
              </div>
            </div>

            <div class="text-right shrink-0 space-y-1">
              <div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold" :class="getStatusBadgeClass(emp.status)">
                  {{ getStatusLabel(emp.status) }}
                </span>
              </div>
              <div v-if="emp.check_in || emp.check_out" class="text-[11px] font-mono text-slate-600 dark:text-slate-300">
                <span title="Jam Masuk">In: <b>{{ formatTimeShort(emp.check_in) }}</b></span>
                <span class="mx-1 text-slate-300">|</span>
                <span title="Jam Pulang">Out: <b>{{ formatTimeShort(emp.check_out) }}</b></span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Tutup" icon="pi pi-times" severity="secondary" text size="small" @click="showCategoryModal = false" />
      </template>
    </Dialog>

    <!-- Dialog Pengaturan Jam Masuk, Jam Pulang & Toleransi Keterlambatan -->
    <Dialog 
      v-model:visible="showWorkHoursDialog" 
      header="Pengaturan Jam Kerja & Toleransi Keterlambatan" 
      modal 
      :style="{ width: '480px', maxWidth: '95vw' }"
    >
      <div class="space-y-4">
        <div class="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-900 dark:text-emerald-200 leading-relaxed">
          Pengaturan ini berlaku otomatis untuk <b>Penarikan Mesin Fingerprint</b> maupun <b>Presensi Mandiri GPS</b>. Anda juga dapat mengatur titik koordinat &amp; radius GPS lengkap di menu
          <NuxtLink to="/dashboard/settings/sekolah" class="font-bold underline hover:text-emerald-700">
            Pengaturan &rarr; Identitas &amp; Lokasi Sekolah
          </NuxtLink>.
        </div>

        <!-- Bagian 1: Jam Masuk & Toleransi -->
        <div class="p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/40 space-y-3">
          <div class="font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
            <i class="pi pi-sign-in text-emerald-600"></i>
            <span>Jam Masuk &amp; Toleransi</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">Jam Masuk Sekolah</label>
              <InputText v-model="geofenceConfig.work_start_time" placeholder="06:45" class="w-full text-xs font-mono" />
              <span class="text-[10px] text-slate-400">Default: 06:45</span>
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">Toleransi Terlambat</label>
              <InputNumber 
                v-model="geofenceConfig.late_tolerance_minutes" 
                :min="0" 
                :max="120" 
                suffix=" menit" 
                class="w-full text-xs" 
                inputClass="w-full font-mono"
              />
              <span class="text-[10px] text-slate-400">Lewat batas dihitung Terlambat</span>
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-1">Toleransi Pulang Cepat</label>
              <InputNumber 
                v-model="geofenceConfig.early_tolerance_minutes" 
                :min="0" 
                :max="60" 
                suffix=" menit" 
                class="w-full text-xs" 
                inputClass="w-full font-mono"
              />
              <span class="text-[10px] text-slate-400">Batas toleransi sebelum jadwal</span>
            </div>
          </div>
        </div>

        <!-- Bagian 2: Jam Kepulangan Berdasarkan Hari & Unit -->
        <div class="p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/40 space-y-3">
          <div class="font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
            <i class="pi pi-sign-out text-blue-600"></i>
            <span>Jadwal Jam Kepulangan (Beda Hari &amp; Unit)</span>
          </div>

          <div class="space-y-2">
            <div class="text-[11px] font-bold text-slate-600 dark:text-slate-300">
              📅 Senin s/d Kamis:
            </div>
            <div class="grid grid-cols-3 gap-2">
              <div>
                <label class="block text-[10px] font-semibold text-slate-600 dark:text-slate-400 mb-0.5">Unit RA</label>
                <InputText v-model="geofenceConfig.schedule_ra_mon_thu" placeholder="14:00" class="w-full text-xs font-mono" />
              </div>
              <div>
                <label class="block text-[10px] font-semibold text-slate-600 dark:text-slate-400 mb-0.5">Unit SDIT</label>
                <InputText v-model="geofenceConfig.schedule_sdit_mon_thu" placeholder="15:00" class="w-full text-xs font-mono" />
              </div>
              <div>
                <label class="block text-[10px] font-semibold text-slate-600 dark:text-slate-400 mb-0.5">Unit SMPIT</label>
                <InputText v-model="geofenceConfig.schedule_smpit_mon_thu" placeholder="15:30" class="w-full text-xs font-mono" />
              </div>
            </div>

            <div class="pt-1.5">
              <label class="block text-[10px] font-semibold text-slate-600 dark:text-slate-400 mb-0.5">
                🏢 Unit Lainnya / Yayasan / Non-Unit (Senin - Kamis)
              </label>
              <InputText 
                v-model="geofenceConfig.schedule_default_mon_thu" 
                placeholder="15:30 (Otomatis ikuti unit terakhir pulang)" 
                class="w-full text-xs font-mono" 
              />
              <span class="text-[10px] text-slate-400">
                Jika dikosongkan, otomatis mengikuti unit sekolah yang paling terakhir pulang (default: 15:30).
              </span>
            </div>
          </div>

          <div class="pt-2 border-t border-slate-200/60 dark:border-slate-700/60 grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                🕌 Jum'at (Semua Unit)
              </label>
              <InputText v-model="geofenceConfig.schedule_friday" placeholder="11:30" class="w-full text-xs font-mono" />
              <span class="text-[10px] text-slate-400">Pulang sebelum Sholat Jum'at</span>
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                🏫 Sabtu (Semua Unit)
              </label>
              <InputText v-model="geofenceConfig.schedule_saturday" placeholder="12:00" class="w-full text-xs font-mono" />
              <span class="text-[10px] text-slate-400">Pulang tengah hari</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="flex items-center justify-between w-full">
          <NuxtLink 
            to="/dashboard/settings/sekolah" 
            class="text-xs text-slate-500 hover:text-emerald-600 font-medium flex items-center gap-1"
          >
            <i class="pi pi-external-link text-[10px]"></i>
            Buka Pengaturan Lokasi Lengkap
          </NuxtLink>
          <div class="flex gap-2">
            <Button label="Batal" severity="secondary" text size="small" @click="showWorkHoursDialog = false" />
            <Button label="Simpan Jam Kerja" icon="pi pi-save" severity="success" size="small" :loading="savingWorkHours" @click="saveWorkHoursConfig" />
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Dialog Hubungkan PIN/Nama Mesin Fingerprint ke Pegawai SDM -->
    <Dialog
      v-model:visible="showPinMappingModal"
      header="Hubungkan ID Fingerprint ke Pegawai SDM"
      modal
      :style="{ width: '480px', maxWidth: '95vw' }"
    >
      <div class="space-y-4 text-xs">
        <div class="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200">
          <div class="font-bold mb-1">Data dari Mesin Fingerprint:</div>
          <div class="font-mono text-sm font-bold">{{ pinMappingForm.rawLabel }}</div>
          <div class="mt-1 opacity-80">ID/PIN Mesin: <b>{{ pinMappingForm.fp_nik }}</b> &bull; Nama Mesin: <b>{{ pinMappingForm.fp_name }}</b></div>
        </div>

        <div class="space-y-1.5">
          <label class="font-bold text-slate-700 dark:text-slate-200 block">Pilih Pegawai di Database Asy-Syuuraa:</label>
          <Dropdown
            v-model="pinMappingForm.employee_id"
            :options="employeeSelectOptions"
            optionLabel="label"
            optionValue="value"
            filter
            filterPlaceholder="Cari nama atau NIK pegawai..."
            placeholder="Pilih Pegawai..."
            class="w-full text-xs"
          />
          <p class="text-[11px] text-slate-500">
            Setelah disimpan, setiap kali ID Fingerprint <b>{{ pinMappingForm.fp_nik }}</b> melakukan tap, sistem akan otomatis mencatatnya ke pegawai tersebut.
          </p>
        </div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text size="small" @click="showPinMappingModal = false" />
        <Button label="Simpan & Tarik Ulang" icon="pi pi-link" severity="success" size="small" :loading="savingPinMapping" @click="savePinMapping" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const toast = useToast()
const api = useApi()

// Local timezone safe helper
function formatLocalDate(d: Date): string {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatDisplayDate(d: Date | null): string {
  if (!d) return ''
  return new Intl.DateTimeFormat('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(d)
}

function formatLocalDateTime(dateBase: Date, timeObj: Date | null): string | null {
  if (!timeObj) return null
  const year = dateBase.getFullYear()
  const month = String(dateBase.getMonth() + 1).padStart(2, '0')
  const day = String(dateBase.getDate()).padStart(2, '0')
  const hours = String(timeObj.getHours()).padStart(2, '0')
  const minutes = String(timeObj.getMinutes()).padStart(2, '0')
  const seconds = String(timeObj.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
}

const filterDate = ref(new Date())
const filterUnit = ref(null)
const units = ref<any[]>([])
const attendances = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const syncingFingerprint = ref(false)
const isSavedInDb = ref(false)

// Holiday & Calendar info for active date
const dateInfo = ref<{
  date: string
  day_name: string
  is_holiday: boolean
  holiday_desc: string
  is_sunday: boolean
} | null>(null)

// Work Hours & Late Tolerance State
const showWorkHoursDialog = ref(false)
const savingWorkHours = ref(false)
const geofenceConfig = reactive({
  is_enabled: true,
  location_name: 'Komplek Sekolah Asy-Syuuraa Batam',
  latitude: 1.123456,
  longitude: 104.012345,
  radius_meters: 30,
  work_start_time: '06:45',
  work_end_time: '16:00',
  late_tolerance_minutes: 5,
  early_tolerance_minutes: 0,
  schedule_ra_mon_thu: '14:00',
  schedule_sdit_mon_thu: '15:00',
  schedule_smpit_mon_thu: '15:30',
  schedule_friday: '11:30',
  schedule_saturday: '12:00',
  schedule_default_mon_thu: '16:00'
})

// Quick-View Category Modal State
type CategoryKey = 'HADIR' | 'LATE' | 'SICK' | 'PERMIT' | 'LEAVE' | 'ABSENT' | 'UNRECORDED'
const showCategoryModal = ref(false)
const selectedCategory = ref<CategoryKey>('HADIR')

function openCategoryModal(cat: CategoryKey) {
  selectedCategory.value = cat
  showCategoryModal.value = true
}

function formatTimeShort(dt: Date | null): string {
  if (!dt || !(dt instanceof Date) || isNaN(dt.getTime())) return '--:--'
  const h = String(dt.getHours()).padStart(2, '0')
  const m = String(dt.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

function getExpectedCheckoutTime(dateObj: Date | string, unitName?: string | null): string | null {
  const d = typeof dateObj === 'string' ? new Date(dateObj) : dateObj
  if (!d || isNaN(d.getTime())) return null
  const day = d.getDay() // 0 = Sunday, 5 = Friday, 6 = Saturday
  if (day === 0) return null // Sunday / Libur
  if (day === 5) return geofenceConfig.schedule_friday || '11:30'
  if (day === 6) return geofenceConfig.schedule_saturday || '12:00'

  const u = (unitName || '').toUpperCase().trim()
  const defaultVal = geofenceConfig.schedule_default_mon_thu || '15:30'

  if (u.includes('YAYASAN') || u.startsWith('YYS')) return defaultVal
  if (/\bRA\b/.test(u) || u.startsWith('RA ') || u === 'RA' || u.includes('RAUDHATUL')) return geofenceConfig.schedule_ra_mon_thu || '14:00'
  if (u.includes('SDIT') || /\bSD\b/.test(u)) return geofenceConfig.schedule_sdit_mon_thu || '15:00'
  if (u.includes('SMPIT') || /\bSMP\b/.test(u)) return geofenceConfig.schedule_smpit_mon_thu || '15:30'

  return defaultVal
}

function getEarlyLeaveInfo(row: any) {
  if (!row.check_out || !isAttendancePhysical(row.status)) return null
  const outDate = row.check_out instanceof Date ? row.check_out : new Date(row.check_out)
  if (isNaN(outDate.getTime())) return null

  // Overtime if hour >= 18
  if (outDate.getHours() >= 18) return null

  const targetDate = filterDate.value || new Date()
  const expStr = getExpectedCheckoutTime(targetDate, row.employee?.unit?.name)
  if (!expStr) return null

  const [eh, em] = expStr.split(':').map(Number)
  const expMinutes = eh * 60 + em
  const actMinutes = outDate.getHours() * 60 + outDate.getMinutes()
  const earlyTol = Number(geofenceConfig.early_tolerance_minutes || 0)

  const diff = expMinutes - actMinutes
  if (diff > earlyTol) {
    const notesLower = (row.notes || '').toLowerCase()
    const isDuty = notesLower.includes('tugas luar') || notesLower.includes('dinas') || notesLower.includes('dispensasi') || notesLower.includes('izin')
    return {
      isEarly: true,
      earlyMinutes: diff,
      expectedTime: expStr,
      isDuty
    }
  }
  return null
}

// Step-by-Step Progress & Sync Logs State
const syncProgress = ref({
  active: false,
  stageText: '',
  current: 0,
  total: 0,
  percent: 0,
  currentEmployeeName: '',
  failed: 0
})
const showSyncLogsDialog = ref(false)
const loadingSyncLogs = ref(false)
const syncLogs = ref<any[]>([])
const failedLogsCount = computed(() => syncLogs.value.filter(l => l.status === 'failed').length)

const activeLogFilter = ref<'all' | 'cron' | 'manual' | 'issues'>('all')
const cronLogsCount = computed(() => syncLogs.value.filter(l => l.source === 'cron').length)
const manualLogsCount = computed(() => syncLogs.value.filter(l => l.source === 'manual' || l.source === 'manual_range').length)
const issuesLogsCount = computed(() => syncLogs.value.filter(l => 
  l.status === 'failed' || l.status === 'partial' || (l.unmatched_logs && l.unmatched_logs.length > 0) || Boolean(l.error_detail)
).length)

const logFilterOptions = computed(() => [
  { label: 'Semua Log', value: 'all' as const, count: syncLogs.value.length },
  { label: '🤖 Cron Otomatis', value: 'cron' as const, count: cronLogsCount.value },
  { label: '🖐️ Tarik Manual', value: 'manual' as const, count: manualLogsCount.value },
  { label: '⚠️ Ada Kendala/Catatan', value: 'issues' as const, count: issuesLogsCount.value },
])

const filteredSyncLogs = computed(() => {
  if (activeLogFilter.value === 'cron') {
    return syncLogs.value.filter(l => l.source === 'cron')
  }
  if (activeLogFilter.value === 'manual') {
    return syncLogs.value.filter(l => l.source === 'manual' || l.source === 'manual_range')
  }
  if (activeLogFilter.value === 'issues') {
    return syncLogs.value.filter(l => 
      l.status === 'failed' || l.status === 'partial' || (l.unmatched_logs && l.unmatched_logs.length > 0) || Boolean(l.error_detail)
    )
  }
  return syncLogs.value
})

// Grouped status options with extended leave types
const statusOptions = [
  {
    group: 'Status Awal',
    items: [
      { label: 'Belum Presensi', value: 'UNRECORDED' }
    ]
  },
  {
    group: 'Kehadiran Fisik',
    items: [
      { label: 'Hadir Tepat Waktu', value: 'PRESENT' },
      { label: 'Hadir Terlambat', value: 'LATE' },
    ]
  },
  {
    group: 'Izin & Medis',
    items: [
      { label: 'Sakit (Surat Dokter / Ket.)', value: 'SICK' },
      { label: 'Izin Biasa / Pribadi', value: 'PERMIT' },
      { label: 'Dispensasi / Tugas Luar', value: 'DISPENSATION' },
    ]
  },
  {
    group: 'Cuti Resmi Yayasan',
    items: [
      { label: 'Cuti Melahirkan (3 Bulan)', value: 'LEAVE_MATERNITY' },
      { label: 'Cuti Menikah (3 Hari)', value: 'LEAVE_MARRIAGE' },
      { label: 'Cuti Berkabung (Kedukaan)', value: 'LEAVE_BEREAVEMENT' },
      { label: 'Cuti Ibadah (Haji / Umroh)', value: 'LEAVE_PILGRIMAGE' },
      { label: 'Cuti di Luar Tanggungan', value: 'LEAVE_UNPAID' },
      { label: 'Cuti Tahunan', value: 'LEAVE_ANNUAL' },
    ]
  },
  {
    group: 'Kedisiplinan',
    items: [
      { label: 'Alpa / Mangkir', value: 'ABSENT' },
    ]
  }
]

const formattedDate = computed(() => {
  if (!filterDate.value) return ''
  return filterDate.value.toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

const isTodaySelected = computed(() => {
  if (!filterDate.value) return false
  return formatLocalDate(filterDate.value) === formatLocalDate(new Date())
})

function changeDate(offsetDays: number) {
  const d = new Date(filterDate.value)
  d.setDate(d.getDate() + offsetDays)
  filterDate.value = d
  fetchData()
}

function setToday() {
  filterDate.value = new Date()
  fetchData()
}

function isAttendancePhysical(status?: string | null) {
  return status === 'PRESENT' || status === 'LATE'
}

function isLockedBySystem(row: any): boolean {
  if (!row) return false
  if (row.check_in_distance != null) return true
  const n = String(row.notes || '')
  return n.includes('Sinkronisasi Fingerprint') || n.includes('Presensi Mandiri GPS')
}

function extractManualNote(rawNotes?: string | null): string {
  if (!rawNotes) return ''
  let s = String(rawNotes).trim()
  s = s.replace(/^Tidak ada data di Fingerprint\s*(—|-|:|\|)?\s*/i, '')
  s = s.replace(/^Ket\.\s*Manual\s*:\s*/i, '')
  if (s.toLowerCase() === 'tidak ada data di fingerprint') return ''
  return s.trim()
}

function getStatusLabel(val?: string | null) {
  if (!val || val === 'UNRECORDED') return 'Belum Presensi'
  for (const group of statusOptions) {
    const found = group.items.find(i => i.value === val)
    if (found) return found.label
  }
  return val
}

function getStatusBadgeClass(status?: string | null) {
  if (!status || status === 'UNRECORDED') return 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600'
  if (status === 'PRESENT') return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
  if (status === 'LATE') return 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
  if (status === 'SICK') return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-950 dark:text-yellow-300'
  if (status === 'PERMIT' || status === 'DISPENSATION') return 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
  if (status.startsWith('LEAVE_')) return 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300'
  return 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
}

const summary = computed(() => {
  const hadir = attendances.value.filter(a => a.status === 'PRESENT' || a.status === 'LATE').length
  const terlambat = attendances.value.filter(a => a.status === 'LATE').length
  const sakit = attendances.value.filter(a => a.status === 'SICK').length
  const izin = attendances.value.filter(a => a.status === 'PERMIT' || a.status === 'DISPENSATION').length
  const cuti = attendances.value.filter(a => typeof a.status === 'string' && a.status.startsWith('LEAVE_')).length
  const alpa = attendances.value.filter(a => a.status === 'ABSENT').length
  const belum = attendances.value.filter(a => !a.status || a.status === 'UNRECORDED').length
  const totalSudah = attendances.value.length - belum

  return { hadir, terlambat, sakit, izin, cuti, alpa, belum, totalSudah }
})

const categoryTabs = computed(() => [
  { key: 'HADIR' as CategoryKey, label: 'Hadir (Semua)', count: summary.value.hadir },
  { key: 'LATE' as CategoryKey, label: 'Terlambat', count: summary.value.terlambat },
  { key: 'SICK' as CategoryKey, label: 'Sakit', count: summary.value.sakit },
  { key: 'PERMIT' as CategoryKey, label: 'Izin / Dinas', count: summary.value.izin },
  { key: 'LEAVE' as CategoryKey, label: 'Cuti', count: summary.value.cuti },
  { key: 'ABSENT' as CategoryKey, label: 'Alpa', count: summary.value.alpa },
  { key: 'UNRECORDED' as CategoryKey, label: 'Belum Presensi', count: summary.value.belum }
])

const categoryModalTitle = computed(() => {
  const map: Record<CategoryKey, string> = {
    HADIR: 'Daftar Pegawai Hadir (Tepat & Terlambat)',
    LATE: 'Daftar Pegawai Terlambat',
    SICK: 'Daftar Pegawai Sakit',
    PERMIT: 'Daftar Pegawai Izin / Tugas Luar',
    LEAVE: 'Daftar Pegawai Cuti Resmi',
    ABSENT: 'Daftar Pegawai Alpa (Tanpa Keterangan)',
    UNRECORDED: 'Daftar Pegawai Belum Presensi'
  }
  return map[selectedCategory.value] || 'Daftar Pegawai'
})

const categoryModalList = computed(() => {
  const list = attendances.value || []
  switch (selectedCategory.value) {
    case 'HADIR':
      return list.filter(a => a.status === 'PRESENT' || a.status === 'LATE')
    case 'LATE':
      return list.filter(a => a.status === 'LATE')
    case 'SICK':
      return list.filter(a => a.status === 'SICK')
    case 'PERMIT':
      return list.filter(a => a.status === 'PERMIT' || a.status === 'DISPENSATION')
    case 'LEAVE':
      return list.filter(a => typeof a.status === 'string' && a.status.startsWith('LEAVE_'))
    case 'ABSENT':
      return list.filter(a => a.status === 'ABSENT')
    case 'UNRECORDED':
      return list.filter(a => !a.status || a.status === 'UNRECORDED')
    default:
      return []
  }
})

const fetchGeofenceConfig = async () => {
  try {
    const res = await api.get<any>('/sdm/settings/geofence')
    if (res) {
      Object.assign(geofenceConfig, res)
    }
  } catch (e) {
    console.error('Failed to load geofence settings:', e)
  }
}

const saveWorkHoursConfig = async () => {
  savingWorkHours.value = true
  try {
    await api.put('/sdm/settings/geofence', { ...geofenceConfig })
    toast.add({
      severity: 'success',
      summary: 'Tersimpan',
      detail: `Jam kerja (${geofenceConfig.work_start_time} - ${geofenceConfig.work_end_time}) & toleransi (${geofenceConfig.late_tolerance_minutes || 0} menit) berhasil diperbarui.`,
      life: 4000
    })
    showWorkHoursDialog.value = false
  } catch (e) {
    toast.add({
      severity: 'error',
      summary: 'Gagal',
      detail: 'Gagal menyimpan pengaturan jam kerja.',
      life: 3000
    })
  } finally {
    savingWorkHours.value = false
  }
}

const fetchUnits = async () => {
  try {
    const data = await api.get<any[]>('/units')
    units.value = data || []
  } catch (error) {
    console.error('Failed to fetch units')
  }
}

const fetchData = async () => {
  if (!filterDate.value) return
  
  loading.value = true
  try {
    const dateStr = formatLocalDate(filterDate.value)

    // Fetch date info & holiday calendar status
    try {
      dateInfo.value = await api.get<any>(`/sdm/attendance/date-info?date=${dateStr}`)
    } catch {
      dateInfo.value = null
    }
    
    // Fetch active employees
    const empQuery = new URLSearchParams({ is_active: 'true' })
    if (filterUnit.value) empQuery.append('unit_id', filterUnit.value)
    
    const emps = await api.get<any[]>(`/sdm/employees?${empQuery.toString()}`)
    
    // Fetch existing attendance records from database for this date
    const attQuery = new URLSearchParams({ date: dateStr })
    if (filterUnit.value) attQuery.append('unit_id', filterUnit.value)
    
    const existingAtts = await api.get<any[]>(`/sdm/attendance?${attQuery.toString()}`) || []
    
    // Check if there are real saved records in database for this date
    isSavedInDb.value = existingAtts.length > 0
    
    // Merge data: If record exists in DB, use its real status & check-in. If not, mark as UNRECORDED
    const isHolidayDay = Boolean(dateInfo.value?.is_holiday)
    const defaultNote = isHolidayDay 
      ? `Libur: ${dateInfo.value?.holiday_desc || 'Hari Libur'}` 
      : 'Tidak ada data di Fingerprint'

    attendances.value = (emps || []).map(emp => {
      const existing = existingAtts.find((a: any) => a.employee_id === emp.id)
      
      let check_in: Date | null = null
      let check_out: Date | null = null
      
      if (existing) {
        if (existing.check_in) check_in = new Date(existing.check_in)
        if (existing.check_out) check_out = new Date(existing.check_out)
      }

      const rawNotes = existing?.notes || (existing ? (isHolidayDay ? defaultNote : 'Tidak ada data di Fingerprint') : '')
      const isAutoLocked = (existing?.check_in_distance != null) 
        || rawNotes.includes('Sinkronisasi Fingerprint') 
        || rawNotes.includes('Presensi Mandiri GPS')
        || rawNotes.includes('Piket')
        || rawNotes.includes('Hari Libur')
      
      return {
        employee_id: emp.id,
        nama_lengkap: emp.nama_lengkap,
        nip: emp.nip,
        position: emp.position,
        unit_name: emp.unit?.name,
        photo_url: emp.photo_url,
        status: existing?.status || 'UNRECORDED',
        check_in: check_in,
        check_out: check_out,
        check_in_distance: existing?.check_in_distance,
        notes: isAutoLocked ? (rawNotes || `Presensi Mandiri GPS (Jarak ${existing?.check_in_distance}m)`) : (rawNotes || defaultNote),
        manual_notes: isAutoLocked ? '' : extractManualNote(rawNotes)
      }
    })
    
  } catch (error) {
    console.error('Failed to load attendance:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data presensi', life: 3000 })
  } finally {
    loading.value = false
  }
}

const fetchSyncLogs = async () => {
  loadingSyncLogs.value = true
  try {
    const data = await api.get<any[]>('/sdm/attendance/sync-logs?limit=100')
    syncLogs.value = data || []
  } catch (e) {
    console.error('Failed to fetch sync logs:', e)
  } finally {
    loadingSyncLogs.value = false
  }
}

const openSyncLogsDialog = () => {
  showSyncLogsDialog.value = true
  fetchSyncLogs()
}

const syncFingerprint = async () => {
  if (!filterDate.value) return
  syncingFingerprint.value = true
  const dateStr = formatLocalDate(filterDate.value)

  syncProgress.value = {
    active: true,
    stageText: `Menghubungi mesin presensi (sdit.asysyuuraa.my.id) untuk tanggal ${dateStr}...`,
    current: 0,
    total: 0,
    percent: 5,
    currentEmployeeName: '',
    failed: 0
  }

  try {
    // Tahap 1: Tarik daftar antrian log dari mesin fingerprint
    const res = await api.post<any>('/sdm/attendance/sync-fingerprint', {
      date: dateStr,
      mode: 'fetch_raw',
      source: 'manual'
    })

    if (res?.status === 'empty' || !res?.queue || res.queue.length === 0) {
      toast.add({
        severity: 'warn',
        summary: 'Data Kosong',
        detail: res?.message || `Tidak ada data tap mesin fingerprint pada tanggal ${dateStr}.`,
        life: 4000
      })
      await fetchSyncLogs()
      return
    }

    const queue: any[] = res.queue
    const rawCount: number = res.raw_count || 0
    const unmatchedLogs: string[] = res.unmatched_logs || []

    syncProgress.value.total = queue.length
    syncProgress.value.stageText = `Menyinkronkan presensi pegawai satu per satu (${rawCount} log tap)...`

    let successCount = 0
    let failCount = 0
    const errorDetails: string[] = []

    // Tahap 2: Proses satu per satu pegawai agar terlihat progress-nya dan tidak membebani server
    for (let i = 0; i < queue.length; i++) {
      const item = queue[i]
      syncProgress.value.current = i + 1
      syncProgress.value.currentEmployeeName = `${item.nama_lengkap} (${item.nik_kepegawaian || '-'})`
      syncProgress.value.percent = Math.round(((i + 1) / queue.length) * 100)

      try {
        const singleRes = await api.post<any>('/sdm/attendance/sync-fingerprint', {
          date: dateStr,
          mode: 'process_one',
          employee_id: item.employee_id,
          raw_logs: item.punches
        })
        successCount++

        // Update baris di tabel secara langsung (real-time visual update)
        const rowInTable = attendances.value.find(a => a.employee_id === item.employee_id)
        if (rowInTable && singleRes) {
          rowInTable.status = singleRes.attendance_status || 'PRESENT'
          if (singleRes.check_in) {
            const [ih, im, is] = singleRes.check_in.split(':').map(Number)
            const inD = new Date(filterDate.value)
            inD.setHours(ih || 0, im || 0, is || 0, 0)
            rowInTable.check_in = inD
          }
          if (singleRes.check_out) {
            const [oh, om, os] = singleRes.check_out.split(':').map(Number)
            const outD = new Date(filterDate.value)
            outD.setHours(oh || 0, om || 0, os || 0, 0)
            rowInTable.check_out = outD
          }
          rowInTable.notes = `Sinkronisasi Fingerprint (${item.punches.length}x tap)`
        }
      } catch (errOne: any) {
        failCount++
        syncProgress.value.failed = failCount
        errorDetails.push(`${item.nama_lengkap}: ${errOne?.data?.detail || 'Gagal simpan'}`)
      }
    }

    isSavedInDb.value = true

    // Tahap 3: Catat hasil akhir ke Log Sinkronisasi (sekaligus menandai pegawai tanpa data finger sebagai 'Tidak ada data di Fingerprint')
    const finalStatus = failCount === 0 ? 'success' : (successCount > 0 ? 'partial' : 'failed')
    const finalMsg = `Berhasil menyinkronkan ${successCount} dari ${queue.length} pegawai (${rawCount} log mesin) pada tanggal ${dateStr}.`
    await api.post('/sdm/attendance/sync-logs', {
      date: dateStr,
      source: 'manual',
      status: finalStatus,
      raw_count: rawCount,
      synced_employees: successCount,
      failed_employees: failCount,
      unmatched_logs: unmatchedLogs,
      message: finalMsg,
      error_detail: errorDetails.length > 0 ? errorDetails.join('; ') : null
    })

    const extraInfo = unmatchedLogs.length
      ? ` (${unmatchedLogs.length} nama di mesin belum cocok NIK/Nama)`
      : ''
    toast.add({
      severity: failCount > 0 ? 'warn' : 'success',
      summary: 'Sinkronisasi Selesai',
      detail: finalMsg + extraInfo,
      life: 5000
    })

    await fetchData()
    await fetchSyncLogs()
  } catch (error: any) {
    console.error('Sync fingerprint error:', error)
    const errDetail = error?.data?.detail || 'Koneksi ke mesin presensi (192.168.188.222) terputus atau timeout. Detail telah dicatat di Log Sinkronisasi.'
    toast.add({
      severity: 'error',
      summary: 'Gagal Sinkronisasi Mesin',
      detail: errDetail,
      life: 6000
    })
    await fetchSyncLogs()
  } finally {
    syncingFingerprint.value = false
    setTimeout(() => {
      syncProgress.value.active = false
    }, 1500)
  }
}

const setAllPresent = () => {
  attendances.value.forEach(a => {
    if (isLockedBySystem(a)) return
    // Only update if not already an official permit/sick/cuti
    if (!a.status || a.status === 'UNRECORDED' || a.status === 'ABSENT') {
      a.status = 'PRESENT'
      if (!a.check_in) {
        const def = new Date(filterDate.value)
        def.setHours(7, 0, 0, 0)
        a.check_in = def
      }
    }
  })
  toast.add({ 
    severity: 'info', 
    summary: 'Set Hadir Manual', 
    detail: 'Pegawai yang tidak memiliki data Fingerprint/GPS telah diatur Hadir Tepat Waktu (07:00). Klik Simpan untuk mempermanenkan.', 
    life: 3000 
  })
}

const saveAttendance = async () => {
  if (!filterDate.value || attendances.value.length === 0) return
  
  saving.value = true
  try {
    const dateStr = formatLocalDate(filterDate.value)
    
    // Only build payload for unlocked items or preserve locked items safely
    const payloadItems = attendances.value.map(a => {
      if (isLockedBySystem(a)) {
        return {
          employee_id: a.employee_id,
          status: a.status,
          check_in: formatLocalDateTime(filterDate.value, a.check_in),
          check_out: formatLocalDateTime(filterDate.value, a.check_out),
          notes: a.notes
        }
      }

      let finalStatus = a.status
      if (!finalStatus || finalStatus === 'UNRECORDED') {
        finalStatus = 'ABSENT' // Default remaining unrecorded becomes absent
      }

      let inDateStr: string | null = null
      let outDateStr: string | null = null
      
      if (isAttendancePhysical(finalStatus)) {
        if (a.check_in) {
          inDateStr = formatLocalDateTime(filterDate.value, a.check_in)
        } else {
          const defTime = new Date(filterDate.value)
          defTime.setHours(7, 0, 0, 0)
          inDateStr = formatLocalDateTime(filterDate.value, defTime)
        }
        if (a.check_out) {
          outDateStr = formatLocalDateTime(filterDate.value, a.check_out)
        }
      }

      const manualReason = (a.manual_notes || '').trim()
      const combinedNote = manualReason
        ? `Tidak ada data di Fingerprint — ${manualReason}`
        : 'Tidak ada data di Fingerprint'
      
      return {
        employee_id: a.employee_id,
        status: finalStatus,
        check_in: inDateStr,
        check_out: outDateStr,
        notes: combinedNote
      }
    })
    
    await api.post('/sdm/attendance/bulk', {
      date: dateStr,
      items: payloadItems
    })
    
    toast.add({ 
      severity: 'success', 
      summary: 'Berhasil Disimpan', 
      detail: `Data presensi manual tanggal ${dateStr} berhasil disimpan (Data Fingerprint/GPS tetap terkunci).`, 
      life: 3500 
    })
    
    await fetchData()
    
  } catch (error: any) {
    console.error('Save attendance error:', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Gagal Menyimpan', 
      detail: error?.data?.detail || 'Terjadi kesalahan saat menyimpan presensi', 
      life: 4000 
    })
  } finally {
    saving.value = false
  }
}

// --- Fingerprint PIN Mapping Modal ---
const showPinMappingModal = ref(false)
const savingPinMapping = ref(false)
const pinMappingForm = reactive({
  rawLabel: '',
  fp_nik: '',
  fp_name: '',
  employee_id: null as number | null
})

const allEmployees = ref<any[]>([])

const fetchAllEmployees = async () => {
  try {
    const data = await api.get<any[]>('/sdm/employees?is_active=true')
    allEmployees.value = data || []
  } catch (e) {
    console.error('Failed to fetch all employees', e)
  }
}

const employeeSelectOptions = computed(() => {
  const source = allEmployees.value.length > 0 ? allEmployees.value : attendances.value
  return source.map((emp: any) => {
    const empId = emp.id != null ? emp.id : emp.employee_id
    const nama = emp.nama_lengkap || emp.name || 'Tanpa Nama'
    const nip = emp.nip || emp.nik_kepegawaian || '-'
    const unit = emp.unit?.name || emp.unit_name || ''
    const unitStr = unit ? ` • ${unit}` : ''
    return {
      label: `${nama} (NIP: ${nip}${unitStr})`,
      value: empId,
      nama
    }
  }).sort((a, b) => a.nama.localeCompare(b.nama))
})

const openPinMappingModal = async (rawItem: string) => {
  pinMappingForm.rawLabel = rawItem
  // Parse format "NAMA (PIN)"
  const match = rawItem.match(/^(.*)\(([^)]+)\)\s*$/)
  if (match) {
    pinMappingForm.fp_name = match[1].trim()
    pinMappingForm.fp_nik = match[2].trim()
  } else {
    pinMappingForm.fp_name = rawItem.trim()
    pinMappingForm.fp_nik = rawItem.trim()
  }
  pinMappingForm.employee_id = null

  if (allEmployees.value.length === 0) {
    await fetchAllEmployees()
  }

  showPinMappingModal.value = true
}

const savePinMapping = async () => {
  if (!pinMappingForm.employee_id || !pinMappingForm.fp_nik) {
    toast.add({ severity: 'warn', summary: 'Pilih Pegawai', detail: 'Silakan pilih pegawai terlebih dahulu', life: 3000 })
    return
  }
  savingPinMapping.value = true
  try {
    const res = await api.post<any>('/sdm/attendance/fingerprint-mappings', {
      fp_nik: pinMappingForm.fp_nik,
      fp_name: pinMappingForm.fp_name,
      employee_id: pinMappingForm.employee_id
    })
    toast.add({
      severity: 'success',
      summary: 'Berhasil Ditautkan',
      detail: `ID Fingerprint ${pinMappingForm.fp_nik} berhasil ditautkan ke ${res.employee_name}. Menarik ulang data...`,
      life: 4000
    })
    showPinMappingModal.value = false
    showSyncLogsDialog.value = false
    await syncFingerprint()
  } catch (e: any) {
    console.error('Error saving pin mapping:', e)
    toast.add({
      severity: 'error',
      summary: 'Gagal Menautkan',
      detail: e?.data?.detail || e?.message || 'Gagal menyimpan tautan ID Fingerprint',
      life: 4000
    })
  } finally {
    savingPinMapping.value = false
  }
}

// --- Quick Jump to Log Date & Bulk Range Sync ---
const syncingRange = ref(false)
const showCustomRangeInputs = ref(false)
const customSyncStartDate = ref(new Date(2026, 0, 1)) // 1 Januari 2026
const customSyncEndDate = ref(new Date())

const goToLogDate = (dateStr: string) => {
  if (!dateStr) return
  const [y, m, d] = dateStr.split('-').map(Number)
  filterDate.value = new Date(y, m - 1, d)
  showSyncLogsDialog.value = false
  fetchData()
  toast.add({
    severity: 'info',
    summary: 'Melihat Tanggal ' + dateStr,
    detail: `Menampilkan data presensi untuk tanggal ${dateStr}.`,
    life: 3000
  })
}

const syncRangeExecutor = async (startStr: string, endStr: string, title: string) => {
  syncingRange.value = true
  toast.add({
    severity: 'info',
    summary: 'Memulai Tarik Data ' + title,
    detail: `Sedang memproses data dari ${startStr} s/d ${endStr}...`,
    life: 4000
  })

  try {
    const sDate = new Date(startStr)
    const eDate = new Date(endStr)

    // Break into monthly chunks so long ranges (e.g. from Jan 2026) won't time out
    const chunks: { start: string, end: string }[] = []
    let curr = new Date(sDate)
    while (curr <= eDate) {
      let chunkEnd = new Date(curr.getFullYear(), curr.getMonth() + 1, 0)
      if (chunkEnd > eDate) chunkEnd = new Date(eDate)

      chunks.push({
        start: formatLocalDate(curr),
        end: formatLocalDate(chunkEnd)
      })

      curr = new Date(curr.getFullYear(), curr.getMonth() + 1, 1)
    }

    let totalSuccess = 0
    let totalEmpty = 0
    let totalFailed = 0
    let totalDays = 0

    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i]
      if (chunks.length > 1) {
        toast.add({
          severity: 'info',
          summary: `Progres Penarikan (${i + 1}/${chunks.length})`,
          detail: `Menarik data periode ${chunk.start} s/d ${chunk.end}...`,
          life: 3000
        })
      }

      const res = await api.post<any>('/sdm/attendance/sync-fingerprint-range', {
        start_date: chunk.start,
        end_date: chunk.end
      })

      const results: any[] = res?.results || []
      totalDays += results.length
      totalSuccess += results.filter(r => r.status === 'success').length
      totalEmpty += results.filter(r => r.status === 'empty').length
      totalFailed += results.filter(r => r.status === 'failed').length
    }

    toast.add({
      severity: totalFailed > 0 ? 'warn' : 'success',
      summary: 'Tarik Data Rentang Selesai',
      detail: `Berhasil memproses ${totalDays} hari (${totalSuccess} hari ada tap presensi, ${totalEmpty} data kosong, ${totalFailed} gagal).`,
      life: 6000
    })

    await fetchSyncLogs()
    await fetchData()
  } catch (e: any) {
    console.error('Sync range error:', e)
    toast.add({
      severity: 'error',
      summary: 'Gagal Tarik Rentang',
      detail: e?.data?.detail || e?.message || 'Terjadi kesalahan saat memproses rentang tanggal',
      life: 5000
    })
  } finally {
    syncingRange.value = false
  }
}

const syncFromYearStart = () => {
  const todayStr = formatLocalDate(new Date())
  const yearStartStr = todayStr.slice(0, 4) + '-01-01'
  syncRangeExecutor(yearStartStr, todayStr, 'Tahun 2026 (01 Jan s/d Hari Ini)')
}

const syncMonthToDate = () => {
  const todayStr = formatLocalDate(new Date())
  const startStr = todayStr.slice(0, 8) + '01'
  syncRangeExecutor(startStr, todayStr, 'Bulan Ini')
}

const syncCustomRange = () => {
  if (!customSyncStartDate.value || !customSyncEndDate.value) {
    toast.add({ severity: 'warn', summary: 'Pilih Tanggal', detail: 'Pilih tanggal mulai dan tanggal selesai', life: 3000 })
    return
  }
  const sStr = formatLocalDate(customSyncStartDate.value)
  const eStr = formatLocalDate(customSyncEndDate.value)
  syncRangeExecutor(sStr, eStr, 'Rentang Kustom')
}

// --- Dedicated Bulk Sync Modal State & Operations ---
const showBulkSyncModal = ref(false)
const bulkSyncMode = ref<'month' | 'year' | 'custom'>('month')
const bulkSyncSelectedMonth = ref(new Date())
const bulkSyncCustomStart = ref(new Date(2026, 0, 1))
const bulkSyncCustomEnd = ref(new Date())

const bulkSyncRunning = ref(false)
const bulkSyncFinished = ref(false)
const bulkSyncCancelRequested = ref(false)
const bulkSyncPercent = ref(0)
const bulkSyncStatusText = ref('')
const bulkSyncTotalDays = ref(0)
const bulkSyncSuccessDays = ref(0)
const bulkSyncEmptyDays = ref(0)
const bulkSyncFailedDays = ref(0)
const bulkSyncLogs = ref<{ date: string, status: string, msg: string }[]>([])

const openBulkSyncModal = () => {
  if (filterDate.value) {
    bulkSyncSelectedMonth.value = new Date(filterDate.value)
  }
  bulkSyncFinished.value = false
  bulkSyncRunning.value = false
  bulkSyncLogs.value = []
  bulkSyncPercent.value = 0
  bulkSyncStatusText.value = 'Siap melakukan penarikan data massal.'
  showBulkSyncModal.value = true
}

const getDaysInMonthCount = (d: any) => {
  if (!d) return 31
  const m = d instanceof Date ? d : new Date(d)
  if (isNaN(m.getTime())) return 31
  return new Date(m.getFullYear(), m.getMonth() + 1, 0).getDate()
}

const startBulkSync = async () => {
  const dates: string[] = []
  
  if (bulkSyncMode.value === 'month') {
    const raw = bulkSyncSelectedMonth.value || new Date()
    const m = raw instanceof Date ? raw : new Date(raw)
    const y = m.getFullYear()
    const mon = m.getMonth()
    const totalDays = new Date(y, mon + 1, 0).getDate()
    for (let day = 1; day <= totalDays; day++) {
      const d = new Date(y, mon, day)
      dates.push(formatLocalDate(d))
    }
  } else if (bulkSyncMode.value === 'year') {
    let curr = new Date(2026, 0, 1)
    const today = new Date()
    while (curr <= today) {
      dates.push(formatLocalDate(curr))
      curr.setDate(curr.getDate() + 1)
    }
  } else {
    const rawStart = bulkSyncCustomStart.value
    const rawEnd = bulkSyncCustomEnd.value
    if (!rawStart || !rawEnd) {
      toast.add({ severity: 'warn', summary: 'Pilih Tanggal', detail: 'Pilih tanggal mulai dan tanggal akhir', life: 3000 })
      return
    }
    let curr = rawStart instanceof Date ? new Date(rawStart) : new Date(rawStart)
    const endD = rawEnd instanceof Date ? new Date(rawEnd) : new Date(rawEnd)
    while (curr <= endD) {
      dates.push(formatLocalDate(curr))
      curr.setDate(curr.getDate() + 1)
    }
  }

  if (dates.length === 0) {
    toast.add({ severity: 'warn', summary: 'Periode Kosong', detail: 'Tidak ada tanggal yang dapat diproses', life: 3000 })
    return
  }

  bulkSyncRunning.value = true
  bulkSyncFinished.value = false
  bulkSyncCancelRequested.value = false
  bulkSyncTotalDays.value = dates.length
  bulkSyncSuccessDays.value = 0
  bulkSyncEmptyDays.value = 0
  bulkSyncFailedDays.value = 0
  bulkSyncLogs.value = []
  bulkSyncPercent.value = 0
  let totalRawCount = 0
  let totalSyncedCount = 0
  const allUnmatchedLogs = new Set<string>()

  for (let i = 0; i < dates.length; i++) {
    if (bulkSyncCancelRequested.value) {
      toast.add({ severity: 'warn', summary: 'Proses Dihentikan', detail: 'Penarikan dihentikan oleh pengguna.', life: 3000 })
      break
    }

    const dStr = dates[i]
    bulkSyncPercent.value = Math.round(((i + 1) / dates.length) * 100)
    bulkSyncStatusText.value = `Menarik data: ${dStr} (${i + 1} dari ${dates.length} hari)...`

    try {
      const res = await api.post<any>('/sdm/attendance/sync-fingerprint', {
        date: dStr,
        mode: 'all',
        source: 'manual',
        record_log: false
      })

      if (res?.status === 'empty') {
        bulkSyncEmptyDays.value++
        bulkSyncLogs.value.unshift({ date: dStr, status: 'empty', msg: 'Data kosong / Libur' })
      } else {
        bulkSyncSuccessDays.value++
        totalRawCount += Number(res?.raw_count || 0)
        totalSyncedCount += Number(res?.synced_employees || 0)
        if (res?.unmatched_logs && Array.isArray(res.unmatched_logs)) {
          res.unmatched_logs.forEach((u: string) => allUnmatchedLogs.add(u))
        }
        bulkSyncLogs.value.unshift({ 
          date: dStr, 
          status: 'success', 
          msg: `${res?.raw_count || 0} tap, ${res?.synced_employees || 0} pegawai` 
        })
      }
    } catch (err: any) {
      bulkSyncFailedDays.value++
      bulkSyncLogs.value.unshift({ 
        date: dStr, 
        status: 'failed', 
        msg: err?.data?.detail || err?.message || 'Gagal koneksi' 
      })
    }
  }

  bulkSyncRunning.value = false
  bulkSyncFinished.value = true
  bulkSyncStatusText.value = `Selesai: ${bulkSyncSuccessDays.value} hari ada data, ${bulkSyncEmptyDays.value} hari libur/kosong.`

  // Save 1 consolidated recap log for the entire bulk sync session
  const failedItems = bulkSyncLogs.value.filter(l => l.status === 'failed')
  const failedSummary = failedItems.length > 0 
    ? 'Tanggal Gagal: ' + failedItems.map(f => `${f.date} (${f.msg})`).slice(0, 10).join('; ') + (failedItems.length > 10 ? ` (+${failedItems.length - 10} lainnya)` : '')
    : null

  try {
    await api.post('/sdm/attendance/sync-logs', {
      date: `${dates[0]} s/d ${dates[dates.length - 1]}`,
      source: 'manual_range',
      status: bulkSyncFailedDays.value > 0 ? (bulkSyncSuccessDays.value > 0 ? 'partial' : 'failed') : (bulkSyncSuccessDays.value > 0 ? 'success' : 'empty'),
      raw_count: totalRawCount,
      synced_employees: totalSyncedCount,
      failed_employees: bulkSyncFailedDays.value,
      unmatched_logs: Array.from(allUnmatchedLogs),
      message: `Rekap Tarik Massal (${dates[0]} s/d ${dates[dates.length - 1]}): ${dates.length} hari (${bulkSyncSuccessDays.value} hari sukses, ${bulkSyncEmptyDays.value} libur/kosong${bulkSyncFailedDays.value > 0 ? `, ${bulkSyncFailedDays.value} gagal` : ''}). Total ${totalSyncedCount} pegawai disinkronkan.`,
      error_detail: failedSummary
    })
  } catch (e) {
    console.error('Failed to save bulk sync summary log:', e)
  }

  await fetchSyncLogs()
}

const finishBulkSync = async () => {
  showBulkSyncModal.value = false
  bulkSyncFinished.value = false
  await fetchData()
  toast.add({
    severity: 'success',
    summary: 'Data Berhasil Disinkronkan',
    detail: 'Data presensi pegawai telah diperbarui dari mesin fingerprint.',
    life: 4000
  })
}

onMounted(() => {
  fetchGeofenceConfig()
  fetchUnits()
  fetchAllEmployees()
  fetchData()
  fetchSyncLogs()
})
</script>
