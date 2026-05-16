<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <label class="text-sm font-medium text-slate-700 dark:text-slate-300">{{ label }}</label>
      <div class="flex bg-slate-100 dark:bg-slate-700 rounded-lg p-1 text-xs">
        <button 
          @click="mode = 'url'"
          class="px-3 py-1 rounded-md transition-all"
          :class="mode === 'url' ? 'bg-white dark:bg-slate-600 shadow-sm font-medium' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'"
        >
          Link URL
        </button>
        <button 
          @click="mode = 'upload'"
          class="px-3 py-1 rounded-md transition-all"
          :class="mode === 'upload' ? 'bg-white dark:bg-slate-600 shadow-sm font-medium' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400'"
        >
          Upload
        </button>
      </div>
    </div>

    <!-- URL Input Mode -->
    <div v-if="mode === 'url'">
      <div class="p-inputgroup">
        <span class="p-inputgroup-addon">
          <i class="pi pi-link"></i>
        </span>
        <InputText 
          :modelValue="modelValue" 
          @update:modelValue="$emit('update:modelValue', $event)" 
          :placeholder="placeholder || 'https://...'" 
        />
      </div>
    </div>

    <!-- File Upload Mode -->
    <div v-else>
      <div 
        class="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-6 text-center transition-colors hover:border-primary cursor-pointer bg-slate-50 dark:bg-slate-800/50"
        @click="triggerFileInput"
        @dragover.prevent
        @drop.prevent="handleDrop"
      >
        <input 
          type="file" 
          ref="fileInput" 
          class="hidden" 
          accept="image/*" 
          @change="handleFileSelect"
        />
        
        <div v-if="uploading" class="flex flex-col items-center gap-2 py-2">
          <i class="pi pi-spin pi-spinner text-3xl text-primary"></i>
          <span class="text-sm text-slate-500">Mengupload...</span>
        </div>

        <div v-else class="flex flex-col items-center gap-2">
          <div class="w-10 h-10 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center text-slate-500">
            <i class="pi pi-image text-xl"></i>
          </div>
          <div class="text-sm">
            <span class="font-medium text-primary hover:underline">Klik untuk upload</span>
            <span class="text-slate-500"> atau drag & drop</span>
          </div>
          <p class="text-xs text-slate-400">PNG, JPG, WEBP (Max 5MB)</p>
        </div>
      </div>
    </div>

    <!-- Preview -->
    <div v-if="modelValue" class="relative group mt-2 w-full min-h-[100px] max-h-[400px] bg-slate-100 dark:bg-slate-800 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 flex items-center justify-center">
      <img :src="modelValue" alt="Preview" class="max-w-full max-h-[400px] object-contain">
      
      <!-- Delete Action (Top Right) -->
      <div class="absolute top-2 right-2 flex gap-1">
        <Button 
          icon="pi pi-trash" 
          severity="danger" 
          rounded 
          class="shadow-md"
          @click="$emit('update:modelValue', '')" 
          tooltip="Hapus Gambar"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const props = defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
}>()

const emit = defineEmits(['update:modelValue'])
const toast = useToast()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const mode = ref<'url' | 'upload'>('upload')
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    const file = input.files[0]
    if (file) uploadFile(file)
  }
}

function handleDrop(event: DragEvent) {
  if (event.dataTransfer?.files.length) {
    const file = event.dataTransfer.files[0]
    if (file) uploadFile(file)
  }
}

async function uploadFile(file: File) {
  // Validate
  if (!file.type.startsWith('image/')) {
    toast.add({ severity: 'warn', summary: 'Format Salah', detail: 'Harap upload file gambar', life: 3000 })
    return
  }
  if (file.size > 5 * 1024 * 1024) { // 5MB
    toast.add({ severity: 'warn', summary: 'File Terlalu Besar', detail: 'Maksimal ukuran file 5MB', life: 3000 })
    return
  }

  uploading.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const { $api } = useNuxtApp()
    // Using direct fetch to handle FormData properly if Nuxt $api wrapper has issues with it
    // But attempting with default fetch first
    
    // Auth Store for Token
    const authStore = useAuthStore()
    
    const response = await $fetch<{ url: string }>(`${apiBase}/cms/upload`, {
      method: 'POST',
      body: formData,
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    emit('update:modelValue', response.url)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Gambar berhasil diupload', life: 3000 })
    
  } catch (e) {
    console.error('Upload failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal mengupload gambar', life: 3000 })
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = '' // Reset input
  }
}

import { useAuthStore } from '~/stores/auth'
</script>
