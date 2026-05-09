<template>
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Berita & Artikel</h1>
          <p class="text-slate-500 dark:text-slate-400">Kelola berita sekolah, artikel, dan pengumuman.</p>
        </div>
        <Button severity="success" @click="showFormDialog = true">
          <i class="pi pi-plus mr-2"></i>
          Tambah Berita
        </Button>
      </div>

      <!-- Data Table -->
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
        <DataTable
          :value="posts"
          :loading="loading"
          paginator
          :rows="10"
          stripedRows
          class="p-datatable-sm"
        >
          <template #empty>
            <div class="text-center py-8 text-slate-500">Belum ada berita.</div>
          </template>

          <Column header="Gambar" style="width: 80px">
            <template #body="{ data }">
              <img
                v-if="data.image_url"
                :src="data.image_url"
                alt="thumbnail"
                class="w-16 h-12 object-cover rounded-lg"
              />
              <div v-else class="w-16 h-12 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
                <i class="pi pi-image text-slate-400"></i>
              </div>
            </template>
          </Column>

          <Column field="title" header="Judul">
            <template #body="{ data }">
              <div>
                <span class="font-medium">{{ data.title }}</span>
                <div class="text-xs text-slate-500">/{{ data.slug }}</div>
              </div>
            </template>
          </Column>

          <Column field="is_published" header="Status">
            <template #body="{ data }">
              <Tag
                :value="data.is_published ? 'Published' : 'Draft'"
                :severity="data.is_published ? 'success' : 'secondary'"
              />
            </template>
          </Column>

          <Column header="Tanggal">
            <template #body="{ data }">
              {{ new Date(data.created_at).toLocaleDateString('id-ID') }}
            </template>
          </Column>

          <Column header="Aksi" style="width: 130px">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" severity="secondary" size="small" text rounded @click="editPost(data)" />
                <Button icon="pi pi-trash" severity="danger" size="small" text rounded @click="confirmDelete(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Add/Edit Dialog -->
      <Dialog
        v-model:visible="showFormDialog"
        :header="editingPost ? 'Edit Berita' : 'Tambah Berita Baru'"
        :style="{ width: '90vw', maxWidth: '800px' }"
        modal
        @hide="resetForm"
      >
        <form @submit.prevent="submitForm" class="space-y-4">
          <!-- Title -->
          <div class="flex flex-col gap-2">
            <label for="title" class="font-medium">Judul *</label>
            <InputText id="title" v-model="form.title" placeholder="Judul berita" class="w-full" />
          </div>

          <!-- Slug -->
          <div class="flex flex-col gap-2">
            <label for="slug" class="font-medium">Slug (URL)</label>
            <InputText id="slug" v-model="form.slug" placeholder="judul-berita" class="w-full" />
          </div>

          <!-- Image Upload -->
          <div class="flex flex-col gap-2">
            <label class="font-medium">Gambar / Thumbnail</label>
            <div class="flex items-center gap-4">
              <div v-if="form.image_url" class="relative">
                <img :src="form.image_url" alt="preview" class="w-32 h-24 object-cover rounded-lg border" />
                <button
                  type="button"
                  @click="form.image_url = ''"
                  class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600"
                >✕</button>
              </div>
              <div>
                <input
                  type="file"
                  ref="fileInput"
                  accept="image/*"
                  class="hidden"
                  @change="handleFileUpload"
                />
                <Button
                  type="button"
                  severity="secondary"
                  size="small"
                  :loading="uploading"
                  @click="($refs.fileInput as HTMLInputElement)?.click()"
                >
                  <i class="pi pi-upload mr-2"></i>
                  {{ form.image_url ? 'Ganti Gambar' : 'Upload Gambar' }}
                </Button>
              </div>
            </div>
          </div>

          <!-- Excerpt -->
          <div class="flex flex-col gap-2">
            <label for="excerpt" class="font-medium">Ringkasan</label>
            <Textarea id="excerpt" v-model="form.excerpt" rows="2" placeholder="Ringkasan singkat berita..." class="w-full" />
          </div>

          <!-- Content (Rich Text) -->
          <div class="flex flex-col gap-2">
            <label class="font-medium">Konten *</label>
            <Editor v-model="form.content" editorStyle="height: 250px" />
          </div>

          <!-- Published -->
          <div class="flex items-center gap-2">
            <Checkbox id="is_published" v-model="form.is_published" :binary="true" />
            <label for="is_published" class="font-medium">Publish sekarang</label>
          </div>

          <!-- Footer -->
          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" label="Batal" severity="secondary" @click="showFormDialog = false" />
            <Button type="submit" :label="editingPost ? 'Update' : 'Simpan'" :loading="submitting" />
          </div>
        </form>
      </Dialog>

      <ConfirmDialog />
    </div>
</template>

<script setup lang="ts">
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const confirm = useConfirm()
const toast = useToast()

// State
const posts = ref<any[]>([])
const loading = ref(true)
const submitting = ref(false)
const uploading = ref(false)
const showFormDialog = ref(false)
const editingPost = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const form = reactive({
  title: '',
  slug: '',
  excerpt: '',
  content: '',
  image_url: '',
  is_published: false,
})

// Fetch posts
async function fetchPosts() {
  loading.value = true
  try {
    posts.value = await api.get('/cms/posts')
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

// Handle file upload
async function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return
  
  const file = input.files[0]
  uploading.value = true
  try {
    const result = await api.upload('/cms/upload', file)
    form.image_url = result.url
    toast.add({ severity: 'success', summary: 'Upload berhasil', detail: 'Gambar berhasil diupload', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Upload gagal', detail: 'Gagal mengupload gambar', life: 3000 })
    console.error(e)
  } finally {
    uploading.value = false
    input.value = '' // Reset input
  }
}

// Edit post
function editPost(post: any) {
  editingPost.value = post
  form.title = post.title
  form.slug = post.slug
  form.excerpt = post.excerpt || ''
  form.content = post.content || ''
  form.image_url = post.image_url || ''
  form.is_published = post.is_published
  showFormDialog.value = true
}

// Reset form
function resetForm() {
  editingPost.value = null
  form.title = ''
  form.slug = ''
  form.excerpt = ''
  form.content = ''
  form.image_url = ''
  form.is_published = false
}

// Auto-generate slug
watch(() => form.title, (val) => {
  if (!editingPost.value && val) {
    form.slug = val
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
  }
})

// Submit form
async function submitForm() {
  submitting.value = true
  try {
    const payload = { ...form }
    if (editingPost.value) {
      await api.put(`/cms/posts/${editingPost.value.id}`, payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Berita diupdate', life: 3000 })
    } else {
      await api.post('/cms/posts', payload)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Berita dibuat', life: 3000 })
    }
    showFormDialog.value = false
    resetForm()
    fetchPosts()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan berita', life: 3000 })
  } finally {
    submitting.value = false
  }
}

// Confirm delete
function confirmDelete(post: any) {
  confirm.require({
    message: `Hapus berita "${post.title}"?`,
    header: 'Konfirmasi Hapus',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await api.delete(`/cms/posts/${post.id}`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Berita dihapus', life: 3000 })
        fetchPosts()
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus berita', life: 3000 })
      }
    },
  })
}

onMounted(fetchPosts)
</script>
