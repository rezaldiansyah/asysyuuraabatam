<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Notulen Rapat Digital</h1>
        <p class="text-slate-500 text-sm mt-1">Dokumentasi hasil rapat, pengesahan pimpinan, dan pelacakan tindak lanjut tugas (*action items*).</p>
      </div>
      <div class="flex items-center gap-2">
        <NuxtLink to="/dashboard/internal/notulen/buat">
          <Button label="Tulis Notulen Baru" icon="pi pi-plus" class="p-button-primary shadow-sm" />
        </NuxtLink>
      </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-lg">
          <i class="pi pi-book"></i>
        </div>
        <div>
          <p class="text-xs text-slate-500">Total Notulen</p>
          <p class="text-xl font-bold text-slate-800 dark:text-white mt-0.5">{{ minutes.length }}</p>
        </div>
      </div>

      <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-lg bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center text-lg">
          <i class="pi pi-clock"></i>
        </div>
        <div>
          <p class="text-xs text-slate-500">Menunggu Approval</p>
          <p class="text-xl font-bold text-amber-600 dark:text-amber-400 mt-0.5">{{ countByStatus('submitted') }}</p>
        </div>
      </div>

      <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center text-lg">
          <i class="pi pi-check-circle"></i>
        </div>
        <div>
          <p class="text-xs text-slate-500">Disahkan / Terbit</p>
          <p class="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">{{ countByStatus('approved') }}</p>
        </div>
      </div>

      <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-lg bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center text-lg">
          <i class="pi pi-list-check"></i>
        </div>
        <div>
          <p class="text-xs text-slate-500">Tugas Tindak Lanjut</p>
          <p class="text-xl font-bold text-purple-600 dark:text-purple-400 mt-0.5">{{ totalPendingActions }}</p>
        </div>
      </div>
    </div>

    <!-- Filter & Tabs Bar -->
    <div class="card p-4 space-y-4">
      <!-- Tabs -->
      <div class="flex items-center gap-2 border-b border-slate-200 dark:border-slate-700 pb-3 flex-wrap">
        <button
          v-for="tab in tabOptions"
          :key="tab.value"
          @click="activeTab = tab.value"
          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition"
          :class="activeTab === tab.value ? 'bg-primary text-white shadow-sm' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'"
        >
          <i :class="tab.icon" class="mr-1.5 text-[11px]"></i> {{ tab.label }}
          <span v-if="tab.badge" class="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-white/20">{{ tab.badge }}</span>
        </button>
      </div>

      <!-- Filters (only in all & approval tabs) -->
      <div v-if="activeTab !== 'my_tasks'" class="flex flex-col md:flex-row gap-3">
        <div class="relative flex-1">
          <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
          <InputText 
            v-model="searchQuery" 
            placeholder="Cari judul rapat, nomor notulen, lokasi..." 
            class="w-full !pl-9"
            @input="debouncedFetch"
          />
        </div>

        <Select 
          v-model="filterScope" 
          :options="scopeOptions" 
          optionLabel="label" 
          optionValue="value" 
          placeholder="Cakupan Rapat" 
          class="w-full md:w-52"
          @change="fetchMinutes"
        />

        <Select 
          v-model="filterStatus" 
          :options="statusFilterOptions" 
          optionLabel="label" 
          optionValue="value" 
          placeholder="Status Approval" 
          class="w-full md:w-52"
          @change="fetchMinutes"
        />
      </div>
    </div>

    <!-- View Mode 1: Table of Minutes -->
    <div v-if="activeTab !== 'my_tasks'" class="card">
      <DataTable :value="filteredMinutes" :loading="loading" stripedRows responsiveLayout="scroll" class="text-sm">
        <Column header="Rapat & Nomor Notulen" style="min-width: 320px">
          <template #body="{ data }">
            <div class="space-y-1">
              <div class="flex items-center gap-2 flex-wrap">
                <span v-if="data.nomor_notulen" class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-mono font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                  #{{ data.nomor_notulen }}
                </span>
                <NuxtLink :to="`/dashboard/internal/notulen/${data.id}`">
                  <span class="font-bold text-slate-800 dark:text-white hover:text-primary transition cursor-pointer">
                    {{ data.title }}
                  </span>
                </NuxtLink>
              </div>
              <div class="flex items-center gap-2 text-xs text-slate-400 flex-wrap">
                <span><i class="pi pi-calendar text-[10px]"></i> {{ formatDate(data.meeting_date) }}</span>
                <span v-if="data.start_time">· {{ data.start_time }} s/d {{ data.end_time || '-' }}</span>
                <span v-if="data.location">· <i class="pi pi-map-marker text-[10px]"></i> {{ data.location }}</span>
              </div>
            </div>
          </template>
        </Column>

        <Column header="Cakupan / Unit" style="min-width: 140px">
          <template #body="{ data }">
            <Tag 
              :value="data.scope === 'yayasan_global' ? 'Yayasan / Global' : (data.unit_name || 'Unit')" 
              :severity="data.scope === 'yayasan_global' ? 'success' : 'info'" 
              class="text-xs"
            />
          </template>
        </Column>

        <Column header="Status" style="min-width: 150px">
          <template #body="{ data }">
            <Tag 
              :value="getStatusText(data.status)" 
              :severity="getStatusSeverity(data.status)" 
              class="text-xs font-semibold"
            />
          </template>
        </Column>

        <Column header="Notulis & Pengesah" style="min-width: 160px">
          <template #body="{ data }">
            <div class="text-xs space-y-0.5">
              <p class="text-slate-600 dark:text-slate-300"><span class="text-slate-400">Notulis:</span> {{ data.notulis_name || '-' }}</p>
              <p v-if="data.approver_name" class="text-slate-600 dark:text-slate-300">
                <span class="text-slate-400">Pengesah:</span> <strong class="text-emerald-600 dark:text-emerald-400">{{ data.approver_name }}</strong>
              </p>
            </div>
          </template>
        </Column>

        <Column header="Tindak Lanjut" style="min-width: 120px">
          <template #body="{ data }">
            <div v-if="data.action_items_count?.total > 0" class="flex items-center gap-1.5 text-xs">
              <span 
                class="px-2 py-0.5 rounded-full font-bold text-[10px]"
                :class="data.action_items_count.pending === 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
              >
                {{ data.action_items_count.done }} / {{ data.action_items_count.total }} Selesai
              </span>
            </div>
            <span v-else class="text-xs text-slate-400">-</span>
          </template>
        </Column>

        <Column header="Aksi" style="min-width: 160px">
          <template #body="{ data }">
            <div class="flex items-center gap-1">
              <NuxtLink :to="`/dashboard/internal/notulen/${data.id}`" class="p-2 text-primary hover:bg-primary/10 rounded-lg transition" title="Lihat Notulen">
                <i class="pi pi-eye"></i>
              </NuxtLink>
              <a 
                :href="`${apiBase}/meeting/minutes/${data.id}/export-pdf`" 
                target="_blank" 
                class="p-2 text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30 rounded-lg transition" 
                title="Download PDF Resmi"
              >
                <i class="pi pi-file-pdf"></i>
              </a>
              <button 
                v-if="canDelete(data)" 
                @click="deleteMinute(data)" 
                class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition" 
                title="Hapus"
              >
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </template>
        </Column>

        <template #empty>
          <div class="text-center py-10 text-slate-400">
            <i class="pi pi-inbox text-4xl mb-3 block"></i>
            <p>Tidak ada notulen rapat yang ditemukan.</p>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- View Mode 2: Personal Action Items Tracker -->
    <div v-else class="card p-5 space-y-4">
      <div class="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-3">
        <div>
          <h2 class="font-bold text-base text-slate-800 dark:text-white">Tugas & Tindak Lanjut Rapat Saya</h2>
          <p class="text-xs text-slate-500">Daftar tugas yang diamanahkan kepada Anda dari berbagai hasil rapat.</p>
        </div>
        <Button label="Segarkan" icon="pi pi-refresh" severity="secondary" size="small" @click="fetchMyActionItems" />
      </div>

      <div v-if="loadingActions" class="text-center py-8 text-slate-400">
        <i class="pi pi-spin pi-spinner text-2xl mb-2"></i>
        <p class="text-xs">Memuat daftar tugas...</p>
      </div>

      <div v-else>
        <InternalActionItemTracker :items="myActionItems" @updated="fetchMyActionItems" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const authStore = useAuthStore()

const loading = ref(false)
const minutes = ref<any[]>([])
const activeTab = ref<'all' | 'waiting' | 'my_tasks'>('all')

const searchQuery = ref('')
const filterScope = ref('')
const filterStatus = ref('')

const myActionItems = ref<any[]>([])
const loadingActions = ref(false)

const tabOptions = computed(() => [
  { value: 'all', label: 'Semua Notulen', icon: 'pi pi-folder' },
  { value: 'waiting', label: 'Menunggu Persetujuan', icon: 'pi pi-clock', badge: countByStatus('submitted') || undefined },
  { value: 'my_tasks', label: 'Tugas Saya', icon: 'pi pi-check-square', badge: totalPendingActions.value || undefined },
])

const scopeOptions = [
  { value: '', label: 'Semua Cakupan' },
  { value: 'yayasan_global', label: 'Yayasan / Seluruh Unit' },
  { value: 'unit', label: 'Tingkat Unit' },
]

const statusFilterOptions = [
  { value: '', label: 'Semua Status' },
  { value: 'draft', label: 'Draf' },
  { value: 'submitted', label: 'Menunggu Persetujuan' },
  { value: 'approved', label: 'Disahkan' },
  { value: 'rejected', label: 'Perlu Revisi' },
]

const filteredMinutes = computed(() => {
  if (activeTab.value === 'waiting') {
    return minutes.value.filter(m => m.status === 'submitted')
  }
  return minutes.value
})

const totalPendingActions = computed(() => {
  return myActionItems.value.filter(ai => ai.status !== 'done').length
})

function countByStatus(status: string) {
  return minutes.value.filter(m => m.status === status).length
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    draft: 'Draf',
    submitted: 'Menunggu Persetujuan',
    approved: 'Disahkan',
    rejected: 'Perlu Revisi',
    archived: 'Diarsipkan'
  }
  return map[status] || status
}

function getStatusSeverity(status: string) {
  const map: Record<string, string> = {
    draft: 'secondary',
    submitted: 'warn',
    approved: 'success',
    rejected: 'danger',
    archived: 'secondary'
  }
  return map[status] || 'secondary'
}

function formatDate(iso: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

function canDelete(doc: any) {
  const user = authStore.user
  if (!user) return false
  const roleCode = user.role?.code || ''
  return ['superadmin', 'ketua_yayasan'].includes(roleCode) || (doc.notulis_id === user.id && ['draft', 'rejected'].includes(doc.status))
}

let debounceTimer: any = null
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchMinutes()
  }, 300)
}

async function fetchMinutes() {
  loading.value = true
  try {
    let url = '/meeting/minutes?'
    if (filterScope.value) url += `scope=${filterScope.value}&`
    if (filterStatus.value) url += `status=${filterStatus.value}&`
    if (searchQuery.value) url += `search=${encodeURIComponent(searchQuery.value)}&`
    minutes.value = await api.get<any[]>(url)
  } catch (e) {
    console.error('Failed to fetch minutes', e)
  } finally {
    loading.value = false
  }
}

async function fetchMyActionItems() {
  loadingActions.value = true
  try {
    myActionItems.value = await api.get<any[]>('/meeting/action-items/my')
  } catch (e) {
    console.error('Failed to fetch my action items', e)
  } finally {
    loadingActions.value = false
  }
}

async function deleteMinute(doc: any) {
  if (!confirm(`Hapus notulen "${doc.title}"?`)) return
  try {
    await api.delete(`/meeting/minutes/${doc.id}`)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Notulen berhasil dihapus', life: 3000 })
    await fetchMinutes()
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus notulen', life: 3000 })
  }
}

onMounted(async () => {
  await Promise.all([fetchMinutes(), fetchMyActionItems()])
})
</script>
