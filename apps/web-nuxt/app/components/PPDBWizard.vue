<template>
  <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-lg p-6 md:p-10">
    <!-- Success State -->
    <Message v-if="submitSuccess" severity="success" class="mb-6">
      <div class="space-y-2">
        <p class="font-bold">🎉 Pendaftaran berhasil dikirim!</p>
        <p>No. Registrasi: <strong>{{ registrationNumber }}</strong></p>
        <p>Status pendaftaran Anda akan diproses oleh panitia. Silakan login untuk memantau status.</p>
      </div>
    </Message>

    <div v-else>
      <!-- Stepper Header -->
      <div class="flex items-center justify-between mb-8 overflow-x-auto pb-4 gap-1">
        <div v-for="(step, index) in activeSteps" :key="step.key"
          class="flex flex-col items-center min-w-[70px] cursor-pointer transition-all"
          @click="goToStep(index)">
          <div :class="[
            'w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm mb-2 transition-all duration-300',
            currentStepIndex === index
              ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg scale-110'
              : currentStepIndex > index
                ? 'bg-emerald-500 text-white'
                : 'bg-slate-100 dark:bg-slate-700 text-slate-400'
          ]">
            <i v-if="currentStepIndex > index" class="pi pi-check text-xs"></i>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span :class="[
            'text-[10px] md:text-xs text-center font-medium leading-tight',
            currentStepIndex === index ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-500'
          ]">{{ step.title }}</span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="h-1.5 w-full bg-slate-100 dark:bg-slate-700 rounded-full mb-8">
        <div class="h-1.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full transition-all duration-500"
          :style="{ width: ((currentStepIndex / (activeSteps.length - 1)) * 100) + '%' }"></div>
      </div>

      <form @submit.prevent="handleNext">
        <!-- ============ STEP 1: Identitas Calon Siswa ============ -->
        <div v-if="currentStepKey === 'siswa'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-indigo-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Identitas Calon Siswa</h3>
          </div>

          <div class="flex flex-col gap-2">
            <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Pilih Unit Pendidikan <span class="text-red-500">*</span></label>
            <div class="grid grid-cols-3 gap-4">
              <div v-for="u in ['RA', 'SDIT', 'SMPIT']" :key="u"
                class="border-2 rounded-xl p-4 text-center cursor-pointer transition-all hover:shadow-md"
                :class="form.unit === u ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 shadow-md' : 'border-slate-200 dark:border-slate-600 hover:border-slate-300'"
                @click="form.unit = u">
                <p class="font-bold text-lg" :class="form.unit === u ? 'text-indigo-600' : ''">{{ u }}</p>
                <p class="text-xs text-slate-500 mt-1">{{ u === 'RA' ? 'Raudlatul Athfal' : u === 'SDIT' ? 'SD Islam Terpadu' : 'SMP Islam Terpadu' }}</p>
              </div>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Nama Lengkap <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.full_name" placeholder="Nama lengkap sesuai akta" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Jenis Kelamin <span class="text-red-500">*</span></label>
              <Select v-model="form.student_data.gender" :options="[{label:'Laki-laki',value:'L'},{label:'Perempuan',value:'P'}]" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">NIK Siswa <span class="text-red-500">*</span></label>
              <InputMask v-model="form.student_data.nik" mask="9999999999999999" placeholder="16 digit NIK" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. KK <span class="text-red-500">*</span></label>
              <InputMask v-model="form.student_data.no_kk" mask="9999999999999999" placeholder="16 digit No. KK" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">NISN</label>
              <InputMask v-model="form.student_data.nisn" mask="9999999999" placeholder="10 digit NISN (opsional)" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tempat Lahir <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.tempat_lahir" placeholder="Contoh: Batam" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tanggal Lahir <span class="text-red-500">*</span></label>
              <DatePicker v-model="form.student_data.tanggal_lahir" dateFormat="dd/mm/yy" placeholder="Pilih tanggal" showIcon :maxDate="new Date()" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Agama <span class="text-red-500">*</span></label>
              <Select v-model="form.student_data.agama" :options="AGAMA_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih agama" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Berkebutuhan Khusus</label>
              <Select v-model="form.student_data.berkebutuhan_khusus" :options="KEBUTUHAN_KHUSUS_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
          </div>

          <!-- Collapsible: Data Sekolah Asal -->
          <div class="border rounded-xl overflow-hidden">
            <button type="button" class="w-full flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
              @click="showSekolahAsal = !showSekolahAsal">
              <span class="font-medium text-sm text-slate-600 dark:text-slate-300">📄 Data Sekolah Asal (Opsional)</span>
              <i :class="['pi', showSekolahAsal ? 'pi-chevron-up' : 'pi-chevron-down']"></i>
            </button>
            <div v-if="showSekolahAsal" class="p-4 grid md:grid-cols-2 gap-4">
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Nama Sekolah Asal</label>
                <InputText v-model="form.student_data.nama_sekolah_asal" placeholder="Nama sekolah sebelumnya" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">NPSN Sekolah Asal</label>
                <InputText v-model="form.student_data.npsn_sekolah_asal" placeholder="8 digit NPSN" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. Seri Ijazah</label>
                <InputText v-model="form.student_data.no_ijazah" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. Seri SKHUN</label>
                <InputText v-model="form.student_data.no_skhun" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. Ujian Nasional</label>
                <InputText v-model="form.student_data.no_un" />
              </div>
            </div>
          </div>
        </div>

        <!-- ============ STEP 2: Alamat & Tempat Tinggal ============ -->
        <div v-if="currentStepKey === 'alamat'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-blue-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Alamat & Tempat Tinggal</h3>
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Alamat Tempat Tinggal <span class="text-red-500">*</span></label>
            <Textarea v-model="form.student_data.alamat" rows="3" placeholder="Jalan, Gang, No. Rumah" />
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">RT <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.rt" placeholder="001" maxlength="3" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">RW <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.rw" placeholder="001" maxlength="3" />
            </div>
            <div class="flex flex-col gap-1.5 col-span-2">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Kelurahan / Desa <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.kelurahan" placeholder="Kelurahan / Desa" />
            </div>
          </div>
          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Kecamatan <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.kecamatan" placeholder="Kecamatan" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Kabupaten / Kota <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.kota" placeholder="Kabupaten / Kota" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Provinsi <span class="text-red-500">*</span></label>
              <InputText v-model="form.student_data.provinsi" placeholder="Provinsi" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Kode Pos</label>
              <InputMask v-model="form.student_data.kode_pos" mask="99999" placeholder="Kode pos" />
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. Telepon Rumah</label>
              <InputText v-model="form.student_data.telp_rumah" placeholder="Opsional" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. HP Siswa</label>
              <InputText v-model="form.student_data.no_hp" placeholder="08xxxxxxxxxx" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Email Pribadi Siswa</label>
              <InputText v-model="form.student_data.email" type="email" placeholder="email@contoh.com" />
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Jenis Tempat Tinggal <span class="text-red-500">*</span></label>
              <Select v-model="form.student_data.jenis_tinggal" :options="TEMPAT_TINGGAL_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Alat Transportasi <span class="text-red-500">*</span></label>
              <Select v-model="form.student_data.transportasi" :options="TRANSPORTASI_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Jarak ke Sekolah (km)</label>
              <InputNumber v-model="form.student_data.jarak" :min="0" :max="100" suffix=" km" placeholder="Opsional" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Waktu Tempuh (menit)</label>
              <InputNumber v-model="form.student_data.waktu_tempuh" :min="0" :max="300" suffix=" menit" placeholder="Opsional" />
            </div>
          </div>
        </div>

        <!-- ============ STEP 3: Data Ayah ============ -->
        <div v-if="currentStepKey === 'ayah'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-cyan-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Data Ayah Kandung</h3>
          </div>
          <div class="bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 p-4 rounded-xl text-sm flex items-start gap-2">
            <i class="pi pi-info-circle mt-0.5"></i>
            <span>Data NIK Ayah akan digunakan sebagai <strong>Username</strong> dan No. WA sebagai <strong>Password</strong> untuk login ke sistem sekolah.</span>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Nama Ayah <span class="text-red-500">*</span></label>
              <InputText v-model="form.father_data.name" placeholder="Nama lengkap ayah" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">NIK Ayah <span class="text-red-500">*</span></label>
              <InputMask v-model="form.father_data.nik" mask="9999999999999999" placeholder="16 digit NIK" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tempat Lahir <span class="text-red-500">*</span></label>
              <InputText v-model="form.father_data.tempat_lahir" placeholder="Kota kelahiran" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tanggal Lahir <span class="text-red-500">*</span></label>
              <DatePicker v-model="form.father_data.tanggal_lahir" dateFormat="dd/mm/yy" placeholder="Pilih tanggal" showIcon :maxDate="new Date()" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Status <span class="text-red-500">*</span></label>
              <Select v-model="form.father_data.status" :options="STATUS_ORTU_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih status" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Pendidikan Terakhir <span class="text-red-500">*</span></label>
              <Select v-model="form.father_data.pendidikan" :options="PENDIDIKAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Pekerjaan <span class="text-red-500">*</span></label>
              <Select v-model="form.father_data.pekerjaan" :options="PEKERJAAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Penghasilan Bulanan <span class="text-red-500">*</span></label>
              <Select v-model="form.father_data.penghasilan" :options="PENGHASILAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Berkebutuhan Khusus</label>
              <Select v-model="form.father_data.berkebutuhan_khusus" :options="KEBUTUHAN_KHUSUS_OPTIONS" optionLabel="label" optionValue="value" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. HP / WhatsApp <span class="text-red-500">*</span></label>
              <InputText v-model="form.father_data.phone" placeholder="08xxxxxxxxxx" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Email</label>
              <InputText v-model="form.father_data.email" type="email" placeholder="email@contoh.com" />
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Alamat (jika berbeda dengan siswa)</label>
            <Textarea v-model="form.father_data.alamat" rows="2" placeholder="Kosongkan jika sama dengan alamat siswa" />
          </div>
        </div>

        <!-- ============ STEP 4: Data Ibu ============ -->
        <div v-if="currentStepKey === 'ibu'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-pink-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Data Ibu Kandung</h3>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Nama Ibu <span class="text-red-500">*</span></label>
              <InputText v-model="form.mother_data.name" placeholder="Nama lengkap ibu" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">NIK Ibu <span class="text-red-500">*</span></label>
              <InputMask v-model="form.mother_data.nik" mask="9999999999999999" placeholder="16 digit NIK" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tempat Lahir <span class="text-red-500">*</span></label>
              <InputText v-model="form.mother_data.tempat_lahir" placeholder="Kota kelahiran" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tanggal Lahir <span class="text-red-500">*</span></label>
              <DatePicker v-model="form.mother_data.tanggal_lahir" dateFormat="dd/mm/yy" placeholder="Pilih tanggal" showIcon :maxDate="new Date()" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Status <span class="text-red-500">*</span></label>
              <Select v-model="form.mother_data.status" :options="STATUS_ORTU_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih status" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Pendidikan Terakhir <span class="text-red-500">*</span></label>
              <Select v-model="form.mother_data.pendidikan" :options="PENDIDIKAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Pekerjaan <span class="text-red-500">*</span></label>
              <Select v-model="form.mother_data.pekerjaan" :options="PEKERJAAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Penghasilan Bulanan <span class="text-red-500">*</span></label>
              <Select v-model="form.mother_data.penghasilan" :options="PENGHASILAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Berkebutuhan Khusus</label>
              <Select v-model="form.mother_data.berkebutuhan_khusus" :options="KEBUTUHAN_KHUSUS_OPTIONS" optionLabel="label" optionValue="value" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. HP / WhatsApp <span class="text-red-500">*</span></label>
              <InputText v-model="form.mother_data.phone" placeholder="08xxxxxxxxxx" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Email</label>
              <InputText v-model="form.mother_data.email" type="email" placeholder="email@contoh.com" />
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Alamat (jika berbeda dengan siswa)</label>
            <Textarea v-model="form.mother_data.alamat" rows="2" placeholder="Kosongkan jika sama dengan alamat siswa" />
          </div>
        </div>

        <!-- ============ STEP 5: Data Wali (Conditional) ============ -->
        <div v-if="currentStepKey === 'wali'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-amber-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Data Wali</h3>
          </div>
          <div class="bg-amber-50 dark:bg-amber-900/20 text-amber-800 dark:text-amber-300 p-4 rounded-xl text-sm flex items-start gap-2">
            <i class="pi pi-exclamation-triangle mt-0.5"></i>
            <span>Data wali wajib diisi karena status salah satu orang tua tidak memungkinkan sebagai wali utama.</span>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Hubungan dengan Anak <span class="text-red-500">*</span></label>
              <Select v-model="form.guardian_data.hubungan" :options="HUBUNGAN_WALI_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih hubungan" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Nama Wali <span class="text-red-500">*</span></label>
              <InputText v-model="form.guardian_data.name" placeholder="Nama lengkap wali" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">NIK Wali <span class="text-red-500">*</span></label>
              <InputMask v-model="form.guardian_data.nik" mask="9999999999999999" placeholder="16 digit NIK" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tempat Lahir <span class="text-red-500">*</span></label>
              <InputText v-model="form.guardian_data.tempat_lahir" placeholder="Kota kelahiran" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tanggal Lahir <span class="text-red-500">*</span></label>
              <DatePicker v-model="form.guardian_data.tanggal_lahir" dateFormat="dd/mm/yy" placeholder="Pilih tanggal" showIcon :maxDate="new Date()" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Pendidikan Terakhir</label>
              <Select v-model="form.guardian_data.pendidikan" :options="PENDIDIKAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Pekerjaan</label>
              <Select v-model="form.guardian_data.pekerjaan" :options="PEKERJAAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Penghasilan Bulanan</label>
              <Select v-model="form.guardian_data.penghasilan" :options="PENGHASILAN_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. HP <span class="text-red-500">*</span></label>
              <InputText v-model="form.guardian_data.phone" placeholder="08xxxxxxxxxx" />
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Alamat</label>
            <Textarea v-model="form.guardian_data.alamat" rows="2" placeholder="Alamat wali" />
          </div>
        </div>

        <!-- ============ STEP 6: Data Periodik & Bantuan Sosial ============ -->
        <div v-if="currentStepKey === 'periodik'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-teal-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Data Periodik Siswa</h3>
          </div>

          <div class="grid md:grid-cols-2 gap-4">
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Tinggi Badan <span class="text-red-500">*</span></label>
              <InputNumber v-model="form.periodic_data.tinggi" :min="30" :max="250" suffix=" cm" placeholder="cm" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Berat Badan <span class="text-red-500">*</span></label>
              <InputNumber v-model="form.periodic_data.berat" :min="5" :max="200" suffix=" kg" placeholder="kg" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Anak Ke- <span class="text-red-500">*</span></label>
              <InputNumber v-model="form.periodic_data.anak_ke" :min="1" :max="20" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Jumlah Saudara Kandung <span class="text-red-500">*</span></label>
              <InputNumber v-model="form.periodic_data.jumlah_saudara" :min="0" :max="20" />
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. Registrasi Akta Lahir</label>
              <InputText v-model="form.periodic_data.no_akta_lahir" placeholder="Opsional" />
            </div>
          </div>

          <!-- Bantuan Sosial -->
          <div class="border rounded-xl p-5 space-y-4 mt-4">
            <div class="flex items-center gap-3">
              <Checkbox v-model="form.periodic_data.penerima_bansos" :binary="true" inputId="bansos" />
              <label for="bansos" class="font-medium text-sm text-slate-700 dark:text-slate-300 cursor-pointer">Apakah menerima bantuan sosial?</label>
            </div>

            <div v-if="form.periodic_data.penerima_bansos" class="space-y-4 pl-4 border-l-2 border-indigo-200">
              <div class="grid md:grid-cols-2 gap-4">
                <div class="flex items-center gap-3">
                  <Checkbox v-model="form.periodic_data.penerima_kps" :binary="true" inputId="kps" />
                  <label for="kps" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">Penerima KPS / PKH</label>
                </div>
                <div v-if="form.periodic_data.penerima_kps" class="flex flex-col gap-1.5">
                  <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. KPS</label>
                  <InputText v-model="form.periodic_data.no_kps" placeholder="Nomor KPS" />
                </div>
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. KKS (Kartu Keluarga Sejahtera)</label>
                <InputText v-model="form.periodic_data.no_kks" placeholder="Nomor KKS" />
              </div>
              <div class="grid md:grid-cols-2 gap-4">
                <div class="flex items-center gap-3">
                  <Checkbox v-model="form.periodic_data.penerima_kip" :binary="true" inputId="kip" />
                  <label for="kip" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">Penerima KIP</label>
                </div>
              </div>
              <div v-if="form.periodic_data.penerima_kip" class="grid md:grid-cols-2 gap-4">
                <div class="flex flex-col gap-1.5">
                  <label class="font-medium text-sm text-slate-700 dark:text-slate-300">No. KIP</label>
                  <InputText v-model="form.periodic_data.no_kip" placeholder="Nomor KIP" />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Nama Tertera di KIP</label>
                  <InputText v-model="form.periodic_data.nama_kip" />
                </div>
              </div>
              <div class="grid md:grid-cols-2 gap-4">
                <div class="flex items-center gap-3">
                  <Checkbox v-model="form.periodic_data.layak_pip" :binary="true" inputId="pip" />
                  <label for="pip" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">Usulan Layak PIP</label>
                </div>
                <div v-if="form.periodic_data.layak_pip" class="flex flex-col gap-1.5">
                  <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Alasan Layak PIP</label>
                  <InputText v-model="form.periodic_data.alasan_pip" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ============ STEP 7: Prestasi & Info Tambahan ============ -->
        <div v-if="currentStepKey === 'prestasi'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-yellow-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Prestasi & Informasi Tambahan</h3>
          </div>

          <!-- Prestasi -->
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <label class="font-medium text-slate-700 dark:text-slate-300">Riwayat Prestasi (Maks. 3)</label>
              <Button v-if="form.achievements_data.length < 3" type="button" severity="secondary" size="small" @click="addPrestasi">
                <i class="pi pi-plus mr-1"></i> Tambah
              </Button>
            </div>

            <div v-for="(prestasi, i) in form.achievements_data" :key="i"
              class="border rounded-xl p-4 space-y-3 relative bg-slate-50 dark:bg-slate-800">
              <button type="button"
                class="absolute top-2 right-2 text-red-400 hover:text-red-600 transition"
                @click="form.achievements_data.splice(i, 1)">
                <i class="pi pi-times"></i>
              </button>
              <p class="text-sm font-semibold text-slate-500">Prestasi #{{ i + 1 }}</p>
              <div class="grid md:grid-cols-2 gap-3">
                <div class="flex flex-col gap-1">
                  <label class="text-xs text-slate-500">Jenis Prestasi</label>
                  <Select v-model="prestasi.jenis" :options="[{l:'Akademik',v:'akademik'},{l:'Non-Akademik',v:'non_akademik'},{l:'Seni',v:'seni'},{l:'Olahraga',v:'olahraga'}]" optionLabel="l" optionValue="v" placeholder="Pilih" />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-xs text-slate-500">Tingkat</label>
                  <Select v-model="prestasi.tingkat" :options="[{l:'Kecamatan',v:'kecamatan'},{l:'Kota/Kabupaten',v:'kota'},{l:'Provinsi',v:'provinsi'},{l:'Nasional',v:'nasional'},{l:'Internasional',v:'internasional'}]" optionLabel="l" optionValue="v" placeholder="Pilih" />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-xs text-slate-500">Nama Prestasi</label>
                  <InputText v-model="prestasi.nama" placeholder="Juara 1 Olimpiade" />
                </div>
                <div class="flex flex-col gap-1">
                  <label class="text-xs text-slate-500">Tahun</label>
                  <InputNumber v-model="prestasi.tahun" :min="2000" :max="2030" :useGrouping="false" placeholder="2025" />
                </div>
                <div class="flex flex-col gap-1 md:col-span-2">
                  <label class="text-xs text-slate-500">Penyelenggara / Asal Sekolah</label>
                  <InputText v-model="prestasi.penyelenggara" placeholder="Nama penyelenggara" />
                </div>
              </div>
            </div>

            <p v-if="form.achievements_data.length === 0" class="text-sm text-slate-400 italic">Belum ada data prestasi. Klik "Tambah" untuk menambahkan.</p>
          </div>

          <!-- Informasi Tambahan -->
          <div class="space-y-4 pt-4 border-t">
            <h4 class="font-bold text-slate-700 dark:text-slate-200">Informasi Tambahan</h4>
            <div class="grid md:grid-cols-2 gap-4">
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Dapat Informasi Pendaftaran dari <span class="text-red-500">*</span></label>
                <Select v-model="form.other_data.sumber_info" :options="SUMBER_INFO_OPTIONS" optionLabel="label" optionValue="value" placeholder="Pilih" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Ada kerabat di Asy Syuuraa? <span class="text-red-500">*</span></label>
                <Select v-model="form.other_data.ada_kerabat" :options="[{label:'Ya',value:'ya'},{label:'Tidak',value:'tidak'}]" optionLabel="label" optionValue="value" placeholder="Pilih" />
              </div>
            </div>
            <div v-if="form.other_data.ada_kerabat === 'ya'" class="grid md:grid-cols-2 gap-4">
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Nama Siswa / Orang Tua Kerabat</label>
                <InputText v-model="form.other_data.nama_kerabat" placeholder="Nama kerabat" />
              </div>
              <div class="flex flex-col gap-1.5">
                <label class="font-medium text-sm text-slate-700 dark:text-slate-300">Kelas</label>
                <InputText v-model="form.other_data.kelas_kerabat" placeholder="Contoh: 3A SDIT" />
              </div>
            </div>
          </div>
        </div>

        <!-- ============ STEP 8: Upload Berkas & Konfirmasi ============ -->
        <div v-if="currentStepKey === 'berkas'" class="space-y-6">
          <div class="flex items-center gap-3 border-b pb-3 mb-4">
            <div class="w-1 h-8 bg-emerald-500 rounded-full"></div>
            <h3 class="text-xl font-bold text-slate-800 dark:text-white">Upload Berkas & Konfirmasi</h3>
          </div>

          <div class="bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 p-4 rounded-xl text-sm flex items-start gap-2">
            <i class="pi pi-info-circle mt-0.5"></i>
            <span>Harap unggah foto atau scan dokumen asli (Format: JPG, PNG, atau PDF).</span>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <CmsImageUploader v-model="form.file_kk_url" label="Kartu Keluarga (KK) *" placeholder="Klik untuk upload KK" accept="image/*,application/pdf" />
            <CmsImageUploader v-model="form.file_akta_url" label="Akta Kelahiran *" placeholder="Klik untuk upload Akta" accept="image/*,application/pdf" />
            <CmsImageUploader v-model="form.file_foto_url" label="Foto 3x4 (Opsional)" placeholder="Bisa dilengkapi nanti" accept="image/*" />
          </div>

          <!-- Review Summary -->
          <div class="mt-8 space-y-4">
            <h4 class="text-lg font-bold text-slate-800 dark:text-white border-b pb-2">📋 Ringkasan Data Pendaftaran</h4>

            <div class="grid md:grid-cols-2 gap-4">
              <!-- Siswa Summary -->
              <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 space-y-2">
                <h5 class="font-bold text-indigo-600 text-sm">Data Siswa</h5>
                <div class="text-sm space-y-1 text-slate-600 dark:text-slate-300">
                  <p><span class="text-slate-400">Nama:</span> {{ form.student_data.full_name }}</p>
                  <p><span class="text-slate-400">NIK:</span> {{ form.student_data.nik }}</p>
                  <p><span class="text-slate-400">TTL:</span> {{ form.student_data.tempat_lahir }}, {{ formatDate(form.student_data.tanggal_lahir) }}</p>
                  <p><span class="text-slate-400">Unit:</span> {{ form.unit }}</p>
                  <p><span class="text-slate-400">Alamat:</span> {{ form.student_data.alamat }}</p>
                </div>
              </div>
              <!-- Ayah Summary -->
              <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 space-y-2">
                <h5 class="font-bold text-cyan-600 text-sm">Data Ayah</h5>
                <div class="text-sm space-y-1 text-slate-600 dark:text-slate-300">
                  <p><span class="text-slate-400">Nama:</span> {{ form.father_data.name }}</p>
                  <p><span class="text-slate-400">NIK:</span> {{ form.father_data.nik }}</p>
                  <p><span class="text-slate-400">HP:</span> {{ form.father_data.phone }}</p>
                  <p><span class="text-slate-400">Pekerjaan:</span> {{ getLabelFor(PEKERJAAN_OPTIONS, form.father_data.pekerjaan) }}</p>
                </div>
              </div>
              <!-- Ibu Summary -->
              <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 space-y-2">
                <h5 class="font-bold text-pink-600 text-sm">Data Ibu</h5>
                <div class="text-sm space-y-1 text-slate-600 dark:text-slate-300">
                  <p><span class="text-slate-400">Nama:</span> {{ form.mother_data.name }}</p>
                  <p><span class="text-slate-400">NIK:</span> {{ form.mother_data.nik }}</p>
                  <p><span class="text-slate-400">HP:</span> {{ form.mother_data.phone }}</p>
                  <p><span class="text-slate-400">Pekerjaan:</span> {{ getLabelFor(PEKERJAAN_OPTIONS, form.mother_data.pekerjaan) }}</p>
                </div>
              </div>
              <!-- Wali Summary (if applicable) -->
              <div v-if="needsWali" class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 space-y-2">
                <h5 class="font-bold text-amber-600 text-sm">Data Wali</h5>
                <div class="text-sm space-y-1 text-slate-600 dark:text-slate-300">
                  <p><span class="text-slate-400">Hubungan:</span> {{ getLabelFor(HUBUNGAN_WALI_OPTIONS, form.guardian_data.hubungan) }}</p>
                  <p><span class="text-slate-400">Nama:</span> {{ form.guardian_data.name }}</p>
                  <p><span class="text-slate-400">HP:</span> {{ form.guardian_data.phone }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Pernyataan -->
          <div class="bg-yellow-50 dark:bg-yellow-900/20 p-5 border border-yellow-200 dark:border-yellow-800 rounded-xl mt-4">
            <div class="flex items-start gap-3">
              <Checkbox v-model="pernyataan" :binary="true" inputId="pernyataan" />
              <label for="pernyataan" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
                Dengan ini saya menyatakan bahwa data yang saya isikan adalah <strong>benar</strong> dan dapat <strong>dipertanggungjawabkan</strong> secara hukum.
              </label>
            </div>
          </div>
        </div>

        <!-- ============ NAVIGATION BUTTONS ============ -->
        <div class="flex justify-between mt-8 pt-4 border-t">
          <Button v-if="currentStepIndex > 0" type="button" severity="secondary" @click="currentStepIndex--">
            <i class="pi pi-arrow-left mr-2"></i> Kembali
          </Button>
          <div v-else></div>

          <Button v-if="currentStepIndex < activeSteps.length - 1" type="submit" :loading="loading">
            Selanjutnya <i class="pi pi-arrow-right ml-2"></i>
          </Button>
          <Button v-else type="button" severity="success" @click="submitFinal" :loading="loading" :disabled="!pernyataan">
            <i class="pi pi-check mr-2"></i> Kirim Pendaftaran
          </Button>
        </div>
      </form>

      <!-- Draft Saved Dialog -->
      <Dialog v-model:visible="showDraftDialog" modal header="✅ Draft Berhasil Disimpan" :style="{ width: '450px' }">
        <div class="space-y-4">
          <p class="text-slate-600">Akun orangtua telah dibuat secara otomatis. Anda dapat login kapan saja untuk melanjutkan pengisian formulir.</p>
          <div class="bg-slate-50 dark:bg-slate-800 rounded-xl p-4 space-y-2">
            <p class="text-sm"><span class="text-slate-400">Username:</span> <strong>{{ draftLoginInfo.username }}</strong></p>
            <p class="text-sm"><span class="text-slate-400">Password:</span> <strong>{{ draftLoginInfo.password }}</strong></p>
            <p class="text-sm"><span class="text-slate-400">No. Registrasi:</span> <strong>{{ registrationNumber }}</strong></p>
          </div>
          <div class="bg-amber-50 dark:bg-amber-900/20 text-amber-800 dark:text-amber-300 p-3 rounded-lg text-xs">
            <i class="pi pi-exclamation-triangle mr-1"></i> Harap simpan informasi login ini. Anda memerlukannya untuk melanjutkan pendaftaran dan mengecek status.
          </div>
        </div>
        <template #footer>
          <Button label="Lanjutkan Pengisian" @click="showDraftDialog = false; currentStepIndex++" />
        </template>
      </Dialog>
    </div>
  </div>
</template>

<script setup>
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const config = useRuntimeConfig()

// --- Dropdown Options ---
const AGAMA_OPTIONS = [
  { label: 'Islam', value: 'islam' },
  { label: 'Kristen Protestan', value: 'kristen' },
  { label: 'Kristen Katolik', value: 'katolik' },
  { label: 'Hindu', value: 'hindu' },
  { label: 'Buddha', value: 'buddha' },
  { label: 'Konghucu', value: 'konghucu' },
]
const KEBUTUHAN_KHUSUS_OPTIONS = [
  { label: 'Tidak', value: 'tidak' },
  { label: 'Tunanetra', value: 'tunanetra' },
  { label: 'Tunarungu', value: 'tunarungu' },
  { label: 'Tunawicara', value: 'tunawicara' },
  { label: 'Tunadaksa', value: 'tunadaksa' },
  { label: 'Tunagrahita', value: 'tunagrahita' },
  { label: 'Tunalaras', value: 'tunalaras' },
  { label: 'Autis', value: 'autis' },
  { label: 'ADHD', value: 'adhd' },
  { label: 'Lainnya', value: 'lainnya' },
]
const TEMPAT_TINGGAL_OPTIONS = [
  { label: 'Tinggal dengan Orang Tua / Wali', value: 'ortu_wali' },
  { label: 'Saudara / Kerabat', value: 'kerabat' },
  { label: 'Asrama Siswa', value: 'asrama_siswa' },
  { label: 'Kontrak / Kost', value: 'kontrak' },
  { label: 'Asrama Pesantren', value: 'asrama_pesantren' },
  { label: 'Panti Asuhan', value: 'panti_asuhan' },
  { label: 'Rumah Singgah', value: 'rumah_singgah' },
  { label: 'Lainnya', value: 'lainnya' },
]
const TRANSPORTASI_OPTIONS = [
  { label: 'Jalan Kaki', value: 'jalan_kaki' },
  { label: 'Sepeda', value: 'sepeda' },
  { label: 'Sepeda Motor', value: 'sepeda_motor' },
  { label: 'Mobil Pribadi', value: 'mobil' },
  { label: 'Antar Jemput', value: 'antar_jemput' },
  { label: 'Angkutan Umum', value: 'angkutan_umum' },
]
const PENDIDIKAN_OPTIONS = [
  { label: 'Tidak Sekolah', value: 'tidak_sekolah' },
  { label: 'Putus SD', value: 'putus_sd' },
  { label: 'SD / Sederajat', value: 'sd' },
  { label: 'SMP / Sederajat', value: 'smp' },
  { label: 'SMA / Sederajat', value: 'sma' },
  { label: 'D1', value: 'd1' },
  { label: 'D2', value: 'd2' },
  { label: 'D3', value: 'd3' },
  { label: 'D4 / S1', value: 'd4_s1' },
  { label: 'S2', value: 's2' },
  { label: 'S3', value: 's3' },
]
const PEKERJAAN_OPTIONS = [
  { label: 'Tidak Bekerja', value: 'tidak_bekerja' },
  { label: 'Nelayan', value: 'nelayan' },
  { label: 'Petani', value: 'petani' },
  { label: 'Peternak', value: 'peternak' },
  { label: 'PNS / TNI / POLRI', value: 'pns_tni_polri' },
  { label: 'Karyawan Swasta', value: 'karyawan_swasta' },
  { label: 'Guru / Dosen', value: 'guru_dosen' },
  { label: 'Pedagang', value: 'pedagang' },
  { label: 'Dokter / Bidan / Perawat', value: 'tenaga_medis' },
  { label: 'Pengacara / Hakim / Jaksa', value: 'tenaga_hukum' },
  { label: 'Wiraswasta', value: 'wiraswasta' },
  { label: 'Wirausaha', value: 'wirausaha' },
  { label: 'Buruh', value: 'buruh' },
  { label: 'Pensiunan', value: 'pensiunan' },
]
const PENGHASILAN_OPTIONS = [
  { label: 'Tidak Berpenghasilan', value: 'tidak_berpenghasilan' },
  { label: 'Kurang dari Rp 500.000', value: 'lt_500k' },
  { label: 'Rp 500.000 – Rp 999.999', value: '500k_999k' },
  { label: 'Rp 1.000.000 – Rp 1.999.999', value: '1m_1.9m' },
  { label: 'Rp 2.000.000 – Rp 4.999.999', value: '2m_4.9m' },
  { label: 'Rp 5.000.000 – Rp 20.000.000', value: '5m_20m' },
  { label: 'Lebih dari Rp 20.000.000', value: 'gt_20m' },
]
const STATUS_ORTU_OPTIONS = [
  { label: 'Masih Hidup', value: 'hidup' },
  { label: 'Sudah Meninggal', value: 'meninggal' },
  { label: 'Tidak Diketahui', value: 'tidak_diketahui' },
]
const HUBUNGAN_WALI_OPTIONS = [
  { label: 'Kakek', value: 'kakek' },
  { label: 'Nenek', value: 'nenek' },
  { label: 'Ayah Sambung', value: 'ayah_sambung' },
  { label: 'Ibu Sambung', value: 'ibu_sambung' },
  { label: 'Paman', value: 'paman' },
  { label: 'Bibi', value: 'bibi' },
  { label: 'Lainnya', value: 'lainnya' },
]
const SUMBER_INFO_OPTIONS = [
  { label: 'Instagram', value: 'ig' },
  { label: 'Facebook', value: 'fb' },
  { label: 'TikTok', value: 'tiktok' },
  { label: 'Kerabat', value: 'kerabat' },
  { label: 'Tetangga', value: 'tetangga' },
  { label: 'Spanduk', value: 'spanduk' },
  { label: 'Masjid', value: 'masjid' },
  { label: 'Lainnya', value: 'lainnya' },
]

// --- State ---
const currentStepIndex = ref(0)
const submitSuccess = ref(false)
const loading = ref(false)
const showSekolahAsal = ref(false)
const showDraftDialog = ref(false)
const pernyataan = ref(false)

const registrationId = ref(null)
const registrationNumber = ref('')
const draftLoginInfo = ref({ username: '', password: '' })

// --- All Steps Definition ---
const ALL_STEPS = [
  { key: 'siswa', title: 'Data Siswa' },
  { key: 'alamat', title: 'Alamat' },
  { key: 'ayah', title: 'Data Ayah' },
  { key: 'ibu', title: 'Data Ibu' },
  { key: 'wali', title: 'Data Wali' },
  { key: 'periodik', title: 'Data Periodik' },
  { key: 'prestasi', title: 'Prestasi' },
  { key: 'berkas', title: 'Berkas' },
]

// --- Form Data ---
const form = reactive({
  unit: '',
  student_data: {
    full_name: '', nik: '', no_kk: '', nisn: '', gender: 'L',
    tempat_lahir: '', tanggal_lahir: null, agama: 'islam',
    berkebutuhan_khusus: 'tidak',
    no_ijazah: '', no_skhun: '', no_un: '',
    npsn_sekolah_asal: '', nama_sekolah_asal: '',
    alamat: '', rt: '', rw: '', kelurahan: '', kecamatan: '',
    kota: '', provinsi: '', kode_pos: '', telp_rumah: '',
    no_hp: '', email: '',
    jenis_tinggal: 'ortu_wali', transportasi: '',
    jarak: null, waktu_tempuh: null,
  },
  father_data: {
    name: '', nik: '', tempat_lahir: '', tanggal_lahir: null,
    status: 'hidup', pendidikan: '', pekerjaan: '', penghasilan: '',
    berkebutuhan_khusus: 'tidak', phone: '', email: '', alamat: '',
  },
  mother_data: {
    name: '', nik: '', tempat_lahir: '', tanggal_lahir: null,
    status: 'hidup', pendidikan: '', pekerjaan: '', penghasilan: '',
    berkebutuhan_khusus: 'tidak', phone: '', email: '', alamat: '',
  },
  guardian_data: {
    hubungan: '', name: '', nik: '', tempat_lahir: '', tanggal_lahir: null,
    pendidikan: '', pekerjaan: '', penghasilan: '',
    berkebutuhan_khusus: 'tidak', phone: '', alamat: '',
  },
  periodic_data: {
    tinggi: null, berat: null, anak_ke: null, jumlah_saudara: null,
    no_akta_lahir: '',
    penerima_bansos: false, penerima_kps: false, no_kps: '',
    no_kks: '', penerima_kip: false, no_kip: '', nama_kip: '',
    layak_pip: false, alasan_pip: '',
  },
  achievements_data: [],
  other_data: {
    sumber_info: '', ada_kerabat: 'tidak',
    nama_kerabat: '', kelas_kerabat: '',
  },
  file_kk_url: '',
  file_akta_url: '',
  file_foto_url: '',
})

// --- Computed ---
const needsWali = computed(() => {
  return form.father_data.status === 'meninggal' ||
    form.father_data.status === 'tidak_diketahui' ||
    form.mother_data.status === 'meninggal' ||
    form.mother_data.status === 'tidak_diketahui'
})

const activeSteps = computed(() => {
  if (needsWali.value) return ALL_STEPS
  return ALL_STEPS.filter(s => s.key !== 'wali')
})

const currentStepKey = computed(() => {
  return activeSteps.value[currentStepIndex.value]?.key || 'siswa'
})

// --- Helpers ---
function getLabelFor(options, value) {
  return options.find(o => o.value === value)?.label || value || '-'
}

function formatDate(d) {
  if (!d) return '-'
  const date = new Date(d)
  return date.toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })
}

function addPrestasi() {
  if (form.achievements_data.length < 3) {
    form.achievements_data.push({ jenis: '', tingkat: '', nama: '', tahun: null, penyelenggara: '' })
  }
}

function goToStep(index) {
  if (index < currentStepIndex.value) {
    currentStepIndex.value = index
  }
}

function cleanNik(val) {
  return (val || '').replace(/[^0-9]/g, '')
}

// --- Validation ---
function validateCurrentStep() {
  const key = currentStepKey.value
  const errors = []

  if (key === 'siswa') {
    if (!form.unit) errors.push('Pilih Unit Pendidikan')
    if (!form.student_data.full_name?.trim()) errors.push('Nama Lengkap wajib diisi')
    if (cleanNik(form.student_data.nik).length !== 16) errors.push('NIK Siswa harus 16 digit')
    if (cleanNik(form.student_data.no_kk).length !== 16) errors.push('No. KK harus 16 digit')
    if (!form.student_data.tempat_lahir?.trim()) errors.push('Tempat Lahir wajib diisi')
    if (!form.student_data.tanggal_lahir) errors.push('Tanggal Lahir wajib diisi')
    if (form.student_data.nisn && cleanNik(form.student_data.nisn).length !== 10) errors.push('NISN harus tepat 10 digit')
  }

  if (key === 'alamat') {
    if (!form.student_data.alamat?.trim()) errors.push('Alamat wajib diisi')
    if (!form.student_data.rt?.trim()) errors.push('RT wajib diisi')
    if (!form.student_data.rw?.trim()) errors.push('RW wajib diisi')
    if (!form.student_data.kelurahan?.trim()) errors.push('Kelurahan wajib diisi')
    if (!form.student_data.kecamatan?.trim()) errors.push('Kecamatan wajib diisi')
    if (!form.student_data.kota?.trim()) errors.push('Kota wajib diisi')
    if (!form.student_data.provinsi?.trim()) errors.push('Provinsi wajib diisi')
    if (!form.student_data.jenis_tinggal) errors.push('Jenis Tempat Tinggal wajib diisi')
    if (!form.student_data.transportasi) errors.push('Alat Transportasi wajib diisi')
  }

  if (key === 'ayah') {
    if (!form.father_data.name?.trim()) errors.push('Nama Ayah wajib diisi')
    if (cleanNik(form.father_data.nik).length !== 16) errors.push('NIK Ayah harus 16 digit')
    if (!form.father_data.tempat_lahir?.trim()) errors.push('Tempat Lahir Ayah wajib diisi')
    if (!form.father_data.tanggal_lahir) errors.push('Tanggal Lahir Ayah wajib diisi')
    if (!form.father_data.status) errors.push('Status Ayah wajib diisi')
    if (!form.father_data.pendidikan) errors.push('Pendidikan Ayah wajib diisi')
    if (!form.father_data.pekerjaan) errors.push('Pekerjaan Ayah wajib diisi')
    if (!form.father_data.penghasilan) errors.push('Penghasilan Ayah wajib diisi')
    if (!form.father_data.phone?.trim()) errors.push('No. HP Ayah wajib diisi')
  }

  if (key === 'ibu') {
    if (!form.mother_data.name?.trim()) errors.push('Nama Ibu wajib diisi')
    if (cleanNik(form.mother_data.nik).length !== 16) errors.push('NIK Ibu harus 16 digit')
    if (!form.mother_data.tempat_lahir?.trim()) errors.push('Tempat Lahir Ibu wajib diisi')
    if (!form.mother_data.tanggal_lahir) errors.push('Tanggal Lahir Ibu wajib diisi')
    if (!form.mother_data.status) errors.push('Status Ibu wajib diisi')
    if (!form.mother_data.pendidikan) errors.push('Pendidikan Ibu wajib diisi')
    if (!form.mother_data.pekerjaan) errors.push('Pekerjaan Ibu wajib diisi')
    if (!form.mother_data.penghasilan) errors.push('Penghasilan Ibu wajib diisi')
    if (!form.mother_data.phone?.trim()) errors.push('No. HP Ibu wajib diisi')
  }

  if (key === 'wali') {
    if (!form.guardian_data.hubungan) errors.push('Hubungan Wali wajib diisi')
    if (!form.guardian_data.name?.trim()) errors.push('Nama Wali wajib diisi')
    if (cleanNik(form.guardian_data.nik).length !== 16) errors.push('NIK Wali harus 16 digit')
    if (!form.guardian_data.phone?.trim()) errors.push('No. HP Wali wajib diisi')
  }

  if (key === 'periodik') {
    if (!form.periodic_data.tinggi) errors.push('Tinggi Badan wajib diisi')
    if (!form.periodic_data.berat) errors.push('Berat Badan wajib diisi')
    if (!form.periodic_data.anak_ke) errors.push('Anak Ke- wajib diisi')
    if (form.periodic_data.jumlah_saudara === null || form.periodic_data.jumlah_saudara === undefined) errors.push('Jumlah Saudara wajib diisi')
  }

  if (key === 'prestasi') {
    if (!form.other_data.sumber_info) errors.push('Sumber Info Pendaftaran wajib diisi')
    if (!form.other_data.ada_kerabat) errors.push('Info kerabat di Asy Syuuraa wajib diisi')
  }

  if (errors.length > 0) {
    toast.add({ severity: 'warn', summary: 'Data Belum Lengkap', detail: errors[0], life: 4000 })
    return false
  }
  return true
}

// --- API Calls ---
async function saveDraft() {
  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/ppdb/register/draft`, {
      method: 'POST',
      body: {
        unit: form.unit,
        student_data: form.student_data,
        father_data: form.father_data,
      }
    })
    registrationId.value = response.registration_id
    registrationNumber.value = response.registration_number
    draftLoginInfo.value = response.login_info
    showDraftDialog.value = true
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Gagal Menyimpan',
      detail: error.data?.detail || 'Terjadi kesalahan',
      life: 4000
    })
  } finally {
    loading.value = false
  }
}

async function saveStep(step, body) {
  if (!registrationId.value) return
  loading.value = true
  try {
    // We need auth token for PUT. Try to get it from localStorage
    const token = localStorage.getItem('token')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

    await $fetch(`${config.public.apiBase}/ppdb/register/${registrationId.value}`, {
      method: 'PUT',
      headers,
      body: { step, ...body }
    })
  } catch (error) {
    console.warn(`Step ${step} save skipped (user may not be logged in yet):`, error.message)
    // Don't block — user may not be logged in. Data will be saved at final submit.
  } finally {
    loading.value = false
  }
}

async function submitFinal() {
  if (!pernyataan.value) {
    toast.add({ severity: 'warn', summary: 'Pernyataan', detail: 'Harap centang pernyataan kebenaran data', life: 3000 })
    return
  }
  if (!form.file_kk_url || !form.file_akta_url) {
    toast.add({ severity: 'warn', summary: 'Berkas Belum Lengkap', detail: 'Harap unggah Kartu Keluarga dan Akta Kelahiran.', life: 3000 })
    return
  }

  loading.value = true
  try {
    if (registrationId.value) {
      // Step-by-step save for logged-in user
      const token = localStorage.getItem('token')
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {}

      await $fetch(`${config.public.apiBase}/ppdb/register/${registrationId.value}`, {
        method: 'PUT',
        headers,
        body: {
          step: 8,
          file_kk_url: form.file_kk_url,
          file_akta_url: form.file_akta_url,
          file_foto_url: form.file_foto_url,
        }
      })
    } else {
      // Fallback: full registration in one shot (legacy)
      await $fetch(`${config.public.apiBase}/ppdb/register`, {
        method: 'POST',
        body: form
      })
    }

    submitSuccess.value = true
    toast.add({ severity: 'success', summary: 'Berhasil!', detail: 'Pendaftaran berhasil dikirim', life: 5000 })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: error.data?.detail || 'Terjadi kesalahan', life: 3000 })
  } finally {
    loading.value = false
  }
}

// --- Step Navigation ---
async function handleNext() {
  if (!validateCurrentStep()) return

  const key = currentStepKey.value

  // Save Point: After Step 3 (Ayah), create draft
  if (key === 'ayah' && !registrationId.value) {
    await saveDraft()
    return // Dialog will handle navigation
  }

  // Auto-save subsequent steps if we have a registration ID
  if (registrationId.value) {
    if (key === 'ibu') {
      await saveStep(4, { mother_data: form.mother_data })
    } else if (key === 'wali') {
      await saveStep(5, { guardian_data: form.guardian_data })
    } else if (key === 'periodik') {
      await saveStep(6, { periodic_data: form.periodic_data })
    } else if (key === 'prestasi') {
      await saveStep(7, { achievements_data: form.achievements_data, other_data: form.other_data })
    }
  }

  if (currentStepIndex.value < activeSteps.value.length - 1) {
    currentStepIndex.value++
  }
}
</script>
