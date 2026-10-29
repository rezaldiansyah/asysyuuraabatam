<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Master Unit Lembaga &amp; Sekolah</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Kelola unit kerja Yayasan dan sekolah. Seluruh unit yang aktif otomatis terintegrasi ke modul presensi, akademik, dan SDM.
        </p>
      </div>
      <Button 
        label="Tambah Unit Baru" 
        icon="pi pi-plus" 
        severity="primary" 
        size="small" 
        @click="openCreateModal"
      />
    </div>

    <!-- Main Table Card -->
    <div class="card bg-white dark:bg-slate-800 rounded-2xl p-5 shadow-sm border border-slate-200 dark:border-slate-700 space-y-4">
      <DataTable
        :value="units"
        :loading="loading"
        responsiveLayout="scroll"
        class="text-xs"
        stripedRows
      >
        <template #empty>
          <div class="p-8 text-center text-slate-400">
            <i class="pi pi-building text-3xl mb-2 text-slate-300"></i>
            <p>Belum ada data unit terdaftar.</p>
          </div>
        </template>

        <Column header="No." style="width: 50px">
          <template #body="{ index }">
            <span class="font-bold text-slate-500">{{ index + 1 }}</span>
          </template>
        </Column>

        <Column header="Kode Unit" style="width: 120px">
          <template #body="{ data }">
            <span class="px-2.5 py-1 rounded-lg font-mono font-bold text-xs bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border border-blue-200 dark:border-blue-900">
              {{ data.code }}
            </span>
          </template>
        </Column>

        <Column header="Nama Unit / Lembaga" style="min-width: 220px">
          <template #body="{ data }">
            <div class="font-bold text-slate-800 dark:text-white text-sm">{{ data.name }}</div>
            <div class="text-[11px] text-slate-400 mt-0.5">{{ data.address || 'Alamat belum diatur' }}</div>
          </template>
        </Column>

        <Column header="Status" style="width: 110px">
          <template #body="{ data }">
            <span 
              class="px-2 py-0.5 rounded text-[10px] font-bold"
              :class="data.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-slate-100 text-slate-500'"
            >
              {{ data.is_active ? 'Aktif' : 'Nonaktif' }}
            </span>
          </template>
        </Column>

        <Column header="Aksi" style="width: 110px; text-align: center">
          <template #body="{ data }">
            <div class="flex items-center justify-center gap-1.5">
              <Button
                icon="pi pi-pencil"
                severity="warning"
                text
                rounded
                size="small"
                title="Edit Unit"
                @click="openEditModal(data)"
              />
              <Button
                v-if="data.is_active"
                icon="pi pi-ban"
                severity="danger"
                text
                rounded
                size="small"
                title="Nonaktifkan Unit"
                @click="toggleUnitActive(data, false)"
              />
              <Button
                v-else
                icon="pi pi-check"
                severity="success"
                text
                rounded
                size="small"
                title="Aktifkan Kembali"
                @click="toggleUnitActive(data, true)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Modal Form Tambah / Edit Unit -->
    <Dialog
      v-model:visible="showModal"
      modal
      :header="isEdit ? 'Ubah Data Unit' : 'Tambah Unit Baru'"
      :style="{ width: '420px', maxWidth: '95vw' }"
    >
      <div class="space-y-4 pt-2 text-xs">
        <div>
          <label class="block font-bold text-slate-700 dark:text-slate-200 mb-1">
            Kode Singkat Unit <span class="text-rose-500">*</span>
          </label>
          <InputText 
            v-model="form.code" 
            placeholder="Contoh: SMAIT, TAHFIDZ, KOP" 
            class="w-full text-xs font-mono uppercase" 
            :disabled="isEdit"
          />
          <p class="text-[10px] text-slate-400 mt-1">Gunakan singkatan unik huruf kapital (huruf dan angka tanpa spasi).</p>
        </div>

        <div>
          <label class="block font-bold text-slate-700 dark:text-slate-200 mb-1">
            Nama Lengkap Unit <span class="text-rose-500">*</span>
          </label>
          <InputText 
            v-model="form.name" 
            placeholder="Contoh: SMAIT Asy-Syuuraa Batam" 
            class="w-full text-xs" 
          />
        </div>

        <div>
          <label class="block font-bold text-slate-700 dark:text-slate-200 mb-1">Alamat / Lokasi Operasional</label>
          <Textarea 
            v-model="form.address" 
            rows="2" 
            placeholder="Alamat kampus atau gedung unit" 
            class="w-full text-xs" 
          />
        </div>

        <div class="flex items-center gap-2 pt-1">
          <input 
            id="unit-active" 
            type="checkbox" 
            v-model="form.is_active" 
            class="w-4 h-4 text-emerald-600 rounded cursor-pointer"
          />
          <label for="unit-active" class="font-bold text-slate-700 dark:text-slate-300 cursor-pointer">
            Unit Berstatus Aktif
          </label>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2">
          <Button label="Batal" severity="secondary" text size="small" @click="showModal = false" />
          <Button 
            :label="isEdit ? 'Simpan Perubahan' : 'Tambah Unit'" 
            icon="pi pi-check" 
            severity="primary" 
            size="small" 
            :loading="saving" 
            @click="saveUnit" 
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const toast = useToast()
const api = useApi()

const units = ref<any[]>([])
const loading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)

const form = ref({
  code: '',
  name: '',
  address: '',
  is_active: true
})

async function fetchUnits() {
  loading.value = true
  try {
    const data = await api.get<any[]>('/units')
    units.value = data || []
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengambil data unit', life: 3000 })
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  isEdit.value = false
  editingId.value = null
  form.value = { code: '', name: '', address: '', is_active: true }
  showModal.value = true
}

function openEditModal(unit: any) {
  isEdit.value = true
  editingId.value = unit.id
  form.value = {
    code: unit.code,
    name: unit.name,
    address: unit.address || '',
    is_active: unit.is_active !== false
  }
  showModal.value = true
}

async function saveUnit() {
  if (!form.value.code.trim() || !form.value.name.trim()) {
    toast.add({ severity: 'warn', summary: 'Validasi', detail: 'Kode dan Nama Unit wajib diisi', life: 3000 })
    return
  }

  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      await api.put(`/units/${editingId.value}`, {
        code: form.value.code.trim().toUpperCase(),
        name: form.value.name.trim(),
        address: form.value.address.trim() || null,
        is_active: form.value.is_active
      })
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Data unit berhasil diperbarui', life: 3000 })
    } else {
      await api.post('/units', {
        code: form.value.code.trim().toUpperCase(),
        name: form.value.name.trim(),
        address: form.value.address.trim() || null,
        is_active: form.value.is_active
      })
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Unit baru berhasil ditambahkan', life: 3000 })
    }
    showModal.value = false
    fetchUnits()
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: err?.data?.detail || err?.message || 'Terjadi kesalahan sistem', life: 4000 })
  } finally {
    saving.value = false
  }
}

async function toggleUnitActive(unit: any, active: boolean) {
  try {
    await api.put(`/units/${unit.id}`, { is_active: active })
    unit.is_active = active
    toast.add({
      severity: 'success',
      summary: 'Status Diperbarui',
      detail: `Unit ${unit.name} sekarang ${active ? 'Aktif' : 'Nonaktif'}`,
      life: 3000
    })
  } catch (err: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal memperbarui status unit', life: 3000 })
  }
}

onMounted(() => {
  fetchUnits()
})
</script>
