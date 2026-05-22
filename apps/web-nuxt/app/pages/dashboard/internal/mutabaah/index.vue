<template>
  <div class="space-y-6 max-w-4xl mx-auto">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          <i class="pi pi-calendar-plus text-primary text-2xl"></i>
          Mutaba'ah Yaumiyah
        </h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1">Evaluasi Ibadah, Karakter, dan Pengembangan Diri Harian & Pekanan.</p>
      </div>
      <div v-if="isTUOrAdmin" class="flex flex-col gap-1 w-full md:w-64">
        <label class="text-xs font-semibold text-slate-500 dark:text-slate-400">Pilih Pegawai (Isi atas nama):</label>
        <Select
          v-model="selectedUserId"
          :options="employeeOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Isi untuk Diri Sendiri"
          class="w-full"
          @change="onUserChanged"
        />
      </div>
    </div>

    <!-- Mode Selector Tabs -->
    <div class="flex border-b border-slate-200 dark:border-slate-700">
      <button
        @click="activeTab = 'daily'"
        class="flex-1 py-3 text-center font-medium border-b-2 transition"
        :class="activeTab === 'daily' ? 'border-primary text-primary font-bold' : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400'"
      >
        <i class="pi pi-clock mr-2"></i> Mutaba'ah Harian
      </button>
      <button
        @click="activeTab = 'weekly'"
        class="flex-1 py-3 text-center font-medium border-b-2 transition"
        :class="activeTab === 'weekly' ? 'border-primary text-primary font-bold' : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400'"
      >
        <i class="pi pi-calendar mr-2"></i> Mutaba'ah Pekanan
      </button>
    </div>

    <!-- DAILY MODE -->
    <div v-if="activeTab === 'daily'" class="space-y-6 animate-fade-in">
      <!-- Date & Haid Toggle -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        <div class="flex flex-col gap-2">
          <label class="font-semibold text-slate-700 dark:text-slate-300">Pilih Tanggal Mutaba'ah:</label>
          <Calendar
            v-model="dailyDate"
            dateFormat="yy-mm-dd"
            showIcon
            :maxDate="todayDate"
            @date-select="onDailyDateSelect"
            class="w-full"
          />
          <!-- Backdate Info Badge -->
          <div class="flex items-center gap-2 mt-1">
            <span class="text-xs px-2 py-0.5 rounded-full" :class="isBackdateValid ? 'bg-green-50 text-green-600 dark:bg-green-900/20' : 'bg-red-50 text-red-600 dark:bg-red-900/20'">
              <i class="pi mr-1" :class="isBackdateValid ? 'pi-check-circle' : 'pi-exclamation-triangle'"></i>
              Batas edit: {{ backdateLimitDays }} hari (Maks. {{ formatDate(maxAllowedBackdate) }})
            </span>
          </div>
        </div>

        <div class="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-100 dark:border-slate-800">
          <div>
            <p class="font-semibold text-slate-800 dark:text-white flex items-center gap-2">
              <i class="pi pi-heart-fill text-pink-500"></i>
              Sedang Haid / Uzur Syar'i
            </p>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-0.5">Khusus Akhwat. Ibadah sholat & dzikir otomatis disesuaikan.</p>
          </div>
          <ToggleSwitch v-model="isHaid" />
        </div>
      </div>

      <!-- Daily Form Items -->
      <div v-if="!isBackdateValid" class="p-6 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-2xl border border-red-200 dark:border-red-800 flex items-start gap-3">
        <i class="pi pi-info-circle text-xl mt-0.5"></i>
        <div>
          <h4 class="font-bold">Batas Pengisian Terlewati</h4>
          <p class="text-sm mt-1">Maaf, Anda tidak dapat mengisi atau memperbarui mutaba'ah untuk tanggal ini karena telah melewati batas maksimal {{ backdateLimitDays }} hari ke belakang.</p>
        </div>
      </div>

      <div :class="{ 'opacity-60 pointer-events-none': !isBackdateValid }">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- Column 1: Ruhiyah & Ibadah -->
          <div class="space-y-6">
            <!-- Quran Card -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-book text-emerald-500"></i> Tilawah Al-Qur'an
              </h3>
              <div class="flex flex-col gap-2">
                <label class="text-sm font-semibold text-slate-600 dark:text-slate-400">
                  Jumlah Halaman Hari Ini:
                </label>
                <div class="flex items-center gap-3">
                  <InputNumber
                    v-model="dailyForm.tilawah_pages"
                    :min="0"
                    placeholder="0"
                    showButtons
                    buttonLayout="horizontal"
                    class="w-32"
                  />
                  <span class="text-sm text-slate-400">halaman</span>
                </div>
                <p v-if="isHaid" class="text-xs text-pink-500 italic mt-1">
                  * Uzur Syar'i: Dapat diganti dengan membaca terjemahan/tadabbur Al-Qur'an.
                </p>
              </div>
            </div>

            <!-- Shalat Fardhu -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-shield text-indigo-500"></i> Shalat Fardhu (5 Waktu)
              </h3>
              <p class="text-xs text-slate-400 dark:text-slate-500">
                Laki-laki diutamakan berjamaah di Masjid.
              </p>
              
              <div class="space-y-3">
                <div v-for="waktu in ['subuh', 'dzuhur', 'ashar', 'maghrib', 'isya']" :key="waktu" class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <span class="font-medium text-slate-700 dark:text-slate-300 capitalize">{{ waktu }}</span>
                  <div class="flex items-center gap-2">
                    <span v-if="isHaid" class="text-xs text-pink-500 italic">Uzur Syar'i</span>
                    <Checkbox v-model="dailyForm.ibadah_data['shalat_' + waktu]" :binary="true" :disabled="isHaid" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 2: Dzikir & Sunnah -->
          <div class="space-y-6">
            <!-- Dzikir & Pembiasaan -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-sparkles text-amber-500"></i> Zikir & Pembiasaan Harian
              </h3>
              
              <div class="space-y-3">
                <!-- Zikir Ba'da Shalat -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Zikir Ba'da Shalat</p>
                    <p v-if="isHaid" class="text-xxs text-pink-500 italic mt-0.5">Diganti Shalawat 100x</p>
                  </div>
                  <Checkbox v-model="dailyForm.ibadah_data.zikir_bada_shalat" :binary="true" />
                </div>
                <!-- Zikir Pagi -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <p class="font-medium text-slate-700 dark:text-slate-300">Zikir Al-Ma'tsurat Pagi</p>
                  <Checkbox v-model="dailyForm.ibadah_data.zikir_matsurat_pagi" :binary="true" />
                </div>
                <!-- Zikir Petang -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <p class="font-medium text-slate-700 dark:text-slate-300">Zikir Al-Ma'tsurat Petang</p>
                  <Checkbox v-model="dailyForm.ibadah_data.zikir_matsurat_petang" :binary="true" />
                </div>
                <!-- Menghabiskan Makanan -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <p class="font-medium text-slate-700 dark:text-slate-300">Menghabiskan makanan</p>
                  <Checkbox v-model="dailyForm.ibadah_data.habiskan_makanan" :binary="true" />
                </div>
                <!-- Infaq Harian -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <p class="font-medium text-slate-700 dark:text-slate-300">Infaq Harian</p>
                  <Checkbox v-model="dailyForm.ibadah_data.infaq_harian" :binary="true" />
                </div>
                <!-- Ikrar Asy Syuuraa -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <p class="font-medium text-slate-700 dark:text-slate-300">Mengucapkan Ikrar Asy Syuuraa</p>
                  <Checkbox v-model="dailyForm.ibadah_data.ikrar_asy_syuuraa" :binary="true" />
                </div>
              </div>
            </div>

            <!-- Shalat Sunnah -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-clock text-rose-500"></i> Shalat Sunnah (Rawatib, QL & Dhuha)
              </h3>
              
              <div class="space-y-2">
                <!-- Qiyamul Lail -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Qiyamul Lail (Tahajjud & Witir)</p>
                    <p v-if="isHaid" class="text-xxs text-pink-500 italic mt-0.5">Diganti Shalawat 33x</p>
                  </div>
                  <Checkbox v-model="dailyForm.ibadah_data.qiyamul_lail" :binary="true" />
                </div>
                <!-- Shalat Dhuha -->
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Shalat Dhuha</p>
                    <p v-if="isHaid" class="text-xxs text-pink-500 italic mt-0.5">Diganti Shalawat 33x</p>
                  </div>
                  <Checkbox v-model="dailyForm.ibadah_data.sholat_dhuha" :binary="true" />
                </div>
                
                <!-- Qobliyah/Ba'diyah Grid -->
                <div class="pt-2">
                  <p class="text-xs font-semibold text-slate-500 mb-2">Sunnah Rawatib:</p>
                  <div class="grid grid-cols-2 gap-3 text-xs">
                    <div v-for="rawatib in ['qobliyah_subuh', 'qobliyah_zuhur', 'badiyah_zuhur', 'qobliyah_ashar', 'badiyah_maghrib', 'qobliyah_isya', 'badiyah_isya']" :key="rawatib" class="flex items-center justify-between p-1.5 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-100 dark:border-slate-800">
                      <span class="text-slate-600 dark:text-slate-400 capitalize">{{ rawatib.replace('_', ' ') }}</span>
                      <Checkbox v-model="dailyForm.ibadah_data['rawatib_' + rawatib]" :binary="true" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Notes Reflection Area -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-3 mt-6">
          <label class="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2">
            <i class="pi pi-comment text-slate-500"></i> Catatan & Refleksi Diri (Opsional)
          </label>
          <Textarea v-model="dailyForm.notes" rows="3" class="w-full" placeholder="Tuliskan refleksi harian atau evaluasi kendala Anda hari ini..." />
        </div>

        <!-- Action Submit -->
        <div class="flex justify-end mt-6">
          <Button
            label="Simpan Mutaba'ah Harian"
            icon="pi pi-save"
            :loading="saving"
            class="px-6 py-3 font-semibold text-base"
            @click="submitDailyMutabaah"
          />
        </div>
      </div>
    </div>

    <!-- WEEKLY MODE -->
    <div v-if="activeTab === 'weekly'" class="space-y-6 animate-fade-in">
      <!-- Select Week -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
        <div class="flex flex-col gap-2 w-full md:w-96">
          <label class="font-semibold text-slate-700 dark:text-slate-300">Pilih Pekan Mutaba'ah:</label>
          <Select
            v-model="selectedWeekStart"
            :options="weekOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Pilih Pekan"
            class="w-full"
            @change="onWeekChanged"
          />
        </div>
        
        <div v-if="selectedWeekStart" class="text-xs px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg">
          <p class="font-semibold text-slate-600 dark:text-slate-400">
            Siklus Tarbiyah Aktif: {{ formatDate(weekStartNormalized) }} - {{ formatDate(weekEndNormalized) }}
          </p>
          <p class="text-slate-400 mt-1">Batas edit pekanan: {{ weeklyBackdateDays }} hari.</p>
        </div>
      </div>

      <!-- Weekly Backdate Validation Info -->
      <div v-if="selectedWeekStart && !isWeeklyBackdateValid" class="p-6 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-2xl border border-red-200 dark:border-red-800 flex items-start gap-3">
        <i class="pi pi-info-circle text-xl mt-0.5"></i>
        <div>
          <h4 class="font-bold">Batas Pengisian Pekanan Terlewati</h4>
          <p class="text-sm mt-1">Maaf, Anda tidak dapat mengubah data pekan ini karena sudah melewati batas waktu {{ weeklyBackdateDays }} hari dari Senin pekan tersebut.</p>
        </div>
      </div>

      <!-- Weekly Checklists -->
      <div v-if="selectedWeekStart" :class="{ 'opacity-60 pointer-events-none': !isWeeklyBackdateValid }" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- Column 1: Ruhiyah & Jasadiyah Pekanan -->
          <div class="space-y-6">
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-bookmark text-emerald-500"></i> Ruhiyah & Jasadiyah Pekanan
              </h3>
              
              <div class="space-y-3">
                <!-- Halaqoh -->
                <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900/30 hover:bg-slate-100 rounded-xl transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Bina Pribadi Islam (Halaqoh)</p>
                    <p class="text-xs text-slate-400 mt-0.5">Mengikuti halaqoh minimal 1x per pekan.</p>
                  </div>
                  <Checkbox v-model="weeklyForm.pekanan_data.halaqoh" :binary="true" />
                </div>
                <!-- Puasa Sunnah -->
                <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900/30 hover:bg-slate-100 rounded-xl transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Puasa Sunnah</p>
                    <p class="text-xs text-slate-400 mt-0.5">Melaksanakan puasa sunnah minimal 1x per pekan.</p>
                  </div>
                  <Checkbox v-model="weeklyForm.pekanan_data.puasa_sunnah" :binary="true" />
                </div>
                <!-- Olahraga -->
                <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900/30 hover:bg-slate-100 rounded-xl transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Olahraga (Jasadiyah)</p>
                    <p class="text-xs text-slate-400 mt-0.5">Melakukan aktivitas olahraga/fisik pekanan.</p>
                  </div>
                  <Checkbox v-model="weeklyForm.pekanan_data.olahraga" :binary="true" />
                </div>
              </div>
            </div>

            <!-- Lingkungan & Sosial -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-users text-blue-500"></i> Lingkungan & Sosial
              </h3>
              
              <div class="space-y-3">
                <!-- Kajian/Ta'lim -->
                <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900/30 hover:bg-slate-100 rounded-xl transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Mengikuti Kajian / Ta'lim</p>
                    <p class="text-xs text-slate-400 mt-0.5">Mengikuti kajian rutin/keislaman di luar sekolah.</p>
                  </div>
                  <Checkbox v-model="weeklyForm.pekanan_data.talim_rutin" :binary="true" />
                </div>
                <!-- Kegiatan Sosial -->
                <div class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900/30 hover:bg-slate-100 rounded-xl transition">
                  <div>
                    <p class="font-medium text-slate-700 dark:text-slate-300">Kegiatan Kemasyarakatan</p>
                    <p class="text-xs text-slate-400 mt-0.5">Aktif di RT/RW, gotong royong, atau pertemuan warga.</p>
                  </div>
                  <Checkbox v-model="weeklyForm.pekanan_data.sosmas" :binary="true" />
                </div>
              </div>
            </div>
          </div>

          <!-- Column 2: Fikriyah (Buku & Kajian) Pekanan -->
          <div class="space-y-6">
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-book text-amber-500"></i> Fikriyah & Literasi (Membaca)
              </h3>
              <p class="text-xs text-slate-400 dark:text-slate-500">
                Membaca artikel / buku dalam rentang pekan ini.
              </p>
              
              <div class="space-y-2">
                <div v-for="buku in ['Islam', 'Motivasi', 'Pendidikan', 'Umum']" :key="buku" class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <span class="font-medium text-slate-700 dark:text-slate-300">Membaca Buku/Artikel {{ buku }}</span>
                  <Checkbox v-model="weeklyForm.pekanan_data['membaca_' + buku.toLowerCase()]" :binary="true" />
                </div>
                <div class="flex items-center justify-between p-2 hover:bg-slate-50 dark:hover:bg-slate-700/30 rounded-lg transition">
                  <span class="font-medium text-slate-700 dark:text-slate-300">Membaca Berita / Info Terkini</span>
                  <Checkbox v-model="weeklyForm.pekanan_data.membaca_berita" :binary="true" />
                </div>
              </div>
            </div>

            <!-- Resume Kajian Tarbiyah -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 space-y-4">
              <h3 class="text-base font-bold text-slate-800 dark:text-white flex items-center gap-2 pb-2 border-b dark:border-slate-700">
                <i class="pi pi-pencil text-purple-500"></i> Kajian Bulanan Lembaga
              </h3>
              
              <div class="p-3 bg-purple-50 dark:bg-purple-950/20 border border-purple-100 dark:border-purple-900 rounded-xl flex items-center justify-between">
                <div class="flex-1 mr-4">
                  <p class="font-bold text-purple-800 dark:text-purple-400">Resume Kajian Ust Baihaqi</p>
                  <p class="text-xs text-purple-600 dark:text-purple-500/80 mt-1">
                    Diisi khusus di **Pekan ke-3** tiap bulannya.
                  </p>
                </div>
                <Checkbox v-model="weeklyForm.pekanan_data.resume_kajian" :binary="true" />
              </div>
            </div>
          </div>

        </div>

        <!-- Action Submit -->
        <div class="flex justify-end mt-6">
          <Button
            label="Simpan Mutaba'ah Pekanan"
            icon="pi pi-save"
            :loading="saving"
            class="px-6 py-3 font-semibold text-base"
            @click="submitWeeklyMutabaah"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const authStore = useAuthStore()

// State
const activeTab = ref<'daily' | 'weekly'>('daily')
const dailyDate = ref<Date>(new Date())
const todayDate = ref<Date>(new Date())
const isHaid = ref(false)
const selectedUserId = ref<number | null>(null)
const employees = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)

// Weekly State
const selectedWeekStart = ref<string>('')
const weekOptions = ref<{ label: string; value: string }[]>([])

// Forms
const dailyForm = reactive({
  tilawah_pages: 0,
  notes: '',
  ibadah_data: {} as Record<string, any>
})

const weeklyForm = reactive({
  pekanan_data: {} as Record<string, any>
})

// Current Target User Role Code
const targetUserRole = computed(() => {
  if (!selectedUserId.value || selectedUserId.value === authStore.user?.id) {
    return authStore.user?.role?.code || ''
  }
  const emp = employees.value.find(e => e.user_id === selectedUserId.value)
  return emp?.user?.role?.code || 'karyawan'
})

// Check if current logged in user has TU / Admin privilege
const isTUOrAdmin = computed(() => {
  const code = authStore.user?.role?.code || ''
  return ['superadmin', 'tu_yayasan', 'tu_unit', 'kabid_umum'].includes(code)
})

// Dropdown options for Employees (Only load non-teachers/Karyawan if filling on-behalf)
const employeeOptions = computed(() => {
  const options = [{ label: `Diri Sendiri (${authStore.user?.full_name})`, value: authStore.user?.id || 0 }]
  employees.value.forEach(emp => {
    // Exclude self and exclude Teachers (Guru) as TU cannot fill on behalf of Guru
    if (emp.user_id !== authStore.user?.id && emp.user?.role?.code !== 'guru') {
      options.push({
        label: `${emp.name} (${emp.user?.role?.name || 'Karyawan'})`,
        value: emp.user_id
      })
    }
  })
  return options
})

// Backdate Limit Checks
const backdateLimitDays = computed(() => {
  return targetUserRole.value === 'guru' ? 7 : 20
})

const weeklyBackdateDays = computed(() => {
  return targetUserRole.value === 'guru' ? 14 : 28
})

const maxAllowedBackdate = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() - backdateLimitDays.value)
  return d
})

const isBackdateValid = computed(() => {
  if (!dailyDate.value) return false
  const diffTime = Math.abs(todayDate.value.getTime() - dailyDate.value.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  // If requested date is in future, invalid.
  if (dailyDate.value > todayDate.value) return false
  
  // Calculate exact date difference
  const tDate = new Date(todayDate.value.getFullYear(), todayDate.value.getMonth(), todayDate.value.getDate())
  const rDate = new Date(dailyDate.value.getFullYear(), dailyDate.value.getMonth(), dailyDate.value.getDate())
  const daysDiff = Math.floor((tDate.getTime() - rDate.getTime()) / (1000 * 3600 * 24))
  
  return daysDiff <= backdateLimitDays.value
})

const isWeeklyBackdateValid = computed(() => {
  if (!selectedWeekStart.value) return false
  const wDate = new Date(selectedWeekStart.value)
  const tDate = new Date(todayDate.value.getFullYear(), todayDate.value.getMonth(), todayDate.value.getDate())
  const daysDiff = Math.floor((tDate.getTime() - wDate.getTime()) / (1000 * 3600 * 24))
  
  return daysDiff <= weeklyBackdateDays.value
})

// Normalize date objects for display
const weekStartNormalized = computed(() => {
  if (!selectedWeekStart.value) return new Date()
  return new Date(selectedWeekStart.value)
})

const weekEndNormalized = computed(() => {
  if (!selectedWeekStart.value) return new Date()
  const d = new Date(selectedWeekStart.value)
  d.setDate(d.getDate() + 6)
  return d
})

// Watchers & Handlers
function onUserChanged() {
  // Reload data for newly selected user
  if (activeTab.value === 'daily') {
    fetchDailyMutabaah()
  } else {
    fetchWeeklyMutabaah()
  }
}

function onDailyDateSelect() {
  fetchDailyMutabaah()
}

function onWeekChanged() {
  fetchWeeklyMutabaah()
}

// Generate the 5 cycles of weeks centered around the selected date
function generateWeeksList(date: Date) {
  const options = []
  const y = date.getFullYear()
  const m = date.getMonth()
  
  // Define Tarbiyah Cycle boundaries (26th of last month to 25th of current month)
  let cycleStart: Date
  let cycleEnd: Date
  
  if (date.getDate() >= 26) {
    cycleStart = new Date(y, m, 26)
    cycleEnd = new Date(y, m + 1, 25)
  } else {
    cycleStart = new Date(y, m - 1, 26)
    cycleEnd = new Date(y, m, 25)
  }
  
  // Find Monday of the cycleStart week
  let temp = new Date(cycleStart)
  const day = temp.getDay()
  const diff = temp.getDate() - day + (day === 0 ? -6 : 1)
  let currentMonday = new Date(temp.setDate(diff))
  
  let weekIndex = 1
  while (currentMonday <= cycleEnd) {
    const mondayStr = formatDateISO(currentMonday)
    const sunday = new Date(currentMonday)
    sunday.setDate(sunday.getDate() + 6)
    
    options.push({
      label: `Pekan ${weekIndex} (${formatDateShort(currentMonday)} - ${formatDateShort(sunday)})`,
      value: mondayStr
    })
    
    currentMonday.setDate(currentMonday.getDate() + 7)
    weekIndex++
  }
  
  weekOptions.value = options
  
  // Set default selected week start to the Monday of the current week (or first week in options)
  const today = new Date()
  const tDay = today.getDay()
  const tDiff = today.getDate() - tDay + (tDay === 0 ? -6 : 1)
  const todayMondayStr = formatDateISO(new Date(today.setDate(tDiff)))
  
  const hasCurrentWeek = options.some(opt => opt.value === todayMondayStr)
  if (hasCurrentWeek) {
    selectedWeekStart.value = todayMondayStr
  } else {
    const lastOpt = options[options.length - 1]
    if (lastOpt) {
      selectedWeekStart.value = lastOpt.value
    }
  }
}

// Initializations & API Calls
async function fetchEmployees() {
  if (!isTUOrAdmin.value) return
  try {
    employees.value = await api.get<any[]>('/sdm/employees')
  } catch (e) {
    console.error('Failed to load employees list', e)
  }
}

async function fetchDailyMutabaah() {
  if (!dailyDate.value) return
  loading.value = true
  
  // Reset Daily Form
  dailyForm.tilawah_pages = 0
  dailyForm.notes = ''
  dailyForm.ibadah_data = {
    // 5 Shalat Fardhu
    shalat_subuh: false,
    shalat_dzuhur: false,
    shalat_ashar: false,
    shalat_maghrib: false,
    shalat_isya: false,
    
    // Zikir & Sunnah
    zikir_bada_shalat: false,
    zikir_matsurat_pagi: false,
    zikir_matsurat_petang: false,
    habiskan_makanan: false,
    infaq_harian: false,
    ikrar_asy_syuuraa: false,
    
    qiyamul_lail: false,
    sholat_dhuha: false,
    
    // Rawatib
    rawatib_qobliyah_subuh: false,
    rawatib_qobliyah_zuhur: false,
    rawatib_badiyah_zuhur: false,
    rawatib_qobliyah_ashar: false,
    rawatib_badiyah_maghrib: false,
    rawatib_qobliyah_isya: false,
    rawatib_badiyah_isya: false,
  }
  isHaid.value = false

  try {
    const targetId = selectedUserId.value || authStore.user?.id
    const dateStr = formatDateISO(dailyDate.value)
    
    const records = await api.get<any[]>(`/internal/mutabaah/daily?user_id=${targetId}&start_date=${dateStr}&end_date=${dateStr}`)
    
    if (records && records.length > 0) {
      const record = records[0]
      dailyForm.tilawah_pages = record.tilawah_pages || 0
      dailyForm.notes = record.notes || ''
      
      // Load saved values
      Object.assign(dailyForm.ibadah_data, record.ibadah_data)
      
      // Determine if haid was active (stored inside ibadah_data)
      isHaid.value = !!record.ibadah_data.is_haid
    }
  } catch (e) {
    console.error('Failed to fetch daily mutabaah record', e)
  } finally {
    loading.value = false
  }
}

async function fetchWeeklyMutabaah() {
  if (!selectedWeekStart.value) return
  loading.value = true
  
  // Reset Weekly Form
  weeklyForm.pekanan_data = {
    halaqoh: false,
    puasa_sunnah: false,
    olahraga: false,
    talim_rutin: false,
    sosmas: false,
    
    membaca_islam: false,
    membaca_motivasi: false,
    membaca_pendidikan: false,
    membaca_umum: false,
    membaca_berita: false,
    resume_kajian: false
  }

  try {
    const targetId = selectedUserId.value || authStore.user?.id
    const records = await api.get<any[]>(`/internal/mutabaah/weekly?user_id=${targetId}&start_date=${selectedWeekStart.value}&end_date=${selectedWeekStart.value}`)
    
    if (records && records.length > 0) {
      const record = records[0]
      Object.assign(weeklyForm.pekanan_data, record.pekanan_data)
    }
  } catch (e) {
    console.error('Failed to fetch weekly mutabaah record', e)
  } finally {
    loading.value = false
  }
}

// Watch Haid variable to auto-check prayers
watch(isHaid, (newVal) => {
  // If Haid is checked, we set all prayers to true but locked.
  if (newVal) {
    dailyForm.ibadah_data.is_haid = true
    // Auto check mandatory/recommended replacements
    dailyForm.ibadah_data.shalat_subuh = true
    dailyForm.ibadah_data.shalat_dzuhur = true
    dailyForm.ibadah_data.shalat_ashar = true
    dailyForm.ibadah_data.shalat_maghrib = true
    dailyForm.ibadah_data.shalat_isya = true
    
    dailyForm.ibadah_data.zikir_bada_shalat = true
    dailyForm.ibadah_data.qiyamul_lail = true
    dailyForm.ibadah_data.sholat_dhuha = true
    
    dailyForm.ibadah_data.rawatib_qobliyah_subuh = true
    dailyForm.ibadah_data.rawatib_qobliyah_zuhur = true
    dailyForm.ibadah_data.rawatib_badiyah_zuhur = true
    dailyForm.ibadah_data.rawatib_qobliyah_ashar = true
    dailyForm.ibadah_data.rawatib_badiyah_maghrib = true
    dailyForm.ibadah_data.rawatib_qobliyah_isya = true
    dailyForm.ibadah_data.rawatib_badiyah_isya = true
  } else {
    dailyForm.ibadah_data.is_haid = false
  }
})

// Submit actions
async function submitDailyMutabaah() {
  if (!isBackdateValid.value) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Melebihi batas pengisian backdate!', life: 3000 })
    return
  }
  
  saving.value = true
  try {
    const payload = {
      user_id: selectedUserId.value || authStore.user?.id,
      date: formatDateISO(dailyDate.value),
      tilawah_pages: dailyForm.tilawah_pages,
      notes: dailyForm.notes,
      ibadah_data: {
        ...dailyForm.ibadah_data,
        is_haid: isHaid.value // Track haid status in payload
      }
    }
    
    await api.post('/internal/mutabaah/daily', payload)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Mutaba\'ah harian berhasil disimpan', life: 3000 })
    await fetchDailyMutabaah()
  } catch (e: any) {
    console.error('Save failed', e)
    toast.add({ severity: 'error', summary: 'Gagal Menyimpan', detail: e.message || 'Gagal menyimpan mutaba\'ah harian', life: 3000 })
  } finally {
    saving.value = false
  }
}

async function submitWeeklyMutabaah() {
  if (!isWeeklyBackdateValid.value) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Melebihi batas pengisian pekanan!', life: 3000 })
    return
  }
  
  saving.value = true
  try {
    const payload = {
      user_id: selectedUserId.value || authStore.user?.id,
      week_start_date: selectedWeekStart.value,
      pekanan_data: weeklyForm.pekanan_data
    }
    
    await api.post('/internal/mutabaah/weekly', payload)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Mutaba\'ah pekanan berhasil disimpan', life: 3000 })
    await fetchWeeklyMutabaah()
  } catch (e: any) {
    console.error('Save failed', e)
    toast.add({ severity: 'error', summary: 'Gagal Menyimpan', detail: e.message || 'Gagal menyimpan mutaba\'ah pekanan', life: 3000 })
  } finally {
    saving.value = false
  }
}

// Helpers
function formatDate(d: Date) {
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatDateShort(d: Date) {
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
}

function formatDateISO(d: Date) {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

onMounted(async () => {
  selectedUserId.value = authStore.user?.id || null
  generateWeeksList(new Date())
  await fetchEmployees()
  await fetchDailyMutabaah()
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.25s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.text-xxs {
  font-size: 0.65rem;
}
</style>
