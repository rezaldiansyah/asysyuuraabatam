<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <i class="pi pi-chart-bar text-emerald-600"></i>
          Rekapitulasi Presensi Pegawai
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
          Laporan agregat kehadiran, tren kedisiplinan, lembur, dan penugasan hari libur pegawai Asy-Syuuraa.
        </p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <NuxtLink 
          to="/dashboard/sdm/presensi"
          class="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 rounded-xl shadow-sm transition"
        >
          <i class="pi pi-arrow-left text-xs"></i>
          Presensi Harian
        </NuxtLink>
        <Button 
          label="Analisis & Tren Grafik" 
          icon="pi pi-chart-line" 
          severity="primary" 
          size="small"
          class="text-xs font-semibold shadow-sm"
          @click="openAnalyticsModal(null, 'discipline')" 
          :disabled="recapData.length === 0" 
        />
        <Button 
          label="Export Excel (CSV)" 
          icon="pi pi-file-excel" 
          severity="success" 
          outlined 
          size="small"
          class="text-xs font-semibold"
          @click="exportExcel" 
          :disabled="recapData.length === 0 || periodStats.totalTercatat === 0" 
        />
      </div>
    </div>

    <!-- Filter Bar Card -->
    <Card class="shadow-sm border border-slate-100 dark:border-slate-800">
      <template #content>
        <div class="space-y-4">
          <!-- Row 1: Mode Periode & Presets -->
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3.5">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-slate-700 dark:text-slate-300">Mode Rentang Waktu:</span>
              <SelectButton
                v-model="periodMode"
                :options="periodOptions"
                optionLabel="label"
                optionValue="value"
                :allowEmpty="false"
                size="small"
                @change="handlePeriodModeChange"
              />
            </div>
            <div class="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
              <i class="pi pi-calendar text-emerald-600"></i>
              <span>Periode Aktif: <strong class="text-slate-800 dark:text-slate-100">{{ activePeriodLabel }}</strong></span>
            </div>
          </div>

          <!-- Row 2: Dynamic Filters & Action -->
          <div class="flex flex-wrap items-end justify-between gap-4">
            <div class="flex flex-wrap items-end gap-3.5">
              <!-- Mode 1 Bulan -->
              <div v-if="periodMode === '1m'">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Pilih Bulan &amp; Tahun</label>
                <Calendar 
                  v-model="filterMonth" 
                  view="month" 
                  dateFormat="mm/yy" 
                  :showIcon="true" 
                  class="w-44 text-xs" 
                  @date-select="fetchData" 
                />
              </div>

              <!-- Mode 3 Bulan / 6 Bulan -->
              <div v-else-if="periodMode === '3m' || periodMode === '6m'">
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Sampai Bulan</label>
                <Calendar 
                  v-model="filterMonth" 
                  view="month" 
                  dateFormat="mm/yy" 
                  :showIcon="true" 
                  class="w-44 text-xs" 
                  @date-select="fetchData" 
                />
              </div>

              <!-- Mode Kustom Rentang -->
              <div v-else-if="periodMode === 'custom'" class="flex items-center gap-2">
                <div>
                  <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Dari Tanggal</label>
                  <Calendar 
                    v-model="filterStartDate" 
                    dateFormat="dd/mm/yy" 
                    :showIcon="true" 
                    placeholder="Mulai" 
                    class="w-36 text-xs" 
                  />
                </div>
                <div class="pt-5 text-slate-400">s/d</div>
                <div>
                  <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Sampai Tanggal</label>
                  <Calendar 
                    v-model="filterEndDate" 
                    dateFormat="dd/mm/yy" 
                    :showIcon="true" 
                    placeholder="Selesai" 
                    class="w-36 text-xs" 
                  />
                </div>
              </div>

              <!-- Filter Unit Sekolah -->
              <div>
                <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Pilih Unit Sekolah</label>
                <Dropdown 
                  v-model="filterUnit" 
                  :options="units" 
                  optionLabel="name" 
                  optionValue="id" 
                  placeholder="Semua Unit" 
                  showClear 
                  class="w-52 text-xs" 
                  @change="fetchData" 
                />
              </div>
            </div>

            <!-- Submit Button -->
            <div>
              <Button 
                label="Tampilkan Rekap" 
                icon="pi pi-search" 
                size="small" 
                class="text-xs font-semibold px-4"
                @click="fetchData" 
                :loading="loading" 
              />
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Period KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5" v-if="recapData.length > 0">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 flex items-center justify-center shrink-0">
          <i class="pi pi-users text-lg"></i>
        </div>
        <div>
          <div class="text-[11px] text-slate-500 font-medium">Total Pegawai</div>
          <div class="text-lg font-bold text-slate-800 dark:text-white mt-0.5">{{ periodStats.totalEmployees }} Orang</div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 flex items-center justify-center shrink-0">
          <i class="pi pi-chart-pie text-lg"></i>
        </div>
        <div>
          <div class="text-[11px] text-slate-500 font-medium">Rata-rata Kehadiran</div>
          <div class="text-lg font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">{{ periodStats.avgPresence }}%</div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center justify-between gap-2">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-950/40 text-purple-600 flex items-center justify-center shrink-0">
            <i class="pi pi-check-circle text-lg"></i>
          </div>
          <div>
            <div class="text-[11px] text-slate-500 font-medium">Total Hari Hadir</div>
            <div class="text-lg font-bold text-slate-800 dark:text-white mt-0.5 flex items-center gap-1.5">
              <span>{{ periodStats.totalHadir + periodStats.totalTerlambat }} Kali</span>
            </div>
            <div v-if="periodStats.totalTerlambat > 0" class="text-[10px] text-amber-600 font-semibold">
              {{ periodStats.totalTerlambat }}x Terlambat
            </div>
          </div>
        </div>
        <button
          v-if="periodStats.totalTerlambat > 0"
          type="button"
          class="w-7 h-7 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-600 flex items-center justify-center transition shrink-0"
          title="Lihat pegawai yang pernah terlambat"
          @click="openRecapModal('terlambat')"
        >
          <i class="pi pi-eye text-xs"></i>
        </button>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm flex items-center justify-between gap-2">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/40 text-amber-600 flex items-center justify-center shrink-0">
            <i class="pi pi-calendar-minus text-lg"></i>
          </div>
          <div>
            <div class="text-[11px] text-slate-500 font-medium">Izin / Sakit / Cuti</div>
            <div class="text-lg font-bold text-slate-800 dark:text-white mt-0.5">{{ periodStats.totalIzinSakitCuti }} Kali</div>
          </div>
        </div>
        <button
          v-if="periodStats.totalIzinSakitCuti > 0"
          type="button"
          class="w-7 h-7 rounded-lg bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center justify-center transition shrink-0"
          title="Lihat daftar pegawai Izin / Sakit / Cuti"
          @click="openRecapModal('izin_sakit_cuti')"
        >
          <i class="pi pi-eye text-xs"></i>
        </button>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-rose-200 dark:border-rose-900/50 shadow-sm flex items-center justify-between gap-2">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-rose-50 dark:bg-rose-950/40 text-rose-600 flex items-center justify-center shrink-0">
            <i class="pi pi-times-circle text-lg"></i>
          </div>
          <div>
            <div class="text-[11px] text-rose-600 dark:text-rose-400 font-semibold">Total Alpa (Tanpa Ket.)</div>
            <div class="text-lg font-bold text-rose-600 dark:text-rose-400 mt-0.5">{{ periodStats.totalAlpa }} Kali</div>
          </div>
        </div>
        <button
          v-if="periodStats.totalAlpa > 0"
          type="button"
          class="w-7 h-7 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-600 flex items-center justify-center transition shrink-0"
          title="Lihat daftar pegawai yang memiliki Alpa"
          @click="openRecapModal('alpa')"
        >
          <i class="pi pi-eye text-xs"></i>
        </button>
      </div>
    </div>

    <!-- Empty State Alert when zero records found -->
    <div 
      v-if="hasFetched && periodStats.totalTercatat === 0" 
      class="p-6 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left"
    >
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-300 flex items-center justify-center shrink-0">
          <i class="pi pi-inbox text-2xl"></i>
        </div>
        <div>
          <h3 class="font-bold text-slate-800 dark:text-white text-base">Belum Ada Presensi yang Tersimpan untuk Periode {{ activePeriodLabel }}</h3>
          <p class="text-xs text-amber-800 dark:text-amber-300 mt-1 max-w-xl">
            Tabel rekap saat ini masih bernilai 0 karena belum ada rekaman kehadiran harian yang tersimpan pada rentang waktu yang dipilih.
          </p>
        </div>
      </div>
      <NuxtLink 
        to="/dashboard/sdm/presensi"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-sm transition shrink-0"
      >
        <i class="pi pi-calendar-plus"></i>
        Buka Presensi Hari Ini
      </NuxtLink>
    </div>

    <!-- Data Table Card with Page Size Options [20, 50, 100] & Overtime Badges -->
    <Card v-if="recapData.length > 0">
      <template #content>
        <div class="mb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white">Laporan Presensi: {{ activePeriodLabel }}</h2>
            <p class="text-xs text-slate-400 mt-0.5">
              Rekapitulasi otomatis kehadiran, jam lembur (>18:00), dan kehadiran hari libur/Ahad. Pilih 20 / 50 / 100 baris.
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-500 font-medium bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-full">
              {{ recapData.length }} Pegawai Aktif
            </span>
          </div>
        </div>
        
        <DataTable 
          :value="recapData" 
          :loading="loading" 
          paginator 
          :rows="20" 
          :rowsPerPageOptions="[20, 50, 100]"
          dataKey="employee_id" 
          class="p-datatable-sm" 
          stripedRows 
          responsiveLayout="scroll"
        >
          <Column field="nama_lengkap" header="Nama Pegawai" sortable style="min-width: 240px">
            <template #body="{ data }">
              <div class="flex items-center gap-1.5 flex-wrap">
                <span class="font-semibold text-slate-800 dark:text-white">{{ data.nama_lengkap }}</span>
                <span v-if="data.join_date" class="px-1.5 py-0.2 rounded text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-medium" :title="'Tanggal Mulai Masuk (TMT): ' + formatDateDisplay(data.join_date)">
                  TMT: {{ formatDateDisplay(data.join_date) }}
                </span>
              </div>
              <div class="flex items-center gap-2 text-[11px] text-slate-400 mt-0.5">
                <span>NIP: {{ data.nip || '-' }}</span>
                <span>&bull;</span>
                <span class="text-emerald-700 dark:text-emerald-400 font-medium">{{ data.unit_name }}</span>
                <span v-if="data.position">&bull; {{ data.position }}</span>
              </div>
            </template>
          </Column>

          <Column field="hadir" header="Hadir Tepat" sortable style="width: 95px">
            <template #body="{ data }">
              <span class="font-bold text-emerald-600">{{ data.hadir }}</span>
            </template>
          </Column>

          <Column field="terlambat" header="Terlambat" sortable style="width: 95px">
            <template #body="{ data }">
              <span class="font-semibold text-amber-600">{{ data.terlambat || 0 }}</span>
            </template>
          </Column>

          <Column field="sakit" header="Sakit" sortable style="width: 75px">
            <template #body="{ data }">
              <span class="font-semibold text-yellow-600">{{ data.sakit }}</span>
            </template>
          </Column>

          <Column field="izin" header="Izin" sortable style="width: 75px">
            <template #body="{ data }">
              <span class="font-semibold text-blue-600">{{ data.izin }}</span>
            </template>
          </Column>

          <Column field="cuti" header="Cuti" sortable style="width: 75px">
            <template #body="{ data }">
              <span class="font-semibold text-purple-600">{{ data.cuti || 0 }}</span>
            </template>
          </Column>

          <Column field="alpa" header="Alpa" sortable style="width: 75px">
            <template #body="{ data }">
              <span class="font-semibold text-rose-600">{{ data.alpa }}</span>
            </template>
          </Column>

          <Column field="total" header="Total Hari" sortable style="width: 90px">
            <template #body="{ data }">
              <span class="font-bold text-slate-700 dark:text-slate-200">{{ data.total }}</span>
            </template>
          </Column>

          <!-- Kolom Lembur & Masuk Hari Ahad -->
          <Column header="Lembur & Ahad" style="min-width: 145px">
            <template #body="{ data }">
              <div class="flex flex-wrap items-center gap-1.5">
                <button 
                  v-if="data.total_lembur > 0" 
                  type="button"
                  class="px-2 py-0.5 rounded-md bg-indigo-100 text-indigo-700 dark:bg-indigo-950/70 dark:text-indigo-300 text-[11px] font-bold inline-flex items-center gap-1 hover:bg-indigo-200 transition"
                  title="Klik untuk melihat detail kejadian lembur (>18:00)"
                  @click="openAnalyticsModal(data.employee_id, 'overtime')"
                >
                  <i class="pi pi-moon text-[10px]"></i>
                  {{ data.total_lembur }}x Lembur
                </button>
                <button 
                  v-if="data.total_ahad > 0" 
                  type="button"
                  class="px-2 py-0.5 rounded-md bg-amber-100 text-amber-800 dark:bg-amber-950/70 dark:text-amber-300 text-[11px] font-bold inline-flex items-center gap-1 hover:bg-amber-200 transition"
                  title="Klik untuk melihat detail kehadiran hari Ahad/libur"
                  @click="openAnalyticsModal(data.employee_id, 'overtime')"
                >
                  <i class="pi pi-sun text-[10px]"></i>
                  {{ data.total_ahad }}x Ahad
                </button>
                <span v-if="!data.total_lembur && !data.total_ahad" class="text-slate-300 dark:text-slate-600 text-xs">-</span>
              </div>
            </template>
          </Column>

          <Column field="persentase" header="Tingkat Kehadiran" sortable style="min-width: 140px">
            <template #body="{ data }">
              <div class="space-y-1">
                <div class="flex justify-between text-[11px] font-semibold">
                  <span class="text-slate-600 dark:text-slate-300">{{ data.persentase }}</span>
                </div>
                <ProgressBar 
                  :value="parseFloat(data.persentase) || 0" 
                  :showValue="false" 
                  class="!h-2"
                />
              </div>
            </template>
          </Column>

          <Column header="Tren" style="width: 65px" bodyClass="text-center">
            <template #body="{ data }">
              <button 
                type="button" 
                class="p-1.5 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 dark:hover:bg-slate-700 transition"
                title="Lihat grafik tren individu"
                @click="openAnalyticsModal(data.employee_id, 'discipline')"
              >
                <i class="pi pi-chart-line text-sm"></i>
              </button>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Modal Quick-View Daftar Pegawai per Kategori Rekap -->
    <Dialog
      v-model:visible="showRecapModal"
      :header="recapModalTitle"
      :modal="true"
      :style="{ width: '38rem', maxWidth: '95vw' }"
    >
      <div class="space-y-2.5 max-h-[60vh] overflow-y-auto pr-1">
        <div
          v-for="emp in recapModalList"
          :key="emp.employee_id"
          class="flex items-center justify-between p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50/70 dark:bg-slate-800/60"
        >
          <div>
            <div class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-1.5 flex-wrap">
              <span>{{ emp.nama_lengkap }}</span>
              <span v-if="emp.join_date" class="px-1.5 py-0.2 rounded text-[10px] bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold" :title="'Tanggal Mulai Masuk: ' + formatDateDisplay(emp.join_date)">
                TMT: {{ formatDateDisplay(emp.join_date) }}
              </span>
            </div>
            <div class="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
              <span>NIP: {{ emp.nip || '-' }}</span>
              <span>&bull;</span>
              <span class="text-slate-600 dark:text-slate-300 font-medium">{{ emp.unit_name }}</span>
              <span v-if="emp.position">&bull; {{ emp.position }}</span>
            </div>
          </div>
          <div class="flex items-center gap-1.5 text-xs font-bold">
            <span v-if="recapModalType === 'terlambat'" class="px-2.5 py-1 rounded-lg bg-amber-100 text-amber-700">
              {{ emp.terlambat }}x Terlambat
            </span>
            <template v-else-if="recapModalType === 'izin_sakit_cuti'">
              <span v-if="emp.sakit > 0" class="px-2 py-0.5 rounded bg-yellow-100 text-yellow-700">{{ emp.sakit }} Sakit</span>
              <span v-if="emp.izin > 0" class="px-2 py-0.5 rounded bg-blue-100 text-blue-700">{{ emp.izin }} Izin</span>
              <span v-if="emp.cuti > 0" class="px-2 py-0.5 rounded bg-purple-100 text-purple-700">{{ emp.cuti }} Cuti</span>
            </template>
            <span v-else-if="recapModalType === 'alpa'" class="px-2.5 py-1 rounded-lg bg-rose-100 text-rose-700">
              {{ emp.alpa }}x Alpa
            </span>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Tutup" icon="pi pi-times" severity="secondary" text size="small" @click="showRecapModal = false" />
      </template>
    </Dialog>

    <!-- Dialog Pop-Up Analisis & Tren Grafik Dinamis -->
    <Dialog
      v-model:visible="showAnalyticsModal"
      :modal="true"
      :style="{ width: '66rem', maxWidth: '96vw' }"
      :breakpoints="{ '960px': '95vw', '640px': '98vw' }"
    >
      <template #header>
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 flex items-center justify-center shrink-0">
            <i class="pi pi-chart-line text-lg"></i>
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-800 dark:text-white">Analisis &amp; Tren Presensi Pegawai</h3>
            <p class="text-xs text-slate-400">Periode: {{ activePeriodLabel }}</p>
          </div>
        </div>
      </template>

      <div class="space-y-5 pt-1 max-h-[75vh] overflow-y-auto pr-1">
        <!-- Tab Navigation inside Modal: Kedisiplinan vs Overtime/Dedikasi -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
          <SelectButton
            v-model="analyticsTab"
            :options="[
              { label: '📊 Kedisiplinan Reguler', value: 'discipline' },
              { label: '🌙 Dedikasi & Overtime (Lembur / Ahad)', value: 'overtime' }
            ]"
            optionLabel="label"
            optionValue="value"
            :allowEmpty="false"
            size="small"
          />
          <div class="text-right">
            <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
              {{ filteredAnalyticsEmployees.length }} Pegawai Terpilih
            </span>
          </div>
        </div>

        <!-- Controls Inside Analytics Modal: Filter Unit & Pegawai -->
        <div class="bg-slate-50 dark:bg-slate-800/80 p-3.5 rounded-2xl border border-slate-200 dark:border-slate-700 flex flex-wrap items-center justify-between gap-3">
          <div class="flex flex-wrap items-center gap-3">
            <div>
              <label class="block text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">Filter Unit</label>
              <Dropdown 
                v-model="analyticsUnit" 
                :options="analyticsUnitOptions" 
                optionLabel="label" 
                optionValue="value" 
                placeholder="Semua Unit" 
                class="w-48 text-xs" 
                @change="onAnalyticsFilterChange"
              />
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">Fokus Tampilan</label>
              <Dropdown 
                v-model="analyticsEmployeeId" 
                :options="analyticsEmployeeOptions" 
                optionLabel="label" 
                optionValue="value" 
                placeholder="Semua Pegawai (Tren Agregat)" 
                filter 
                filterPlaceholder="Cari nama pegawai..."
                class="w-64 text-xs" 
              />
            </div>
          </div>
        </div>

        <!-- Detail Profile Card jika memilih 1 Pegawai Spesifik -->
        <div v-if="selectedEmployeeDetail" class="p-4 rounded-2xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50/50 dark:bg-emerald-950/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-emerald-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
              {{ selectedEmployeeDetail.nama_lengkap.charAt(0) }}
            </div>
            <div>
              <div class="font-bold text-base text-slate-800 dark:text-white">{{ selectedEmployeeDetail.nama_lengkap }}</div>
              <div class="text-xs text-slate-500 flex items-center gap-2 mt-0.5">
                <span>NIP: {{ selectedEmployeeDetail.nip || '-' }}</span>
                <span>&bull;</span>
                <span class="font-semibold text-emerald-700 dark:text-emerald-400">{{ selectedEmployeeDetail.unit_name }}</span>
                <span>&bull;</span>
                <span>{{ selectedEmployeeDetail.position }}</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="text-right">
              <div class="text-[11px] text-slate-500">Tingkat Kehadiran</div>
              <div class="text-xl font-black text-emerald-600 dark:text-emerald-400">{{ selectedEmployeeDetail.persentase }}</div>
            </div>
            <div class="border-l border-emerald-200 dark:border-emerald-800 pl-3 text-right">
              <div class="text-[11px] text-slate-500">Total Lembur &amp; Ahad</div>
              <div class="text-sm font-bold text-indigo-700 dark:text-indigo-300">
                {{ selectedEmployeeDetail.total_lembur || 0 }}x Lembur &bull; {{ selectedEmployeeDetail.total_ahad || 0 }}x Ahad
              </div>
            </div>
          </div>
        </div>

        <!-- =================== TAB 1: KEDISIPLINAN REGULER =================== -->
        <div v-if="analyticsTab === 'discipline'" class="space-y-6">
          <!-- KPI Metric Strip -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-center">
              <div class="text-xs text-slate-500 font-medium">Rata-rata Kehadiran</div>
              <div class="text-2xl font-black text-emerald-600 dark:text-emerald-400 mt-1">{{ analyticsStats.avgPresence }}%</div>
              <div class="text-[10px] text-slate-400 mt-0.5">{{ analyticsStats.totalHadir }} hari hadir</div>
            </div>
            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-center">
              <div class="text-xs text-slate-500 font-medium">Total Terlambat</div>
              <div class="text-2xl font-black text-amber-600 mt-1">{{ analyticsStats.totalTerlambat }}x</div>
              <div class="text-[10px] text-slate-400 mt-0.5">Rasio: {{ analyticsStats.lateRate }}%</div>
            </div>
            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-center">
              <div class="text-xs text-slate-500 font-medium">Izin / Sakit / Cuti</div>
              <div class="text-2xl font-black text-blue-600 mt-1">{{ analyticsStats.totalIzinSakitCuti }}x</div>
              <div class="text-[10px] text-slate-400 mt-0.5">Disetujui manajemen</div>
            </div>
            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-center">
              <div class="text-xs text-slate-500 font-medium">Total Alpa (Bolos)</div>
              <div class="text-2xl font-black text-rose-600 mt-1">{{ analyticsStats.totalAlpa }}x</div>
              <div class="text-[10px] text-slate-400 mt-0.5">Perlu perhatian</div>
            </div>
          </div>

          <!-- Visual Multi-Month Bar Trend Chart -->
          <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
            <div class="flex items-center justify-between">
              <h4 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2">
                <i class="pi pi-chart-bar text-emerald-600"></i>
                Grafik Tren Presensi per Bulan
              </h4>
              <div class="flex items-center gap-3 text-[11px] text-slate-500">
                <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Hadir Tepat</span>
                <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Terlambat</span>
                <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Izin/Skt</span>
                <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Alpa</span>
              </div>
            </div>

            <!-- Trend Bars Container -->
            <div class="space-y-3.5 pt-1">
              <div 
                v-for="monthItem in monthlyTrendList" 
                :key="monthItem.monthKey"
                class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800 space-y-2"
              >
                <div class="flex items-center justify-between text-xs">
                  <div class="font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
                    <span>{{ monthItem.monthLabel }}</span>
                    <span class="text-[10px] font-semibold text-emerald-700 bg-emerald-100 dark:bg-emerald-950/70 px-2 py-0.5 rounded-full">
                      Kehadiran: {{ monthItem.presencePct }}%
                    </span>
                  </div>
                  <div class="text-[11px] text-slate-500 font-medium flex items-center gap-3">
                    <span class="text-emerald-600 font-bold">{{ monthItem.hadir }} Hadir</span>
                    <span v-if="monthItem.terlambat > 0" class="text-amber-600 font-semibold">{{ monthItem.terlambat }} Telat</span>
                    <span v-if="monthItem.izinSakit > 0" class="text-blue-600 font-semibold">{{ monthItem.izinSakit }} Izin/Skt</span>
                    <span v-if="monthItem.alpa > 0" class="text-rose-600 font-bold">{{ monthItem.alpa }} Alpa</span>
                  </div>
                </div>

                <!-- Proportional Stacked Progress Bar -->
                <div class="h-3.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden flex">
                  <div 
                    :style="{ width: `${monthItem.hadirPct}%` }" 
                    class="bg-emerald-500 transition-all duration-300" 
                    title="Hadir Tepat"
                  ></div>
                  <div 
                    :style="{ width: `${monthItem.terlambatPct}%` }" 
                    class="bg-amber-400 transition-all duration-300" 
                    title="Terlambat"
                  ></div>
                  <div 
                    :style="{ width: `${monthItem.izinSakitPct}%` }" 
                    class="bg-blue-400 transition-all duration-300" 
                    title="Izin / Sakit / Cuti"
                  ></div>
                  <div 
                    :style="{ width: `${monthItem.alpaPct}%` }" 
                    class="bg-rose-500 transition-all duration-300" 
                    title="Alpa"
                  ></div>
                </div>
              </div>

              <div v-if="monthlyTrendList.length === 0" class="text-center py-6 text-slate-400 text-xs">
                Belum ada riwayat per bulan pada periode ini.
              </div>
            </div>
          </div>

          <!-- Komparasi Antar Unit (Only when viewing All Employees) -->
          <div v-if="!analyticsEmployeeId && unitComparisonList.length > 1" class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3.5">
            <div class="flex items-center justify-between">
              <h4 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2">
                <i class="pi pi-building text-blue-600"></i>
                Komparasi Tingkat Disiplin Antar Unit
              </h4>
              <span class="text-[11px] text-slate-400">Benchmark Kedisiplinan Staf</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              <div 
                v-for="u in unitComparisonList" 
                :key="u.unit_name" 
                class="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/40 space-y-2"
              >
                <div class="flex items-center justify-between text-xs">
                  <span class="font-bold text-slate-800 dark:text-white">{{ u.unit_name }}</span>
                  <span class="font-extrabold text-emerald-600 dark:text-emerald-400">{{ u.avgPresence }}%</span>
                </div>
                <ProgressBar :value="parseFloat(u.avgPresence) || 0" :showValue="false" class="!h-2" />
                <div class="flex items-center justify-between text-[10px] text-slate-500">
                  <span>{{ u.count }} Staf</span>
                  <span class="text-amber-600 font-semibold">{{ u.totalTerlambat }}x Terlambat</span>
                  <span class="text-rose-600 font-semibold">{{ u.totalAlpa }}x Alpa</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Peringkat Disiplin: Teladan & Perlu Pembinaan -->
          <div v-if="!analyticsEmployeeId && filteredAnalyticsEmployees.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Top Kehadiran Teladan -->
            <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3">
              <div class="flex items-center gap-2 text-emerald-700 dark:text-emerald-400">
                <i class="pi pi-star-fill text-amber-500"></i>
                <h4 class="font-bold text-xs uppercase tracking-wider">Top 5 Disiplin Tertinggi</h4>
              </div>
              <div class="space-y-2 max-h-56 overflow-y-auto pr-1">
                <div 
                  v-for="(emp, idx) in topDisciplineList" 
                  :key="emp.employee_id"
                  class="flex items-center justify-between p-2.5 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/40 text-xs"
                >
                  <div class="flex items-center gap-2.5">
                    <span class="w-5 h-5 rounded-full bg-emerald-200 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-300 text-[10px] font-bold flex items-center justify-center shrink-0">
                      {{ idx + 1 }}
                    </span>
                    <div>
                      <div class="font-bold text-slate-800 dark:text-white">{{ emp.nama_lengkap }}</div>
                      <div class="text-[10px] text-slate-400">{{ emp.unit_name }} &bull; {{ emp.position }}</div>
                    </div>
                  </div>
                  <div class="text-right">
                    <div class="font-bold text-emerald-600">{{ emp.persentase }}</div>
                    <div class="text-[10px] text-slate-400">{{ emp.hadir }}x Hadir</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Perlu Pembinaan -->
            <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3">
              <div class="flex items-center gap-2 text-rose-600 dark:text-rose-400">
                <i class="pi pi-exclamation-triangle text-rose-500"></i>
                <h4 class="font-bold text-xs uppercase tracking-wider">Perlu Perhatian / Pembinaan</h4>
              </div>
              <div class="space-y-2 max-h-56 overflow-y-auto pr-1">
                <div 
                  v-for="emp in needsAttentionList" 
                  :key="emp.employee_id"
                  class="flex items-center justify-between p-2.5 rounded-xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/40 text-xs"
                >
                  <div>
                    <div class="font-bold text-slate-800 dark:text-white">{{ emp.nama_lengkap }}</div>
                    <div class="text-[10px] text-slate-400">{{ emp.unit_name }} &bull; {{ emp.position }}</div>
                  </div>
                  <div class="flex items-center gap-1.5 font-bold">
                    <span v-if="emp.alpa > 0" class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 text-[10px]">
                      {{ emp.alpa }}x Alpa
                    </span>
                    <span v-if="emp.terlambat > 0" class="px-2 py-0.5 rounded bg-amber-100 text-amber-700 text-[10px]">
                      {{ emp.terlambat }}x Telat
                    </span>
                  </div>
                </div>
                <div v-if="needsAttentionList.length === 0" class="text-center py-4 text-xs text-emerald-600 font-semibold">
                  Tidak ada staf dengan catatan alpa atau keterlambatan berlebih pada periode ini.
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- =================== TAB 2: DEDIKASI & OVERTIME (LEMBUR & AHAD) =================== -->
        <div v-else-if="analyticsTab === 'overtime'" class="space-y-6">
          <!-- Overtime Metric Strip -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="p-4 rounded-xl border border-indigo-200 dark:border-indigo-800 bg-indigo-50/50 dark:bg-indigo-950/30">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 flex items-center justify-center shrink-0">
                  <i class="pi pi-moon text-lg"></i>
                </div>
                <div>
                  <div class="text-xs text-slate-500 font-medium">Pulang Larut Malam (> 18:00)</div>
                  <div class="text-2xl font-black text-indigo-700 dark:text-indigo-300 mt-0.5">
                    {{ overtimeStats.totalLembur }} <span class="text-sm font-semibold">Kejadian</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="p-4 rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/30">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-300 flex items-center justify-center shrink-0">
                  <i class="pi pi-sun text-lg"></i>
                </div>
                <div>
                  <div class="text-xs text-slate-500 font-medium">Masuk Hari Libur (Ahad)</div>
                  <div class="text-2xl font-black text-amber-700 dark:text-amber-300 mt-0.5">
                    {{ overtimeStats.totalAhad }} <span class="text-sm font-semibold">Kejadian</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 flex items-center justify-center shrink-0">
                  <i class="pi pi-star text-lg"></i>
                </div>
                <div class="min-w-0">
                  <div class="text-xs text-slate-500 font-medium">Staf Terbanyak Bertugas</div>
                  <div v-if="overtimeStats.topStaff" class="truncate font-bold text-slate-800 dark:text-white mt-0.5 text-sm">
                    {{ overtimeStats.topStaff.name }}
                  </div>
                  <div v-if="overtimeStats.topStaff" class="text-[11px] text-emerald-600 font-semibold">
                    {{ overtimeStats.topStaff.count }}x Overtime / Ahad
                  </div>
                  <div v-else class="text-xs text-slate-400 mt-1">Belum ada data</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section: Grafik Tren Bulanan Lembur vs Ahad & Distribusi Kategori -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Tren Bulanan Overtime & Ahad -->
            <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3">
              <div class="flex items-center justify-between">
                <h4 class="font-bold text-xs uppercase tracking-wider text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                  <i class="pi pi-calendar text-indigo-600"></i>
                  Tren Bulanan Lembur vs Masuk Ahad
                </h4>
                <div class="flex items-center gap-2 text-[10px]">
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-indigo-500"></span> Lembur</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-500"></span> Ahad</span>
                </div>
              </div>

              <div class="space-y-3 pt-1">
                <div 
                  v-for="m in monthlyOvertimeTrendList" 
                  :key="m.monthKey"
                  class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/40 border border-slate-100 dark:border-slate-800 space-y-1.5"
                >
                  <div class="flex items-center justify-between text-xs">
                    <span class="font-bold text-slate-700 dark:text-slate-200">{{ m.monthLabel }}</span>
                    <span class="text-[11px] text-slate-500">
                      <strong class="text-indigo-600">{{ m.lembur }}x</strong> Lembur &bull; 
                      <strong class="text-amber-600">{{ m.ahad }}x</strong> Ahad
                    </span>
                  </div>
                  <div class="h-2.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden flex">
                    <div 
                      :style="{ width: `${m.total > 0 ? (m.lembur / m.total) * 100 : 0}%` }" 
                      class="bg-indigo-500 transition-all duration-300"
                    ></div>
                    <div 
                      :style="{ width: `${m.total > 0 ? (m.ahad / m.total) * 100 : 0}%` }" 
                      class="bg-amber-400 transition-all duration-300"
                    ></div>
                  </div>
                </div>

                <div v-if="monthlyOvertimeTrendList.length === 0" class="text-center py-6 text-slate-400 text-xs">
                  Tidak ada catatan lembur atau masuk hari Ahad pada periode ini.
                </div>
              </div>
            </div>

            <!-- Distribusi Kategori Kegiatan -->
            <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3">
              <div class="flex items-center justify-between">
                <h4 class="font-bold text-xs uppercase tracking-wider text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                  <i class="pi pi-tag text-emerald-600"></i>
                  Proporsi Kategori Kegiatan
                </h4>
                <span class="text-[11px] text-slate-400">{{ allFilteredOvertimeLogs.length }} Catatan</span>
              </div>

              <div class="space-y-2.5 pt-1">
                <div 
                  v-for="cat in categoryBreakdownList" 
                  :key="cat.category" 
                  class="p-2.5 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/40 space-y-1.5"
                >
                  <div class="flex items-center justify-between text-xs">
                    <span class="font-semibold text-slate-800 dark:text-white">{{ cat.category }}</span>
                    <span class="font-bold text-slate-600 dark:text-slate-300">{{ cat.count }}x ({{ cat.pct }}%)</span>
                  </div>
                  <ProgressBar :value="parseFloat(cat.pct) || 0" :showValue="false" class="!h-1.5" />
                </div>

                <div v-if="categoryBreakdownList.length === 0" class="text-center py-6 text-slate-400 text-xs">
                  Belum ada log kategori kegiatan.
                </div>
              </div>
            </div>
          </div>

          <!-- Section: Rangkuman Staf Bertugas vs Log Detail Kejadian Lembur & Masuk Ahad -->
          <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
              <div>
                <h4 class="font-bold text-sm text-slate-800 dark:text-white flex items-center gap-2">
                  <i class="pi pi-briefcase text-indigo-600"></i>
                  Data Dedikasi Staf (Lembur &amp; Hari Ahad)
                </h4>
                <p class="text-xs text-slate-400 mt-0.5">
                  Rangkuman siapa saja staf terbanyak bertugas, frekuensi, serta rincian waktu dan catatan aktivitasnya.
                </p>
              </div>

              <!-- Sub-tab switch between Summary and All Logs -->
              <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-1 rounded-xl shrink-0">
                <button
                  type="button"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
                  :class="overtimeSubTab === 'summary' 
                    ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-bold' 
                    : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
                  @click="overtimeSubTab = 'summary'"
                >
                  <i class="pi pi-users text-[11px]"></i>
                  <span>Rangkuman Staf ({{ staffOvertimeSummaryList.length }})</span>
                </button>
                <button
                  type="button"
                  class="px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
                  :class="overtimeSubTab === 'all_logs' 
                    ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm font-bold' 
                    : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
                  @click="overtimeSubTab = 'all_logs'"
                >
                  <i class="pi pi-list text-[11px]"></i>
                  <span>Semua Log Kejadian ({{ allFilteredOvertimeLogs.length }})</span>
                </button>
              </div>
            </div>

            <!-- VIEW 1: RANGKUMAN PER STAF (LEADERBOARD / RANKING & DETAIL) -->
            <div v-if="overtimeSubTab === 'summary'" class="space-y-3">
              <div v-if="staffOvertimeSummaryList.length === 0" class="text-center py-8 text-slate-400 text-xs">
                Tidak ada staf yang tercatat lembur (>18:00) atau hadir pada hari Ahad pada periode ini.
              </div>

              <DataTable
                v-else
                :value="staffOvertimeSummaryList"
                paginator
                :rows="10"
                class="p-datatable-sm"
                stripedRows
                responsiveLayout="scroll"
              >
                <Column header="No." style="width: 50px">
                  <template #body="{ index }">
                    <span class="font-bold text-xs text-slate-500">{{ index + 1 }}</span>
                  </template>
                </Column>

                <Column header="Nama Pegawai" style="min-width: 200px">
                  <template #body="{ data }">
                    <div class="font-bold text-slate-800 dark:text-white text-xs">{{ data.nama_lengkap }}</div>
                    <div class="flex items-center gap-1.5 text-[11px] text-slate-400 mt-0.5">
                      <span>{{ data.unit_name }}</span>
                      <span>&bull;</span>
                      <span>{{ data.position }}</span>
                      <span v-if="data.join_date" class="px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 text-[10px]">
                        TMT: {{ formatDateDisplay(data.join_date) }}
                      </span>
                    </div>
                  </template>
                </Column>

                <Column header="Total Bertugas" style="min-width: 170px">
                  <template #body="{ data }">
                    <div class="flex items-center gap-2 flex-wrap">
                      <span class="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 font-black text-xs border border-indigo-200 dark:border-indigo-900">
                        {{ data.total_kejadian }}x Kejadian
                      </span>
                      <div class="flex items-center gap-1 text-[10px] text-slate-500 font-semibold">
                        <span v-if="data.total_lembur > 0" class="text-indigo-600 font-bold">🌙 {{ data.total_lembur }}x Lembur</span>
                        <span v-if="data.total_lembur > 0 && data.total_ahad > 0">&bull;</span>
                        <span v-if="data.total_ahad > 0" class="text-amber-600 font-bold">☀️ {{ data.total_ahad }}x Ahad</span>
                      </div>
                    </div>
                  </template>
                </Column>

                <Column header="Kategori Kegiatan" style="min-width: 180px">
                  <template #body="{ data }">
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-for="cat in data.categories" 
                        :key="cat"
                        class="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[10px] font-medium"
                      >
                        {{ cat }}
                      </span>
                    </div>
                  </template>
                </Column>

                <Column header="Aksi" style="width: 130px; text-align: center">
                  <template #body="{ data }">
                    <Button
                      label="Lihat Rincian"
                      icon="pi pi-calendar"
                      size="small"
                      severity="info"
                      outlined
                      class="!text-xs !py-1 !px-2.5 font-semibold"
                      @click="openStaffOvertimeDetail(data)"
                    />
                  </template>
                </Column>
              </DataTable>
            </div>

            <!-- VIEW 2: SEMUA LOG KEJADIAN (FLAT LOG) -->
            <div v-else-if="overtimeSubTab === 'all_logs'" class="space-y-3">
              <DataTable 
                :value="allFilteredOvertimeLogs" 
                paginator 
                :rows="10" 
                class="p-datatable-sm" 
                stripedRows 
                responsiveLayout="scroll"
              >
                <Column header="Nama Pegawai" style="min-width: 180px">
                  <template #body="{ data }">
                    <div class="font-bold text-slate-800 dark:text-white text-xs">{{ data.nama_lengkap }}</div>
                    <div class="text-[11px] text-slate-400">{{ data.unit_name }} &bull; {{ data.position }}</div>
                  </template>
                </Column>

                <Column header="Hari &amp; Tanggal" style="min-width: 130px">
                  <template #body="{ data }">
                    <div class="text-xs font-semibold text-slate-700 dark:text-slate-200">
                      {{ data.day_name }}, {{ formatDateDisplay(data.date) }}
                    </div>
                  </template>
                </Column>

                <Column header="Jam Kerja" style="min-width: 120px">
                  <template #body="{ data }">
                    <div class="font-mono text-xs text-slate-700 dark:text-slate-200">
                      <span>{{ data.check_in }}</span> &rarr; <span>{{ data.check_out }}</span>
                    </div>
                  </template>
                </Column>

                <Column header="Tipe Kejadian" style="min-width: 140px">
                  <template #body="{ data }">
                    <div class="flex flex-wrap gap-1">
                      <span 
                        v-if="data.is_overtime" 
                        class="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 text-[10px] font-bold"
                      >
                        🌙 Pulang >18:00
                      </span>
                      <span 
                        v-if="data.is_sunday" 
                        class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 text-[10px] font-bold"
                      >
                        ☀️ Hari Ahad
                      </span>
                    </div>
                  </template>
                </Column>

                <Column header="Kategori" style="min-width: 140px">
                  <template #body="{ data }">
                    <span class="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[11px] font-medium">
                      {{ data.category }}
                    </span>
                  </template>
                </Column>

                <Column header="Alasan / Catatan Presensi" style="min-width: 220px">
                  <template #body="{ data }">
                    <div v-if="data.notes && data.notes.trim()" class="text-xs text-slate-700 dark:text-slate-200">
                      {{ data.notes }}
                    </div>
                    <div v-else class="text-[11px] text-amber-600 font-semibold flex items-center gap-1">
                      <i class="pi pi-exclamation-circle text-[10px]"></i>
                      Tanpa Keterangan
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Tutup" icon="pi pi-times" severity="secondary" text size="small" @click="showAnalyticsModal = false" />
      </template>
    </Dialog>

    <!-- Dialog Rincian Riwayat Tanggal & Kegiatan Lembur / Ahad Pegawai -->
    <Dialog
      v-model:visible="showStaffOvertimeDetailModal"
      modal
      :header="'Riwayat Lembur &amp; Hari Ahad: ' + (selectedStaffOvertimeDetail?.nama_lengkap || '')"
      :style="{ width: '750px', maxWidth: '95vw' }"
    >
      <div v-if="selectedStaffOvertimeDetail" class="space-y-4">
        <!-- Profile Banner -->
        <div class="p-3.5 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div class="font-bold text-sm text-indigo-950 dark:text-indigo-200">
              {{ selectedStaffOvertimeDetail.nama_lengkap }}
            </div>
            <div class="text-xs text-indigo-800/80 dark:text-indigo-300 flex items-center gap-2 mt-0.5">
              <span>NIP: {{ selectedStaffOvertimeDetail.nip || '-' }}</span>
              <span>&bull;</span>
              <span>{{ selectedStaffOvertimeDetail.unit_name }}</span>
              <span>&bull;</span>
              <span>{{ selectedStaffOvertimeDetail.position }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-bold text-xs">
              {{ selectedStaffOvertimeDetail.total_kejadian }}x Total
            </span>
            <span v-if="selectedStaffOvertimeDetail.total_lembur > 0" class="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200 text-xs font-semibold">
              🌙 {{ selectedStaffOvertimeDetail.total_lembur }}x Lembur
            </span>
            <span v-if="selectedStaffOvertimeDetail.total_ahad > 0" class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200 text-xs font-semibold">
              ☀️ {{ selectedStaffOvertimeDetail.total_ahad }}x Ahad
            </span>
          </div>
        </div>

        <!-- Detail Table -->
        <DataTable
          :value="selectedStaffOvertimeDetail.records"
          paginator
          :rows="8"
          class="p-datatable-sm"
          stripedRows
          responsiveLayout="scroll"
        >
          <Column header="Hari &amp; Tanggal" style="min-width: 140px">
            <template #body="{ data }">
              <div class="text-xs font-bold text-slate-800 dark:text-white">
                {{ data.day_name }}, {{ formatDateDisplay(data.date) }}
              </div>
            </template>
          </Column>

          <Column header="Jam Kerja" style="min-width: 110px">
            <template #body="{ data }">
              <span class="font-mono text-xs font-semibold text-slate-700 dark:text-slate-200">
                {{ data.check_in }} &rarr; {{ data.check_out }}
              </span>
            </template>
          </Column>

          <Column header="Tipe" style="min-width: 120px">
            <template #body="{ data }">
              <span 
                v-if="data.is_overtime" 
                class="px-2 py-0.5 rounded bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 text-[10px] font-bold"
              >
                🌙 Pulang >18:00
              </span>
              <span 
                v-else-if="data.is_sunday" 
                class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 text-[10px] font-bold"
              >
                ☀️ Hari Ahad
              </span>
            </template>
          </Column>

          <Column header="Kategori" style="min-width: 130px">
            <template #body="{ data }">
              <span class="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 text-[11px] font-medium">
                {{ data.category }}
              </span>
            </template>
          </Column>

          <Column header="Aktivitas / Catatan Presensi" style="min-width: 200px">
            <template #body="{ data }">
              <span class="text-xs text-slate-700 dark:text-slate-200">{{ data.notes || 'Tanpa keterangan' }}</span>
            </template>
          </Column>
        </DataTable>
      </div>

      <template #footer>
        <Button label="Tutup" severity="secondary" size="small" text @click="showStaffOvertimeDetailModal = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const toast = useToast()
const api = useApi()

// Period Filter State
const periodMode = ref<'1m' | '3m' | '6m' | 'custom'>('1m')
const periodOptions = [
  { label: '1 Bulan', value: '1m' },
  { label: '3 Bulan (Kuartal)', value: '3m' },
  { label: '6 Bulan (Semester)', value: '6m' },
  { label: 'Kustom Rentang', value: 'custom' }
]

const filterMonth = ref(new Date())
const filterStartDate = ref<Date | null>(null)
const filterEndDate = ref<Date | null>(null)
const filterUnit = ref<number | null>(null)

const units = ref<any[]>([])
const recapData = ref<any[]>([])
const loading = ref(false)
const hasFetched = ref(false)

// Quick View Modal
const showRecapModal = ref(false)
const recapModalType = ref<'terlambat' | 'izin_sakit_cuti' | 'alpa'>('alpa')

// Analytics Modal State
const showAnalyticsModal = ref(false)
const analyticsTab = ref<'discipline' | 'overtime'>('discipline')
const analyticsUnit = ref<number | null>(null)
const analyticsEmployeeId = ref<number | null>(null)

function handlePeriodModeChange() {
  if (periodMode.value === 'custom') {
    if (!filterStartDate.value) {
      const now = new Date()
      filterStartDate.value = new Date(now.getFullYear(), now.getMonth(), 1)
      filterEndDate.value = now
    }
  }
  fetchData()
}

// Compute active period string for header/badge
const activePeriodLabel = computed(() => {
  const d = filterMonth.value || new Date()
  const monthNames = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
  ]

  if (periodMode.value === '1m') {
    return `${monthNames[d.getMonth()]} ${d.getFullYear()}`
  } else if (periodMode.value === '3m' || periodMode.value === '6m') {
    const span = periodMode.value === '3m' ? 3 : 6
    const eYear = d.getFullYear()
    const eMonth = d.getMonth()
    const startD = new Date(eYear, eMonth - span + 1, 1)
    return `${monthNames[startD.getMonth()]} ${startD.getFullYear()} - ${monthNames[eMonth]} ${eYear} (${span} Bulan)`
  } else if (periodMode.value === 'custom') {
    if (filterStartDate.value && filterEndDate.value) {
      const s = filterStartDate.value.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
      const e = filterEndDate.value.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
      return `${s} s/d ${e}`
    }
    return 'Kustom Rentang'
  }
  return ''
})

// Period summary statistics
const periodStats = computed(() => {
  const list = recapData.value || []
  const totalEmployees = list.length
  let totalHadir = 0
  let totalTerlambat = 0
  let totalIzinSakitCuti = 0
  let totalAlpa = 0
  let totalTercatat = 0
  let sumPercentage = 0

  for (const item of list) {
    totalHadir += (item.hadir || 0)
    totalTerlambat += (item.terlambat || 0)
    totalIzinSakitCuti += (item.sakit || 0) + (item.izin || 0) + (item.cuti || 0)
    totalAlpa += (item.alpa || 0)
    totalTercatat += (item.total || 0)
    const pct = parseFloat(item.persentase) || 0
    sumPercentage += pct
  }

  const avgPresence = totalEmployees > 0 && totalTercatat > 0
    ? (sumPercentage / totalEmployees).toFixed(1)
    : '0.0'

  return { totalEmployees, totalHadir, totalTerlambat, totalIzinSakitCuti, totalAlpa, totalTercatat, avgPresence }
})

// Quick View Modal helpers
const recapModalTitle = computed(() => {
  if (recapModalType.value === 'terlambat') return `Daftar Pegawai Terlambat — ${activePeriodLabel.value}`
  if (recapModalType.value === 'izin_sakit_cuti') return `Daftar Pegawai Izin / Sakit / Cuti — ${activePeriodLabel.value}`
  return `Daftar Pegawai Alpa (Tanpa Keterangan) — ${activePeriodLabel.value}`
})

const recapModalList = computed(() => {
  const list = recapData.value || []
  if (recapModalType.value === 'terlambat') {
    return list.filter(i => (i.terlambat || 0) > 0).sort((a, b) => (b.terlambat || 0) - (a.terlambat || 0))
  }
  if (recapModalType.value === 'izin_sakit_cuti') {
    return list.filter(i => ((i.sakit || 0) + (i.izin || 0) + (i.cuti || 0)) > 0)
  }
  return list.filter(i => (i.alpa || 0) > 0).sort((a, b) => (b.alpa || 0) - (a.alpa || 0))
})

function openRecapModal(type: 'terlambat' | 'izin_sakit_cuti' | 'alpa') {
  recapModalType.value = type
  showRecapModal.value = true
}

// Fetch Units
const fetchUnits = async () => {
  try {
    const data = await api.get<any[]>('/units')
    units.value = data || []
  } catch (error) {
    console.error('Failed to fetch units')
  }
}

// Fetch Data with Multi-Month support
const fetchData = async () => {
  loading.value = true
  try {
    const query = new URLSearchParams()
    if (filterUnit.value) query.append('unit_id', String(filterUnit.value))

    if (periodMode.value === '1m') {
      const d = filterMonth.value || new Date()
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      query.append('month', `${year}-${month}`)
    } else if (periodMode.value === '3m' || periodMode.value === '6m') {
      const span = periodMode.value === '3m' ? 3 : 6
      const endD = filterMonth.value || new Date()
      const eYear = endD.getFullYear()
      const eMonth = endD.getMonth()
      const lastDay = new Date(eYear, eMonth + 1, 0).getDate()
      const endDateStr = `${eYear}-${String(eMonth + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`

      const startD = new Date(eYear, eMonth - span + 1, 1)
      const sYear = startD.getFullYear()
      const sMonth = startD.getMonth()
      const startDateStr = `${sYear}-${String(sMonth + 1).padStart(2, '0')}-01`

      query.append('start_date', startDateStr)
      query.append('end_date', endDateStr)
    } else if (periodMode.value === 'custom') {
      if (!filterStartDate.value || !filterEndDate.value) {
        toast.add({ severity: 'warn', summary: 'Periode Belum Lengkap', detail: 'Pilih tanggal mulai dan tanggal akhir', life: 3000 })
        loading.value = false
        return
      }
      const sD = filterStartDate.value
      const eD = filterEndDate.value
      const sStr = `${sD.getFullYear()}-${String(sD.getMonth() + 1).padStart(2, '0')}-${String(sD.getDate()).padStart(2, '0')}`
      const eStr = `${eD.getFullYear()}-${String(eD.getMonth() + 1).padStart(2, '0')}-${String(eD.getDate()).padStart(2, '0')}`
      query.append('start_date', sStr)
      query.append('end_date', eStr)
    }

    const data = await api.get<any[]>(`/sdm/attendance/recap?${query.toString()}`)
    recapData.value = data || []
    hasFetched.value = true
  } catch (error) {
    console.error('Fetch recap error:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat rekap presensi', life: 3000 })
  } finally {
    loading.value = false
  }
}

// ------------------- ANALYTICS MODAL LOGIC -------------------
function openAnalyticsModal(empId?: number | null, tab: 'discipline' | 'overtime' = 'discipline') {
  analyticsTab.value = tab
  analyticsUnit.value = filterUnit.value || null
  analyticsEmployeeId.value = empId || null
  showAnalyticsModal.value = true
}

function onAnalyticsFilterChange() {
  analyticsEmployeeId.value = null
}

const analyticsUnitOptions = computed(() => {
  return [
    { label: 'Semua Unit', value: null },
    ...units.value.map(u => ({ label: u.name, value: u.id }))
  ]
})

const analyticsEmployeeOptions = computed(() => {
  let list = recapData.value || []
  if (analyticsUnit.value) {
    list = list.filter(e => e.unit_id === analyticsUnit.value)
  }
  return [
    { label: 'Semua Pegawai (Tren Agregat)', value: null },
    ...list.map(e => ({ label: `${e.nama_lengkap} (${e.unit_name})`, value: e.employee_id }))
  ]
})

const filteredAnalyticsEmployees = computed(() => {
  let list = recapData.value || []
  if (analyticsUnit.value) {
    list = list.filter(e => e.unit_id === analyticsUnit.value)
  }
  if (analyticsEmployeeId.value) {
    list = list.filter(e => e.employee_id === analyticsEmployeeId.value)
  }
  return list
})

const selectedEmployeeDetail = computed(() => {
  if (!analyticsEmployeeId.value) return null
  return (recapData.value || []).find(e => e.employee_id === analyticsEmployeeId.value) || null
})

const analyticsStats = computed(() => {
  const list = filteredAnalyticsEmployees.value
  let totalHadir = 0
  let totalTerlambat = 0
  let totalIzinSakitCuti = 0
  let totalAlpa = 0
  let totalTercatat = 0
  let sumPct = 0

  for (const item of list) {
    totalHadir += (item.hadir || 0)
    totalTerlambat += (item.terlambat || 0)
    totalIzinSakitCuti += (item.sakit || 0) + (item.izin || 0) + (item.cuti || 0)
    totalAlpa += (item.alpa || 0)
    totalTercatat += (item.total || 0)
    sumPct += parseFloat(item.persentase) || 0
  }

  const avgPresence = list.length > 0 && totalTercatat > 0 ? (sumPct / list.length).toFixed(1) : '0.0'
  const lateRate = (totalHadir + totalTerlambat) > 0 ? ((totalTerlambat / (totalHadir + totalTerlambat)) * 100).toFixed(1) : '0.0'

  return { totalHadir, totalTerlambat, totalIzinSakitCuti, totalAlpa, totalTercatat, avgPresence, lateRate }
})

// Monthly Trend breakdown for visual chart
const monthlyTrendList = computed(() => {
  const list = filteredAnalyticsEmployees.value
  const monthMap: Record<string, { hadir: number, terlambat: number, sakit: number, izin: number, cuti: number, alpa: number, total: number }> = {}

  for (const emp of list) {
    const trend = emp.monthly_trend || {}
    for (const [mKey, val] of Object.entries<any>(trend)) {
      if (!monthMap[mKey]) {
        monthMap[mKey] = { hadir: 0, terlambat: 0, sakit: 0, izin: 0, cuti: 0, alpa: 0, total: 0 }
      }
      monthMap[mKey].hadir += (val.hadir || 0)
      monthMap[mKey].terlambat += (val.terlambat || 0)
      monthMap[mKey].sakit += (val.sakit || 0)
      monthMap[mKey].izin += (val.izin || 0)
      monthMap[mKey].cuti += (val.cuti || 0)
      monthMap[mKey].alpa += (val.alpa || 0)
      monthMap[mKey].total += (val.total || 0)
    }
  }

  const sortedKeys = Object.keys(monthMap).sort()
  const monthNames = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

  return sortedKeys.map(key => {
    const [yStr, mStr] = key.split('-')
    const mIdx = parseInt(mStr, 10)
    const mLabel = `${monthNames[mIdx] || mStr} ${yStr}`

    const item = monthMap[key]
    const hadirTepat = Math.max(0, item.hadir - item.terlambat)
    const izinSakit = item.sakit + item.izin + item.cuti
    const grandTotal = item.total > 0 ? item.total : (item.hadir + izinSakit + item.alpa)

    const presencePct = grandTotal > 0 ? ((item.hadir / grandTotal) * 100).toFixed(1) : '0.0'

    const hadirPct = grandTotal > 0 ? (hadirTepat / grandTotal) * 100 : 0
    const terlambatPct = grandTotal > 0 ? (item.terlambat / grandTotal) * 100 : 0
    const izinSakitPct = grandTotal > 0 ? (izinSakit / grandTotal) * 100 : 0
    const alpaPct = grandTotal > 0 ? (item.alpa / grandTotal) * 100 : 0

    return {
      monthKey: key,
      monthLabel: mLabel,
      hadir: item.hadir,
      terlambat: item.terlambat,
      izinSakit,
      alpa: item.alpa,
      total: grandTotal,
      presencePct,
      hadirPct,
      terlambatPct,
      izinSakitPct,
      alpaPct
    }
  })
})

// Unit comparison list
const unitComparisonList = computed(() => {
  const list = recapData.value || []
  const group: Record<string, { unit_name: string, count: number, sumPct: number, totalTerlambat: number, totalAlpa: number }> = {}

  for (const emp of list) {
    const uName = emp.unit_name || 'Tanpa Unit'
    if (!group[uName]) {
      group[uName] = { unit_name: uName, count: 0, sumPct: 0, totalTerlambat: 0, totalAlpa: 0 }
    }
    group[uName].count += 1
    group[uName].sumPct += parseFloat(emp.persentase) || 0
    group[uName].totalTerlambat += (emp.terlambat || 0)
    group[uName].totalAlpa += (emp.alpa || 0)
  }

  return Object.values(group).map(g => ({
    unit_name: g.unit_name,
    count: g.count,
    avgPresence: g.count > 0 ? (g.sumPct / g.count).toFixed(1) : '0.0',
    totalTerlambat: g.totalTerlambat,
    totalAlpa: g.totalAlpa
  })).sort((a, b) => parseFloat(b.avgPresence) - parseFloat(a.avgPresence))
})

// Top Discipline List
const topDisciplineList = computed(() => {
  return [...filteredAnalyticsEmployees.value]
    .sort((a, b) => {
      const diff = parseFloat(b.persentase) - parseFloat(a.persentase)
      if (diff !== 0) return diff
      return (a.terlambat || 0) - (b.terlambat || 0)
    })
    .slice(0, 5)
})

// Needs Attention List
const needsAttentionList = computed(() => {
  return [...filteredAnalyticsEmployees.value]
    .filter(e => (e.alpa || 0) > 0 || (e.terlambat || 0) >= 3)
    .sort((a, b) => ((b.alpa || 0) * 3 + (b.terlambat || 0)) - ((a.alpa || 0) * 3 + (a.terlambat || 0)))
    .slice(0, 5)
})

// ------------------- OVERTIME & SUNDAY LOGIC -------------------
const overtimeSubTab = ref<'summary' | 'all_logs'>('summary')
const showStaffOvertimeDetailModal = ref(false)
const selectedStaffOvertimeDetail = ref<any | null>(null)

const openStaffOvertimeDetail = (staff: any) => {
  selectedStaffOvertimeDetail.value = staff
  showStaffOvertimeDetailModal.value = true
}

const staffOvertimeSummaryList = computed(() => {
  const emps = filteredAnalyticsEmployees.value
  const list: any[] = []

  for (const emp of emps) {
    const records = emp.overtime_records || []
    const totalLembur = emp.total_lembur || 0
    const totalAhad = emp.total_ahad || 0
    const totalKejadian = totalLembur + totalAhad

    if (totalKejadian > 0) {
      const categories = Array.from(new Set(records.map((r: any) => r.category).filter(Boolean)))
      list.push({
        employee_id: emp.employee_id,
        nama_lengkap: emp.nama_lengkap,
        nip: emp.nip,
        unit_name: emp.unit_name,
        position: emp.position,
        join_date: emp.join_date,
        total_kejadian: totalKejadian,
        total_lembur: totalLembur,
        total_ahad: totalAhad,
        categories,
        records: [...records].sort((a: any, b: any) => b.date.localeCompare(a.date))
      })
    }
  }

  return list.sort((a, b) => b.total_kejadian - a.total_kejadian)
})

const allFilteredOvertimeLogs = computed(() => {
  const emps = filteredAnalyticsEmployees.value
  const logs: any[] = []
  for (const emp of emps) {
    for (const rec of (emp.overtime_records || [])) {
      logs.push({
        ...rec,
        employee_id: emp.employee_id,
        nama_lengkap: emp.nama_lengkap,
        unit_name: emp.unit_name,
        position: emp.position
      })
    }
  }
  return logs.sort((a, b) => b.date.localeCompare(a.date))
})

const overtimeStats = computed(() => {
  const emps = filteredAnalyticsEmployees.value
  let totalLembur = 0
  let totalAhad = 0

  for (const emp of emps) {
    totalLembur += (emp.total_lembur || 0)
    totalAhad += (emp.total_ahad || 0)
  }

  const staffOvertimeCounts = emps
    .map(e => ({
      name: e.nama_lengkap,
      unit: e.unit_name,
      count: (e.total_lembur || 0) + (e.total_ahad || 0)
    }))
    .filter(e => e.count > 0)
    .sort((a, b) => b.count - a.count)

  const topStaff = staffOvertimeCounts.length > 0 ? staffOvertimeCounts[0] : null

  return { totalLembur, totalAhad, topStaff }
})

const categoryBreakdownList = computed(() => {
  const logs = allFilteredOvertimeLogs.value
  const counts: Record<string, number> = {
    'Pendampingan Lomba': 0,
    'Kegiatan Keagamaan / Mabit': 0,
    'Rapat Dinas / Yayasan': 0,
    'Akreditasi / Asesmen': 0,
    'Piket Sekolah / SPMB': 0,
    'Lainnya / Umum': 0,
  }

  for (const log of logs) {
    const cat = log.category || 'Lainnya / Umum'
    if (counts[cat] !== undefined) {
      counts[cat] += 1
    } else {
      counts['Lainnya / Umum'] += 1
    }
  }

  const total = logs.length
  return Object.entries(counts)
    .map(([category, count]) => ({
      category,
      count,
      pct: total > 0 ? ((count / total) * 100).toFixed(1) : '0.0'
    }))
    .filter(item => item.count > 0 || total === 0)
    .sort((a, b) => b.count - a.count)
})

const monthlyOvertimeTrendList = computed(() => {
  const emps = filteredAnalyticsEmployees.value
  const monthMap: Record<string, { lembur: number, ahad: number }> = {}

  for (const emp of emps) {
    for (const [mKey, val] of Object.entries<any>(emp.monthly_trend || {})) {
      if (!monthMap[mKey]) {
        monthMap[mKey] = { lembur: 0, ahad: 0 }
      }
      monthMap[mKey].lembur += (val.lembur || 0)
      monthMap[mKey].ahad += (val.ahad || 0)
    }
  }

  const sortedKeys = Object.keys(monthMap).sort()
  const monthNames = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

  return sortedKeys.map(key => {
    const [yStr, mStr] = key.split('-')
    const mIdx = parseInt(mStr, 10)
    const mLabel = `${monthNames[mIdx] || mStr} ${yStr}`
    const item = monthMap[key]
    const total = item.lembur + item.ahad

    return {
      monthKey: key,
      monthLabel: mLabel,
      lembur: item.lembur,
      ahad: item.ahad,
      total
    }
  })
})

function formatDateDisplay(dateStr: string) {
  if (!dateStr) return '-'
  try {
    const [y, m, d] = dateStr.split('-')
    const months = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
    return `${d} ${months[parseInt(m, 10)]} ${y}`
  } catch {
    return dateStr
  }
}

// Export to Excel/CSV
const exportExcel = () => {
  const headers = ['Nama Pegawai', 'NIP', 'Unit', 'Jabatan', 'Hadir Tepat', 'Terlambat', 'Sakit', 'Izin', 'Cuti', 'Alpa', 'Lembur >18:00', 'Hadir Ahad', 'Total Hari', 'Persentase Hadir']
  const rows = recapData.value.map((r: any) => [
    `"${r.nama_lengkap}"`, 
    `"${r.nip || '-'}"`, 
    `"${r.unit_name || '-'}"`,
    `"${r.position || '-'}"`,
    r.hadir, 
    r.terlambat || 0,
    r.sakit, 
    r.izin, 
    r.cuti || 0,
    r.alpa, 
    r.total_lembur || 0,
    r.total_ahad || 0,
    r.total, 
    `"${r.persentase}"`
  ])
  
  const csvContent = "data:text/csv;charset=utf-8,\uFEFF" 
    + headers.join(",") + "\n" 
    + rows.map(e => e.join(",")).join("\n")
    
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  const filename = `Rekap_Presensi_${activePeriodLabel.value.replace(/[^a-zA-Z0-9]/g, '_')}.csv`
  link.setAttribute("download", filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

onMounted(() => {
  fetchUnits()
  fetchData()
})
</script>
