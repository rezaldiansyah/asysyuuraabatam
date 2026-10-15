<template>
  <div class="space-y-4 text-sm" v-if="employee">
    <!-- Top bar -->
    <div class="flex justify-between items-center gap-3">
      <div class="flex items-center gap-2 min-w-0">
        <Button icon="pi pi-arrow-left" text rounded size="small" @click="router.push('/dashboard/sdm/pegawai')" />
        <div class="min-w-0">
          <h1 class="text-lg font-semibold text-slate-800 dark:text-white leading-tight">Profil Pegawai</h1>
          <p class="text-xs text-slate-500 dark:text-slate-400">Detail informasi kepegawaian dan riwayat.</p>
        </div>
      </div>
      <div class="flex gap-2 shrink-0">
        <Button label="Edit" icon="pi pi-pencil" outlined size="small" @click="openEdit" />
        <Button v-if="employee.is_active" label="Nonaktifkan" icon="pi pi-power-off" severity="danger" outlined size="small" @click="deactivate" />
      </div>
    </div>

    <!-- Header profil -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 flex flex-col sm:flex-row items-center sm:items-start gap-5">
      <!-- Pasfoto 4x6 cm Box (Rasio 2:3) -->
      <div class="relative shrink-0 flex flex-col items-center">
        <div class="w-24 h-36 rounded-xl border-2 border-slate-200 dark:border-slate-700 overflow-hidden bg-slate-100 dark:bg-slate-900 shadow-sm relative flex items-center justify-center">
          <img 
            v-if="employee.photo_url" 
            :src="employee.photo_url" 
            :alt="employee.nama_lengkap" 
            class="w-full h-full object-cover"
          />
          <div v-else class="flex flex-col items-center justify-center text-slate-400 p-2 text-center">
            <i class="pi pi-user text-3xl mb-1"></i>
            <span class="text-[9px] font-medium leading-tight">Pasfoto 4x6</span>
          </div>
          <div v-if="uploadingPhoto" class="absolute inset-0 bg-black/60 flex flex-col items-center justify-center text-white text-xs gap-1">
            <i class="pi pi-spin pi-spinner text-xl"></i>
            <span class="text-[10px]">Mengupload...</span>
          </div>
        </div>

        <!-- Tombol Aksi Pasfoto Cepat -->
        <div class="flex items-center gap-1 mt-2">
          <input 
            type="file" 
            ref="photoFileInput" 
            class="hidden" 
            accept="image/png,image/jpeg,image/jpg,image/webp" 
            @change="handlePhotoUpload"
          />
          <Button 
            label="Ganti Foto" 
            icon="pi pi-camera" 
            size="small" 
            outlined 
            class="!text-[11px] !py-1 !px-2 font-medium" 
            :loading="uploadingPhoto"
            @click="triggerPhotoInput" 
          />
          <Button 
            v-if="employee.photo_url"
            icon="pi pi-trash" 
            size="small" 
            text 
            severity="danger" 
            class="!py-1 !px-1.5" 
            title="Hapus Pasfoto"
            @click="deletePhoto" 
          />
        </div>
        <span class="text-[10px] text-slate-400 mt-0.5">Standar 4x6 (Maks 2MB)</span>
      </div>

      <div class="text-center sm:text-left flex-1 min-w-0">
        <h2 class="text-xl font-bold text-slate-800 dark:text-white">{{ employee.nama_lengkap }}</h2>
        <div class="text-slate-600 dark:text-slate-300 mt-0.5 text-sm">
          {{ employee.position || 'Jabatan belum diatur' }} <span class="text-slate-400">•</span> {{ employee.unit?.name || 'Unit belum diatur' }}
        </div>
        <div class="flex flex-wrap gap-1.5 mt-2.5 justify-center sm:justify-start">
          <Tag :value="employee.employee_type" severity="info" class="uppercase !text-xs" />
          <Tag :value="employee.is_active ? 'Aktif' : 'Nonaktif'" :severity="employee.is_active ? 'success' : 'danger'" class="!text-xs" />
          <Tag :value="`NIK: ${employee.nik_kepegawaian || '-'}`" severity="secondary" class="!text-xs" />
          <Tag v-if="employee.user?.email" :value="employee.user.email" severity="secondary" class="!text-xs" />
        </div>
      </div>
    </div>

    <!-- Masa kerja -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3">
        <div class="text-xs text-slate-500">Masa Kerja</div>
        <div class="font-semibold text-slate-800 dark:text-slate-100 mt-0.5"><i class="pi pi-clock text-blue-500 mr-1.5 text-xs"></i>{{ computedInfo?.masa_kerja || '-' }}</div>
        <div class="text-[11px] text-slate-400 mt-0.5">Dihitung sejak TMT {{ formatDate(employee.join_date) }}</div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3">
        <div class="text-xs text-slate-500">Usia Pensiun (55 th)</div>
        <div class="font-semibold text-slate-800 dark:text-slate-100 mt-0.5"><i class="pi pi-calendar text-orange-500 mr-1.5 text-xs"></i>{{ computedInfo?.tahun_pensiun ? formatDate(computedInfo.tahun_pensiun) : '-' }}</div>
      </div>
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3">
        <div class="text-xs text-slate-500">Lama Kerja Saat Pensiun</div>
        <div class="font-semibold text-slate-800 dark:text-slate-100 mt-0.5"><i class="pi pi-chart-line text-green-500 mr-1.5 text-xs"></i>{{ computedInfo?.lama_kerja_pensiun || '-' }}</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Data pribadi -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <h3 class="font-semibold text-slate-700 dark:text-slate-200 mb-2 flex items-center gap-2"><i class="pi pi-user text-slate-400 text-xs"></i>Data Pribadi</h3>
        <dl class="divide-y divide-slate-100 dark:divide-slate-700">
          <div v-for="row in personalRows" :key="row.label" class="flex justify-between gap-4 py-1.5">
            <dt class="text-slate-500 shrink-0">{{ row.label }}</dt>
            <dd class="font-medium text-slate-800 dark:text-slate-100 text-right break-words">{{ row.value }}</dd>
          </div>
        </dl>
      </div>

      <!-- Administrasi -->
      <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
        <h3 class="font-semibold text-slate-700 dark:text-slate-200 mb-2 flex items-center gap-2"><i class="pi pi-id-card text-slate-400 text-xs"></i>Administrasi &amp; Kepegawaian</h3>
        <dl class="divide-y divide-slate-100 dark:divide-slate-700">
          <div v-for="row in adminRows" :key="row.label" class="flex justify-between gap-4 py-1.5">
            <dt class="text-slate-500 shrink-0">{{ row.label }}</dt>
            <dd class="font-medium text-slate-800 dark:text-slate-100 text-right break-words">{{ row.value }}</dd>
          </div>
        </dl>
      </div>
    </div>

    <!-- Riwayat pendidikan -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-2"><i class="pi pi-book text-slate-400 text-xs"></i>Riwayat Pendidikan</h3>
        <Button label="Tambah" icon="pi pi-plus" size="small" text @click="openEducation()" :disabled="availableLevels.length === 0" />
      </div>
      <DataTable :value="sortedEducation" size="small" class="text-sm">
        <Column field="tingkat" header="Jenjang"><template #body="{ data }"><Tag :value="data.tingkat" severity="secondary" class="!text-xs" /></template></Column>
        <Column field="jurusan" header="Jurusan"></Column>
        <Column field="institusi" header="Institusi"></Column>
        <Column field="tahun_lulus" header="Lulus"></Column>
        <Column header="" style="width: 6rem">
          <template #body="{ data }">
            <div class="flex gap-1 justify-end">
              <Button icon="pi pi-pencil" text rounded size="small" @click="openEducation(data)" />
              <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="deleteEducation(data)" />
            </div>
          </template>
        </Column>
        <template #empty><div class="text-center py-3 text-slate-500">Belum ada data riwayat pendidikan.</div></template>
      </DataTable>
    </div>

    <!-- SK & Dokumen terkait -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-2">
          <i class="pi pi-file text-slate-400 text-xs"></i>SK &amp; Dokumen Terkait
          <span class="text-xs font-normal bg-slate-100 dark:bg-slate-700 text-slate-500 rounded-full px-2 py-0.5">{{ documents.length }}</span>
        </h3>
        <Button label="Kelola di Pusat Dokumen" icon="pi pi-external-link" size="small" text @click="router.push('/dashboard/internal/dokumen')" />
      </div>
      <DataTable :value="documents" size="small" class="text-sm" :loading="loadingDocs">
        <Column header="Dokumen">
          <template #body="{ data }">
            <div class="font-medium text-slate-800 dark:text-slate-100">{{ data.title }}</div>
            <div class="text-xs text-slate-500">{{ data.document_number || 'Tanpa nomor' }}<span v-if="data.position_title"> • {{ data.position_title }}</span></div>
          </template>
        </Column>
        <Column header="Jenis" style="width: 9rem">
          <template #body="{ data }"><Tag :value="skTypeLabel(data.sk_type) || data.category || '-'" severity="secondary" class="!text-xs" /></template>
        </Column>
        <Column header="Berlaku" style="width: 9rem">
          <template #body="{ data }">{{ formatDate(data.effective_date || data.term_start_date) }}</template>
        </Column>
        <Column header="Status" style="width: 8rem">
          <template #body="{ data }"><Tag v-bind="docStatus(data)" class="!text-xs" /></template>
        </Column>
        <Column header="" style="width: 4rem">
          <template #body="{ data }">
            <a v-if="data.file_url" :href="data.file_url" target="_blank" rel="noopener" title="Buka berkas">
              <Button icon="pi pi-eye" text rounded size="small" as="span" />
            </a>
          </template>
        </Column>
        <template #empty><div class="text-center py-3 text-slate-500">Belum ada SK/dokumen yang terhubung dengan pegawai ini.</div></template>
      </DataTable>
    </div>

    <!-- Riwayat jabatan -->

    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div class="flex justify-between items-center mb-2">
        <h3 class="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-2"><i class="pi pi-briefcase text-slate-400 text-xs"></i>Riwayat Jabatan</h3>
        <Button label="Tambah" icon="pi pi-plus" size="small" text @click="openPosition()" />
      </div>
      <DataTable :value="employee.position_history" size="small" class="text-sm">
        <Column field="jabatan" header="Jabatan"></Column>
        <Column field="status_pegawai" header="Status"></Column>
        <Column header="TMT Mulai"><template #body="{ data }">{{ formatDate(data.tmt_mulai) }}</template></Column>
        <Column header="TMT Selesai"><template #body="{ data }">{{ data.tmt_selesai ? formatDate(data.tmt_selesai) : 'Sekarang' }}</template></Column>
        <Column header="" style="width: 6rem">
          <template #body="{ data }">
            <div class="flex gap-1 justify-end">
              <Button icon="pi pi-pencil" text rounded size="small" @click="openPosition(data)" />
              <Button icon="pi pi-trash" text rounded size="small" severity="danger" @click="deletePosition(data)" />
            </div>
          </template>
        </Column>
        <template #empty><div class="text-center py-3 text-slate-500">Belum ada data riwayat jabatan.</div></template>
      </DataTable>
    </div>

    <!-- Dialog edit pegawai -->
    <Dialog v-model:visible="showEdit" modal header="Edit Data Pegawai" :style="{ width: '760px' }" :breakpoints="{ '800px': '95vw' }">
      <div class="grid grid-cols-2 gap-3 text-sm">
        <!-- Pasfoto 4x6 Field -->
        <div class="col-span-2 flex items-center gap-4 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
          <div class="w-16 h-24 rounded-lg border border-slate-300 dark:border-slate-700 overflow-hidden bg-white dark:bg-slate-800 flex items-center justify-center shrink-0 shadow-xs">
            <img v-if="form.photo_url" :src="form.photo_url" class="w-full h-full object-cover" />
            <div v-else class="flex flex-col items-center justify-center text-slate-300 dark:text-slate-600 text-center">
              <i class="pi pi-user text-2xl"></i>
              <span class="text-[8px] font-medium mt-0.5">4x6</span>
            </div>
          </div>
          <div class="space-y-1 flex-1 min-w-0">
            <div class="font-bold text-xs text-slate-700 dark:text-slate-300">Pasfoto Pegawai (Standar 4x6 cm)</div>
            <p class="text-[11px] text-slate-400 leading-tight">Disarankan foto formal berlatar belakang polos. Maksimal ukuran file 2MB (otomatis dikompresi ke WebP).</p>
            <div class="flex items-center gap-2 pt-1">
              <input type="file" ref="dialogPhotoInput" class="hidden" accept="image/png,image/jpeg,image/jpg,image/webp" @change="handleDialogPhotoUpload" />
              <Button label="Pilih Pasfoto" icon="pi pi-upload" size="small" outlined class="!text-xs !py-1 !px-2.5 font-medium" :loading="uploadingDialogPhoto" @click="dialogPhotoInput?.click()" />
              <Button v-if="form.photo_url" label="Hapus Foto" icon="pi pi-trash" size="small" text severity="danger" class="!text-xs !py-1 !px-2" @click="form.photo_url = null" />
            </div>
          </div>
        </div>

        <div class="col-span-2 sm:col-span-1"><label class="lbl">Nama Lengkap</label><InputText v-model="form.nama_lengkap" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Email (opsional)</label><InputText v-model="form.email" type="email" placeholder="nama@email.com" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">NIK Kepegawaian (username login)</label><InputText v-model="form.nik_kepegawaian" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">No. KTP</label><InputText v-model="form.no_ktp" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Tempat Lahir</label><InputText v-model="form.tempat_lahir" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Tanggal Lahir</label><DatePicker v-model="form.tanggal_lahir" dateFormat="dd/mm/yy" showIcon fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Jenis Kelamin</label><Select v-model="form.jenis_kelamin" :options="['Laki-laki', 'Perempuan']" showClear fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Status Pernikahan</label><Select v-model="form.status_pernikahan" :options="['Kawin', 'Belum Kawin', 'Cerai']" showClear fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Jumlah Anak</label><InputNumber v-model="form.jumlah_anak" :min="0" :useGrouping="false" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">No. HP / WhatsApp</label><InputText v-model="form.no_hp" fluid size="small" /></div>
        <div class="col-span-2"><label class="lbl">Alamat</label><Textarea v-model="form.alamat" rows="2" fluid size="small" /></div>

        <div class="col-span-2 border-t pt-3 font-semibold text-slate-600">Kepegawaian</div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Jabatan</label><InputText v-model="form.position" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Jenis Pegawai</label><Select v-model="form.employee_type" :options="['tetap', 'kontrak', 'honorer']" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Unit</label><Select v-model="form.unit_id" :options="units" optionLabel="name" optionValue="id" showClear fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1">
          <label class="lbl">TMT Mulai Kerja (tanggal masuk)</label>
          <DatePicker v-model="form.join_date" dateFormat="dd/mm/yy" showIcon fluid size="small" />
          <small class="text-slate-400">Masa kerja dihitung dari tanggal ini sampai hari ini.</small>
        </div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">NIP</label><InputText v-model="form.nip" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">NUPTK</label><InputText v-model="form.nuptk" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">NPWP</label><InputText v-model="form.npwp" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">BPJS Ketenagakerjaan</label><InputText v-model="form.no_bpjs_tk" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">BPJS Kesehatan</label><InputText v-model="form.no_bpjs_kes" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">Bank</label><InputText v-model="form.nama_bank" fluid size="small" /></div>
        <div class="col-span-2 sm:col-span-1"><label class="lbl">No. Rekening</label><InputText v-model="form.no_rekening" fluid size="small" /></div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text size="small" @click="showEdit = false" />
        <Button label="Simpan Perubahan" icon="pi pi-save" size="small" :loading="saving" @click="saveEmployee" />
      </template>
    </Dialog>

    <!-- Dialog pendidikan -->
    <Dialog v-model:visible="showEducation" modal :header="eduForm.id ? 'Edit Pendidikan' : 'Tambah Pendidikan'" :style="{ width: '460px' }" :breakpoints="{ '500px': '95vw' }">
      <div class="space-y-3 text-sm">
        <div>
          <label class="lbl">Jenjang</label>
          <Select v-model="eduForm.tingkat" :options="eduLevelOptions" fluid size="small" placeholder="Pilih jenjang" />
          <small class="text-slate-400">Satu jenjang hanya boleh punya satu record per pegawai.</small>
        </div>
        <div><label class="lbl">Jurusan / Program Studi</label><InputText v-model="eduForm.jurusan" fluid size="small" /></div>
        <div><label class="lbl">Institusi</label><InputText v-model="eduForm.institusi" fluid size="small" /></div>
        <div><label class="lbl">Tahun Lulus</label><InputNumber v-model="eduForm.tahun_lulus" :useGrouping="false" :min="1950" :max="2100" fluid size="small" /></div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text size="small" @click="showEducation = false" />
        <Button label="Simpan" icon="pi pi-save" size="small" :loading="saving" @click="saveEducation" />
      </template>
    </Dialog>

    <!-- Dialog jabatan -->
    <Dialog v-model:visible="showPosition" modal :header="posForm.id ? 'Edit Riwayat Jabatan' : 'Tambah Riwayat Jabatan'" :style="{ width: '460px' }" :breakpoints="{ '500px': '95vw' }">
      <div class="space-y-3 text-sm">
        <div><label class="lbl">Jabatan</label><InputText v-model="posForm.jabatan" fluid size="small" /></div>
        <div><label class="lbl">Status Pegawai</label><Select v-model="posForm.status_pegawai" :options="['tetap', 'kontrak', 'honorer']" showClear fluid size="small" /></div>
        <div><label class="lbl">No. SK (opsional)</label><InputText v-model="posForm.sk_number" fluid size="small" /></div>
        <div class="grid grid-cols-2 gap-3">
          <div><label class="lbl">TMT Mulai</label><DatePicker v-model="posForm.tmt_mulai" dateFormat="dd/mm/yy" showIcon fluid size="small" /></div>
          <div><label class="lbl">TMT Selesai</label><DatePicker v-model="posForm.tmt_selesai" dateFormat="dd/mm/yy" showIcon showButtonBar fluid size="small" /></div>
        </div>
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" text size="small" @click="showPosition = false" />
        <Button label="Simpan" icon="pi pi-save" size="small" :loading="saving" @click="savePosition" />
      </template>
    </Dialog>
  </div>

  <div v-else class="flex justify-center py-20">
    <ProgressSpinner />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const router = useRouter()
const toast = useToast()
const config = useRuntimeConfig()
const apiToken = useCookie('auth_token')
const api = useApi()

const uploadingPhoto = ref(false)
const photoFileInput = ref<HTMLInputElement | null>(null)
const uploadingDialogPhoto = ref(false)
const dialogPhotoInput = ref<HTMLInputElement | null>(null)

function triggerPhotoInput() {
  photoFileInput.value?.click()
}

async function handlePhotoUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  const file = input.files[0]

  if (!file.type.startsWith('image/')) {
    toast.add({ severity: 'warn', summary: 'Format Salah', detail: 'Harap upload file gambar (JPG, PNG, WEBP)', life: 3000 })
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    toast.add({ severity: 'warn', summary: 'File Terlalu Besar', detail: 'Ukuran foto maksimal 2MB', life: 4000 })
    return
  }

  uploadingPhoto.value = true
  try {
    const res = await api.upload('/cms/upload', file)
    await api.put(`/sdm/employees/${route.params.id}`, { photo_url: res.url })
    employee.value.photo_url = res.url
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pasfoto berhasil diupload ke Cloudflare R2', life: 3500 })
  } catch (e: any) {
    console.error('Upload photo error:', e)
    toast.add({ severity: 'error', summary: 'Gagal Upload', detail: e?.data?.detail || e?.message || 'Gagal mengupload pasfoto', life: 4000 })
  } finally {
    uploadingPhoto.value = false
    if (photoFileInput.value) photoFileInput.value.value = ''
  }
}

async function handleDialogPhotoUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  const file = input.files[0]

  if (!file.type.startsWith('image/')) {
    toast.add({ severity: 'warn', summary: 'Format Salah', detail: 'Harap upload file gambar (JPG, PNG, WEBP)', life: 3000 })
    return
  }

  if (file.size > 2 * 1024 * 1024) {
    toast.add({ severity: 'warn', summary: 'File Terlalu Besar', detail: 'Ukuran foto maksimal 2MB', life: 4000 })
    return
  }

  uploadingDialogPhoto.value = true
  try {
    const res = await api.upload('/cms/upload', file)
    form.value.photo_url = res.url
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pasfoto terpilih dan siap disimpan', life: 3000 })
  } catch (e: any) {
    console.error('Upload photo dialog error:', e)
    toast.add({ severity: 'error', summary: 'Gagal Upload', detail: e?.data?.detail || e?.message || 'Gagal mengupload pasfoto', life: 4000 })
  } finally {
    uploadingDialogPhoto.value = false
    if (dialogPhotoInput.value) dialogPhotoInput.value.value = ''
  }
}

async function deletePhoto() {
  if (!confirm('Hapus pasfoto pegawai ini?')) return
  try {
    await api.put(`/sdm/employees/${route.params.id}`, { photo_url: null })
    employee.value.photo_url = null
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pasfoto berhasil dihapus', life: 3000 })
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus pasfoto', life: 3000 })
  }
}

const employee = ref<any>(null)
const computedInfo = ref<any>(null)
const units = ref<any[]>([])
const saving = ref(false)
const documents = ref<any[]>([])
const loadingDocs = ref(false)

const SK_LABELS: Record<string, string> = {
  PENGANGKATAN: 'Pengangkatan', PROMOSI: 'Promosi', MUTASI: 'Mutasi', PEMBERHENTIAN: 'Pemberhentian',
  PENGUNDURAN_DIRI: 'Pengunduran Diri', TUGAS_TAMBAHAN: 'Tugas Tambahan', UMUM: 'Umum',
}
const skTypeLabel = (t?: string) => (t ? SK_LABELS[t] || t : '')
const docStatus = (d: any) => {
  if (!d.expired_date) return { value: 'Berlaku', severity: 'success' }
  const exp = new Date(d.expired_date).getTime()
  const now = Date.now()
  if (exp < now) return { value: 'Kedaluwarsa', severity: 'danger' }
  if (exp - now < 90 * 86400000) return { value: 'Segera Berakhir', severity: 'warn' }
  return { value: 'Berlaku', severity: 'success' }
}
const fetchDocuments = async () => {
  loadingDocs.value = true
  try {
    documents.value = await $fetch<any[]>(`${base}/sdm/employees/${route.params.id}/documents`, { headers: headers() })
  } catch {
    documents.value = []
  } finally {
    loadingDocs.value = false
  }
}

const showEdit = ref(false)
const showEducation = ref(false)
const showPosition = ref(false)
const form = ref<any>({})
const eduForm = ref<any>({})
const posForm = ref<any>({})

const EDU_LEVELS = ['SD', 'SMP', 'SMA/SMK', 'D1', 'D2', 'D3', 'D4', 'S1', 'S2', 'S3']
const normLevel = (t: string) => (['SMA', 'SMK', 'MA'].includes((t || '').toUpperCase()) ? 'SMA/SMK' : t)

const headers = () => ({ Authorization: `Bearer ${apiToken.value}` })
const base = config.public.apiBase

const formatDate = (d: any) => {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' })
}

// Kirim tanggal sebagai tanggal lokal (hindari geser sehari akibat UTC)
const toApiDate = (d: any) => {
  if (!d) return null
  const dt = new Date(d)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${dt.getFullYear()}-${p(dt.getMonth() + 1)}-${p(dt.getDate())}T00:00:00`
}
const toDateObj = (d: any) => (d ? new Date(d) : null)

const errMsg = (e: any, fallback: string) => e?.data?.detail || e?.response?._data?.detail || fallback

const personalRows = computed(() => {
  const e = employee.value
  return [
    { label: 'Email', value: e.user?.email || '-' },
    { label: 'Tempat, Tanggal Lahir', value: `${e.tempat_lahir || '-'}, ${formatDate(e.tanggal_lahir)}` },
    { label: 'Jenis Kelamin', value: e.jenis_kelamin || '-' },
    { label: 'Status Pernikahan', value: `${e.status_pernikahan || '-'} (Anak: ${e.jumlah_anak ?? 0})` },
    { label: 'Alamat', value: e.alamat || '-' },
    { label: 'No. HP / WhatsApp', value: e.no_hp || '-' },
    { label: 'No. KTP', value: e.no_ktp || '-' },
  ]
})
const adminRows = computed(() => {
  const e = employee.value
  return [
    { label: 'TMT Mulai Kerja', value: formatDate(e.join_date) },
    { label: 'NIP', value: e.nip || '-' },
    { label: 'NUPTK', value: e.nuptk || '-' },
    { label: 'NPWP', value: e.npwp || '-' },
    { label: 'BPJS Ketenagakerjaan', value: e.no_bpjs_tk || '-' },
    { label: 'BPJS Kesehatan', value: e.no_bpjs_kes || '-' },
    { label: 'Rekening Bank', value: `${e.nama_bank || '-'} - ${e.no_rekening || '-'}` },
  ]
})

const sortedEducation = computed(() =>
  [...(employee.value?.education_history || [])].sort((a, b) => EDU_LEVELS.indexOf(a.tingkat) - EDU_LEVELS.indexOf(b.tingkat))
)
const usedLevels = computed(() => (employee.value?.education_history || []).map((e: any) => normLevel(e.tingkat)))
const availableLevels = computed(() => EDU_LEVELS.filter(l => !usedLevels.value.includes(l)))
// Saat edit, jenjang record itu sendiri tetap boleh dipilih
const eduLevelOptions = computed(() =>
  eduForm.value.id ? EDU_LEVELS.filter(l => l === eduForm.value.tingkat || !usedLevels.value.includes(l)) : availableLevels.value
)

const fetchEmployeeDetail = async () => {
  try {
    const id = route.params.id
    employee.value = await $fetch(`${base}/sdm/employees/${id}`, { headers: headers() })
    computedInfo.value = await $fetch(`${base}/sdm/employees/${id}/computed`, { headers: headers() })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal mengambil detail pegawai', life: 3000 })
    router.push('/dashboard/sdm/pegawai')
  }
}

const fetchUnits = async () => {
  try { units.value = await $fetch<any[]>(`${base}/units`, { headers: headers() }) } catch { /* ignore */ }
}

const openEdit = () => {
  const e = employee.value
  form.value = {
    nama_lengkap: e.nama_lengkap, email: e.user?.email || '', nik_kepegawaian: e.nik_kepegawaian, no_ktp: e.no_ktp,
    tempat_lahir: e.tempat_lahir, tanggal_lahir: toDateObj(e.tanggal_lahir), jenis_kelamin: e.jenis_kelamin,
    status_pernikahan: e.status_pernikahan, jumlah_anak: e.jumlah_anak ?? 0, no_hp: e.no_hp, alamat: e.alamat,
    position: e.position, employee_type: e.employee_type, unit_id: e.unit_id, join_date: toDateObj(e.join_date),
    nip: e.nip, nuptk: e.nuptk, npwp: e.npwp, no_bpjs_tk: e.no_bpjs_tk, no_bpjs_kes: e.no_bpjs_kes,
    nama_bank: e.nama_bank, no_rekening: e.no_rekening,
    photo_url: e.photo_url || null,
  }
  showEdit.value = true
}

const saveEmployee = async () => {
  if (!form.value.nama_lengkap?.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Nama lengkap wajib diisi', life: 3000 })
    return
  }
  saving.value = true
  try {
    const payload = { ...form.value, tanggal_lahir: toApiDate(form.value.tanggal_lahir), join_date: toApiDate(form.value.join_date) }
    await $fetch(`${base}/sdm/employees/${route.params.id}`, { method: 'PUT', headers: headers(), body: payload })
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data pegawai diperbarui', life: 3000 })
    showEdit.value = false
    await fetchEmployeeDetail()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: errMsg(e, 'Gagal menyimpan perubahan'), life: 5000 })
  } finally {
    saving.value = false
  }
}

const deactivate = async () => {
  if (!confirm('Nonaktifkan pegawai ini?')) return
  try {
    await $fetch(`${base}/sdm/employees/${route.params.id}`, { method: 'DELETE', headers: headers() })
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Pegawai dinonaktifkan', life: 3000 })
    await fetchEmployeeDetail()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: errMsg(e, 'Gagal menonaktifkan'), life: 4000 })
  }
}

// --- Pendidikan ---
const openEducation = (row?: any) => {
  eduForm.value = row
    ? { id: row.id, tingkat: normLevel(row.tingkat), jurusan: row.jurusan, institusi: row.institusi, tahun_lulus: row.tahun_lulus }
    : { tingkat: null, jurusan: '', institusi: '', tahun_lulus: null }
  showEducation.value = true
}
const saveEducation = async () => {
  if (!eduForm.value.tingkat) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Pilih jenjang pendidikan', life: 3000 })
    return
  }
  saving.value = true
  try {
    const { id, ...body } = eduForm.value
    const url = id ? `${base}/sdm/education/${id}` : `${base}/sdm/employees/${route.params.id}/education`
    await $fetch(url, { method: id ? 'PUT' : 'POST', headers: headers(), body })
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Riwayat pendidikan disimpan', life: 3000 })
    showEducation.value = false
    await fetchEmployeeDetail()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: errMsg(e, 'Gagal menyimpan pendidikan'), life: 5000 })
  } finally {
    saving.value = false
  }
}
const deleteEducation = async (row: any) => {
  if (!confirm(`Hapus riwayat pendidikan ${row.tingkat}?`)) return
  try {
    await $fetch(`${base}/sdm/education/${row.id}`, { method: 'DELETE', headers: headers() })
    await fetchEmployeeDetail()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: errMsg(e, 'Gagal menghapus'), life: 4000 })
  }
}

// --- Jabatan ---
const openPosition = (row?: any) => {
  posForm.value = row
    ? { id: row.id, jabatan: row.jabatan, status_pegawai: row.status_pegawai, sk_number: row.sk_number, unit_id: row.unit_id, tmt_mulai: toDateObj(row.tmt_mulai), tmt_selesai: toDateObj(row.tmt_selesai) }
    : { jabatan: '', status_pegawai: null, sk_number: '', unit_id: employee.value?.unit_id ?? null, tmt_mulai: null, tmt_selesai: null }
  showPosition.value = true
}
const savePosition = async () => {
  if (!posForm.value.jabatan?.trim() || !posForm.value.tmt_mulai) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Jabatan dan TMT Mulai wajib diisi', life: 3000 })
    return
  }
  saving.value = true
  try {
    const { id, ...rest } = posForm.value
    const body = { ...rest, tmt_mulai: toApiDate(rest.tmt_mulai), tmt_selesai: toApiDate(rest.tmt_selesai) }
    const url = id ? `${base}/sdm/positions/${id}` : `${base}/sdm/employees/${route.params.id}/positions`
    await $fetch(url, { method: id ? 'PUT' : 'POST', headers: headers(), body })
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Riwayat jabatan disimpan', life: 3000 })
    showPosition.value = false
    await fetchEmployeeDetail()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: errMsg(e, 'Gagal menyimpan jabatan'), life: 5000 })
  } finally {
    saving.value = false
  }
}
const deletePosition = async (row: any) => {
  if (!confirm(`Hapus riwayat jabatan "${row.jabatan}"?`)) return
  try {
    await $fetch(`${base}/sdm/positions/${row.id}`, { method: 'DELETE', headers: headers() })
    await fetchEmployeeDetail()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: errMsg(e, 'Gagal menghapus'), life: 4000 })
  }
}

onMounted(async () => {
  if (route.params.id) {
    await Promise.all([fetchEmployeeDetail(), fetchUnits(), fetchDocuments()])
    if (route.query.edit === 'true' && employee.value) openEdit()
  }
})
</script>

<style scoped>
.lbl { display: block; margin-bottom: 0.25rem; font-size: 0.75rem; font-weight: 500; color: rgb(100 116 139); }
</style>
