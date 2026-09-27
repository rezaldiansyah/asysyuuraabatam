<template>
  <div class="space-y-3">
    <div v-if="items.length === 0" class="text-center py-6 text-slate-400">
      <i class="pi pi-check-circle text-2xl mb-1 block"></i>
      <p class="text-xs">Belum ada tindak lanjut (action items) untuk rapat ini.</p>
    </div>

    <div v-else class="space-y-2">
      <div 
        v-for="item in items" 
        :key="item.id"
        class="p-3.5 rounded-xl border transition-all"
        :class="item.status === 'done' ? 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700 opacity-80' : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 shadow-sm'"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3 flex-1 min-w-0">
            <!-- Quick Toggle Status Checkbox -->
            <button 
              @click="toggleItemStatus(item)" 
              class="mt-0.5 w-5 h-5 rounded flex items-center justify-center transition border"
              :class="item.status === 'done' ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-300 dark:border-slate-600 hover:border-emerald-500'"
              :title="item.status === 'done' ? 'Tandai belum selesai' : 'Tandai selesai'"
            >
              <i v-if="item.status === 'done'" class="pi pi-check text-xs"></i>
            </button>

            <div class="flex-1 min-w-0">
              <p 
                class="text-sm font-medium text-slate-800 dark:text-white"
                :class="{ 'line-through text-slate-400 dark:text-slate-500': item.status === 'done' }"
              >
                {{ item.task_description }}
              </p>

              <div class="flex items-center gap-2 flex-wrap text-xs text-slate-500 mt-1.5">
                <span class="inline-flex items-center gap-1 font-medium text-slate-700 dark:text-slate-300">
                  <i class="pi pi-user text-[10px] text-primary"></i> PIC: {{ item.pic_name || '-' }}
                </span>

                <span v-if="item.deadline" class="inline-flex items-center gap-1" :class="isOverdue(item) ? 'text-red-500 font-bold' : 'text-slate-500'">
                  <i class="pi pi-calendar text-[10px]"></i> 
                  Deadline: {{ formatDate(item.deadline) }}
                </span>

                <Tag 
                  v-if="isOverdue(item)" 
                  value="Terlewat" 
                  severity="danger" 
                  class="text-[9px] px-1.5 py-0" 
                />

                <span v-if="item.completion_date" class="text-emerald-600 text-[10px]">
                  ✓ Selesai: {{ formatDate(item.completion_date) }}
                </span>
              </div>

              <!-- Notes -->
              <p v-if="item.notes" class="text-xs text-slate-400 mt-1.5 italic bg-slate-50 dark:bg-slate-750 p-1.5 rounded">
                Catatan: {{ item.notes }}
              </p>
            </div>
          </div>

          <!-- Status Selector Dropdown -->
          <div class="flex-shrink-0">
            <Select 
              v-model="item.status" 
              :options="statusOptions" 
              optionLabel="label" 
              optionValue="value" 
              class="!text-xs w-36"
              @change="updateStatus(item)"
            >
              <template #value="slotProps">
                <Tag :value="getStatusLabel(slotProps.value)" :severity="getStatusSeverity(slotProps.value)" class="text-[10px]" />
              </template>
              <template #option="slotProps">
                <Tag :value="slotProps.option.label" :severity="slotProps.option.severity" class="text-[10px]" />
              </template>
            </Select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  items: any[]
}>()

const emit = defineEmits(['updated'])
const api = useApi()

const statusOptions = [
  { value: 'pending', label: 'Menunggu', severity: 'secondary' },
  { value: 'in_progress', label: 'Sedang Berjalan', severity: 'warn' },
  { value: 'done', label: 'Selesai', severity: 'success' },
]

function getStatusLabel(val: string) {
  const map: Record<string, string> = {
    pending: 'Menunggu',
    in_progress: 'Sedang Berjalan',
    done: 'Selesai'
  }
  return map[val] || val
}

function getStatusSeverity(val: string) {
  const map: Record<string, string> = {
    pending: 'secondary',
    in_progress: 'warn',
    done: 'success'
  }
  return map[val] || 'secondary'
}

function isOverdue(item: any): boolean {
  if (!item.deadline || item.status === 'done') return false
  return new Date(item.deadline) < new Date()
}

function formatDate(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function updateStatus(item: any) {
  try {
    await api.put(`/meeting/action-items/${item.id}`, { status: item.status })
    emit('updated')
  } catch (e) {
    console.error('Failed to update action item status', e)
  }
}

async function toggleItemStatus(item: any) {
  item.status = item.status === 'done' ? 'pending' : 'done'
  await updateStatus(item)
}
</script>
