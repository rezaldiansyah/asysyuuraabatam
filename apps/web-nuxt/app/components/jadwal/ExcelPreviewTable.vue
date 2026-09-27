<template>
  <div class="space-y-4">
    <!-- Stat Counter Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div 
        @click="filterStatus = 'ALL'"
        class="p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between"
        :class="filterStatus === 'ALL' ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300'"
      >
        <div>
          <div class="text-xs text-slate-500 font-medium">Total Baris</div>
          <div class="text-2xl font-bold text-slate-800 dark:text-white mt-1">{{ totalCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300">
          <i class="pi pi-list"></i>
        </div>
      </div>

      <div 
        @click="filterStatus = 'VALID'"
        class="p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between"
        :class="filterStatus === 'VALID' ? 'border-green-500 bg-green-50/50 dark:bg-green-950/20 ring-2 ring-green-500/20' : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300'"
      >
        <div>
          <div class="text-xs text-green-600 dark:text-green-400 font-medium">Siap Diimpor (Valid)</div>
          <div class="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">{{ validCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600">
          <i class="pi pi-check-circle"></i>
        </div>
      </div>

      <div 
        @click="filterStatus = 'CONFLICT'"
        class="p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between"
        :class="filterStatus === 'CONFLICT' ? 'border-amber-500 bg-amber-50/50 dark:bg-amber-950/20 ring-2 ring-amber-500/20' : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300'"
      >
        <div>
          <div class="text-xs text-amber-600 dark:text-amber-400 font-medium">Bentrok / Konflik</div>
          <div class="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">{{ conflictCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center text-amber-600">
          <i class="pi pi-exclamation-triangle"></i>
        </div>
      </div>

      <div 
        @click="filterStatus = 'ERROR'"
        class="p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between"
        :class="filterStatus === 'ERROR' ? 'border-red-500 bg-red-50/50 dark:bg-red-950/20 ring-2 ring-red-500/20' : 'border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300'"
      >
        <div>
          <div class="text-xs text-red-600 dark:text-red-400 font-medium">Format Error</div>
          <div class="text-2xl font-bold text-red-600 dark:text-red-400 mt-1">{{ errorCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-lg bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600">
          <i class="pi pi-times-circle"></i>
        </div>
      </div>
    </div>

    <!-- Filter Buttons Bar -->
    <div class="flex flex-wrap items-center justify-between gap-2 pt-2">
      <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg text-xs">
        <button 
          v-for="btn in filterButtons" 
          :key="btn.value"
          @click="filterStatus = btn.value"
          class="px-3 py-1.5 rounded-md font-medium transition-all"
          :class="filterStatus === btn.value ? 'bg-white dark:bg-slate-700 shadow-sm text-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-800'"
        >
          {{ btn.label }}
        </button>
      </div>

      <div class="text-xs text-slate-400">
        Menampilkan {{ filteredRows.length }} dari {{ rows.length }} baris
      </div>
    </div>

    <!-- Table -->
    <div class="border rounded-xl overflow-hidden border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-sm">
      <DataTable :value="filteredRows" stripedRows class="p-datatable-sm text-xs" paginator :rows="15">
        <template #empty>
          <div class="text-center py-8 text-slate-400">
            Tidak ada data baris jadwal yang sesuai filter.
          </div>
        </template>

        <Column field="row_index" header="Baris" style="width: 70px" class="font-mono text-center">
          <template #body="{ data }">#{{ data.row_index }}</template>
        </Column>

        <Column field="day" header="Hari" style="width: 100px">
          <template #body="{ data }">
            <span class="font-semibold">{{ data.day || '-' }}</span>
          </template>
        </Column>

        <Column header="Jam" style="width: 110px">
          <template #body="{ data }">
            <span class="font-mono">{{ data.start_time }} - {{ data.end_time }}</span>
          </template>
        </Column>

        <Column field="classroom_name" header="Kelas" style="min-width: 120px">
          <template #body="{ data }">
            <div :class="!data.classroom_id ? 'text-red-500 font-semibold' : 'text-slate-800 dark:text-white'">
              {{ data.classroom_name || '-' }}
            </div>
          </template>
        </Column>

        <Column field="subject_name" header="Mata Pelajaran" style="min-width: 140px">
          <template #body="{ data }">
            <div :class="!data.subject_id ? 'text-red-500 font-semibold' : 'text-slate-800 dark:text-white'">
              {{ data.subject_name || '-' }}
            </div>
          </template>
        </Column>

        <Column field="teacher_name" header="Guru" style="min-width: 160px">
          <template #body="{ data }">
            <div :class="!data.teacher_id ? 'text-red-500 font-semibold' : 'text-slate-800 dark:text-white'">
              {{ data.teacher_name || '-' }}
            </div>
            <div v-if="data.teacher_nik" class="text-[10px] text-slate-400 font-mono">
              NIK: {{ data.teacher_nik }}
            </div>
          </template>
        </Column>

        <Column header="Status" style="width: 110px">
          <template #body="{ data }">
            <Tag 
              :value="data.status === 'VALID' ? 'Valid' : data.status === 'CONFLICT' ? 'Bentrok' : 'Error'" 
              :severity="data.status === 'VALID' ? 'success' : data.status === 'CONFLICT' ? 'warn' : 'danger'"
              class="text-[11px] px-2 py-0.5"
            />
          </template>
        </Column>

        <Column header="Catatan Validasi" style="min-width: 240px">
          <template #body="{ data }">
            <div v-if="data.errors && data.errors.length > 0" class="space-y-1">
              <div v-for="(err, idx) in data.errors" :key="'e-' + idx" class="text-red-500 flex items-start gap-1">
                <i class="pi pi-times-circle text-[10px] mt-0.5"></i>
                <span>{{ err }}</span>
              </div>
            </div>
            <div v-else-if="data.conflicts && data.conflicts.length > 0" class="space-y-1">
              <div v-for="(cnf, idx) in data.conflicts" :key="'c-' + idx" class="text-amber-600 dark:text-amber-400 flex items-start gap-1">
                <i class="pi pi-exclamation-triangle text-[10px] mt-0.5"></i>
                <span>{{ cnf }}</span>
              </div>
            </div>
            <div v-else class="text-green-600 dark:text-green-400 flex items-center gap-1">
              <i class="pi pi-check text-[10px]"></i>
              <span>Siap diimpor</span>
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface PreviewRow {
  row_index: number
  day: string
  start_time: string
  end_time: string
  classroom_name: string
  classroom_id: number | null
  subject_name: string
  subject_id: number | null
  teacher_name: string
  teacher_nik: string
  teacher_id: number | null
  notes?: string
  status: 'VALID' | 'CONFLICT' | 'ERROR'
  errors: string[]
  conflicts: string[]
}

const props = defineProps<{
  rows: PreviewRow[]
  totalCount: number
  validCount: number
  conflictCount: number
  errorCount: number
}>()

const filterStatus = ref<'ALL' | 'VALID' | 'CONFLICT' | 'ERROR'>('ALL')

const filterButtons = [
  { label: 'Semua Baris', value: 'ALL' },
  { label: 'Hanya Valid', value: 'VALID' },
  { label: 'Hanya Bentrok', value: 'CONFLICT' },
  { label: 'Hanya Error', value: 'ERROR' },
]

const filteredRows = computed(() => {
  if (filterStatus.value === 'ALL') return props.rows
  return props.rows.filter(r => r.status === filterStatus.value)
})
</script>
