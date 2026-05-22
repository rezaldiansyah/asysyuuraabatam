<template>
  <div class="space-y-6" v-if="employee">
    <div class="flex justify-between items-center">
      <div class="flex items-center gap-4">
        <Button icon="pi pi-arrow-left" text rounded @click="router.push('/dashboard/sdm/pegawai')" />
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Profil Pegawai</h1>
          <p class="text-slate-500 dark:text-slate-400">Detail informasi kepegawaian dan riwayat.</p>
        </div>
      </div>
      <div class="flex gap-2">
        <Button label="Edit" icon="pi pi-pencil" outlined />
        <Button label="Nonaktifkan" icon="pi pi-power-off" severity="danger" outlined v-if="employee.is_active" />
      </div>
    </div>

    <!-- Header Profil -->
    <Card class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 border-none">
      <template #content>
        <div class="flex flex-col md:flex-row items-center md:items-start gap-6 p-4">
          <Avatar :image="employee.photo_url || `https://ui-avatars.com/api/?name=${employee.nama_lengkap}&size=128&background=random`" shape="circle" class="w-32 h-32 text-4xl shadow-md border-4 border-white dark:border-slate-700" />
          <div class="text-center md:text-left flex-1">
            <h2 class="text-3xl font-bold text-slate-800 dark:text-white mb-2">{{ employee.nama_lengkap }}</h2>
            <div class="text-lg text-slate-600 dark:text-slate-300 font-medium mb-3">
              {{ employee.position || 'Jabatan Belum Diatur' }} — {{ employee.unit?.name || 'Unit Belum Diatur' }}
            </div>
            <div class="flex flex-wrap gap-2 justify-center md:justify-start">
              <Tag :value="employee.employee_type" severity="info" class="uppercase" />
              <Tag :value="employee.is_active ? 'Aktif' : 'Nonaktif'" :severity="employee.is_active ? 'success' : 'danger'" />
              <Tag :value="`NIK: ${employee.nik_kepegawaian || '-'}`" severity="secondary" />
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Info Computed (Masa Kerja, Pensiun) -->
    <Card>
      <template #content>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center divide-y md:divide-y-0 md:divide-x dark:divide-slate-700">
          <div class="py-2">
            <div class="text-sm text-slate-500 dark:text-slate-400 mb-1">Masa Kerja</div>
            <div class="font-semibold text-lg text-slate-800 dark:text-slate-200">
              <i class="pi pi-clock text-blue-500 mr-2"></i>{{ computedInfo?.masa_kerja || '-' }}
            </div>
          </div>
          <div class="py-2">
            <div class="text-sm text-slate-500 dark:text-slate-400 mb-1">Usia Pensiun</div>
            <div class="font-semibold text-lg text-slate-800 dark:text-slate-200">
              <i class="pi pi-calendar text-orange-500 mr-2"></i>{{ computedInfo?.tahun_pensiun || '-' }}
            </div>
          </div>
          <div class="py-2">
            <div class="text-sm text-slate-500 dark:text-slate-400 mb-1">Lama Kerja Saat Pensiun</div>
            <div class="font-semibold text-lg text-slate-800 dark:text-slate-200">
              <i class="pi pi-chart-line text-green-500 mr-2"></i>{{ computedInfo?.lama_kerja_pensiun || '-' }}
            </div>
          </div>
        </div>
      </template>
    </Card>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Data Pribadi -->
      <Card>
        <template #title><div class="flex items-center gap-2"><i class="pi pi-user text-slate-500"></i>Data Pribadi</div></template>
        <template #content>
          <ul class="space-y-4">
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">Tempat, Tanggal Lahir</span>
              <span class="font-medium text-right">{{ employee.tempat_lahir || '-' }}, {{ formatDate(employee.tanggal_lahir) }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">Jenis Kelamin</span>
              <span class="font-medium">{{ employee.jenis_kelamin || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">Status Pernikahan</span>
              <span class="font-medium">{{ employee.status_pernikahan || '-' }} (Anak: {{ employee.jumlah_anak }})</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">Alamat Lengkap</span>
              <span class="font-medium text-right sm:max-w-xs">{{ employee.alamat || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">No. HP / WhatsApp</span>
              <span class="font-medium">{{ employee.no_hp || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between pb-2">
              <span class="text-slate-500">NIK (KTP)</span>
              <span class="font-medium">{{ employee.no_ktp || '-' }}</span>
            </li>
          </ul>
        </template>
      </Card>

      <!-- Administrasi -->
      <Card>
        <template #title><div class="flex items-center gap-2"><i class="pi pi-id-card text-slate-500"></i>Administrasi & Kepegawaian</div></template>
        <template #content>
          <ul class="space-y-4">
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">NIP</span>
              <span class="font-medium">{{ employee.nip || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">NUPTK</span>
              <span class="font-medium">{{ employee.nuptk || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">NPWP</span>
              <span class="font-medium">{{ employee.npwp || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">BPJS Ketenagakerjaan</span>
              <span class="font-medium">{{ employee.no_bpjs_tk || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between border-b dark:border-slate-700 pb-2">
              <span class="text-slate-500">BPJS Kesehatan</span>
              <span class="font-medium">{{ employee.no_bpjs_kes || '-' }}</span>
            </li>
            <li class="flex flex-col sm:flex-row sm:justify-between pb-2">
              <span class="text-slate-500">Rekening Bank</span>
              <span class="font-medium">{{ employee.nama_bank || '-' }} - {{ employee.no_rekening || '-' }}</span>
            </li>
          </ul>
        </template>
      </Card>
    </div>

    <!-- Riwayat Pendidikan -->
    <Card>
      <template #title>
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2"><i class="pi pi-book text-slate-500"></i>Riwayat Pendidikan</div>
          <Button icon="pi pi-plus" text rounded aria-label="Tambah" />
        </div>
      </template>
      <template #content>
        <DataTable :value="employee.education_history" responsiveLayout="scroll" class="p-datatable-sm">
          <Column field="tingkat" header="Tingkat"></Column>
          <Column field="jurusan" header="Jurusan"></Column>
          <Column field="institusi" header="Institusi"></Column>
          <Column field="tahun_lulus" header="Tahun Lulus"></Column>
          <template #empty>
            <div class="text-center py-4 text-slate-500">Belum ada data riwayat pendidikan.</div>
          </template>
        </DataTable>
      </template>
    </Card>

    <!-- Riwayat Jabatan -->
    <Card>
      <template #title>
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2"><i class="pi pi-briefcase text-slate-500"></i>Riwayat Jabatan</div>
          <Button icon="pi pi-plus" text rounded aria-label="Tambah" />
        </div>
      </template>
      <template #content>
        <DataTable :value="employee.position_history" responsiveLayout="scroll" class="p-datatable-sm">
          <Column field="jabatan" header="Jabatan"></Column>
          <Column field="status_pegawai" header="Status"></Column>
          <Column header="TMT Mulai">
            <template #body="{data}">{{ formatDate(data.tmt_mulai) }}</template>
          </Column>
          <Column header="TMT Selesai">
            <template #body="{data}">{{ data.tmt_selesai ? formatDate(data.tmt_selesai) : 'Sekarang' }}</template>
          </Column>
          <template #empty>
            <div class="text-center py-4 text-slate-500">Belum ada data riwayat jabatan.</div>
          </template>
        </DataTable>
      </template>
    </Card>

  </div>
  
  <div v-else class="flex justify-center py-20">
    <ProgressSpinner />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const router = useRouter()
const toast = useToast()
const config = useRuntimeConfig()
const apiToken = useCookie('auth_token')

const employee = ref(null)
const computedInfo = ref(null)

const fetchEmployeeDetail = async () => {
  try {
    const id = route.params.id
    employee.value = await $fetch(`${config.public.apiBase}/sdm/employees/${id}`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
    
    computedInfo.value = await $fetch(`${config.public.apiBase}/sdm/employees/${id}/computed`, {
      headers: { Authorization: `Bearer ${apiToken.value}` }
    })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal mengambil detail pegawai' })
    router.push('/dashboard/sdm/pegawai')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('id-ID', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  if (route.params.id) {
    fetchEmployeeDetail()
  }
})
</script>
