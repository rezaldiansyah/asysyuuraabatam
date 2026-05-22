<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Data Pegawai</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola data kepegawaian dan riwayat karyawan.</p>
      </div>
      <div class="flex gap-2">
        <Button label="Import Data" icon="pi pi-upload" severity="secondary" outlined @click="showImportDialog = true" />
        <Button label="Tambah Pegawai" icon="pi pi-plus" @click="showAddDialog = true" />
      </div>
    </div>

    <!-- Filter Bar -->
    <Card>
      <template #content>
        <div class="flex flex-wrap gap-4">
          <div class="flex-1 min-w-[200px]">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText v-model="filters.search" placeholder="Cari nama atau NIK..." class="w-full" @input="debouncedFetch" />
            </span>
          </div>
          <Dropdown v-model="filters.unit_id" :options="units" optionLabel="name" optionValue="id" placeholder="Semua Unit" showClear class="w-48" @change="fetchEmployees" />
          <Dropdown v-model="filters.employee_type" :options="['tetap', 'kontrak', 'honorer']" placeholder="Semua Jenis" showClear class="w-48" @change="fetchEmployees" />
          <Dropdown v-model="filters.is_active" :options="[{label: 'Aktif', value: true}, {label: 'Nonaktif', value: false}]" optionLabel="label" optionValue="value" placeholder="Status Aktif" showClear class="w-48" @change="fetchEmployees" />
        </div>
      </template>
    </Card>

    <!-- Data Table -->
    <Card>
      <template #content>
        <DataTable :value="employees" :loading="loading" paginator :rows="10" dataKey="id" class="p-datatable-sm" stripedRows responsiveLayout="scroll">
          <Column field="nama_lengkap" header="Nama Pegawai" sortable>
            <template #body="{ data }">
              <div class="flex items-center gap-3">
                <Avatar :image="data.photo_url || `https://ui-avatars.com/api/?name=${data.nama_lengkap}&background=random`" shape="circle" />
                <div>
                  <div class="font-medium text-slate-800 dark:text-white">{{ data.nama_lengkap }}</div>
                  <div class="text-xs text-slate-500">{{ data.nik_kepegawaian || '-' }}</div>
                </div>
              </div>
            </template>
          </Column>
          <Column field="position" header="Jabatan" sortable>
            <template #body="{ data }">
              <div>{{ data.position || '-' }}</div>
              <div class="text-xs text-slate-500">{{ data.nip || data.nuptk || '-' }}</div>
            </template>
          </Column>
          <Column field="employee_type" header="Jenis" sortable>
            <template #body="{ data }">
              <Tag :value="data.employee_type" :severity="getEmployeeTypeSeverity(data.employee_type)" class="uppercase text-xs" />
            </template>
          </Column>
          <Column field="unit.name" header="Unit" sortable>
             <template #body="{ data }">
              {{ data.unit?.name || '-' }}
             </template>
          </Column>
          <Column field="is_active" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.is_active ? 'Aktif' : 'Nonaktif'" :severity="data.is_active ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column header="Aksi" :exportable="false" style="min-width:8rem">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-eye" outlined rounded severity="info" aria-label="View" @click="viewEmployee(data.id)" />
                <Button icon="pi pi-pencil" outlined rounded severity="success" aria-label="Edit" @click="editEmployee(data)" />
                <Button icon="pi pi-trash" outlined rounded severity="danger" aria-label="Delete" @click="confirmDelete(data)" v-if="data.is_active" />
              </div>
            </template>
          </Column>
          
          <template #empty>
            <div class="text-center py-8 text-slate-500">
              Tidak ada data pegawai yang ditemukan.
            </div>
          </template>
        </DataTable>
      </template>
    </Card>

    <!-- Dialog Tambah Pegawai -->
    <Dialog v-model:visible="showAddDialog" modal header="Tambah Pegawai Baru" :style="{ width: '800px' }" class="p-fluid">
      <Stepper value="1">
        <StepList>
          <Step value="1">Data Personal</Step>
          <Step value="2">Kepegawaian</Step>
          <Step value="3">Pendidikan</Step>
        </StepList>
        <StepPanels>
        <!-- STEP 1: DATA PERSONAL -->
        <StepPanel v-slot="{ activateCallback }" value="1">
            <div class="grid grid-cols-2 gap-4 my-4">
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Nama Lengkap *</label>
                <InputText v-model="form.nama_lengkap" placeholder="Masukkan nama lengkap" :class="{ 'p-invalid': v$.nama_lengkap.$invalid && submitted }" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">No. KTP (NIK Negara) *</label>
                <InputMask v-model="form.no_ktp" mask="9999999999999999" placeholder="16 digit NIK" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">NIK Kepegawaian (Username) *</label>
                <InputText v-model="form.nik_kepegawaian" placeholder="Misal: YYS-001" :class="{ 'p-invalid': v$.nik_kepegawaian.$invalid && submitted }" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">No. HP *</label>
                <InputText v-model="form.no_hp" placeholder="08xxxxxxxx" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Tempat Lahir</label>
                <InputText v-model="form.tempat_lahir" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Tanggal Lahir *</label>
                <Calendar v-model="form.tanggal_lahir" dateFormat="yy-mm-dd" :showIcon="true" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Jenis Kelamin</label>
                <Dropdown v-model="form.jenis_kelamin" :options="['Laki-laki', 'Perempuan']" placeholder="Pilih Jenis Kelamin" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Status Pernikahan</label>
                <Dropdown v-model="form.status_pernikahan" :options="['Kawin', 'Belum Kawin']" placeholder="Pilih Status" />
              </div>
              <div class="col-span-2">
                <label class="block mb-1 text-sm font-medium">Alamat</label>
                <Textarea v-model="form.alamat" rows="2" />
              </div>
            </div>
            <div class="flex justify-end mt-4">
              <Button label="Selanjutnya" icon="pi pi-arrow-right" @click="handleNext(() => activateCallback('2'), 1)" />
            </div>
        </StepPanel>

        <!-- STEP 2: KEPEGAWAIAN -->
        <StepPanel v-slot="{ activateCallback }" value="2">
            <div class="grid grid-cols-2 gap-4 my-4">
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Jabatan Saat Ini *</label>
                <InputText v-model="form.position" placeholder="Misal: Guru Wali Kelas 1A" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Jenis Pegawai *</label>
                <Dropdown v-model="form.employee_type" :options="['tetap', 'kontrak', 'honorer']" placeholder="Pilih Jenis" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">Unit Penempatan *</label>
                <Dropdown v-model="form.unit_id" :options="units" optionLabel="name" optionValue="id" placeholder="Pilih Unit" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">TMT Mulai Kerja</label>
                <Calendar v-model="form.join_date" dateFormat="yy-mm-dd" :showIcon="true" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">NIP (Opsional)</label>
                <InputText v-model="form.nip" />
              </div>
              <div class="col-span-2 md:col-span-1">
                <label class="block mb-1 text-sm font-medium">NUPTK (Opsional)</label>
                <InputText v-model="form.nuptk" />
              </div>
              <div class="col-span-2 md:col-span-1 mt-4">
                <h3 class="font-semibold text-slate-700">Data Administrasi</h3>
              </div>
              <div class="col-span-2 grid grid-cols-2 gap-4 border-t pt-4">
                <div class="col-span-2 md:col-span-1">
                  <label class="block mb-1 text-sm font-medium">NPWP</label>
                  <InputText v-model="form.npwp" />
                </div>
                <div class="col-span-2 md:col-span-1">
                  <label class="block mb-1 text-sm font-medium">No. BPJS Kesehatan</label>
                  <InputText v-model="form.no_bpjs_kes" />
                </div>
                <div class="col-span-2 md:col-span-1">
                  <label class="block mb-1 text-sm font-medium">No. BPJS TK</label>
                  <InputText v-model="form.no_bpjs_tk" />
                </div>
                <div class="col-span-2 md:col-span-1 flex gap-2">
                  <div class="w-1/3">
                    <label class="block mb-1 text-sm font-medium">Bank</label>
                    <InputText v-model="form.nama_bank" placeholder="BRI" />
                  </div>
                  <div class="w-2/3">
                    <label class="block mb-1 text-sm font-medium">No Rekening</label>
                    <InputText v-model="form.no_rekening" />
                  </div>
                </div>
              </div>
            </div>
            <div class="flex justify-between mt-4">
              <Button label="Kembali" severity="secondary" icon="pi pi-arrow-left" @click="activateCallback('1')" />
              <Button label="Selanjutnya" icon="pi pi-arrow-right" @click="handleNext(() => activateCallback('3'), 2)" />
            </div>
        </StepPanel>

        <!-- STEP 3: RIWAYAT PENDIDIKAN -->
        <StepPanel v-slot="{ activateCallback }" value="3">
            <div class="my-4">
              <p class="text-slate-500 mb-4">Tambahkan riwayat pendidikan (opsional, bisa ditambah nanti).</p>
              
              <div v-for="(edu, idx) in educationHistory" :key="idx" class="grid grid-cols-12 gap-2 mb-3 items-end p-3 bg-slate-50 dark:bg-slate-800 rounded-md">
                <div class="col-span-2">
                  <label class="block mb-1 text-xs">Tingkat</label>
                  <Dropdown v-model="edu.tingkat" :options="['SMA', 'D2', 'D3', 'S1', 'S2', 'S3']" class="w-full" />
                </div>
                <div class="col-span-3">
                  <label class="block mb-1 text-xs">Jurusan</label>
                  <InputText v-model="edu.jurusan" class="w-full" />
                </div>
                <div class="col-span-4">
                  <label class="block mb-1 text-xs">Institusi</label>
                  <InputText v-model="edu.institusi" class="w-full" />
                </div>
                <div class="col-span-2">
                  <label class="block mb-1 text-xs">Thn Lulus</label>
                  <InputNumber v-model="edu.tahun_lulus" :useGrouping="false" class="w-full" />
                </div>
                <div class="col-span-1 text-right">
                  <Button icon="pi pi-times" severity="danger" text rounded aria-label="Remove" @click="removeEducation(idx)" />
                </div>
              </div>
              
              <Button label="Tambah Riwayat Pendidikan" icon="pi pi-plus" text @click="addEducation" size="small" />
            </div>
            <div class="flex justify-between mt-4">
              <Button label="Kembali" severity="secondary" icon="pi pi-arrow-left" @click="activateCallback('2')" />
              <Button label="Simpan Pegawai" icon="pi pi-save" @click="submitForm" :loading="saving" />
            </div>
        </StepPanel>
        </StepPanels>
      </Stepper>
    </Dialog>
    
    <!-- Success Dialog with Password Info -->
    <Dialog v-model:visible="showSuccessDialog" modal header="Pegawai Berhasil Ditambahkan" :style="{ width: '450px' }" :closable="false">
      <div class="flex flex-col items-center p-4">
        <i class="pi pi-check-circle text-green-500 text-6xl mb-4"></i>
        <p class="text-center mb-6">Akun pengguna otomatis dibuat untuk pegawai ini.</p>
        
        <div class="bg-slate-100 dark:bg-slate-800 w-full p-4 rounded-lg border border-slate-200 dark:border-slate-700">
          <div class="mb-2">
            <span class="text-slate-500 text-sm block">Username (NIK)</span>
            <span class="font-bold text-lg text-slate-800 dark:text-white">{{ successInfo?.username }}</span>
          </div>
          <div>
            <span class="text-slate-500 text-sm block">Password Default</span>
            <span class="font-bold text-lg text-slate-800 dark:text-white">{{ successInfo?.password }}</span>
            <p class="text-xs text-orange-500 mt-1"><i class="pi pi-exclamation-triangle mr-1"></i>Pegawai wajib mengganti password saat login pertama kali.</p>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Selesai" @click="closeSuccessDialog" class="w-full" />
      </template>
    </Dialog>
    </Dialog>
    
    <!-- Import Dialog -->
    <Dialog v-model:visible="showImportDialog" modal header="Import Data Pegawai" :style="{ width: '600px' }">
      <div class="space-y-4">
        <Message severity="info" :closable="false">
          <p class="font-bold">Panduan Import CSV:</p>
          <ul class="list-disc pl-5 mt-2 space-y-1 text-sm">
            <li>Download template CSV dan isi data sesuai format header.</li>
            <li>Kolom <b>Nama Lengkap</b> dan <b>NIK Kepegawaian</b> wajib diisi.</li>
            <li>Gunakan format tanggal lahir <b>YYYY-MM-DD</b> (Contoh: 1990-01-31).</li>
            <li>Sistem akan otomatis membuatkan akun dengan password tanggal lahir (atau password123 jika kosong/salah format).</li>
          </ul>
        </Message>
        
        <div class="flex justify-center mt-4">
          <Button label="Download Template CSV" icon="pi pi-download" outlined @click="downloadTemplate" />
        </div>
        
        <div class="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-6 text-center mt-4">
          <input type="file" ref="fileInput" accept=".csv" class="hidden" @change="onFileSelected" />
          
          <div v-if="!importFile">
            <i class="pi pi-file-excel text-4xl text-slate-400 mb-2"></i>
            <p class="mb-4 text-slate-600 dark:text-slate-400">Pilih file CSV yang sudah diisi</p>
            <Button label="Pilih File" icon="pi pi-search" @click="$refs.fileInput.click()" />
          </div>
          <div v-else class="flex flex-col items-center">
            <i class="pi pi-file text-4xl text-indigo-500 mb-2"></i>
            <p class="font-bold text-slate-800 dark:text-white">{{ importFile.name }}</p>
            <p class="text-xs text-slate-500 mb-4">{{ (importFile.size / 1024).toFixed(2) }} KB</p>
            <div class="flex gap-2">
              <Button label="Batal" severity="secondary" outlined @click="importFile = null" :disabled="importing" />
              <Button label="Mulai Import" icon="pi pi-upload" @click="uploadImportFile" :loading="importing" />
            </div>
          </div>
        </div>
        
        <div v-if="importResult" class="mt-4 p-4 rounded-lg" :class="importResult.errors?.length ? 'bg-orange-50 dark:bg-orange-900/20' : 'bg-green-50 dark:bg-green-900/20'">
          <p class="font-bold mb-2">Hasil Import:</p>
          <p class="text-sm">Berhasil diimpor: <b>{{ importResult.success_count }}</b> data</p>
          
          <div v-if="importResult.errors?.length" class="mt-3">
            <p class="text-sm font-bold text-orange-700 dark:text-orange-400 mb-1">Daftar Error:</p>
            <ul class="list-disc pl-5 text-xs text-orange-600 dark:text-orange-300 max-h-32 overflow-y-auto">
              <li v-for="(err, i) in importResult.errors" :key="i">{{ err }}</li>
            </ul>
          </div>
        </div>
      </div>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useVuelidate } from '@vuelidate/core'
import { required } from '@vuelidate/validators'

definePageMeta({ layout: 'dashboard' })

const router = useRouter()
const toast = useToast()
const apiToken = useCookie('auth_token')
const config = useRuntimeConfig()

// State
const employees = ref([])
const units = ref([])
const loading = ref(false)
const showAddDialog = ref(false)
const showSuccessDialog = ref(false)
const successInfo = ref(null)
const showImportDialog = ref(false)
const importFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const activeStep = ref(0)
const saving = ref(false)
const submitted = ref(false)

// Filters
const filters = reactive({
  search: '',
  unit_id: null,
  employee_type: null,
  is_active: true
})

// Form State
const initForm = () => ({
  nama_lengkap: '',
  no_ktp: '',
  nik_kepegawaian: '',
  tempat_lahir: '',
  tanggal_lahir: null,
  jenis_kelamin: null,
  status_pernikahan: null,
  jumlah_anak: 0,
  alamat: '',
  no_hp: '',
  npwp: '',
  no_bpjs_tk: '',
  no_bpjs_kes: '',
  no_rekening: '',
  nama_bank: '',
  position: '',
  employee_type: 'tetap',
  unit_id: null,
  join_date: null,
  nip: '',
  nuptk: ''
})

const form = reactive(initForm())

// Validation rules
const rules = {
  nama_lengkap: { required },
  nik_kepegawaian: { required }
}

const v$ = useVuelidate(rules, form)

// Education History Array
const educationHistory = ref([
  { tingkat: 'S1', jurusan: '', institusi: '', tahun_lulus: new Date().getFullYear() }
])

const addEducation = () => {
  educationHistory.value.push({ tingkat: '', jurusan: '', institusi: '', tahun_lulus: null })
}

const removeEducation = (index) => {
  educationHistory.value.splice(index, 1)
}

// Fetch Data
const fetchUnits = async () => {
  try {
    const data = await $fetch(`${config.public.apiBase}/units`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    units.value = data
  } catch (error) {
    console.error('Failed to fetch units', error)
  }
}

const fetchEmployees = async () => {
  loading.value = true
  try {
    const query = new URLSearchParams()
    if (filters.search) query.append('search', filters.search)
    if (filters.unit_id) query.append('unit_id', filters.unit_id)
    if (filters.employee_type) query.append('employee_type', filters.employee_type)
    if (filters.is_active !== null) query.append('is_active', filters.is_active)
    
    const data = await $fetch(`${config.public.apiBase}/sdm/employees?${query.toString()}`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    employees.value = data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal mengambil data pegawai' })
  } finally {
    loading.value = false
  }
}

// Import logic
const downloadTemplate = () => {
  window.open(`${config.public.apiBase}/sdm/employees/template`, '_blank')
}

const onFileSelected = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    if (!file.name.endsWith('.csv')) {
      toast.add({ severity: 'error', summary: 'Format Salah', detail: 'Harap unggah file CSV.' })
      return
    }
    importFile.value = file
    importResult.value = null
  }
}

const uploadImportFile = async () => {
  if (!importFile.value) return
  
  importing.value = true
  importResult.value = null
  
  const formData = new FormData()
  formData.append('file', importFile.value)
  
  try {
    const data = await $fetch(`${config.public.apiBase}/sdm/employees/import`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiToken.value}` },
      body: formData
    })
    
    importResult.value = data
    if (data.success_count > 0) {
      toast.add({ severity: 'success', summary: 'Import Selesai', detail: `${data.success_count} data berhasil diimpor` })
      fetchEmployees() // Refresh table
    } else {
      toast.add({ severity: 'warn', summary: 'Import Gagal', detail: 'Tidak ada data yang berhasil diimpor' })
    }
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: error.data?.detail || 'Gagal mengimpor file' })
  } finally {
    importing.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

let timeout = null
const debouncedFetch = () => {
  clearTimeout(timeout)
  timeout = setTimeout(() => {
    fetchEmployees()
  }, 500)
}

// Lifecycle
onMounted(() => {
  fetchUnits()
  fetchEmployees()
})

// Helpers
const getEmployeeTypeSeverity = (type) => {
  switch (type?.toLowerCase()) {
    case 'tetap': return 'success'
    case 'kontrak': return 'warning'
    case 'honorer': return 'info'
    default: return 'secondary'
  }
}

const viewEmployee = (id) => {
  router.push(`/dashboard/sdm/pegawai/${id}`)
}

const editEmployee = (data) => {
  // We'll implement edit form later or navigate to detail page for editing
  router.push(`/dashboard/sdm/pegawai/${data.id}?edit=true`)
}

// Stepper Actions
const handleNext = (nextCallback, step) => {
  submitted.value = true
  
  // Basic validation for step 1
  if (step === 1 && v$.value.$invalid) {
    toast.add({ severity: 'error', summary: 'Validasi Gagal', detail: 'Mohon lengkapi field yang wajib diisi.' })
    return
  }
  
  nextCallback()
  submitted.value = false
}

// Submit Form
const submitForm = async () => {
  saving.value = true
  try {
    // 1. Format dates correctly
    const payload = { ...form }
    if (payload.tanggal_lahir) payload.tanggal_lahir = new Date(payload.tanggal_lahir).toISOString()
    if (payload.join_date) payload.join_date = new Date(payload.join_date).toISOString()
    
    // 2. Clean up empty strings to null for unique fields if needed
    if (!payload.nip) payload.nip = null
    if (!payload.nuptk) payload.nuptk = null
    if (!payload.no_ktp) payload.no_ktp = null
    
    // 3. Create Employee
    const res = await $fetch(`${config.public.apiBase}/sdm/employees`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiToken.value}` },
      body: payload
    })
    
    const newEmpId = res.employee.id
    
    // 4. Save Education History if any
    const validEdus = educationHistory.value.filter(e => e.tingkat && e.institusi)
    for (const edu of validEdus) {
      await $fetch(`${config.public.apiBase}/sdm/employees/${newEmpId}/education`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiToken.value}` },
        body: edu
      })
    }
    
    // 5. Success
    showAddDialog.value = false
    
    // Refresh table
    fetchEmployees()
    
    // Reset form
    Object.assign(form, initForm())
    educationHistory.value = [{ tingkat: 'S1', jurusan: '', institusi: '', tahun_lulus: new Date().getFullYear() }]
    activeStep.value = 0
    
    // Show success modal with login info
    if (res.login_info) {
      successInfo.value = res.login_info
      showSuccessDialog.value = true
    } else {
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data pegawai berhasil disimpan' })
    }
    
  } catch (error) {
    const msg = error.data?.detail || 'Gagal menyimpan data pegawai'
    toast.add({ severity: 'error', summary: 'Error', detail: msg })
  } finally {
    saving.value = false
  }
}

const closeSuccessDialog = () => {
  showSuccessDialog.value = false
  successInfo.value = null
}
</script>
