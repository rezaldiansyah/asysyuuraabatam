<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Setup Landing Page SPMB</h1>
        <p class="text-slate-500 dark:text-slate-400">Compose landing page pendaftaran dari section-section yang sudah disiapkan.</p>
      </div>
      <div class="flex gap-2">
        <Button label="Preview" icon="pi pi-eye" severity="secondary" outlined @click="showPreview = true" />
        <Button label="Simpan" icon="pi pi-save" :loading="saving" @click="saveConfig" />
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Panel: Section List (Sortable) -->
      <div class="lg:col-span-1 space-y-4">
        <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-lg p-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-slate-800 dark:text-white">Sections</h3>
            <Button icon="pi pi-plus" severity="secondary" rounded text size="small" @click="showAddSection = true" />
          </div>

          <!-- Section List -->
          <div class="space-y-2">
            <div
              v-for="(section, index) in config.sections"
              :key="section.id"
              class="flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-all"
              :class="[
                selectedIndex === index
                  ? 'border-primary bg-primary/5 dark:bg-primary/10'
                  : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600',
                !section.visible ? 'opacity-50' : ''
              ]"
              @click="selectedIndex = index"
            >
              <div class="flex flex-col gap-1">
                <Button icon="pi pi-chevron-up" text rounded size="small" :disabled="index === 0" class="!p-1 !w-6 !h-6" @click.stop="moveSection(index, -1)" />
                <Button icon="pi pi-chevron-down" text rounded size="small" :disabled="index === config.sections.length - 1" class="!p-1 !w-6 !h-6" @click.stop="moveSection(index, 1)" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium truncate">{{ getSectionLabel(section.type) }}</div>
                <div class="text-xs text-slate-400 truncate">{{ section.title || getSectionLabel(section.type) }}</div>
              </div>
              <div class="flex items-center gap-1">
                <Button
                  :icon="section.visible ? 'pi pi-eye' : 'pi pi-eye-slash'"
                  text rounded size="small"
                  :severity="section.visible ? 'secondary' : 'danger'"
                  class="!p-1 !w-7 !h-7"
                  @click.stop="section.visible = !section.visible"
                />
                <Button icon="pi pi-trash" text rounded size="small" severity="danger" class="!p-1 !w-7 !h-7" @click.stop="removeSection(index)" />
              </div>
            </div>
          </div>

          <div v-if="config.sections.length === 0" class="text-center py-8 text-slate-400">
            <i class="pi pi-inbox text-3xl mb-2"></i>
            <p class="text-sm">Belum ada section. Klik + untuk menambahkan.</p>
          </div>
        </div>

        <!-- Global Settings -->
        <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-lg p-4 space-y-4">
          <h3 class="font-bold text-slate-800 dark:text-white">Pengaturan Global</h3>
          <div class="space-y-3">
            <div>
              <label class="text-sm font-medium mb-1 block">Label SPMB</label>
              <InputText v-model="config.spmb_label" placeholder="PPDB / SPMB" class="w-full" />
            </div>
            <div>
              <label class="text-sm font-medium mb-1 block">Warna Tema</label>
              <div class="flex gap-2">
                <button
                  v-for="color in themeColors"
                  :key="color.value"
                  class="w-8 h-8 rounded-full border-2 transition-transform"
                  :class="config.theme_color === color.value ? 'scale-110 border-slate-800 dark:border-white' : 'border-transparent'"
                  :style="{ backgroundColor: color.hex }"
                  @click="config.theme_color = color.value"
                />
              </div>
            </div>
            <div>
              <label class="text-sm font-medium mb-1 block">No. WhatsApp Admin</label>
              <InputText v-model="config.wa_number" placeholder="6281234567890" class="w-full" />
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel: Section Editor -->
      <div class="lg:col-span-2">
        <div v-if="selectedSection" class="card bg-white dark:bg-slate-900 shadow-sm rounded-lg p-6 space-y-6">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-lg text-slate-800 dark:text-white">
              <i :class="getSectionIcon(selectedSection.type)" class="mr-2"></i>
              {{ getSectionLabel(selectedSection.type) }}
            </h3>
            <Tag :value="selectedSection.visible ? 'Aktif' : 'Tersembunyi'" :severity="selectedSection.visible ? 'success' : 'warn'" />
          </div>

          <!-- Section Title (optional for all types) -->
          <div>
            <label class="text-sm font-medium mb-1 block">Judul Section (opsional)</label>
            <InputText v-model="selectedSection.title" placeholder="Judul yang ditampilkan di atas section" class="w-full" />
          </div>

          <!-- Dynamic Editor Based on Type -->

          <!-- Hero Carousel -->
          <template v-if="selectedSection.type === 'hero_carousel'">
            <div class="space-y-3">
              <label class="font-medium">Poster / Banner</label>
              <div v-for="(img, i) in selectedSection.images" :key="i" class="p-3 border rounded-lg bg-slate-50 dark:bg-slate-800/50 space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium">Gambar #{{ i + 1 }}</span>
                  <Button v-if="selectedSection.images.length > 1" icon="pi pi-trash" severity="danger" text rounded size="small" @click="selectedSection.images.splice(i, 1)" />
                </div>
                <CmsImageUploader v-model="selectedSection.images[i]" label="" placeholder="Upload poster/banner" />
              </div>
              <Button label="Tambah Gambar" icon="pi pi-plus" outlined severity="secondary" class="w-full" @click="selectedSection.images.push('')" />
            </div>
          </template>

          <!-- Stacked Image -->
          <template v-if="selectedSection.type === 'stacked_image'">
            <PpdbStackedImageUploader
              v-model="selectedSection.images"
              label="Gambar Stacked (dari Tim Desain)"
              :gap="selectedSection.gap || 'none'"
              :border-radius="selectedSection.border_radius || 'none'"
            />
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium mb-1 block">Gap antar gambar</label>
                <Select v-model="selectedSection.gap" :options="gapOptions" optionLabel="label" optionValue="value" placeholder="Pilih gap" class="w-full" />
              </div>
              <div>
                <label class="text-sm font-medium mb-1 block">Border Radius</label>
                <Select v-model="selectedSection.border_radius" :options="borderRadiusOptions" optionLabel="label" optionValue="value" placeholder="Pilih radius" class="w-full" />
              </div>
            </div>
          </template>

          <!-- Info Text -->
          <template v-if="selectedSection.type === 'info_text'">
            <div>
              <label class="font-medium mb-2 block">Konten (Rich Text)</label>
              <Textarea v-model="selectedSection.content" rows="8" class="w-full" placeholder="Tulis informasi pendaftaran di sini..." />
            </div>
          </template>

          <!-- CTA Button -->
          <template v-if="selectedSection.type === 'cta_button'">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium mb-1 block">Label Tombol Daftar</label>
                <InputText v-model="selectedSection.cta_label" placeholder="Daftar Sekarang" class="w-full" />
              </div>
              <div>
                <label class="text-sm font-medium mb-1 block">Label Tombol WhatsApp</label>
                <InputText v-model="selectedSection.wa_label" placeholder="Tanya Admin (WA)" class="w-full" />
              </div>
            </div>
          </template>

          <!-- Unit Cards -->
          <template v-if="selectedSection.type === 'unit_cards'">
            <div class="space-y-3">
              <label class="font-medium">Unit yang Ditampilkan</label>
              <div v-for="unit in unitOptions" :key="unit.code" class="flex items-center gap-3 p-3 border rounded-lg">
                <Checkbox v-model="selectedSection.units" :value="unit.code" :inputId="'unit-' + unit.code" />
                <label :for="'unit-' + unit.code" class="cursor-pointer">
                  <div class="font-medium">{{ unit.name }}</div>
                  <div class="text-xs text-slate-400">{{ unit.desc }}</div>
                </label>
              </div>
            </div>
          </template>

          <!-- Timeline -->
          <template v-if="selectedSection.type === 'timeline'">
            <div class="space-y-3">
              <label class="font-medium">Tahapan Pendaftaran</label>
              <div v-for="(step, i) in selectedSection.steps" :key="i" class="flex items-start gap-3 p-3 border rounded-lg bg-slate-50 dark:bg-slate-800/50">
                <span class="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0">{{ i + 1 }}</span>
                <div class="flex-1 space-y-2">
                  <InputText v-model="step.label" placeholder="Nama tahapan" class="w-full" />
                  <InputText v-model="step.date" placeholder="Tanggal (misal: 1 - 30 Juni 2026)" class="w-full" />
                  <InputText v-model="step.description" placeholder="Deskripsi singkat (opsional)" class="w-full" />
                </div>
                <Button icon="pi pi-trash" severity="danger" text rounded size="small" @click="selectedSection.steps.splice(i, 1)" />
              </div>
              <Button label="Tambah Tahapan" icon="pi pi-plus" outlined severity="secondary" class="w-full" @click="selectedSection.steps.push({ label: '', date: '', description: '' })" />
            </div>
          </template>

        </div>

        <div v-else class="card bg-white dark:bg-slate-900 shadow-sm rounded-lg p-12 text-center text-slate-400">
          <i class="pi pi-arrow-left text-4xl mb-4"></i>
          <p>Pilih section di panel kiri untuk mengedit, atau tambahkan section baru.</p>
        </div>
      </div>
    </div>

    <!-- Add Section Dialog -->
    <Dialog v-model:visible="showAddSection" header="Tambah Section Baru" modal :style="{ width: '500px' }">
      <div class="space-y-2">
        <div
          v-for="type in sectionTypes"
          :key="type.value"
          class="flex items-center gap-4 p-4 border rounded-lg cursor-pointer hover:border-primary hover:bg-primary/5 transition"
          @click="addSection(type.value)"
        >
          <div class="w-10 h-10 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
            <i :class="type.icon" class="text-lg text-primary"></i>
          </div>
          <div>
            <div class="font-medium">{{ type.label }}</div>
            <div class="text-xs text-slate-400">{{ type.desc }}</div>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Preview Dialog -->
    <Dialog v-model:visible="showPreview" header="Preview Landing Page SPMB" modal maximizable :style="{ width: '90vw', maxWidth: '800px' }">
      <div class="bg-slate-50 dark:bg-slate-800 rounded-lg overflow-hidden">
        <template v-for="section in visibleSections" :key="section.id">
          <!-- Hero Carousel Preview -->
          <div v-if="section.type === 'hero_carousel'" class="bg-white dark:bg-slate-900">
            <div class="max-w-4xl mx-auto px-4 py-6">
              <div v-if="section.images?.filter((u: string) => u).length" class="space-y-2">
                <img v-for="(img, i) in section.images.filter((u: string) => u)" :key="i" :src="img" class="w-full rounded-xl object-cover" />
              </div>
              <div v-else class="aspect-[21/9] bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white text-2xl font-bold">
                {{ config.spmb_label || 'PPDB' }}
              </div>
            </div>
          </div>

          <!-- Stacked Image Preview -->
          <div v-if="section.type === 'stacked_image'">
            <div class="max-w-4xl mx-auto" :class="{ 'px-4': section.border_radius !== 'none' }">
              <h3 v-if="section.title" class="text-xl font-bold text-center py-4">{{ section.title }}</h3>
              <div :class="getStackedGapClass(section.gap)">
                <img
                  v-for="(img, i) in (section.images || []).filter((u: string) => u)"
                  :key="i"
                  :src="img"
                  class="w-full object-cover"
                  :class="getStackedRadiusClass(section.border_radius)"
                />
              </div>
            </div>
          </div>

          <!-- CTA Button Preview -->
          <div v-if="section.type === 'cta_button'" class="max-w-sm mx-auto px-4 py-6 space-y-3">
            <button class="w-full py-4 bg-indigo-600 text-white font-bold rounded-xl text-lg">
              <i class="pi pi-pencil mr-2"></i>{{ section.cta_label || 'Daftar Sekarang' }}
            </button>
            <button class="w-full py-4 bg-green-500 text-white font-bold rounded-xl text-lg">
              <i class="pi pi-whatsapp mr-2"></i>{{ section.wa_label || 'Tanya Admin (WA)' }}
            </button>
          </div>

          <!-- Info Text Preview -->
          <div v-if="section.type === 'info_text'" class="max-w-4xl mx-auto px-4 py-8">
            <h3 v-if="section.title" class="text-xl font-bold mb-4">{{ section.title }}</h3>
            <div class="prose dark:prose-invert" v-html="section.content || '<p class=\'text-slate-400\'>Belum ada konten...</p>'"></div>
          </div>

          <!-- Timeline Preview -->
          <div v-if="section.type === 'timeline'" class="max-w-4xl mx-auto px-4 py-8">
            <h3 v-if="section.title" class="text-xl font-bold text-center mb-8">{{ section.title }}</h3>
            <div class="space-y-4">
              <div v-for="(step, i) in (section.steps || [])" :key="i" class="flex items-start gap-4">
                <div class="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center font-bold shrink-0">{{ i + 1 }}</div>
                <div class="flex-1 pb-4 border-b border-slate-200 dark:border-slate-700">
                  <div class="font-bold">{{ step.label || 'Tahapan ' + (i + 1) }}</div>
                  <div v-if="step.date" class="text-sm text-primary font-medium">{{ step.date }}</div>
                  <div v-if="step.description" class="text-sm text-slate-500 mt-1">{{ step.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Unit Cards Preview -->
          <div v-if="section.type === 'unit_cards'" class="max-w-4xl mx-auto px-4 py-8">
            <h3 v-if="section.title" class="text-xl font-bold text-center mb-6">{{ section.title }}</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div v-for="code in (section.units || [])" :key="code" class="p-6 bg-white dark:bg-slate-800 rounded-xl border text-center">
                <div class="text-2xl font-bold text-primary mb-2">{{ unitOptions.find(u => u.code === code)?.name || code }}</div>
                <div class="text-sm text-slate-500">{{ unitOptions.find(u => u.code === code)?.desc || '' }}</div>
              </div>
            </div>
          </div>
        </template>

        <div v-if="visibleSections.length === 0" class="p-12 text-center text-slate-400">
          <p>Belum ada section yang aktif.</p>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({
  layout: 'dashboard'
})

const toast = useToast()
const api = useApi()

const saving = ref(false)
const showAddSection = ref(false)
const showPreview = ref(false)
const selectedIndex = ref<number | null>(null)

// Section types available
const sectionTypes = [
  { value: 'hero_carousel', label: 'Hero Carousel', icon: 'pi pi-images', desc: 'Slider poster/banner di bagian atas' },
  { value: 'stacked_image', label: 'Stacked Image', icon: 'pi pi-th-large', desc: 'Gambar dari tim desain yang di-stack vertikal' },
  { value: 'cta_button', label: 'Tombol CTA', icon: 'pi pi-bolt', desc: 'Tombol Daftar Sekarang & WhatsApp' },
  { value: 'info_text', label: 'Info Teks', icon: 'pi pi-align-left', desc: 'Teks informasi (syarat, biaya, dll)' },
  { value: 'timeline', label: 'Timeline Pendaftaran', icon: 'pi pi-list-check', desc: 'Alur/tahapan pendaftaran' },
  { value: 'unit_cards', label: 'Card Unit', icon: 'pi pi-th-large', desc: 'Kartu unit pendidikan (RA/SDIT/SMPIT)' },
]

const themeColors = [
  { value: 'indigo', hex: '#4F46E5' },
  { value: 'blue', hex: '#2563EB' },
  { value: 'green', hex: '#16A34A' },
  { value: 'teal', hex: '#0D9488' },
  { value: 'purple', hex: '#7C3AED' },
  { value: 'rose', hex: '#E11D48' },
]

const gapOptions = [
  { label: 'Tanpa Gap', value: 'none' },
  { label: 'Kecil (4px)', value: 'small' },
  { label: 'Sedang (16px)', value: 'medium' },
]

const borderRadiusOptions = [
  { label: 'Tanpa Radius', value: 'none' },
  { label: 'Rounded (8px)', value: 'rounded' },
  { label: 'Full Rounded (16px)', value: 'full-rounded' },
]

const unitOptions = [
  { code: 'RA', name: 'RA (TK Islam)', desc: 'Raudhatul Athfal' },
  { code: 'SDIT', name: 'SDIT', desc: 'Sekolah Dasar Islam Terpadu' },
  { code: 'SMPIT', name: 'SMPIT', desc: 'Sekolah Menengah Pertama Islam Terpadu' },
]

interface SectionStep {
  label: string
  date: string
  description: string
}

interface LPSection {
  id: string
  type: string
  title: string
  visible: boolean
  images: string[]
  content: string
  cta_label: string
  wa_label: string
  units: string[]
  steps: SectionStep[]
  gap: string
  border_radius: string
}

interface LPConfig {
  sections: LPSection[]
  spmb_label: string
  theme_color: string
  wa_number: string
}

const config = ref<LPConfig>({
  sections: [],
  spmb_label: 'PPDB',
  theme_color: 'indigo',
  wa_number: '6281234567890',
})

const selectedSection = computed(() => {
  if (selectedIndex.value !== null && selectedIndex.value < config.value.sections.length) {
    return config.value.sections[selectedIndex.value]
  }
  return null
})

const visibleSections = computed(() => config.value.sections.filter(s => s.visible))

function generateId() {
  return 's_' + Math.random().toString(36).substring(2, 9)
}

function addSection(type: string) {
  const newSection: LPSection = {
    id: generateId(),
    type,
    title: '',
    visible: true,
    images: type === 'hero_carousel' || type === 'stacked_image' ? [''] : [],
    content: '',
    cta_label: 'Daftar Sekarang',
    wa_label: 'Tanya Admin (WA)',
    units: ['RA', 'SDIT', 'SMPIT'],
    steps: type === 'timeline' ? [{ label: '', date: '', description: '' }] : [],
    gap: 'none',
    border_radius: 'none',
  }
  config.value.sections.push(newSection)
  selectedIndex.value = config.value.sections.length - 1
  showAddSection.value = false
}

function removeSection(index: number) {
  config.value.sections.splice(index, 1)
  if (selectedIndex.value === index) {
    selectedIndex.value = config.value.sections.length > 0 ? 0 : null
  } else if (selectedIndex.value !== null && selectedIndex.value > index) {
    selectedIndex.value--
  }
}

function moveSection(index: number, direction: number) {
  const target = index + direction
  if (target < 0 || target >= config.value.sections.length) return
  const sections = config.value.sections
  const temp = sections[index]
  sections[index] = sections[target]
  sections[target] = temp
  if (selectedIndex.value === index) {
    selectedIndex.value = target
  } else if (selectedIndex.value === target) {
    selectedIndex.value = index
  }
}

function getSectionLabel(type: string) {
  return sectionTypes.find(t => t.value === type)?.label || type
}

function getSectionIcon(type: string) {
  return sectionTypes.find(t => t.value === type)?.icon || 'pi pi-box'
}

function getStackedGapClass(gap: string) {
  switch (gap) {
    case 'small': return 'flex flex-col gap-1'
    case 'medium': return 'flex flex-col gap-4'
    default: return 'flex flex-col'
  }
}

function getStackedRadiusClass(radius: string) {
  switch (radius) {
    case 'rounded': return 'rounded-lg'
    case 'full-rounded': return 'rounded-2xl'
    default: return ''
  }
}

// Load config
async function loadConfig() {
  try {
    const data = await api.get<any>('/public/content/settings_ppdb')
    if (data && data.content_json) {
      const parsed = JSON.parse(data.content_json)
      // Merge LP config if it exists
      if (parsed.lp_config) {
        config.value = { ...config.value, ...parsed.lp_config }
      }
      // Also load wa_number from parent settings
      if (parsed.wa_number) {
        config.value.wa_number = parsed.wa_number
      }
    }
  } catch (e) {
    // Default config if not found
  }
}

// Save config — merge into existing settings_ppdb
async function saveConfig() {
  saving.value = true
  try {
    // Load existing settings first to preserve posters etc.
    let existingSettings: any = {}
    try {
      const data = await api.get<any>('/public/content/settings_ppdb')
      if (data && data.content_json) {
        existingSettings = JSON.parse(data.content_json)
      }
    } catch (e) {
      // no existing settings
    }

    // Merge LP config into existing settings
    existingSettings.lp_config = {
      sections: config.value.sections,
      spmb_label: config.value.spmb_label,
      theme_color: config.value.theme_color,
    }
    existingSettings.wa_number = config.value.wa_number

    await api.put('/cms/content/settings_ppdb', {
      content_json: JSON.stringify(existingSettings)
    })

    toast.add({ severity: 'success', summary: 'Tersimpan', detail: 'Konfigurasi Landing Page berhasil disimpan', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Terjadi kesalahan saat menyimpan', life: 3000 })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadConfig()
})
</script>
