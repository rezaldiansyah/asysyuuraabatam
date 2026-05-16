<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Data Pendaftar PPDB</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola dan ekspor data calon murid baru.</p>
      </div>
      <div class="flex gap-2">
        <Button label="Export CSV" icon="pi pi-file-excel" severity="success" @click="exportCSV" />
      </div>
    </div>

    <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-lg">
      <DataTable 
        :value="registrations" 
        :loading="loading"
        paginator 
        :rows="10" 
        dataKey="id" 
        filterDisplay="menu"
        responsiveLayout="scroll"
        :globalFilterFields="['student_name', 'registration_number', 'unit', 'nisn']"
      >
        <template #header>
            <div class="flex justify-end">
                <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText v-model="filters['global'].value" placeholder="Cari Nama / No Registrasi..." />
                </span>
            </div>
        </template>
        
        <template #empty> Belum ada data pendaftar. </template>
        <template #loading> Memuat data... </template>

        <Column field="registration_number" header="No. Reg" style="min-width: 10rem"></Column>
        <Column field="unit" header="Unit" style="min-width: 8rem">
            <template #body="{ data }">
                <Badge :value="data.unit" :severity="data.unit === 'SDIT' ? 'success' : 'info'" />
            </template>
        </Column>
        <Column field="student_name" header="Nama Siswa" style="min-width: 14rem"></Column>
        <Column field="gender" header="L/P" style="min-width: 5rem"></Column>
        <Column header="Orang Tua/Wali" style="min-width: 12rem">
            <template #body="{ data }">
                <div class="flex flex-col">
                    <span>{{ data.father_data?.name || 'N/A' }}</span>
                    <span class="text-sm text-slate-500">{{ data.phone }}</span>
                </div>
            </template>
        </Column>
        <Column field="status" header="Status" style="min-width: 8rem">
            <template #body="{ data }">
                <Badge :value="data.status" :severity="data.status === 'PENDING' ? 'warning' : 'success'" />
            </template>
        </Column>
        <Column header="Aksi" style="min-width: 10rem" alignFrozen="right" frozen>
            <template #body="{ data }">
                <div class="flex gap-2">
                    <Button icon="pi pi-file-pdf" rounded text severity="danger" title="Download PDF Formulir" @click="downloadPDF(data)" />
                    <Button icon="pi pi-trash" rounded text severity="danger" title="Hapus" @click="confirmDelete(data.id)" />
                </div>
            </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { FilterMatchMode } from '@primevue/core/api'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

definePageMeta({ layout: 'dashboard' })

const toast = useToast()
const confirm = useConfirm()
const config = useRuntimeConfig()
const authStore = useAuthStore()

const loading = ref(false)
const registrations = ref([])
const filters = ref({
    global: { value: null, matchMode: FilterMatchMode.CONTAINS }
})

async function loadData() {
  loading.value = true
  try {
    const data = await $fetch(`${config.public.apiBase}/ppdb/registrations`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    registrations.value = data || []
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Tidak dapat memuat data pendaftar.', life: 3000 })
  } finally {
    loading.value = false
  }
}

function confirmDelete(id) {
    confirm.require({
        message: 'Apakah Anda yakin ingin menghapus data pendaftaran ini?',
        header: 'Konfirmasi Hapus',
        icon: 'pi pi-exclamation-triangle',
        accept: async () => {
            try {
                await $fetch(`${config.public.apiBase}/ppdb/registrations/${id}`, {
                    method: 'DELETE',
                    headers: { Authorization: `Bearer ${authStore.token}` }
                })
                toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data dihapus', life: 3000 })
                loadData()
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Gagal', detail: 'Tidak dapat menghapus data', life: 3000 })
            }
        }
    })
}

function downloadPDF(data) {
  // Mock PDF generation for now
  toast.add({ severity: 'info', summary: 'Info', detail: `Mencetak formulir untuk ${data.student_name}... (Dalam Pengembangan)`, life: 3000 })
}

function exportCSV() {
    if(!registrations.value.length) return
    
    const headers = ['No. Registrasi', 'Unit', 'Nama Siswa', 'NISN', 'L/P', 'Nama Ayah', 'No HP', 'Email', 'Status']
    const csvContent = "data:text/csv;charset=utf-8," 
        + headers.join(",") + "\n"
        + registrations.value.map(e => [
            e.registration_number, 
            e.unit, 
            e.student_name, 
            e.nisn, 
            e.gender, 
            e.father_data?.name, 
            e.phone, 
            e.email, 
            e.status
        ].join(",")).join("\n")
        
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", "data_pendaftar_ppdb.csv")
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
}

onMounted(() => {
  loadData()
})
</script>
