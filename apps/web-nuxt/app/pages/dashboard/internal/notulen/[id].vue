<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-12">
    <!-- Top Action Bar -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/internal/notulen">
          <Button icon="pi pi-arrow-left" severity="secondary" rounded text />
        </NuxtLink>
        <div>
          <div class="flex items-center gap-2 flex-wrap">
            <span v-if="minute?.nomor_notulen" class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              #{{ minute.nomor_notulen }}
            </span>
            <Tag :value="getStatusText(minute?.status)" :severity="getStatusSeverity(minute?.status)" class="text-xs" />
          </div>
          <h1 class="text-xl md:text-2xl font-bold text-slate-800 dark:text-white mt-1">
            {{ minute?.title || 'Memuat Notulen...' }}
          </h1>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <!-- PDF Export -->
        <a 
          v-if="minute" 
          :href="`${apiBase}/meeting/minutes/${minute.id}/export-pdf`" 
          target="_blank" 
          class="p-button p-component p-button-secondary inline-flex items-center gap-1.5 text-xs px-3 py-2 rounded-lg"
        >
          <i class="pi pi-file-pdf text-rose-500"></i> Unduh PDF Resmi
        </a>

        <!-- Submit for Approval (If Draft/Rejected) -->
        <Button 
          v-if="minute && ['draft', 'rejected'].includes(minute.status) && isNotulisOrAdmin" 
          label="Ajukan Pengesahan" 
          icon="pi pi-send" 
          severity="primary" 
          size="small"
          :loading="submitting" 
          @click="submitForApproval" 
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-16 text-slate-400">
      <i class="pi pi-spin pi-spinner text-3xl mb-3 block text-primary"></i>
      <p>Memuat rincian notulen rapat...</p>
    </div>

    <div v-else-if="minute" class="space-y-6">
      <!-- ALERT: Revision Needed (Rejected) -->
      <div v-if="minute.status === 'rejected'" class="p-4 rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/30 text-red-700 dark:text-red-300 space-y-1.5">
        <div class="flex items-center gap-2 font-bold text-sm">
          <i class="pi pi-exclamation-triangle text-red-500"></i>
          <span>Perlu Perbaikan / Revisi Notulen</span>
        </div>
        <p class="text-xs">
          <strong>Catatan Pimpinan ({{ minute.approver_name || 'Approver' }}):</strong>
          {{ minute.approval_notes }}
        </p>
      </div>

      <!-- APPROVAL ACTION BOX (For Leadership) -->
      <div 
        v-if="minute.status === 'submitted'" 
        class="p-4 rounded-xl border bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800 space-y-3"
      >
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div class="flex items-center gap-2 font-bold text-sm text-amber-800 dark:text-amber-300">
              <i class="pi pi-clock text-amber-600"></i>
              <span>Menunggu Pengesahan {{ minute.scope === 'yayasan_global' ? 'Ketua Yayasan' : 'Kepala Unit' }}</span>
            </div>
            <p class="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
              Notulen ini telah diajukan oleh notulis dan menunggu verifikasi serta persetujuan resmi.
            </p>
          </div>

          <!-- Buttons if authorized -->
          <div v-if="minute.can_approve" class="flex items-center gap-2 shrink-0">
            <Button 
              label="Minta Revisi" 
              icon="pi pi-times" 
              severity="danger" 
              outlined 
              size="small"
              @click="rejectDialogVisible = true" 
            />
            <Button 
              label="Setujui & Sahkan" 
              icon="pi pi-check" 
              severity="success" 
              size="small"
              :loading="approving" 
              @click="approveMinute" 
            />
          </div>
          <div v-else class="text-xs text-slate-400 italic">
            (Hanya pimpinan berwenang yang dapat mengesahkan)
          </div>
        </div>
      </div>

      <!-- SUCCESS STAMP (If Approved) -->
      <div v-if="minute.status === 'approved'" class="p-3.5 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50 dark:bg-emerald-950/20 flex items-center justify-between flex-wrap gap-2 text-xs text-emerald-800 dark:text-emerald-300">
        <div class="flex items-center gap-2">
          <i class="pi pi-verified text-emerald-600 text-lg"></i>
          <span>
            <strong>Disahkan secara resmi</strong> oleh <strong>{{ minute.approver_name }}</strong> pada {{ formatDate(minute.approved_at) }}
          </span>
        </div>
        <span class="font-mono text-[11px] opacity-75">Sistem Verifikasi Digital Yayasan Asy-Syuuraa</span>
      </div>

      <!-- 1. Metadata Info Card -->
      <div class="card p-5 space-y-4">
        <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
          Informasi Pertemuan
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span class="text-slate-400 block mb-0.5">Hari / Tanggal:</span>
            <span class="font-bold text-slate-700 dark:text-slate-200">{{ formatDate(minute.meeting_date) }}</span>
          </div>
          <div>
            <span class="text-slate-400 block mb-0.5">Waktu:</span>
            <span class="font-bold text-slate-700 dark:text-slate-200">{{ minute.start_time || '-' }} s/d {{ minute.end_time || '-' }}</span>
          </div>
          <div>
            <span class="text-slate-400 block mb-0.5">Tempat / Lokasi:</span>
            <span class="font-bold text-slate-700 dark:text-slate-200">{{ minute.location || '-' }}</span>
          </div>
          <div>
            <span class="text-slate-400 block mb-0.5">Cakupan / Unit:</span>
            <Tag :value="minute.scope === 'yayasan_global' ? 'Yayasan / Global' : (minute.unit_name || 'Unit')" severity="info" class="text-[10px]" />
          </div>
        </div>
      </div>

      <!-- 2. Peserta Rapat -->
      <div class="card p-5 space-y-4">
        <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
          Daftar Kehadiran Peserta
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <!-- Hadir -->
          <div class="space-y-2">
            <p class="font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
              <i class="pi pi-check-circle"></i> Peserta Hadir ({{ minute.attendees?.length || 0 }})
            </p>
            <div v-if="!minute.attendees || minute.attendees.length === 0" class="text-slate-400 italic">Tidak ada catatan kehadiran.</div>
            <div v-else class="flex flex-wrap gap-1.5">
              <span 
                v-for="u in minute.attendees" 
                :key="u.id" 
                class="px-2.5 py-1 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800"
              >
                {{ u.full_name }}
              </span>
            </div>
          </div>

          <!-- Izin / Alpa -->
          <div class="space-y-2">
            <p class="font-bold text-rose-700 dark:text-rose-400 flex items-center gap-1.5">
              <i class="pi pi-times-circle"></i> Berhalangan / Izin ({{ minute.absent_members?.length || 0 }})
            </p>
            <div v-if="!minute.absent_members || minute.absent_members.length === 0" class="text-slate-400 italic">Semua hadir.</div>
            <div v-else class="flex flex-wrap gap-1.5">
              <span 
                v-for="u in minute.absent_members" 
                :key="u.id" 
                class="px-2.5 py-1 rounded-lg bg-rose-50 dark:bg-rose-950/40 text-rose-800 dark:text-rose-300 border border-rose-200 dark:border-rose-800"
              >
                {{ u.full_name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Agenda Pembahasan -->
      <div v-if="minute.agenda?.length" class="card p-5 space-y-3">
        <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
          Agenda Pembahasan
        </h2>
        <ul class="list-decimal list-inside space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
          <li v-for="(ag, idx) in minute.agenda" :key="idx" class="font-medium">
            {{ ag }}
          </li>
        </ul>
      </div>

      <!-- 4. Jalannya Rapat & Notulensi -->
      <div class="card p-5 space-y-3">
        <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
          Catatan Jalannya Rapat & Notulensi
        </h2>
        <div class="prose dark:prose-invert max-w-none text-xs text-slate-700 dark:text-slate-300 whitespace-pre-line leading-relaxed">
          {{ minute.content || 'Tidak ada catatan jalannya rapat.' }}
        </div>
      </div>

      <!-- 5. Keputusan & Kesimpulan -->
      <div v-if="minute.decisions?.length" class="card p-5 space-y-3">
        <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
          Keputusan & Kesimpulan Rapat
        </h2>
        <ul class="list-disc list-inside space-y-1.5 text-xs text-slate-700 dark:text-slate-300">
          <li v-for="(dec, idx) in minute.decisions" :key="idx" class="font-medium text-emerald-800 dark:text-emerald-300">
            {{ dec }}
          </li>
        </ul>
      </div>

      <!-- 6. Tindak Lanjut (Action Items) -->
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <div>
            <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-400">
              Tindak Lanjut & Action Items
            </h2>
            <p class="text-xs text-slate-500">Tugas yang harus diselesaikan oleh masing-masing PIC.</p>
          </div>
        </div>

        <InternalActionItemTracker :items="minute.action_items || []" @updated="fetchDetail" />
      </div>

      <!-- 7. Lampiran Berkas -->
      <div v-if="minute.attachment_urls?.length" class="card p-5 space-y-3">
        <h2 class="font-bold text-sm text-slate-800 dark:text-white uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
          Lampiran Berkas & Materi
        </h2>
        <div class="space-y-2">
          <div v-for="(url, idx) in minute.attachment_urls" :key="idx" class="flex items-center justify-between p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 text-xs">
            <div class="flex items-center gap-2 truncate pr-2">
              <i class="pi pi-link text-primary"></i>
              <span class="truncate font-mono">{{ url }}</span>
            </div>
            <a :href="url" target="_blank" class="px-2.5 py-1 text-primary hover:underline font-bold shrink-0">
              Buka <i class="pi pi-external-link ml-1"></i>
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL: Catatan Penolakan / Permintaan Revisi -->
    <Dialog v-model:visible="rejectDialogVisible" header="Kembalikan untuk Revisi" modal class="w-full max-w-md">
      <div class="space-y-3 pt-2">
        <p class="text-xs text-slate-600 dark:text-slate-300">
          Tuliskan catatan perbaikan atau bagian mana yang perlu diperbaiki oleh notulis sebelum disahkan:
        </p>
        <Textarea v-model="rejectNotes" rows="4" placeholder="Contoh: Tambahkan poin keputusan terkait anggaran seragam..." class="w-full text-xs" />
      </div>
      <template #footer>
        <Button label="Batal" severity="secondary" @click="rejectDialogVisible = false" />
        <Button label="Kirim Catatan Revisi" icon="pi pi-send" severity="danger" :loading="rejecting" :disabled="!rejectNotes.trim()" @click="rejectMinute" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'dashboard' })

const route = useRoute()
const router = useRouter()
const toast = useToast()
const api = useApi()
const authStore = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const minuteId = route.params.id
const minute = ref<any>(null)
const loading = ref(true)

const submitting = ref(false)
const approving = ref(false)
const rejecting = ref(false)

const rejectDialogVisible = ref(false)
const rejectNotes = ref('')

const isNotulisOrAdmin = computed(() => {
  if (!minute.value || !authStore.user) return false
  return minute.value.notulis_id === authStore.user.id || ['superadmin', 'ketua_yayasan'].includes(authStore.user.role?.code || '')
})

function getStatusText(status?: string) {
  const map: Record<string, string> = {
    draft: 'Draf',
    submitted: 'Menunggu Persetujuan',
    approved: 'Disahkan',
    rejected: 'Perlu Revisi',
    archived: 'Diarsipkan'
  }
  return map[status || ''] || status || '-'
}

function getStatusSeverity(status?: string) {
  const map: Record<string, string> = {
    draft: 'secondary',
    submitted: 'warn',
    approved: 'success',
    rejected: 'danger',
    archived: 'secondary'
  }
  return map[status || ''] || 'secondary'
}

function formatDate(iso?: string) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

async function fetchDetail() {
  loading.value = true
  try {
    minute.value = await api.get(`/meeting/minutes/${minuteId}`)
  } catch (e) {
    console.error('Failed to load meeting minute', e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Notulen tidak ditemukan', life: 3000 })
    router.push('/dashboard/internal/notulen')
  } finally {
    loading.value = false
  }
}

async function submitForApproval() {
  if (!confirm('Ajukan notulen ini ke pimpinan untuk diverifikasi dan disahkan?')) return
  submitting.value = true
  try {
    await api.post(`/meeting/minutes/${minuteId}/submit`)
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Notulen diajukan ke pimpinan', life: 3000 })
    await fetchDetail()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.data?.detail || 'Gagal mengajukan notulen', life: 3000 })
  } finally {
    submitting.value = false
  }
}

async function approveMinute() {
  if (!confirm('Sahkan dan terbitkan notulen resmi ini?')) return
  approving.value = true
  try {
    await api.post(`/meeting/minutes/${minuteId}/approve`)
    toast.add({ severity: 'success', summary: 'Disahkan', detail: 'Notulen rapat resmi disahkan dan diterbitkan!', life: 3000 })
    await fetchDetail()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.data?.detail || 'Gagal mengesahkan notulen', life: 3000 })
  } finally {
    approving.value = false
  }
}

async function rejectMinute() {
  rejecting.value = true
  try {
    await api.post(`/meeting/minutes/${minuteId}/reject`, { notes: rejectNotes.value })
    toast.add({ severity: 'warn', summary: 'Dikembalikan', detail: 'Catatan revisi berhasil dikirim ke notulis', life: 3000 })
    rejectDialogVisible.value = false
    rejectNotes.value = ''
    await fetchDetail()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.data?.detail || 'Gagal mengembalikan notulen', life: 3000 })
  } finally {
    rejecting.value = false
  }
}

onMounted(() => {
  fetchDetail()
})
</script>
