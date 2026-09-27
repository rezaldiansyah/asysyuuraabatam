<template>
  <div class="flex flex-col gap-4">
    <div v-if="label" class="font-medium text-gray-700 dark:text-gray-300">
      {{ label }}
    </div>

    <!-- Upload Area -->
    <div
      class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center cursor-pointer hover:border-primary transition-colors flex flex-col items-center justify-center gap-2"
      @click="triggerFileInput"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*"
        class="hidden"
        @change="handleFileSelect"
      />
      <div class="pi pi-cloud-upload text-4xl text-gray-400 mb-2"></div>
      <div class="text-sm text-gray-500">
        <span class="font-semibold text-primary">Klik untuk upload</span> atau drag & drop
      </div>
      <div class="text-xs text-gray-400">
        PNG, JPG up to 5MB per file
      </div>
    </div>

    <!-- Preview List -->
    <div v-if="items.length > 0" class="flex flex-col gap-3">
      <div
        v-for="(item, index) in items"
        :key="item.id"
        class="flex items-center gap-4 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700"
      >
        <!-- Preview Image -->
        <div class="relative w-24 h-24 shrink-0 rounded overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
          <img
            v-if="item.url"
            :src="item.url"
            class="w-full h-full object-cover"
          />
          <div v-else-if="item.uploading" class="flex flex-col items-center gap-2">
            <i class="pi pi-spinner pi-spin text-xl text-primary"></i>
          </div>
        </div>

        <!-- Details -->
        <div class="flex-1 min-w-0">
          <div class="truncate text-sm font-medium">{{ item.file?.name || 'Image ' + (index + 1) }}</div>
          <div v-if="item.uploading" class="text-xs text-primary mt-1">Uploading...</div>
          <div v-else-if="item.error" class="text-xs text-red-500 mt-1">{{ item.error }}</div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-1 shrink-0">
          <Button
            icon="pi pi-angle-up"
            text
            rounded
            severity="secondary"
            :disabled="index === 0 || item.uploading"
            @click="moveUp(index)"
          />
          <Button
            icon="pi pi-angle-down"
            text
            rounded
            severity="secondary"
            :disabled="index === items.length - 1 || item.uploading"
            @click="moveDown(index)"
          />
          <Button
            icon="pi pi-trash"
            text
            rounded
            severity="danger"
            @click="remove(index)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'

const props = withDefaults(defineProps<{
  modelValue: string[]
  label?: string
  gap?: 'none' | 'small' | 'medium'
  borderRadius?: 'none' | 'rounded' | 'full-rounded'
}>(), {
  modelValue: () => [],
  gap: 'none',
  borderRadius: 'none'
})

const emit = defineEmits(['update:modelValue'])

const toast = useToast()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const authStore = useAuthStore()

interface UploadItem {
  id: string
  url: string | null
  file: File | null
  uploading: boolean
  error?: string
}

const items = ref<UploadItem[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

// Initialize from props
onMounted(() => {
  if (props.modelValue && props.modelValue.length > 0) {
    items.value = props.modelValue.map(url => ({
      id: crypto.randomUUID(),
      url,
      file: null,
      uploading: false
    }))
  }
})

// Sync back to parent when items change
watch(items, (newItems) => {
  const urls = newItems
    .filter(item => item.url && !item.uploading && !item.error)
    .map(item => item.url as string)
  
  // Only emit if arrays are different to prevent infinite loops
  if (JSON.stringify(urls) !== JSON.stringify(props.modelValue)) {
    emit('update:modelValue', urls)
  }
}, { deep: true })

function triggerFileInput() {
  fileInput.value?.click()
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    await processFiles(Array.from(target.files))
  }
  // Reset input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function handleDrop(event: DragEvent) {
  if (event.dataTransfer?.files) {
    await processFiles(Array.from(event.dataTransfer.files))
  }
}

async function processFiles(files: File[]) {
  const newItems: UploadItem[] = []
  
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      toast.add({ severity: 'warn', summary: 'Format Salah', detail: `${file.name} bukan gambar`, life: 3000 })
      continue
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.add({ severity: 'warn', summary: 'File Terlalu Besar', detail: `${file.name} melebihi 5MB`, life: 3000 })
      continue
    }
    
    const item: UploadItem = {
      id: crypto.randomUUID(),
      url: null,
      file,
      uploading: true
    }
    
    newItems.push(item)
    items.value.push(item)
  }
  
  await Promise.all(newItems.map(item => uploadFile(item)))
}

async function uploadFile(item: UploadItem) {
  if (!item.file) return
  
  const formData = new FormData()
  formData.append('file', item.file)
  
  try {
    const response = await $fetch<{ url: string }>(`${apiBase}/cms/upload`, {
      method: 'POST',
      body: formData,
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    const index = items.value.findIndex(i => i.id === item.id)
    if (index !== -1) {
      items.value[index].url = response.url
      items.value[index].uploading = false
    }
  } catch (e) {
    const index = items.value.findIndex(i => i.id === item.id)
    if (index !== -1) {
      items.value[index].error = 'Gagal upload'
      items.value[index].uploading = false
    }
    toast.add({ severity: 'error', summary: 'Gagal', detail: `Gagal mengupload ${item.file.name}`, life: 3000 })
  }
}

function moveUp(index: number) {
  if (index > 0) {
    const temp = items.value[index]
    items.value[index] = items.value[index - 1]
    items.value[index - 1] = temp
  }
}

function moveDown(index: number) {
  if (index < items.value.length - 1) {
    const temp = items.value[index]
    items.value[index] = items.value[index + 1]
    items.value[index + 1] = temp
  }
}

function remove(index: number) {
  items.value.splice(index, 1)
}
</script>
