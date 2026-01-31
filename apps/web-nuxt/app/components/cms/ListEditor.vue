<template>
  <div class="space-y-4">
    <div v-for="(item, index) in items" :key="item.id" class="border border-slate-200 dark:border-slate-700 rounded-xl p-4 bg-white dark:bg-slate-800">
      <!-- Header -->
      <div class="flex justify-between items-center mb-4 pb-2 border-b border-slate-100 dark:border-slate-700">
        <h4 class="font-medium text-sm text-slate-500">Item #{{ index + 1 }}</h4>
        <div class="flex gap-1">
          <Button icon="pi pi-arrow-up" text rounded size="small" :disabled="index === 0" @click="moveItem(index, -1)" />
          <Button icon="pi pi-arrow-down" text rounded size="small" :disabled="index === items.length - 1" @click="moveItem(index, 1)" />
          <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="removeItem(index)" />
        </div>
      </div>

      <!-- Content -->
      <div class="grid gap-4">
        <!-- Title -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700 dark:text-slate-300">{{ titleLabel }}</label>
          <InputText v-model="item.title" @input="emitUpdate" placeholder="Judul item..." />
        </div>

        <!-- Description -->
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700 dark:text-slate-300">{{ descLabel }}</label>
          <Textarea v-model="item.description" rows="3" @input="emitUpdate" placeholder="Deskripsi..." />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Icon Selection -->
          <div v-if="withIcon" class="flex flex-col gap-2">
            <label class="text-sm font-medium text-slate-700 dark:text-slate-300">Icon</label>
            <Select 
              v-model="item.icon" 
              :options="iconOptions" 
              optionLabel="label" 
              optionValue="value" 
              placeholder="Pilih Icon"
              @change="emitUpdate"
              class="w-full"
            >
              <template #value="slotProps">
                <div v-if="slotProps.value" class="flex items-center gap-2">
                  <span>{{ getIconEmoji(slotProps.value) }}</span>
                  <span>{{ slotProps.value }}</span>
                </div>
                <span v-else>{{ slotProps.placeholder }}</span>
              </template>
              <template #option="slotProps">
                <div class="flex items-center gap-2">
                  <span>{{ getIconEmoji(slotProps.option.value) }}</span>
                  <span>{{ slotProps.option.label }}</span>
                </div>
              </template>
            </Select>
          </div>

          <!-- Image URL -->
          <div class="flex flex-col gap-2">
            <label class="text-sm font-medium text-slate-700 dark:text-slate-300">{{ imageLabel }}</label>
            <InputText v-model="item.image_url" @input="emitUpdate" placeholder="https://..." />
          </div>
        </div>
      </div>
    </div>

    <!-- Add Button -->
    <Button label="Tambah Item Baru" icon="pi pi-plus" class="w-full" outlined severity="secondary" @click="addItem" />
  </div>
</template>

<script setup lang="ts">
interface ListItem {
  id: string
  title: string
  description: string
  image_url?: string
  icon?: string
}

const props = defineProps({
  modelValue: {
    type: String, // Expecting JSON string
    default: '[]'
  },
  titleLabel: { type: String, default: 'Judul' },
  descLabel: { type: String, default: 'Deskripsi' },
  imageLabel: { type: String, default: 'Image URL' },
  withIcon: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])

const items = ref<ListItem[]>([])

// Sync internal state with prop
watch(() => props.modelValue, (newVal) => {
  try {
    const parsed = JSON.parse(newVal || '[]')
    if (Array.isArray(parsed)) {
      // Only update if different to avoid cursor jumps / loops
      if (JSON.stringify(parsed) !== JSON.stringify(items.value)) {
        items.value = parsed.map(p => ({ ...p, id: p.id || String(Date.now() + Math.random()) }))
      }
    }
  } catch (e) {
    console.error('Failed to parse JSON', e)
    items.value = []
  }
}, { immediate: true })

function emitUpdate() {
  emit('update:modelValue', JSON.stringify(items.value))
}

function addItem() {
  items.value.push({
    id: String(Date.now()),
    title: '',
    description: '',
    icon: 'CheckCircle',
    image_url: ''
  })
  emitUpdate()
}

function removeItem(index: number) {
  items.value.splice(index, 1)
  emitUpdate()
}

function moveItem(index: number, direction: number) {
  const newIndex = index + direction
  if (newIndex >= 0 && newIndex < items.value.length) {
    const temp = items.value[index]
    items.value[index] = items.value[newIndex]
    items.value[newIndex] = temp
    emitUpdate()
  }
}

const iconOptions = [
  { value: "BookOpen", label: "Buku/Pendidikan" },
  { value: "Heart", label: "Hati/Karakter" },
  { value: "Sun", label: "Matahari/Tahfidz" },
  { value: "Users", label: "Orang/Pengajar" },
  { value: "Trophy", label: "Piala/Prestasi" },
  { value: "ShieldCheck", label: "Perisai/Aman" },
  { value: "Star", label: "Bintang" },
  { value: "Sparkles", label: "Kilau" },
  { value: "CheckCircle", label: "Centang" },
]

function getIconEmoji(iconName: string) {
  const map: Record<string, string> = {
    BookOpen: '📖',
    Heart: '❤️',
    Sun: '☀️',
    Users: '👥',
    Trophy: '🏆',
    ShieldCheck: '🛡️',
    Star: '⭐',
    Sparkles: '✨',
    CheckCircle: '✅'
  }
  return map[iconName] || '🔹'
}
</script>
