<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Pusat Unduhan</h1>
        <p class="text-slate-500 dark:text-slate-400">Kelola dokumen SK, SOP, Juknis, Kalender Akademik, dan lainnya.</p>
      </div>
      <Button label="Upload Dokumen" icon="pi pi-upload" @click="openDialog()" />
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-1">
          <InputText v-model="searchQuery" placeholder="Cari dokumen..." class="w-full" @input="fetchDocuments" />
        </div>
        <Select v-model="filterCategory" :options="allCategoryOptions" optionLabel="label" optionValue="value" placeholder="Semua Kategori" class="w-full md:w-48" @change="fetchDocuments" />
        <Select v-model="filterVisibility" :options="visibilityOptions" optionLabel="label" optionValue="value" placeholder="Semua Akses" class="w-full md:w-48" @change="fetchDocuments" />
      </div>
    </div>

    <!-- Documents Table -->
    <div class="card">
      <DataTable :value="documents" :loading="loading" stripedRows responsiveLayout="scroll" class="text-sm">
        <Column header="Dokumen" style="min-width: 300px">
          <template #body="{ data }">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" :class="getCategoryColor(data.category)">
                <i :class="getCategoryIcon(data.category)" class="text-lg"></i>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="font-semibold text-slate-800 dark:text-white">{{ data.title }}</p>
                  <Tag :value="'v' + (data.version || '1.0')" severity="secondary" class="text-[10px] px-1.5 py-0.5" />
                </div>
                <p v-if="data.description" class="text-xs text-slate-400 mt-0.5 line-clamp-1">{{ data.description }}</p>
                <div class="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                  <span v-if="isGdriveLink(data.file_url)" class="text-blue-600 dark:text-blue-400 font-semibold inline-flex items-center gap-1 bg-blue-50 dark:bg-blue-950/40 px-1.5 py-0.5 rounded">
                    <i class="pi pi-external-link text-[10px]"></i> Google Drive
                  </span>
                  <span v-else>{{ data.file_name }} · {{ formatSize(data.file_size) }}</span>
                  <span v-if="data.effective_date" class="text-primary font-medium">· Berlaku: {{ formatDate(data.effective_date) }}</span>
                </div>
              </div>
            </div>
          </template>
        </Column>
        <Column header="Kategori" style="min-width: 150px">
          <template #body="{ data }">
            <Tag :value="getCategoryLabel(data.category)" :severity="getCategorySeverity(data.category)" />
          </template>
        </Column>
        <Column header="Akses" style="min-width: 100px">
          <template #body="{ data }">
            <Tag :value="data.visibility === 'public' ? 'Publik' : 'Internal'" :severity="data.visibility === 'public' ? 'success' : 'info'" />
          </template>
        </Column>
        <Column header="Diupload" style="min-width: 150px">
          <template #body="{ data }">
            <div>
              <p class="text-xs text-slate-500">{{ data.uploader_name || '-' }}</p>
              <p class="text-xs text-slate-400">{{ formatDate(data.created_at) }}</p>
            </div>
          </template>
        </Column>
        <Column header="Aksi" style="min-width: 180px">
          <template #body="{ data }">
            <div class="flex items-center gap-1">
              <a :href="data.file_url" target="_blank" class="p-2 text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition" title="Download">
                <i class="pi pi-download"></i>
              </a>
              <button @click="openHistoryDialog(data)" class="p-2 text-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-lg transition" title="Riwayat Versi">
                <i class="pi pi-history"></i>
              </button>
              <button @click="openDialog(data)" class="p-2 text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/30 rounded-lg transition" title="Edit">
                <i class="pi pi-pencil"></i>
              </button>
              <button @click="deleteDoc(data)" class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition" title="Hapus">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </template>
        </Column>
        <template #empty>
          <div class="text-center py-8 text-slate-400">
            <i class="pi pi-folder-open text-4xl mb-3 block"></i>
            <p>Belum ada dokumen. Klik "Upload Dokumen" untuk menambahkan.</p>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Upload/Edit Dialog -->
    <Dialog v-model:visible="dialogVisible" :header="editingDoc ? 'Edit Dokumen' : 'Upload Dokumen Baru'" modal class="w-full max-w-xl">
      <div class="space-y-4 pt-2">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Judul Dokumen *</label>
          <InputText v-model="form.title" placeholder="SK Penetapan Kurikulum 2026" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Deskripsi (opsional)</label>
          <Textarea v-model="form.description" rows="2" placeholder="Keterangan singkat tentang dokumen ini..." />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Kategori *</label>
            <Select v-model="form.category" :options="categoryOptions" optionLabel="label" optionValue="value" placeholder="Pilih kategori" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Visibilitas</label>
            <Select v-model="form.visibility" :options="visibilityOptions" optionLabel="label" optionValue="value" />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-2">
            <label class="font-medium">Versi Dokumen</label>
            <InputText v-model="form.version" placeholder="Contoh: 1.0 atau 2026.1" />
          </div>
          <div class="flex flex-col gap-2">
            <label class="font-medium">Tanggal Berlaku (opsional)</label>
            <InputText v-model="form.effective_date" type="date" class="w-full" />
          </div>
        </div>

        <div class="flex flex-col gap-2" v-if="!editingDoc && documents.length > 0">
          <label class="font-medium">Revisi dari Dokumen Sebelumnya (opsional)</label>
          <Select v-model="form.replaces_id" :options="replacesOptions" optionLabel="title" optionValue="id" placeholder="Pilih jika merupakan revisi/update dokumen lama" showClear class="w-full" />
          <p class="text-xs text-slate-400">Pilih dokumen lama jika upload ini adalah revisi atau versi baru.</p>
        </div>

        <!-- File Source Switcher: Upload Berkas vs Link Google Drive -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <label class="font-medium text-sm">Sumber Dokumen *</label>
            <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg text-xs">
              <button
                type="button"
                @click="fileSourceMode = 'upload'"
                class="px-2.5 py-1 rounded-md transition font-medium"
                :class="fileSourceMode === 'upload' ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm' : 'text-slate-500 hover:text-slate-800'"
              >
                <i class="pi pi-upload mr-1"></i> Upload File
              </button>
              <button
                type="button"
                @click="fileSourceMode = 'gdrive'"
                class="px-2.5 py-1 rounded-md transition font-medium"
                :class="fileSourceMode === 'gdrive' ? 'bg-white dark:bg-slate-700 text-primary shadow-sm' : 'text-slate-500 hover:text-slate-800'"
              >
                <i class="pi pi-external-link mr-1"></i> Link GDrive
              </button>
            </div>
          </div>

          <!-- Mode 1: Upload File Fisik -->
          <div v-if="fileSourceMode === 'upload'">
            <div v-if="form.file_url && !isGdriveLink(form.file_url)" class="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <i class="pi pi-file text-green-500 text-xl"></i>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-green-700 dark:text-green-400 truncate">{{ form.file_name }}</p>
                <p class="text-xs text-green-500">{{ formatSize(form.file_size) }}</p>
              </div>
              <button @click="clearFile" class="text-red-500 hover:text-red-700 p-1">
                <i class="pi pi-times"></i>
              </button>
            </div>
            <div v-else class="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-6 text-center hover:border-primary transition cursor-pointer" @click="triggerFileInput" @drop.prevent="handleDrop" @dragover.prevent>
              <i class="pi pi-cloud-upload text-3xl text-slate-400 mb-2"></i>
              <p class="text-sm text-slate-500">Klik untuk upload atau drag & drop</p>
              <p class="text-xs text-slate-400 mt-1">PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, ZIP (maks 10MB)</p>
            </div>
            <input ref="fileInputRef" type="file" accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar,.jpg,.jpeg,.png" class="hidden" @change="handleFileSelect" />
          </div>

          <!-- Mode 2: Link Google Drive -->
          <div v-else class="space-y-2">
            <div class="relative w-full">
              <i class="pi pi-link absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
              <InputText 
                v-model="gdriveInputUrl" 
                placeholder="https://drive.google.com/file/d/.../view" 
                class="w-full !pl-9"
                @input="handleGdriveInput"
              />
            </div>
            <div class="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800 text-xs text-blue-700 dark:text-blue-300 flex items-start gap-2">
              <i class="pi pi-info-circle text-blue-500 mt-0.5 shrink-0"></i>
              <div>
                <strong>Hemat Storage:</strong> Dokumen tidak diunggah ke server, melainkan langsung ditautkan ke Google Drive Yayasan. Pastikan setelan berbagi di Drive adalah <em>"Siapa saja yang memiliki link dapat melihat"</em>.
              </div>
            </div>
          </div>
        </div>

        <div v-if="uploadProgress > 0 && uploadProgress < 100" class="w-full bg-slate-200 rounded-full h-2">
          <div class="bg-primary h-2 rounded-full transition-all" :style="{ width: uploadProgress + '%' }"></div>
        </div>
      </div>

      <template #footer>
        <Button label="Batal" severity="secondary" @click="dialogVisible = false" />
        <Button :label="editingDoc ? 'Simpan' : 'Upload'" icon="pi pi-save" :loading="saving" @click="saveDocument" :disabled="!form.title || !form.file_url || !form.category" />
      </template>
    </Dialog>

    <!-- History Dialog -->
    <Dialog v-model:visible="historyDialogVisible" header="Riwayat Versi Dokumen" modal class="w-full max-w-lg">
      <div v-if="loadingHistory" class="text-center py-6 text-slate-400">
        <i class="pi pi-spin pi-spinner text-2xl mb-2"></i>
        <p>Memuat riwayat versi...</p>
      </div>
      <div v-else-if="documentHistory.length === 0" class="text-center py-6 text-slate-400">
        Belum ada riwayat versi untuk dokumen ini.
      </div>
      <div v-else class="space-y-3 py-2 max-h-96 overflow-y-auto">
        <div v-for="item in documentHistory" :key="item.id" class="p-3 rounded-lg border flex items-center justify-between"
          :class="item.is_current ? 'border-primary bg-primary/5 dark:bg-primary/10' : 'border-slate-200 dark:border-slate-700'">
          <div class="flex-1 pr-3">
            <div class="flex items-center gap-2">
              <span class="font-bold text-sm text-slate-800 dark:text-white">{{ item.title }}</span>
              <Tag :value="'v' + item.version" :severity="item.is_current ? 'success' : 'secondary'" class="text-xs" />
              <span v-if="item.is_current" class="text-[10px] text-primary font-semibold">(Versi Ini)</span>
            </div>
            <div class="text-xs text-slate-400 mt-1 flex flex-wrap gap-2">
              <span v-if="item.effective_date">Berlaku: {{ formatDate(item.effective_date) }}</span>
              <span>Diupload: {{ formatDate(item.created_at) }}</span>
              <span v-if="item.uploader_name">Oleh: {{ item.uploader_name }}</span>
            </div>
          </div>
          <a :href="item.file_url" target="_blank" class="p-2 text-primary hover:bg-primary/10 rounded-lg flex-shrink-0" title="Unduh Versi Ini">
            <i class="pi pi-download"></i>
          </a>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const historyDialogVisible = ref(false)
const documentHistory = ref<any[]>([])
const loadingHistory = ref(false)
const editingDoc = ref<any>(null)
const documents = ref<any[]>([])
const searchQuery = ref('')
const filterCategory = ref('')
const filterVisibility = ref('')
const uploadProgress = ref(0)
const fileInputRef = ref<HTMLInputElement>()

const replacesOptions = computed(() => {
  return documents.value.map(d => ({
    id: d.id,
    title: `${d.title} (v${d.version || '1.0'})`
  }))
})

const categoryOptions = [
  { value: 'sk_yayasan', label: 'SK Yayasan' },
  { value: 'sop', label: 'SOP' },
  { value: 'kalender_akademik', label: 'Kalender Akademik' },
  { value: 'juknis', label: 'Juknis' },
  { value: 'surat_edaran', label: 'Surat Edaran' },
  { value: 'lainnya', label: 'Lainnya' },
]

const allCategoryOptions = [{ value: '', label: 'Semua Kategori' }, ...categoryOptions]

const visibilityOptions = [
  { value: 'internal', label: 'Internal' },
  { value: 'public', label: 'Publik' },
]

const fileSourceMode = ref<'upload' | 'gdrive'>('upload')
const gdriveInputUrl = ref('')

function isGdriveLink(url?: string): boolean {
  if (!url) return false
  return url.includes('drive.google.com') || url.includes('docs.google.com')
}

function handleGdriveInput() {
  const url = gdriveInputUrl.value.trim()
  if (url) {
    form.file_url = url
    form.file_name = 'Google Drive Document'
    form.file_size = 0
    if (!form.title) {
      form.title = 'Dokumen Google Drive'
    }
  } else {
    form.file_url = ''
    form.file_name = ''
    form.file_size = 0
  }
}

const form = reactive({
  title: '',
  description: '',
  category: 'lainnya',
  visibility: 'internal',
  file_url: '',
  file_name: '',
  file_size: 0,
  version: '1.0',
  replaces_id: null as number | null,
  effective_date: '',
})

function resetForm() {
  form.title = ''
  form.description = ''
  form.category = 'lainnya'
  form.visibility = 'internal'
  form.file_url = ''
  form.file_name = ''
  form.file_size = 0
  form.version = '1.0'
  form.replaces_id = null
  form.effective_date = ''
  fileSourceMode.value = 'upload'
  gdriveInputUrl.value = ''
  uploadProgress.value = 0
}

function openDialog(doc?: any) {
  if (doc) {
    editingDoc.value = doc
    Object.assign(form, {
      title: doc.title,
      description: doc.description || '',
      category: doc.category,
      visibility: doc.visibility,
      file_url: doc.file_url,
      file_name: doc.file_name,
      file_size: doc.file_size,
      version: doc.version || '1.0',
      replaces_id: doc.replaces_id || null,
      effective_date: doc.effective_date ? doc.effective_date.substring(0, 10) : '',
    })
    if (isGdriveLink(doc.file_url)) {
      fileSourceMode.value = 'gdrive'
      gdriveInputUrl.value = doc.file_url
    } else {
      fileSourceMode.value = 'upload'
      gdriveInputUrl.value = ''
    }
  } else {
    editingDoc.value = null
    resetForm()
  }
  dialogVisible.value = true
}

async function openHistoryDialog(doc: any) {
  historyDialogVisible.value = true
  loadingHistory.value = true
  try {
    documentHistory.value = await api.get<any[]>(`/internal/documents/${doc.id}/history`)
  } catch (e) {
    console.error('Failed to fetch document history', e)
    documentHistory.value = []
  } finally {
    loadingHistory.value = false
  }
}

async function fetchDocuments() {
  loading.value = true
  try {
    let url = '/internal/documents?'
    if (filterCategory.value) url += `category=${filterCategory.value}&`
    if (filterVisibility.value) url += `visibility=${filterVisibility.value}&`
    if (searchQuery.value) url += `search=${encodeURIComponent(searchQuery.value)}&`
    documents.value = await api.get<any[]>(url)
  } catch (e) {
    console.error('Failed to fetch documents', e)
  } finally {
    loading.value = false
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) await uploadFile(file)
}

async function handleDrop(e: DragEvent) {
  const file = e.dataTransfer?.files?.[0]
  if (file) await uploadFile(file)
}

async function uploadFile(file: File) {
  if (file.size > 10 * 1024 * 1024) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'File terlalu besar (maks 10MB)', life: 3000 })
    return
  }
  
  uploadProgress.value = 10
  try {
    const result = await api.upload('/cms/upload', file)
    form.file_url = result.url
    form.file_name = file.name
    form.file_size = file.size
    uploadProgress.value = 100
    
    // Auto-fill title if empty
    if (!form.title) {
      form.title = file.name.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' ')
    }
    
    toast.add({ severity: 'success', summary: 'Upload', detail: 'File berhasil diupload', life: 2000 })
  } catch (e) {
    console.error('Upload failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengupload file', life: 3000 })
    uploadProgress.value = 0
  }
}

function clearFile() {
  form.file_url = ''
  form.file_name = ''
  form.file_size = 0
  uploadProgress.value = 0
}

async function saveDocument() {
  saving.value = true
  try {
    if (editingDoc.value) {
      await api.put(`/internal/documents/${editingDoc.value.id}`, { ...form })
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Dokumen berhasil diperbarui', life: 3000 })
    } else {
      await api.post('/internal/documents', { ...form })
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Dokumen berhasil ditambahkan', life: 3000 })
    }
    dialogVisible.value = false
    await fetchDocuments()
  } catch (e) {
    console.error('Save failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan dokumen', life: 3000 })
  } finally {
    saving.value = false
  }
}

async function deleteDoc(doc: any) {
  if (!confirm(`Hapus dokumen "${doc.title}"?`)) return
  try {
    await api.delete(`/internal/documents/${doc.id}`)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Dokumen berhasil dihapus', life: 3000 })
    await fetchDocuments()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus dokumen', life: 3000 })
  }
}

// Helpers
function getCategoryLabel(cat: string) {
  return categoryOptions.find(c => c.value === cat)?.label || cat
}

function getCategoryIcon(cat: string) {
  const map: Record<string, string> = {
    sk_yayasan: 'pi pi-file-pdf',
    sop: 'pi pi-book',
    kalender_akademik: 'pi pi-calendar',
    juknis: 'pi pi-list',
    surat_edaran: 'pi pi-envelope',
    lainnya: 'pi pi-file',
  }
  return map[cat] || 'pi pi-file'
}

function getCategoryColor(cat: string) {
  const map: Record<string, string> = {
    sk_yayasan: 'bg-red-100 dark:bg-red-900/30 text-red-500',
    sop: 'bg-blue-100 dark:bg-blue-900/30 text-blue-500',
    kalender_akademik: 'bg-green-100 dark:bg-green-900/30 text-green-500',
    juknis: 'bg-purple-100 dark:bg-purple-900/30 text-purple-500',
    surat_edaran: 'bg-amber-100 dark:bg-amber-900/30 text-amber-500',
    lainnya: 'bg-slate-100 dark:bg-slate-700 text-slate-500',
  }
  return map[cat] || 'bg-slate-100 dark:bg-slate-700 text-slate-500'
}

function getCategorySeverity(cat: string) {
  const map: Record<string, string> = {
    sk_yayasan: 'danger', sop: 'info', kalender_akademik: 'success',
    juknis: 'warn', surat_edaran: 'warn', lainnya: 'secondary',
  }
  return map[cat] || 'secondary'
}

function formatSize(bytes: number) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(() => fetchDocuments())
</script>
