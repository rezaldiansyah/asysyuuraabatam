<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-12">
    <!-- Top Bar -->
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/internal/notulen">
          <Button icon="pi pi-arrow-left" severity="secondary" rounded text />
        </NuxtLink>
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Tulis Notulen Rapat Baru</h1>
          <p class="text-xs text-slate-500">Catat jalannya rapat resmi, tetapkan kehadiran, dan buat tindak lanjut tugas.</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button label="Batal" severity="secondary" @click="router.back()" />
        <Button label="Simpan Draf" icon="pi pi-save" severity="secondary" :loading="saving" @click="saveMinute(false)" />
        <Button label="Simpan & Ajukan" icon="pi pi-send" severity="primary" :loading="saving" @click="saveMinute(true)" />
      </div>
    </div>

    <!-- Form Body -->
    <div class="space-y-6">
      <!-- 1. Identitas & Cakupan Rapat -->
      <div class="card p-5 space-y-4">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-info-circle text-primary"></i> 1. Identitas & Cakupan Rapat
        </h2>

        <!-- Cakupan Rapat (Scope) -->
        <div>
          <label class="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 block">Tingkat / Cakupan Rapat *</label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div 
              @click="form.scope = 'unit'"
              class="p-3.5 rounded-xl border cursor-pointer transition-all flex items-start gap-3"
              :class="form.scope === 'unit' ? 'border-primary bg-primary/5 ring-1 ring-primary text-primary' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 text-slate-700 dark:text-slate-300'"
            >
              <i class="pi pi-building text-xl mt-0.5"></i>
              <div>
                <p class="font-bold text-sm">Rapat Tingkat Unit</p>
                <p class="text-xs opacity-75 mt-0.5">Rapat intern RA, SDIT, atau SMPIT (Disahkan oleh Kepala Unit)</p>
              </div>
            </div>

            <div 
              @click="form.scope = 'yayasan_global'"
              class="p-3.5 rounded-xl border cursor-pointer transition-all flex items-start gap-3"
              :class="form.scope === 'yayasan_global' ? 'border-primary bg-primary/5 ring-1 ring-primary text-primary' : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 text-slate-700 dark:text-slate-300'"
            >
              <i class="pi pi-globe text-xl mt-0.5"></i>
              <div>
                <p class="font-bold text-sm">Rapat Yayasan / Seluruh Unit</p>
                <p class="text-xs opacity-75 mt-0.5">Rapat Pleno Yayasan / Gabungan Unit (Disahkan oleh Ketua Yayasan)</p>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Pilih Unit jika Scope Unit -->
          <div v-if="form.scope === 'unit'" class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Pilih Unit *</label>
            <Select v-model="form.unit_id" :options="unitOptions" optionLabel="name" optionValue="id" placeholder="Pilih Unit Terkait" class="w-full" />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Jenis Pertemuan *</label>
            <Select v-model="form.meeting_type" :options="meetingTypeOptions" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2 flex flex-col gap-1.5">
            <label class="font-medium text-xs">Topik / Judul Rapat *</label>
            <InputText v-model="form.title" placeholder="Contoh: Rapat Koordinasi Kurikulum & Evaluasi KBM Semester Ganjil" class="w-full" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Nomor Notulen (opsional - otomatis jika kosong)</label>
            <InputText v-model="form.nomor_notulen" placeholder="Contoh: NOT/YYS/2026/09/001" class="w-full" />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Tanggal Pelaksanaan *</label>
            <InputText v-model="form.meeting_date" type="date" class="w-full" />
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Waktu Mulai & Selesai</label>
            <div class="flex items-center gap-2">
              <InputText v-model="form.start_time" placeholder="08:30" class="w-full" />
              <span class="text-slate-400 text-xs">s/d</span>
              <InputText v-model="form.end_time" placeholder="11:30" class="w-full" />
            </div>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs">Lokasi / Tempat</label>
            <InputText v-model="form.location" placeholder="Ruang Rapat Utama / Zoom" class="w-full" />
          </div>
        </div>
      </div>

      <!-- 2. Kehadiran Peserta Rapat -->
      <div class="card p-5 space-y-4">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-users text-primary"></i> 2. Kehadiran Peserta Rapat
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs text-emerald-700 dark:text-emerald-400">
              <i class="pi pi-check text-[10px]"></i> Peserta Hadir ({{ form.attendees.length }})
            </label>
            <MultiSelect 
              v-model="form.attendees" 
              :options="userOptions" 
              optionLabel="label" 
              optionValue="id" 
              placeholder="Pilih peserta yang hadir..." 
              filter 
              display="chip"
              class="w-full"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs text-rose-700 dark:text-rose-400">
              <i class="pi pi-times text-[10px]"></i> Peserta Berhalangan / Izin ({{ form.absent_members.length }})
            </label>
            <MultiSelect 
              v-model="form.absent_members" 
              :options="userOptions" 
              optionLabel="label" 
              optionValue="id" 
              placeholder="Pilih yang berhalangan..." 
              filter 
              display="chip"
              class="w-full"
            />
          </div>
        </div>
      </div>

      <!-- 3. Agenda Pembahasan -->
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
            <i class="pi pi-list text-primary"></i> 3. Agenda Pembahasan
          </h2>
          <Button label="Tambah Poin Agenda" icon="pi pi-plus" size="small" severity="secondary" @click="addAgendaItem" />
        </div>

        <div class="space-y-2">
          <div v-for="(ag, idx) in form.agenda" :key="idx" class="flex items-center gap-2">
            <span class="w-6 text-xs text-slate-400 font-bold text-right">{{ idx + 1 }}.</span>
            <InputText v-model="form.agenda[idx]" placeholder="Ketik poin agenda pembahasan..." class="flex-1" />
            <button v-if="form.agenda.length > 1" @click="removeAgendaItem(idx)" class="p-2 text-slate-400 hover:text-red-500">
              <i class="pi pi-times"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 4. Jalannya Rapat & Notulensi -->
      <div class="card p-5 space-y-3">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-file-edit text-primary"></i> 4. Catatan Pembahasan / Isi Notulensi *
        </h2>
        <p class="text-xs text-slate-500">Tuliskan ringkasan jalannya diskusi, aspirasi, dan tanggapan peserta secara berurutan.</p>
        <Textarea v-model="form.content" rows="8" placeholder="Catatan pembahasan rapat..." class="w-full" />
      </div>

      <!-- 5. Keputusan & Kesimpulan -->
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
            <i class="pi pi-check-circle text-primary"></i> 5. Keputusan & Kesimpulan Rapat
          </h2>
          <Button label="Tambah Keputusan" icon="pi pi-plus" size="small" severity="secondary" @click="addDecisionItem" />
        </div>

        <div class="space-y-2">
          <div v-for="(dec, idx) in form.decisions" :key="idx" class="flex items-center gap-2">
            <span class="w-6 text-xs text-slate-400 font-bold text-right">{{ idx + 1 }}.</span>
            <InputText v-model="form.decisions[idx]" placeholder="Ketik butir keputusan yang disepakati..." class="flex-1" />
            <button v-if="form.decisions.length > 1" @click="removeDecisionItem(idx)" class="p-2 text-slate-400 hover:text-red-500">
              <i class="pi pi-times"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 6. Tindak Lanjut (Action Items) -->
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
              <i class="pi pi-th-large text-primary"></i> 6. Tindak Lanjut / Action Items (Tugas)
            </h2>
            <p class="text-xs text-slate-500">Tugaskan PIC dan tenggat waktu agar hasil rapat langsung tereksekusi.</p>
          </div>
          <Button label="Tambah Tugas" icon="pi pi-plus" size="small" severity="secondary" @click="addActionItem" />
        </div>

        <div v-if="form.action_items.length === 0" class="text-center py-4 text-xs text-slate-400">
          Belum ada tugas tindak lanjut. Klik "Tambah Tugas" untuk menugaskan PIC.
        </div>

        <div v-else class="space-y-3">
          <div v-for="(item, idx) in form.action_items" :key="idx" class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-primary">Tugas #{{ idx + 1 }}</span>
              <button @click="removeActionItem(idx)" class="text-xs text-red-500 hover:text-red-700">
                <i class="pi pi-trash mr-1"></i> Hapus
              </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div class="md:col-span-2">
                <InputText v-model="item.task_description" placeholder="Deskripsi tugas yang harus dikerjakan..." class="w-full text-xs" />
              </div>
              <div>
                <Select v-model="item.pic_user_id" :options="userOptions" optionLabel="label" optionValue="id" placeholder="Pilih PIC Pegawai" class="w-full text-xs" filter />
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="flex items-center gap-2">
                <span class="text-xs text-slate-500 shrink-0">Batas Waktu:</span>
                <InputText v-model="item.deadline" type="date" class="w-full text-xs" />
              </div>
              <div>
                <InputText v-model="item.notes" placeholder="Catatan tambahan (opsional)..." class="w-full text-xs" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 7. Berkas / Lampiran -->
      <div class="card p-5 space-y-3">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-paperclip text-primary"></i> 7. Berkas Lampiran & Link Drive (opsional)
        </h2>
        
        <div class="space-y-2">
          <label class="text-xs font-medium">Link Google Drive Dokumentasi / Materi Rapat</label>
          <div class="relative">
            <i class="pi pi-link absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
            <InputText v-model="gdriveUrl" placeholder="https://drive.google.com/..." class="w-full !pl-9 text-xs" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const router = useRouter()
const toast = useToast()
const api = useApi()

const saving = ref(false)
const gdriveUrl = ref('')

const form = reactive({
  scope: 'unit',
  unit_id: null as number | null,
  meeting_type: 'rapat_unit',
  title: '',
  nomor_notulen: '',
  meeting_date: new Date().toISOString().substring(0, 10),
  start_time: '08:30',
  end_time: '11:00',
  location: 'Ruang Rapat Utama',
  attendees: [] as number[],
  absent_members: [] as number[],
  agenda: ['Pembahasan Utama'] as string[],
  content: '',
  decisions: ['Disepakati tindak lanjut bersama'] as string[],
  action_items: [] as any[],
})

const unitOptions = [
  { id: 1, name: 'Yayasan Asy-Syuuraa', code: 'YYS' },
  { id: 2, name: 'RA Asy-Syuuraa', code: 'RA' },
  { id: 3, name: 'SDIT Asy-Syuuraa', code: 'SDIT' },
  { id: 4, name: 'SMPIT Asy-Syuuraa', code: 'SMPIT' },
]

const meetingTypeOptions = [
  { label: 'Rapat Unit', value: 'rapat_unit' },
  { label: 'Rapat Pleno Yayasan', value: 'rapat_yayasan' },
  { label: 'Rapat Dewan Guru', value: 'rapat_guru' },
  { label: 'Rapat Koordinasi', value: 'rapat_koordinasi' },
  { label: 'Lainnya', value: 'lainnya' },
]

const users = ref<any[]>([])
const userOptions = computed(() => {
  return users.value.map(u => ({
    id: u.id,
    label: `${u.full_name} (${u.nik || '-'})`,
    full_name: u.full_name,
    nik: u.nik
  }))
})

function addAgendaItem() {
  form.agenda.push('')
}
function removeAgendaItem(idx: number) {
  form.agenda.splice(idx, 1)
}

function addDecisionItem() {
  form.decisions.push('')
}
function removeDecisionItem(idx: number) {
  form.decisions.splice(idx, 1)
}

function addActionItem() {
  form.action_items.push({
    task_description: '',
    pic_user_id: null,
    deadline: '',
    notes: '',
  })
}
function removeActionItem(idx: number) {
  form.action_items.splice(idx, 1)
}

async function fetchUsers() {
  try {
    users.value = await api.get<any[]>('/users?limit=200')
  } catch (e) {
    console.error('Failed to fetch users', e)
  }
}

async function saveMinute(submitNow: boolean) {
  if (!form.title.trim()) {
    toast.add({ severity: 'error', summary: 'Validasi', detail: 'Judul rapat wajib diisi', life: 3000 })
    return
  }

  saving.value = true
  try {
    const payload = {
      ...form,
      agenda: form.agenda.filter(a => a.trim().length > 0),
      decisions: form.decisions.filter(d => d.trim().length > 0),
      attachment_urls: gdriveUrl.value.trim() ? [gdriveUrl.value.trim()] : [],
    }

    const res = await api.post<{ id: number; nomor_notulen: string }>('/meeting/minutes', payload)

    if (submitNow) {
      await api.post(`/meeting/minutes/${res.id}/submit`)
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Notulen berhasil diajukan untuk disahkan', life: 3000 })
    } else {
      toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Draf notulen berhasil disimpan', life: 3000 })
    }

    router.push(`/dashboard/internal/notulen/${res.id}`)
  } catch (e) {
    console.error('Save minute failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan notulen', life: 3000 })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
