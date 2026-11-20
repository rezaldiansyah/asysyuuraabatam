<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <i class="pi pi-map-marker text-emerald-600"></i>
          Presensi Mandiri (GPS)
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-sm">
          Check-in dan Check-out kehadiran harian berbasis titik lokasi sekolah.
        </p>
      </div>
      <div class="flex gap-2">
        <NuxtLink 
          to="/dashboard/sdm/presensi"
          class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 rounded-xl shadow-sm transition"
        >
          <i class="pi pi-list text-xs"></i>
          Daftar Presensi Harian
        </NuxtLink>
        <NuxtLink 
          to="/dashboard/sdm/presensi/rekap"
          class="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 rounded-xl shadow-sm transition"
        >
          <i class="pi pi-chart-bar text-xs"></i>
          Rekap Saya
        </NuxtLink>
      </div>
    </div>

    <!-- Alert jika user belum memiliki profil pegawai terhubung -->
    <div v-if="!loadingInit && !todayData.has_employee_profile" class="p-4 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-amber-800 dark:text-amber-200 text-sm flex items-start gap-3">
      <i class="pi pi-exclamation-triangle text-xl mt-0.5 text-amber-600"></i>
      <div>
        <div class="font-bold">Akun Anda Belum Terhubung dengan Data Pegawai</div>
        <div class="text-xs text-amber-700 dark:text-amber-300 mt-0.5">
          Akun ini belum memiliki profil pegawai di modul SDM. Silakan hubungi bagian Tata Usaha (TU) untuk sinkronisasi NIK akun dengan data pegawai.
        </div>
      </div>
    </div>

    <!-- Banner Konfirmasi Kehadiran Hari Ini (Persistent) -->
    <div 
      v-if="todayAttendance?.check_in" 
      class="p-4 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition shadow-xs"
      :class="todayAttendance?.check_out 
        ? 'bg-blue-50/90 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800 text-blue-900 dark:text-blue-100' 
        : 'bg-emerald-50/90 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-100'"
    >
      <div class="flex items-center gap-3">
        <div 
          class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-xs"
          :class="todayAttendance?.check_out ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300' : 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900 dark:text-emerald-300'"
        >
          <i :class="todayAttendance?.check_out ? 'pi pi-verified text-xl' : 'pi pi-check-circle text-xl'"></i>
        </div>
        <div>
          <div class="font-bold text-sm">
            {{ todayAttendance?.check_out ? 'Presensi Hari Ini Selesai (Check-In & Check-Out Lengkap)' : 'Presensi Masuk Hari Ini Tercatat' }}
          </div>
          <div class="text-xs opacity-90 mt-0.5 flex flex-wrap gap-x-3 gap-y-0.5">
            <span>Masuk: <b>{{ formatTimeOnly(todayAttendance?.check_in) }} WIB</b> <span v-if="todayAttendance?.check_in_distance != null">({{ todayAttendance.check_in_distance }}m)</span></span>
            <span v-if="todayAttendance?.check_out">Pulang: <b>{{ formatTimeOnly(todayAttendance?.check_out) }} WIB</b> <span v-if="todayAttendance?.check_out_distance != null">({{ todayAttendance.check_out_distance }}m)</span></span>
            <span>Status: <b>{{ getStatusLabel(todayAttendance?.status) }}</b></span>
          </div>
        </div>
      </div>
      <button 
        type="button"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition self-end sm:self-center"
        :class="todayAttendance?.check_out ? 'bg-blue-200/60 dark:bg-blue-900/60 text-blue-800 dark:text-blue-200 hover:bg-blue-200' : 'bg-emerald-200/60 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 hover:bg-emerald-200'"
        @click="scrollToHistory"
      >
        <i class="pi pi-history text-xs"></i>
        <span>Lihat Riwayat Saya</span>
      </button>
    </div>

    <!-- Main Live Attendance Card -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Left Column: Clock & GPS Radar -->
      <div class="md:col-span-1 space-y-4">
        <!-- Live Clock Card -->
        <div class="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-2xl p-6 shadow-md border border-slate-700 flex flex-col items-center text-center">
          <span class="text-xs font-medium text-emerald-400 uppercase tracking-widest bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-800/60 mb-3">
            Waktu Indonesia Barat (WIB)
          </span>
          <div class="text-4xl font-extrabold tracking-tight font-mono text-emerald-300">
            {{ currentTime }}
          </div>
          <div class="text-xs text-slate-300 mt-2 font-medium">
            {{ currentDate }}
          </div>
          <div class="text-[11px] text-slate-400 mt-3 pt-3 border-t border-slate-700/60 w-full flex justify-between">
            <span>Masuk: <b>{{ geofence.work_start_time || '06:45' }}</b></span>
            <span>Target Pulang: <b class="text-emerald-300 font-bold">{{ expectedCheckOutTime }}</b></span>
          </div>
        </div>

        <!-- Employee Info Card -->
        <div v-if="todayData.employee" class="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-sm border border-slate-200 dark:border-slate-700 flex items-center gap-3.5">
          <div class="w-14 h-20 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden bg-slate-100 dark:bg-slate-900 shrink-0 shadow-xs flex items-center justify-center">
            <img 
              v-if="todayData.employee.photo_url" 
              :src="todayData.employee.photo_url" 
              :alt="todayData.employee.nama_lengkap" 
              class="w-full h-full object-cover" 
            />
            <Avatar 
              v-else 
              :image="`https://ui-avatars.com/api/?name=${encodeURIComponent(todayData.employee.nama_lengkap || '')}&background=random`" 
              shape="circle" 
              size="normal" 
            />
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Identitas Pegawai</div>
            <div class="font-bold text-slate-800 dark:text-white truncate">{{ todayData.employee.nama_lengkap }}</div>
            <div class="text-xs text-slate-500 mt-0.5 truncate">NIP: {{ todayData.employee.nip || '-' }}</div>
            <div class="text-xs text-emerald-600 dark:text-emerald-400 font-semibold mt-1 truncate">{{ todayData.employee.position || 'Staf / Guru' }}</div>
          </div>
        </div>

        <!-- Radar Status Card -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 shadow-sm border border-slate-200 dark:border-slate-700 space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-xs font-bold text-slate-700 dark:text-slate-300">Deteksi Sinyal GPS</span>
            <Button 
              icon="pi pi-refresh" 
              text 
              rounded 
              size="small" 
              :loading="detectingGPS" 
              title="Perbarui Posisi GPS"
              @click="getLiveLocation"
            />
          </div>

          <!-- Radar Status Indicator -->
          <div 
            class="p-3.5 rounded-xl border flex items-center gap-3 transition"
            :class="{
              'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-200': gpsStatus === 'in_radius',
              'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-200': gpsStatus === 'out_radius',
              'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200': gpsStatus === 'loading' || gpsStatus === 'error' || gpsStatus === 'prompt',
              'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300': !geofence.is_enabled
            }"
          >
            <div class="relative flex-shrink-0">
              <span v-if="gpsStatus === 'in_radius'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-4 w-4"
                :class="{
                  'bg-emerald-500': gpsStatus === 'in_radius',
                  'bg-rose-500': gpsStatus === 'out_radius',
                  'bg-amber-500': gpsStatus === 'loading' || gpsStatus === 'prompt' || gpsStatus === 'error',
                  'bg-blue-500': !geofence.is_enabled
                }"
              ></span>
            </div>
            
            <div class="text-xs flex-1">
              <div v-if="!geofence.is_enabled" class="font-bold">
                Validasi Radius Nonaktif
              </div>
              <div v-else-if="gpsStatus === 'in_radius'" class="font-bold">
                Dalam Radius Sekolah ({{ currentDistance }}m)
              </div>
              <div v-else-if="gpsStatus === 'out_radius'" class="font-bold">
                Di Luar Radius Sekolah ({{ currentDistance }}m)
              </div>
              <div v-else-if="gpsStatus === 'loading'" class="font-medium">
                Mendeteksi koordinat GPS...
              </div>
              <div v-else class="font-medium">
                {{ gpsErrorMessage || 'Akses lokasi diperlukan' }}
              </div>
              
              <div class="text-[11px] opacity-80 mt-0.5">
                Maksimal radius: {{ geofence.radius_meters }} meter
              </div>
            </div>
          </div>

          <!-- GPS Precision Info -->
          <div v-if="userCoords.lat && userCoords.lng" class="text-[11px] text-slate-400 space-y-0.5">
            <div class="flex justify-between">
              <span>Posisi Anda:</span>
              <span class="font-mono">{{ userCoords.lat.toFixed(5) }}, {{ userCoords.lng.toFixed(5) }}</span>
            </div>
            <div class="flex justify-between" v-if="userCoords.accuracy">
              <span>Akurasi Perangkat:</span>
              <span>±{{ Math.round(userCoords.accuracy) }} meter</span>
            </div>
            <div class="flex justify-between">
              <span>Titik Sekolah:</span>
              <span class="truncate max-w-[150px]">{{ geofence.location_name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Check-in / Check-out Action Card -->
      <div class="md:col-span-2 space-y-5">
        <!-- Status Card Hari Ini -->
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-700 space-y-6">
          <div class="flex justify-between items-center border-b border-slate-100 dark:border-slate-700 pb-4">
            <div>
              <h2 class="text-base font-bold text-slate-800 dark:text-white">Status Presensi Hari Ini</h2>
              <p class="text-xs text-slate-400">Catatan kehadiran tanggal {{ currentDate }}</p>
            </div>
            <span 
              class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
              :class="getStatusBadgeClass(todayAttendance?.status)"
            >
              {{ getStatusLabel(todayAttendance?.status) }}
            </span>
          </div>

          <!-- Log Check-in & Check-out -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Box Check-in -->
            <div 
              class="rounded-xl p-4 border transition"
              :class="todayAttendance?.check_in ? 'bg-emerald-50/60 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800' : 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700'"
            >
              <div class="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                <i class="pi pi-sign-in text-emerald-600"></i>
                <span>Check-in Masuk</span>
              </div>
              <div class="mt-2 text-2xl font-bold font-mono text-slate-800 dark:text-white">
                {{ formatTimeOnly(todayAttendance?.check_in) || '--:--:--' }}
              </div>
              <div class="mt-1 text-xs text-slate-500">
                <span v-if="todayAttendance?.check_in_distance != null">
                  Jarak: {{ todayAttendance.check_in_distance }} meter
                </span>
                <span v-else-if="todayAttendance?.check_in">Tercatat</span>
                <span v-else>Belum check-in</span>
              </div>
            </div>

            <!-- Box Check-out -->
            <div 
              class="rounded-xl p-4 border transition"
              :class="todayAttendance?.check_out ? 'bg-blue-50/60 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800' : 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700'"
            >
              <div class="flex items-center gap-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                <i class="pi pi-sign-out text-blue-600"></i>
                <span>Check-out Pulang</span>
              </div>
              <div class="mt-2 text-2xl font-bold font-mono text-slate-800 dark:text-white">
                {{ formatTimeOnly(todayAttendance?.check_out) || '--:--:--' }}
              </div>
              <div class="mt-1 text-xs text-slate-500">
                <span v-if="todayAttendance?.check_out_distance != null">
                  Jarak: {{ todayAttendance.check_out_distance }} meter
                </span>
                <span v-else-if="todayAttendance?.check_out">Tercatat</span>
                <span v-else>Belum check-out</span>
              </div>
            </div>
          </div>

          <!-- Banner Peringatan Hari Ahad (Libur) -->
          <div v-if="!isFullyCompleted && isSunday" class="p-3.5 rounded-xl border border-amber-300 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/40 text-amber-900 dark:text-amber-200 text-xs flex items-start gap-2.5">
            <i class="pi pi-info-circle text-amber-600 text-base shrink-0 mt-0.5"></i>
            <div>
              <div class="font-bold">Presensi Khusus Hari Ahad (Libur)</div>
              <div class="mt-0.5 text-slate-600 dark:text-slate-300">
                Hari ini adalah akhir pekan. Pastikan Anda memilih <b>Kategori Kegiatan</b> di bawah agar kehadiran lembur/penugasan tercatat resmi untuk evaluasi manajemen yayasan.
              </div>
            </div>
          </div>

          <!-- Opsi Checkbox Tugas Luar / Dinas / Lomba di Luar Sekolah -->
          <div v-if="!isFullyCompleted" class="p-3.5 rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50/70 dark:bg-blue-950/30 space-y-3">
            <div class="flex items-center gap-2.5">
              <Checkbox v-model="isDutyOutside" :binary="true" inputId="is_duty_outside" />
              <label for="is_duty_outside" class="text-xs font-bold text-blue-900 dark:text-blue-200 cursor-pointer select-none">
                Saya sedang Tugas Luar / Dinas / Mengikuti Lomba (Di Luar Sekolah)
              </label>
            </div>
            
            <div v-if="isDutyOutside" class="space-y-2 pt-1 border-t border-blue-200/60 dark:border-blue-800/60 text-xs">
              <div>
                <label class="font-bold text-blue-900 dark:text-blue-200 block mb-1">
                  Keperluan & Lokasi Tugas Luar <span class="text-rose-500">*</span>
                </label>
                <InputText 
                  v-model="dutyReason" 
                  placeholder="Contoh: Rapat Koordinasi Kurikulum di Kantor Dinas Pendidikan / Lomba OSN" 
                  class="w-full text-xs" 
                />
              </div>
              <div class="text-[11px] text-blue-800 dark:text-blue-300 bg-white/70 dark:bg-slate-900/60 p-2 rounded-lg border border-blue-200 dark:border-blue-900">
                <i class="pi pi-map-marker text-blue-600 mr-1"></i>
                Koordinat GPS perangkat Anda (<span class="font-mono">{{ userCoords.lat ? userCoords.lat.toFixed(5) + ', ' + userCoords.lng?.toFixed(5) : 'Mendeteksi...' }}</span>) akan dicatat sebagai bukti kehadiran tugas luar dan status otomatis dicatat sebagai <b>Dispensasi / Tugas Luar</b>.
              </div>
            </div>
          </div>

          <!-- Kategori Kegiatan (Pilihan Cepat untuk Ahad / Tugas Luar / Lembur) -->
          <div v-if="!isFullyCompleted" class="space-y-1.5">
            <div class="flex items-center justify-between">
              <label class="text-xs font-bold text-slate-700 dark:text-slate-300">
                Kategori Kegiatan <span class="text-slate-400 font-normal">(Opsional / Penugasan Khusus)</span>
              </label>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="cat in categoryList"
                :key="cat.value"
                type="button"
                class="px-2.5 py-1 rounded-lg text-xs font-semibold border transition"
                :class="selectedCategory === cat.value ? 'bg-emerald-600 text-white border-emerald-600 shadow-xs' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50'"
                @click="toggleCategory(cat.value)"
              >
                {{ cat.label }}
              </button>
            </div>
          </div>

          <!-- Input Catatan Opsional -->
          <div v-if="!isFullyCompleted" class="space-y-1.5">
            <label class="text-xs font-semibold text-slate-700 dark:text-slate-300">Catatan Tambahan (Opsional)</label>
            <InputText 
              v-model="attendanceNotes" 
              placeholder="Contoh: Surat tugas terlampir / pendampingan 3 siswa" 
              class="w-full text-sm" 
            />
          </div>

          <!-- Tombol Aksi Check-in / Check-out -->
          <div class="pt-2">
            <!-- Kasus 1: Belum Check-in -->
            <div v-if="!todayAttendance?.check_in" class="space-y-2">
              <Button 
                :label="isDutyOutside ? 'Check-in Tugas Luar Sekarang' : 'Check-in Masuk Sekarang'" 
                :icon="isDutyOutside ? 'pi pi-briefcase' : 'pi pi-check-circle'" 
                size="large"
                class="w-full !py-4 font-bold text-base shadow-lg hover:shadow-xl transition"
                :severity="isDutyOutside ? 'info' : 'success'"
                :loading="submitting"
                :disabled="!canCheckIn"
                @click="handleCheckIn"
              />
              <p v-if="!canCheckIn && geofence.is_enabled && !isDutyOutside" class="text-xs text-center text-rose-500">
                *Tombol check-in aktif saat posisi Anda berada di dalam radius {{ geofence.radius_meters }} meter dari sekolah, atau centang opsi Tugas Luar di atas jika berada di luar sekolah.
              </p>
            </div>

            <!-- Kasus 2: Sudah Check-in tapi Belum Check-out -->
            <div v-else-if="todayAttendance?.check_in && !todayAttendance?.check_out" class="space-y-2">
              <Button 
                label="Check-out Pulang Sekarang" 
                icon="pi pi-arrow-right-arrow-left" 
                size="large"
                class="w-full !py-4 font-bold text-base shadow-lg hover:shadow-xl transition"
                severity="info"
                :loading="submitting"
                :disabled="!canCheckOut"
                @click="handleCheckOut"
              />
              <p v-if="!canCheckOut && geofence.is_enabled" class="text-xs text-center text-rose-500">
                *Tombol check-out aktif saat posisi Anda berada di dalam radius sekolah.
              </p>
            </div>

            <!-- Kasus 3: Sudah Check-in dan Check-out Lengkap -->
            <div v-else class="p-4 bg-emerald-50 dark:bg-emerald-950/30 rounded-xl border border-emerald-200 dark:border-emerald-800 text-center space-y-1">
              <i class="pi pi-verified text-3xl text-emerald-600 dark:text-emerald-400"></i>
              <div class="font-bold text-emerald-800 dark:text-emerald-200 text-sm">
                Presensi Hari Ini Telah Selesai
              </div>
              <p class="text-xs text-emerald-700 dark:text-emerald-300">
                Terima kasih atas dedikasi dan kerja keras Anda hari ini. Selamat beristirahat!
              </p>
            </div>
          </div>
        </div>

        <!-- Panduan & Ketentuan Presensi -->
        <div class="bg-slate-50 dark:bg-slate-900/60 rounded-2xl p-5 border border-slate-200 dark:border-slate-700 text-xs text-slate-600 dark:text-slate-400 space-y-2">
          <div class="font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
            <i class="pi pi-info-circle text-sm text-blue-500"></i>
            Ketentuan Presensi GPS Asy-Syuuraa:
          </div>
          <ul class="list-disc list-inside space-y-1 pl-1">
            <li>Pastikan izin lokasi (GPS) pada browser smartphone atau laptop Anda selalu dalam status <b>Izinkan (Allow)</b>.</li>
            <li>Radius check-in maksimal adalah <b>{{ geofence.radius_meters }} meter</b> dari titik gerbang/gedung komplek sekolah.</li>
            <li>Batas jam masuk tepat waktu adalah pukul <b>{{ geofence.work_start_time || '07:30' }} WIB</b>. Lewat dari waktu tersebut sistem otomatis mencatat status <b>Terlambat</b>.</li>
            <li>Jika ada kendala GPS saat berada di sekolah, silakan lapor kepada petugas Tata Usaha (TU) untuk input manual.</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Section Riwayat Presensi Pegawai (30 Hari Terakhir) -->
    <div id="riwayat-presensi-section" class="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-sm border border-slate-200 dark:border-slate-700 space-y-4">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-slate-100 dark:border-slate-700">
        <div>
          <h2 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <i class="pi pi-history text-emerald-600"></i>
            Riwayat Presensi Saya (30 Hari Terakhir)
          </h2>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            Rekap seluruh rekaman check-in & check-out kehadiran pribadi Anda
          </p>
        </div>
        <div class="flex items-center gap-2">
          <Button 
            icon="pi pi-refresh" 
            label="Segarkan" 
            text 
            size="small" 
            class="text-xs font-semibold"
            :loading="historyLoading"
            @click="fetchMyHistory" 
          />
        </div>
      </div>

      <!-- History Stats Summary Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-center">
          <div class="text-[10px] uppercase font-bold text-slate-400">Total Hari</div>
          <div class="text-xl font-extrabold text-slate-800 dark:text-white mt-0.5">{{ myHistory.length }}</div>
        </div>
        <div class="p-3 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 text-center">
          <div class="text-[10px] uppercase font-bold text-emerald-600">Tepat Waktu</div>
          <div class="text-xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">{{ historyStats.presentCount }}</div>
        </div>
        <div class="p-3 rounded-xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 text-center">
          <div class="text-[10px] uppercase font-bold text-amber-600">Terlambat</div>
          <div class="text-xl font-extrabold text-amber-600 dark:text-amber-400 mt-0.5">{{ historyStats.lateCount }}</div>
        </div>
        <div class="p-3 rounded-xl bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 text-center">
          <div class="text-[10px] uppercase font-bold text-blue-600">Tugas / Izin</div>
          <div class="text-xl font-extrabold text-blue-600 dark:text-blue-400 mt-0.5">{{ historyStats.otherCount }}</div>
        </div>
      </div>

      <!-- History Records Table & Cards -->
      <div v-if="historyLoading" class="py-12 text-center text-slate-400 text-xs">
        <i class="pi pi-spin pi-spinner text-2xl mb-2 text-emerald-600"></i>
        <div>Memuat riwayat presensi...</div>
      </div>

      <div v-else-if="myHistory.length === 0" class="py-12 text-center text-slate-400 text-xs">
        <i class="pi pi-calendar-times text-3xl mb-2 text-slate-300"></i>
        <div>Belum ada data presensi tercatat dalam 30 hari terakhir.</div>
      </div>

      <div v-else class="space-y-3">
        <!-- Desktop Table View -->
        <div class="hidden sm:block overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
          <table class="w-full text-xs text-left">
            <thead class="bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-300 uppercase text-[10px] font-bold border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th class="py-3 px-4">Tanggal & Hari</th>
                <th class="py-3 px-4 text-center">Status</th>
                <th class="py-3 px-4">Check-in Masuk</th>
                <th class="py-3 px-4">Check-out Pulang</th>
                <th class="py-3 px-4">Keterangan / Catatan</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
              <tr v-for="item in myHistory" :key="item.id" class="hover:bg-slate-50/70 dark:hover:bg-slate-800/60 transition">
                <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-100 whitespace-nowrap">
                  <div>{{ formatIndoDate(item.date) }}</div>
                  <div class="text-[10px] text-slate-400 font-normal">{{ item.day_name }}</div>
                </td>
                <td class="py-3 px-4 text-center whitespace-nowrap">
                  <span class="px-2.5 py-1 rounded-full text-[10px] font-bold" :class="getStatusBadgeClass(item.status)">
                    {{ getStatusLabel(item.status) }}
                  </span>
                </td>
                <td class="py-3 px-4 whitespace-nowrap">
                  <div class="font-mono font-bold text-slate-800 dark:text-white">
                    {{ formatTimeOnly(item.check_in) || '-' }}
                  </div>
                  <div v-if="item.check_in_distance != null" class="text-[10px] text-slate-400">
                    Jarak: {{ item.check_in_distance }}m
                  </div>
                </td>
                <td class="py-3 px-4 whitespace-nowrap">
                  <div class="font-mono font-bold text-slate-800 dark:text-white">
                    {{ formatTimeOnly(item.check_out) || '-' }}
                  </div>
                  <div v-if="item.check_out_distance != null" class="text-[10px] text-slate-400">
                    Jarak: {{ item.check_out_distance }}m
                  </div>
                </td>
                <td class="py-3 px-4 text-slate-600 dark:text-slate-300">
                  <span v-if="item.notes" class="truncate max-w-[240px] block" :title="item.notes">
                    {{ item.notes }}
                  </span>
                  <span v-else class="text-slate-400">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile Cards View -->
        <div class="block sm:hidden space-y-2.5">
          <div 
            v-for="item in myHistory" 
            :key="'mobile-' + item.id"
            class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/90 shadow-xs space-y-2 text-xs"
          >
            <div class="flex justify-between items-start gap-2">
              <div>
                <div class="font-bold text-slate-800 dark:text-white">{{ formatIndoDate(item.date) }}</div>
                <div class="text-[10px] text-slate-400">{{ item.day_name }}</div>
              </div>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold" :class="getStatusBadgeClass(item.status)">
                {{ getStatusLabel(item.status) }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-2 pt-1 border-t border-slate-100 dark:border-slate-700/60 text-[11px]">
              <div>
                <span class="text-slate-400 block text-[10px]">Check-in Masuk:</span>
                <span class="font-mono font-bold text-slate-800 dark:text-white">{{ formatTimeOnly(item.check_in) || '-' }}</span>
                <span v-if="item.check_in_distance != null" class="text-slate-400 text-[10px] ml-1">({{ item.check_in_distance }}m)</span>
              </div>
              <div>
                <span class="text-slate-400 block text-[10px]">Check-out Pulang:</span>
                <span class="font-mono font-bold text-slate-800 dark:text-white">{{ formatTimeOnly(item.check_out) || '-' }}</span>
                <span v-if="item.check_out_distance != null" class="text-slate-400 text-[10px] ml-1">({{ item.check_out_distance }}m)</span>
              </div>
            </div>
            <div v-if="item.notes" class="pt-1 border-t border-slate-100 dark:border-slate-700/60 text-[11px] text-slate-600 dark:text-slate-300">
              <span class="text-slate-400">Catatan:</span> {{ item.notes }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Dialog Pop-up Konfirmasi Presensi Berhasil -->
    <Dialog 
      v-model:visible="showSuccessDialog" 
      modal 
      :closable="true" 
      :style="{ width: '92vw', maxWidth: '440px' }"
      class="rounded-3xl overflow-hidden shadow-2xl"
    >
      <template #header>
        <div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold">
          <i class="pi pi-check-circle text-xl"></i>
          <span>Konfirmasi Presensi</span>
        </div>
      </template>

      <div class="py-2 text-center space-y-4">
        <!-- Big Icon -->
        <div class="w-16 h-16 mx-auto rounded-full bg-emerald-100 dark:bg-emerald-950/60 border-2 border-emerald-300 dark:border-emerald-700 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shadow-sm">
          <i class="pi pi-check text-3xl font-black"></i>
        </div>

        <div>
          <h3 class="text-lg font-bold text-slate-800 dark:text-white">
            {{ lastActionResult?.title || 'Presensi Berhasil Dicatat!' }}
          </h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {{ lastActionResult?.message || 'Data kehadiran Anda telah resmi tersimpan di sistem yayasan.' }}
          </p>
        </div>

        <!-- Detail Box -->
        <div class="bg-slate-50 dark:bg-slate-900/80 rounded-2xl p-4 border border-slate-200 dark:border-slate-800 text-left text-xs space-y-2.5">
          <div class="flex justify-between items-center pb-2 border-b border-slate-200/60 dark:border-slate-800">
            <span class="text-slate-500">Jenis Presensi:</span>
            <span class="font-bold text-slate-800 dark:text-white">
              {{ lastActionResult?.type === 'in' ? 'Check-in Masuk' : 'Check-out Pulang' }}
            </span>
          </div>
          <div class="flex justify-between items-center pb-2 border-b border-slate-200/60 dark:border-slate-800">
            <span class="text-slate-500">Waktu (WIB):</span>
            <span class="font-mono font-bold text-emerald-600 dark:text-emerald-400 text-sm">
              {{ lastActionResult?.time || currentTime }} WIB
            </span>
          </div>
          <div class="flex justify-between items-center pb-2 border-b border-slate-200/60 dark:border-slate-800">
            <span class="text-slate-500">Status Kehadiran:</span>
            <span 
              class="px-2.5 py-0.5 rounded-full text-[11px] font-bold"
              :class="getStatusBadgeClass(lastActionResult?.status)"
            >
              {{ getStatusLabel(lastActionResult?.status) }}
            </span>
          </div>
          <div class="flex justify-between items-center pb-2 border-b border-slate-200/60 dark:border-slate-800">
            <span class="text-slate-500">Jarak Lokasi (GPS):</span>
            <span class="font-semibold text-slate-700 dark:text-slate-300">
              {{ lastActionResult?.distance != null ? lastActionResult.distance + ' meter dari sekolah' : 'Dalam Area Sekolah' }}
            </span>
          </div>
          <div v-if="lastActionResult?.notes" class="flex justify-between items-start pt-0.5">
            <span class="text-slate-500">Catatan/Agenda:</span>
            <span class="font-medium text-slate-700 dark:text-slate-300 text-right max-w-[200px] truncate">
              {{ lastActionResult.notes }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="w-full flex gap-2">
          <Button 
            label="Tutup & Lihat Riwayat" 
            icon="pi pi-check" 
            class="w-full font-bold text-xs" 
            severity="success"
            @click="showSuccessDialog = false"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()

const loadingInit = ref(true)
const submitting = ref(false)
const detectingGPS = ref(false)
const attendanceNotes = ref('')
const isDutyOutside = ref(false)
const dutyReason = ref('')
const selectedCategory = ref('')

const showSuccessDialog = ref(false)
const lastActionResult = ref<any>(null)
const historyLoading = ref(false)
const myHistory = ref<any[]>([])

const historyStats = computed(() => {
  let presentCount = 0
  let lateCount = 0
  let otherCount = 0
  for (const r of myHistory.value) {
    if (r.status === 'PRESENT') presentCount++
    else if (r.status === 'LATE') lateCount++
    else otherCount++
  }
  return { presentCount, lateCount, otherCount }
})

const isSunday = computed(() => {
  return new Date().getDay() === 0
})

const categoryList = [
  { label: '🏆 Lomba / Ekskul', value: '[LOMBA]' },
  { label: '🕌 Mabit / Keagamaan', value: '[MABIT]' },
  { label: '🏛️ Rapat Dinas / Yayasan', value: '[RAPAT]' },
  { label: '📝 Akreditasi / Asesmen', value: '[AKREDITASI]' },
  { label: '🏢 Piket Sekolah / SPMB', value: '[PIKET]' },
]

function toggleCategory(val: string) {
  if (selectedCategory.value === val) {
    selectedCategory.value = ''
  } else {
    selectedCategory.value = val
  }
}

const currentTime = ref('00:00:00')
const currentDate = ref('')
let timerInterval: any = null

const userCoords = reactive({
  lat: null as number | null,
  lng: null as number | null,
  accuracy: null as number | null
})

const geofence = reactive({
  is_enabled: true,
  latitude: 1.123456,
  longitude: 104.012345,
  radius_meters: 30,
  location_name: 'Komplek Sekolah Asy-Syuuraa Batam',
  work_start_time: '06:45',
  work_end_time: '16:00',
  schedule_ra_mon_thu: '14:00',
  schedule_sdit_mon_thu: '15:00',
  schedule_smpit_mon_thu: '15:30',
  schedule_friday: '11:30',
  schedule_saturday: '12:00',
  schedule_default_mon_thu: '16:00'
})

const todayData = reactive({
  today: '',
  has_employee_profile: true,
  employee: null as any,
  attendance: null as any
})

const todayAttendance = computed(() => todayData.attendance)
const isFullyCompleted = computed(() => !!(todayAttendance.value?.check_in && todayAttendance.value?.check_out))

const expectedCheckOutTime = computed(() => {
  const now = new Date()
  const day = now.getDay() // 0 = Sunday, 1 = Monday, ..., 5 = Friday, 6 = Saturday
  const cfg = geofence as any
  if (day === 0) {
    return 'Libur (Ahad)'
  }

  const uCode = (todayData.employee?.unit?.code || '').toUpperCase().trim()
  const uName = (todayData.employee?.unit?.name || '').toUpperCase().trim()

  // 1. Dynamic unit schedules
  const unitSched = cfg.unit_schedules?.[uCode]
  if (unitSched) {
    if (day === 5) return unitSched.work_end_friday || cfg.schedule_friday || '11:30'
    if (day === 6) return unitSched.work_end_saturday || cfg.schedule_saturday || '12:00'
    return unitSched.work_end_mon_thu || cfg.schedule_default_mon_thu || '15:30'
  }

  // 2. Legacy fallback
  if (day === 5) {
    return cfg.schedule_friday || '11:30'
  }
  if (day === 6) {
    return cfg.schedule_saturday || '12:00'
  }

  // Senin - Kamis
  const raTime = cfg.schedule_ra_mon_thu || '14:00'
  const sditTime = cfg.schedule_sdit_mon_thu || '15:00'
  const smpitTime = cfg.schedule_smpit_mon_thu || '15:30'
  const defaultVal = cfg.schedule_default_mon_thu || cfg.work_end_time || '15:30'

  if (uCode === 'YYS' || uName.includes('YAYASAN') || uName.startsWith('YYS')) {
    return defaultVal
  }
  if (uCode === 'RA' || /\bRA\b/.test(uName) || uName.startsWith('RA ') || uName.includes('RAUDHATUL')) {
    return raTime
  }
  if (uCode === 'SDIT' || uName.includes('SDIT') || /\bSD\b/.test(uName)) {
    return sditTime
  }
  if (uCode === 'SMPIT' || uName.includes('SMPIT') || /\bSMP\b/.test(uName)) {
    return smpitTime
  }

  return defaultVal
})

// Haversine formula on client
function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371000 // Earth's radius in meters
  const dLat = (lat2 - lat1) * (Math.PI / 180)
  const dLon = (lon2 - lon1) * (Math.PI / 180)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * (Math.PI / 180)) * Math.cos(lat2 * (Math.PI / 180)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return Math.round(R * c)
}

const currentDistance = computed(() => {
  if (userCoords.lat == null || userCoords.lng == null) return null
  return calculateDistance(userCoords.lat, userCoords.lng, geofence.latitude, geofence.longitude)
})

const gpsErrorMessage = ref('')
const gpsStatus = computed(() => {
  if (detectingGPS.value) return 'loading'
  if (gpsErrorMessage.value) return 'error'
  if (currentDistance.value == null) return 'prompt'
  if (!geofence.is_enabled) return 'in_radius'
  return currentDistance.value <= geofence.radius_meters ? 'in_radius' : 'out_radius'
})

const canCheckIn = computed(() => {
  if (!todayData.has_employee_profile) return false
  if (todayAttendance.value?.check_in) return false
  if (isDutyOutside.value) {
    return !!(userCoords.lat && userCoords.lng && dutyReason.value.trim())
  }
  if (!geofence.is_enabled) return true
  return gpsStatus.value === 'in_radius'
})

const canCheckOut = computed(() => {
  if (!todayData.has_employee_profile) return false
  if (!todayAttendance.value?.check_in) return false
  if (todayAttendance.value?.check_out) return false
  if (isDutyOutside.value || (todayAttendance.value?.notes || '').includes('Tugas Luar')) {
    return !!(userCoords.lat && userCoords.lng)
  }
  if (!geofence.is_enabled) return true
  return gpsStatus.value === 'in_radius'
})

function updateLiveClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('id-ID', { hour12: false })
  currentDate.value = now.toLocaleDateString('id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function getLiveLocation() {
  if (typeof window === 'undefined' || !navigator.geolocation) {
    gpsErrorMessage.value = 'Browser Anda tidak mendukung geolokasi GPS'
    return
  }
  detectingGPS.value = true
  gpsErrorMessage.value = ''

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      detectingGPS.value = false
      userCoords.lat = pos.coords.latitude
      userCoords.lng = pos.coords.longitude
      userCoords.accuracy = pos.coords.accuracy
      gpsErrorMessage.value = ''
    },
    (err) => {
      detectingGPS.value = false
      if (err.code === 1) gpsErrorMessage.value = 'Izin lokasi ditolak'
      else if (err.code === 2) gpsErrorMessage.value = 'Posisi tidak dapat diperoleh'
      else if (err.code === 3) gpsErrorMessage.value = 'Waktu sinyal GPS habis'
      else gpsErrorMessage.value = 'Gagal membaca GPS'
    },
    { enableHighAccuracy: true, timeout: 12000, maximumAge: 5000 }
  )
}

async function fetchTodayData() {
  loadingInit.value = true
  try {
    const res = await api.get<any>('/sdm/attendance/today')
    if (res) {
      todayData.today = res.today
      todayData.has_employee_profile = res.has_employee_profile
      todayData.employee = res.employee
      todayData.attendance = res.attendance
      if (res.geofence) {
        Object.assign(geofence, res.geofence)
      }
    }
  } catch (e) {
    console.error('Failed to load today attendance', e)
  } finally {
    loadingInit.value = false
  }
}

async function handleCheckIn() {
  if (!userCoords.lat || !userCoords.lng) {
    toast.add({ severity: 'warn', summary: 'GPS Belum Siap', detail: 'Mohon tunggu atau perbarui posisi GPS Anda.', life: 4000 })
    getLiveLocation()
    return
  }

  if (isDutyOutside.value && !dutyReason.value.trim()) {
    toast.add({ severity: 'warn', summary: 'Isi Keperluan Dinas', detail: 'Mohon isi nama agenda dinas / lokasi lomba.', life: 4000 })
    return
  }

  submitting.value = true
  try {
    let finalDuty = dutyReason.value.trim()
    let finalNote = attendanceNotes.value.trim()

    if (selectedCategory.value) {
      if (isDutyOutside.value && finalDuty) {
        if (!finalDuty.startsWith(selectedCategory.value)) {
          finalDuty = `${selectedCategory.value} ${finalDuty}`
        }
      } else if (finalNote) {
        if (!finalNote.startsWith(selectedCategory.value)) {
          finalNote = `${selectedCategory.value} ${finalNote}`
        }
      } else {
        finalNote = selectedCategory.value
      }
    }

    const res = await api.post<any>('/sdm/attendance/check-in', {
      latitude: userCoords.lat,
      longitude: userCoords.lng,
      device_info: typeof navigator !== 'undefined' ? navigator.userAgent : 'Web Browser',
      notes: finalNote || undefined,
      is_duty_outside: isDutyOutside.value,
      duty_reason: finalDuty || undefined
    })

    // Tampilkan pop-up dialog konfirmasi sukses
    lastActionResult.value = {
      type: 'in',
      title: 'Check-in Berhasil Dicatat!',
      message: res.message || 'Check-in masuk Anda telah berhasil disimpan.',
      time: formatTimeOnly(res?.attendance?.check_in || new Date().toISOString()),
      status: res?.attendance?.status || (isDutyOutside.value ? 'DISPENSATION' : 'PRESENT'),
      distance: res?.attendance?.check_in_distance ?? currentDistance.value,
      notes: res?.attendance?.notes || finalNote || finalDuty
    }
    showSuccessDialog.value = true

    toast.add({
      severity: 'success',
      summary: 'Presensi Berhasil',
      detail: res.message || 'Check-in berhasil dicatat.',
      life: 5000
    })
    attendanceNotes.value = ''
    dutyReason.value = ''
    selectedCategory.value = ''
    isDutyOutside.value = false
    await fetchTodayData()
    await fetchMyHistory()
  } catch (e: any) {
    const msg = e?.data?.detail || 'Gagal melakukan check-in'
    toast.add({ severity: 'error', summary: 'Check-in Gagal', detail: msg, life: 6000 })
  } finally {
    submitting.value = false
  }
}

async function handleCheckOut() {
  if (!userCoords.lat || !userCoords.lng) {
    toast.add({ severity: 'warn', summary: 'GPS Belum Siap', detail: 'Mohon tunggu atau perbarui posisi GPS Anda.', life: 4000 })
    getLiveLocation()
    return
  }

  submitting.value = true
  try {
    let finalDuty = dutyReason.value.trim()
    let finalNote = attendanceNotes.value.trim()

    if (selectedCategory.value) {
      if (isDutyOutside.value && finalDuty) {
        if (!finalDuty.startsWith(selectedCategory.value)) {
          finalDuty = `${selectedCategory.value} ${finalDuty}`
        }
      } else if (finalNote) {
        if (!finalNote.startsWith(selectedCategory.value)) {
          finalNote = `${selectedCategory.value} ${finalNote}`
        }
      } else {
        finalNote = selectedCategory.value
      }
    }

    const res = await api.post<any>('/sdm/attendance/check-out', {
      latitude: userCoords.lat,
      longitude: userCoords.lng,
      device_info: typeof navigator !== 'undefined' ? navigator.userAgent : 'Web Browser',
      notes: finalNote || undefined,
      is_duty_outside: isDutyOutside.value,
      duty_reason: finalDuty || undefined
    })

    // Tampilkan pop-up dialog konfirmasi sukses
    lastActionResult.value = {
      type: 'out',
      title: 'Check-out Berhasil Dicatat!',
      message: res.message || 'Check-out pulang Anda telah berhasil disimpan.',
      time: formatTimeOnly(res?.attendance?.check_out || new Date().toISOString()),
      status: res?.attendance?.status || todayAttendance.value?.status || 'PRESENT',
      distance: res?.attendance?.check_out_distance ?? currentDistance.value,
      notes: res?.attendance?.notes || finalNote
    }
    showSuccessDialog.value = true

    toast.add({
      severity: 'success',
      summary: 'Presensi Berhasil',
      detail: res.message || 'Check-out berhasil dicatat.',
      life: 5000
    })
    attendanceNotes.value = ''
    dutyReason.value = ''
    selectedCategory.value = ''
    await fetchTodayData()
    await fetchMyHistory()
  } catch (e: any) {
    const msg = e?.data?.detail || 'Gagal melakukan check-out'
    toast.add({ severity: 'error', summary: 'Check-out Gagal', detail: msg, life: 6000 })
  } finally {
    submitting.value = false
  }
}

async function fetchMyHistory() {
  historyLoading.value = true
  try {
    const res = await api.get<any>('/sdm/attendance/my-history?limit=31')
    if (res && res.records) {
      myHistory.value = res.records
    }
  } catch (e) {
    console.error('Failed to load attendance history', e)
  } finally {
    historyLoading.value = false
  }
}

function formatIndoDate(dateStr?: string | null) {
  if (!dateStr) return '-'
  try {
    const parts = dateStr.split('T')[0].split('-')
    if (parts.length === 3) {
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
      const d = parseInt(parts[2], 10)
      const m = parseInt(parts[1], 10) - 1
      const y = parts[0]
      return `${d} ${months[m] || ''} ${y}`
    }
    const d = new Date(dateStr)
    return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
  } catch {
    return dateStr
  }
}

function scrollToHistory() {
  if (typeof document !== 'undefined') {
    const el = document.getElementById('riwayat-presensi-section')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }
}

function formatTimeOnly(isoStr?: string | null) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return d.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

function getStatusLabel(status?: string | null) {
  if (!status) return 'Belum Presensi'
  const map: Record<string, string> = {
    PRESENT: 'Hadir Tepat Waktu',
    LATE: 'Hadir Terlambat',
    SICK: 'Sakit',
    PERMIT: 'Izin',
    DISPENSATION: 'Dispensasi',
    LEAVE_ANNUAL: 'Cuti Tahunan',
    LEAVE_MATERNITY: 'Cuti Melahirkan',
    LEAVE_MARRIAGE: 'Cuti Menikah',
    LEAVE_BEREAVEMENT: 'Cuti Berkabung',
    LEAVE_PILGRIMAGE: 'Cuti Ibadah',
    LEAVE_UNPAID: 'Cuti Tanpa Tanggungan',
    ABSENT: 'Alpa'
  }
  return map[status] || status
}

function getStatusBadgeClass(status?: string | null) {
  if (!status) return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
  if (status === 'PRESENT') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
  if (status === 'LATE') return 'bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300'
  if (status === 'SICK' || status === 'PERMIT') return 'bg-blue-100 text-blue-700 dark:bg-blue-950/60 dark:text-blue-300'
  if (status.startsWith('LEAVE_')) return 'bg-purple-100 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300'
  return 'bg-rose-100 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300'
}

onMounted(() => {
  updateLiveClock()
  timerInterval = setInterval(updateLiveClock, 1000)
  fetchTodayData()
  fetchMyHistory()
  getLiveLocation()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>
