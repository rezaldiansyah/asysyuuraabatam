<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-12">
    <!-- Top Bar -->
    <div class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <NuxtLink to="/dashboard/internal/notulen">
          <Button icon="pi pi-arrow-left" severity="secondary" rounded text />
        </NuxtLink>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-slate-800 dark:text-white">
              {{ isEditing ? 'Edit Notulen Rapat' : 'Tulis Notulen Rapat Baru' }}
            </h1>
            <Tag v-if="isEditing" value="Mode Edit" severity="warn" class="text-xs" />
          </div>
          <p class="text-xs text-slate-500">
            {{ isEditing ? 'Perbarui isi notulensi, agenda pembahasan, dan tindak lanjut tugas.' : 'Catat jalannya rapat resmi, tetapkan kehadiran, dan buat tindak lanjut tugas.' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <Button label="Batal" severity="secondary" @click="router.back()" />
        <Button 
          :label="isEditing ? 'Simpan Perubahan' : 'Simpan Draf'" 
          icon="pi pi-save" 
          severity="secondary" 
          :loading="saving" 
          @click="saveMinute(false)" 
        />
        <Button 
          label="Simpan & Ajukan" 
          icon="pi pi-send" 
          severity="primary" 
          :loading="saving" 
          @click="saveMinute(true)" 
        />
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

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
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
          <div class="flex flex-col gap-1.5">
            <label class="font-medium text-xs flex items-center justify-between">
              <span>Notulis Rapat *</span>
              <span class="text-[10px] text-slate-400 font-normal">Default: Akun Login</span>
            </label>
            <Select 
              v-model="form.notulis_id" 
              :options="userOptions" 
              optionLabel="label" 
              optionValue="id" 
              placeholder="Pilih notulis rapat..." 
              filter 
              class="w-full"
            />
          </div>
        </div>
      </div>

      <!-- 2. Kehadiran & Peserta Rapat -->
      <div class="card p-5 space-y-4">
        <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <i class="pi pi-users text-primary"></i> 2. Kehadiran & Peserta Rapat
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

      <!-- 4. Jalannya Rapat & Notulensi (Rich Text Editor) -->
      <div class="card p-5 space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-2">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
              <i class="pi pi-file-edit text-primary"></i> 4. Catatan Pembahasan / Isi Notulensi *
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">
              Gunakan fitur teks tebal, miring, poin, dan tabel untuk mencatat jalannya rapat secara terstruktur.
            </p>
          </div>

          <!-- Quick Template & Table Action Buttons -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <div class="flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5 border border-slate-200 dark:border-slate-700">
              <Button 
                type="button" 
                label="+ Tabel 2 Kolom" 
                icon="pi pi-table" 
                size="small" 
                text 
                class="!text-xs !py-1 !px-2.5 font-semibold text-slate-700 dark:text-slate-200 hover:!bg-white dark:hover:!bg-slate-700"
                @click="insertTable(2)" 
                title="Sisipkan tabel 2 kolom (No, Pembahasan)"
              />
              <Button 
                type="button" 
                label="+ Tabel 3 Kolom" 
                icon="pi pi-table" 
                size="small" 
                text 
                class="!text-xs !py-1 !px-2.5 font-semibold text-slate-700 dark:text-slate-200 hover:!bg-white dark:hover:!bg-slate-700"
                @click="insertTable(3)" 
                title="Sisipkan tabel 3 kolom (No, Masukan, Kesepakatan)"
              />
            </div>

            <div class="flex items-center bg-emerald-50 dark:bg-emerald-950/40 rounded-lg p-0.5 border border-emerald-200 dark:border-emerald-800">
              <Button 
                type="button" 
                label="+ Tambah Baris" 
                icon="pi pi-plus" 
                size="small" 
                severity="success" 
                text 
                class="!text-xs !py-1 !px-2.5 font-bold"
                @click="addTableRow" 
                title="Tambahkan baris baru ke tabel (atau tekan tombol Tab pada kolom terakhir)"
              />
              <Button 
                type="button" 
                label="- Hapus Baris" 
                icon="pi pi-minus" 
                size="small" 
                severity="danger" 
                text 
                class="!text-xs !py-1 !px-2.5"
                @click="deleteTableRow" 
                title="Hapus baris terakhir tabel"
              />
              <Button 
                type="button" 
                label="Gabung Tabel" 
                icon="pi pi-link" 
                size="small" 
                severity="help" 
                text 
                class="!text-xs !py-1 !px-2.5 font-medium"
                @click="mergeTables" 
                title="Gabungkan 2 tabel terpisah menjadi 1 tabel bersambung"
              />
            </div>

            <Button 
              type="button" 
              label="Template Notulen" 
              icon="pi pi-file" 
              size="small" 
              outlined 
              severity="info" 
              class="!text-xs !py-1 font-semibold"
              @click="insertNotulenTemplate" 
              title="Gunakan template format notulensi terstruktur"
            />
          </div>
        </div>

        <p class="text-[11px] text-slate-500 flex items-center gap-1.5 px-0.5">
          <i class="pi pi-info-circle text-primary text-xs"></i>
          <span><b>Panduan Tabel:</b> Klik langsung kolom untuk mengetik. Gunakan tombol <b>Tab</b> di keyboard untuk berpindah ke kolom sebelah atau otomatis menambah baris baru di ujung tabel. Klik <b>Gabung Tabel</b> jika sebelumnya ada 2 tabel terpisah.</span>
        </p>

        <!-- PrimeVue Rich Text Editor with Custom Toolbar -->
        <div class="rich-editor-wrapper">
          <Editor 
            ref="editorRef"
            v-model="form.content" 
            :modules="editorModules"
            @load="onEditorLoad"
            editorStyle="min-height: 280px" 
            placeholder="Tuliskan catatan pembahasan rapat, aspirasi, dan tanggapan peserta di sini...">
            <template #toolbar>
              <span class="ql-formats">
                <select class="ql-header" title="Format Judul / Paragraf">
                  <option value="1">Judul Utama (H1)</option>
                  <option value="2">Sub Judul (H2)</option>
                  <option value="3">Poin Bahasan (H3)</option>
                  <option selected>Teks Normal</option>
                </select>
              </span>
              <span class="ql-formats">
                <button class="ql-bold" type="button" title="Tebal (Bold)"></button>
                <button class="ql-italic" type="button" title="Miring (Italic)"></button>
                <button class="ql-underline" type="button" title="Garis Bawah (Underline)"></button>
                <button class="ql-strike" type="button" title="Coret (Strikethrough)"></button>
              </span>
              <span class="ql-formats">
                <select class="ql-color" title="Warna Teks"></select>
                <select class="ql-background" title="Warna Latar / Sorotan"></select>
              </span>
              <span class="ql-formats">
                <button class="ql-list" value="ordered" type="button" title="Penomoran (1, 2, 3)"></button>
                <button class="ql-list" value="bullet" type="button" title="Daftar Poin (Bullets)"></button>
                <button class="ql-list" value="check" type="button" title="Daftar Centang (Checklist)"></button>
                <button class="ql-indent" value="-1" type="button" title="Geser Kiri (Outdent)"></button>
                <button class="ql-indent" value="+1" type="button" title="Geser Kanan (Indent)"></button>
              </span>
              <span class="ql-formats">
                <select class="ql-align" title="Perataan Paragraf"></select>
              </span>
              <span class="ql-formats">
                <button class="ql-blockquote" type="button" title="Kutipan"></button>
                <button class="ql-code-block" type="button" title="Blok Kode / Format Rapat"></button>
                <button class="ql-link" type="button" title="Sisipkan Link"></button>
              </span>
              <span class="ql-formats">
                <button class="ql-clean" type="button" title="Bersihkan Format"></button>
              </span>
            </template>
          </Editor>
        </div>
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
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'dashboard' })

const router = useRouter()
const route = useRoute()
const toast = useToast()
const api = useApi()
const authStore = useAuthStore()

const editId = computed(() => {
  const q = route.query.id
  return q ? Number(q) : null
})
const isEditing = computed(() => !!editId.value)

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
  notulis_id: authStore.user?.id || (null as number | null),
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
  return users.value.map(u => {
    const roleName = u.role?.name || u.role_name || (u.is_teacher ? 'Guru' : 'Pegawai / Staff')
    return {
      id: u.id,
      label: `${u.full_name} (${roleName}${u.nik ? ' • ' + u.nik : ''})`,
      full_name: u.full_name,
      role_name: roleName,
      nik: u.nik
    }
  })
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

// Helper: Insert formatted table into content
// Editor table management & keyboard navigation
const editorRef = ref<any>(null)
const quillInstance = ref<any>(null)
const editorModules = {
  table: true
}

function onEditorLoad(event: any) {
  const instance = event?.instance || event
  quillInstance.value = instance

  const editorEl = (instance?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorEl) {
    editorEl.removeEventListener('keydown', handleEditorKeyDown)
    editorEl.addEventListener('keydown', handleEditorKeyDown)
  }
}

function focusCell(cell: HTMLElement) {
  if (!cell) return
  const range = document.createRange()
  const sel = window.getSelection()
  range.selectNodeContents(cell)
  range.collapse(false)
  sel?.removeAllRanges()
  sel?.addRange(range)
}

function handleEditorKeyDown(e: KeyboardEvent) {
  if (e.key === 'Tab') {
    const sel = window.getSelection()
    const node = sel?.anchorNode
    const currentCell = (node instanceof HTMLElement ? node : node?.parentElement)?.closest('td') as HTMLElement | null
    if (currentCell) {
      e.preventDefault()
      const table = currentCell.closest('table')
      if (table) {
        const allCells = Array.from(table.querySelectorAll('td')) as HTMLElement[]
        const currentIndex = allCells.indexOf(currentCell)
        if (currentIndex !== -1) {
          if (!e.shiftKey) {
            // Move to next cell
            if (currentIndex < allCells.length - 1) {
              focusCell(allCells[currentIndex + 1])
            } else {
              // At the end of table: automatically append a new row!
              addTableRow()
            }
          } else {
            // Move to previous cell
            if (currentIndex > 0) {
              focusCell(allCells[currentIndex - 1])
            }
          }
        }
      }
    }
  }
}

// Auto-heal legacy or malformed table HTML
function autoHealNotulenTableHtml(raw: string): string {
  if (!raw) return ''
  // 1. Convert any <th> to <td><b>...</b></td> so Quill's delta parser doesn't strip or eject headers
  let cleaned = raw.replace(/<th\b([^>]*)>(.*?)<\/th>/gis, '<td$1><b>$2</b></td>')
  // 2. Remove <thead> and </thead>
  cleaned = cleaned.replace(/<\/?thead\b[^>]*>/gi, '')
  // 3. Ensure border styling on table and cells if missing
  cleaned = cleaned.replace(/<table\b([^>]*)>/gi, (m, attrs) => {
    if (!attrs.includes('border-collapse')) {
      return `<table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">`
    }
    return m
  })
  return cleaned
}

// Helper: Insert formatted table into content (using clean <tr><td> without <th>)
function insertTable(cols: 2 | 3) {
  let tableHtml = ''
  if (cols === 2) {
    tableHtml = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 50px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Poin Pembahasan / Catatan Rapat</b></td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Tuliskan poin pembahasan pertama di sini...</td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">2</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Tuliskan poin pembahasan kedua di sini...</td>
          </tr>
        </tbody>
      </table>
      <p><br></p>
    `
  } else {
    tableHtml = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 50px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="width: 38%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Topik / Masukan Peserta</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tanggapan & Kesepakatan Bersama</b></td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Aspirasi / kendala yang disampaikan...</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Tanggapan pimpinan / solusi yang disepakati...</td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">2</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
          </tr>
        </tbody>
      </table>
      <p><br></p>
    `
  }
  form.content = (form.content ? form.content + '<br/>' : '') + tableHtml
  toast.add({ severity: 'info', summary: 'Tabel Disisipkan', detail: `Tabel ${cols} kolom berhasil ditambahkan ke catatan notulensi`, life: 2500 })
}

// Helper: Add a new row to active or last table
function addTableRow() {
  const editorRoot = (quillInstance.value?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorRoot) {
    const tables = editorRoot.querySelectorAll('table')
    if (tables.length > 0) {
      const sel = window.getSelection()
      const currentCell = (sel?.anchorNode instanceof HTMLElement ? sel.anchorNode : sel?.anchorNode?.parentElement)?.closest('td')
      const targetTable = currentCell?.closest('table') || tables[tables.length - 1]
      const rows = Array.from(targetTable.querySelectorAll('tr'))
      const lastRow = rows[rows.length - 1]
      const colCount = lastRow ? lastRow.querySelectorAll('td').length : 2
      const nextNum = rows.length // row 0 is header

      const newTr = document.createElement('tr')
      let cellsHtml = `<td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">${nextNum}</td>`
      for (let c = 1; c < colCount; c++) {
        cellsHtml += `<td style="padding: 8px; border: 1px solid #94a3b8;"></td>`
      }
      newTr.innerHTML = cellsHtml
      const tbody = targetTable.querySelector('tbody') || targetTable
      tbody.appendChild(newTr)

      // Sync form.content
      form.content = editorRoot.innerHTML

      // Focus second cell of the newly added row
      nextTick(() => {
        const targetTd = newTr.querySelectorAll('td')[1] || newTr.querySelector('td')
        if (targetTd) focusCell(targetTd as HTMLElement)
      })

      toast.add({ severity: 'success', summary: 'Baris Ditambahkan', detail: `Baris ke-${nextNum} berhasil ditambahkan`, life: 2000 })
      return
    }
  }

  // Fallback if no table exists yet
  insertTable(2)
}

// Helper: Delete row from active or last table
function deleteTableRow() {
  const editorRoot = (quillInstance.value?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorRoot) {
    const tables = editorRoot.querySelectorAll('table')
    if (tables.length > 0) {
      const sel = window.getSelection()
      const currentCell = (sel?.anchorNode instanceof HTMLElement ? sel.anchorNode : sel?.anchorNode?.parentElement)?.closest('td')
      const targetTable = currentCell?.closest('table') || tables[tables.length - 1]
      const rows = Array.from(targetTable.querySelectorAll('tr'))

      if (rows.length > 2) {
        const currentRow = currentCell?.closest('tr')
        const rowToDelete = (currentRow && rows.indexOf(currentRow) > 0) ? currentRow : rows[rows.length - 1]
        rowToDelete.remove()

        // Re-number rows
        const remainingRows = Array.from(targetTable.querySelectorAll('tr'))
        let counter = 1
        remainingRows.forEach((r, idx) => {
          if (idx === 0) return
          const firstTd = r.querySelector('td')
          if (firstTd) firstTd.textContent = String(counter++)
        })

        form.content = editorRoot.innerHTML
        toast.add({ severity: 'info', summary: 'Baris Dihapus', detail: 'Baris berhasil dihapus', life: 2000 })
      } else {
        toast.add({ severity: 'warn', summary: 'Peringatan', detail: 'Tabel minimal harus memiliki 1 baris data', life: 2500 })
      }
    } else {
      toast.add({ severity: 'warn', summary: 'Tidak Ada Tabel', detail: 'Belum ada tabel yang dibuat', life: 2500 })
    }
  }
}

// Helper: Merge disjointed tables into one unified table
function mergeTables() {
  const editorRoot = (quillInstance.value?.root || document.querySelector('.rich-editor-wrapper .ql-editor')) as HTMLElement | null
  if (editorRoot) {
    const tables = Array.from(editorRoot.querySelectorAll('table'))
    if (tables.length > 1) {
      const firstTable = tables[0]
      const tbody1 = firstTable.querySelector('tbody') || firstTable

      for (let i = 1; i < tables.length; i++) {
        const nextTable = tables[i]
        const rows = Array.from(nextTable.querySelectorAll('tr'))
        rows.forEach((r, idx) => {
          const text = r.textContent?.trim().toLowerCase() || ''
          // If first row is a repeated header, skip it
          if (idx === 0 && (text.includes('poin pembahasan') || text.includes('topik / masukan') || text === 'no' || text.includes('tanggapan'))) {
            return
          }
          tbody1.appendChild(r)
        })

        // Remove whitespace/paragraphs between the two tables
        let prev = nextTable.previousElementSibling
        while (prev && prev !== firstTable && (prev.tagName === 'P' || prev.tagName === 'BR') && !prev.textContent?.trim()) {
          const toRemove = prev
          prev = prev.previousElementSibling
          toRemove.remove()
        }
        nextTable.remove()
      }

      // Re-number sequentially
      const allRows = Array.from(firstTable.querySelectorAll('tr'))
      let counter = 1
      allRows.forEach((r, idx) => {
        if (idx === 0) return // skip header
        const firstTd = r.querySelector('td')
        if (firstTd) firstTd.textContent = String(counter++)
      })

      form.content = editorRoot.innerHTML
      toast.add({ severity: 'success', summary: 'Tabel Digabung', detail: 'Berhasil menggabungkan seluruh tabel menjadi 1 tabel rapi', life: 3000 })
    } else {
      toast.add({ severity: 'info', summary: 'Info', detail: 'Hanya ada 1 tabel di dalam dokumen notulensi', life: 2500 })
    }
  }
}

// Helper: Insert structured notulen template
function insertNotulenTemplate() {
  const templateHtml = `
    <h3>1. Pembukaan & Pengantar Pimpinan</h3>
    <p>Rapat dibuka secara resmi pada pukul ${form.start_time || '08:30'} WIB dengan membaca Basmalah dan arahan singkat pimpinan terkait fokus pertemuan hari ini.</p>
    
    <h3>2. Pembahasan Pokok & Jalannya Diskusi</h3>
    <p>Berikut rangkuman tanggapan dan aspirasi yang disampaikan oleh seluruh peserta rapat:</p>
    <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
      <tbody>
        <tr style="background-color: #f1f5f9; font-weight: bold;">
          <td style="width: 50px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
          <td style="width: 38%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Topik / Masukan Peserta</b></td>
          <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tanggapan & Solusi yang Disepakati</b></td>
        </tr>
        <tr>
          <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
          <td style="padding: 8px; border: 1px solid #94a3b8;">Evaluasi pelaksanaan kegiatan dan kendala di lapangan...</td>
          <td style="padding: 8px; border: 1px solid #94a3b8;">Disepakati penyesuaian jadwal dan koordinasi tim teknis...</td>
        </tr>
      </tbody>
    </table>

    <h3>3. Catatan Khusus & Rekomendasi</h3>
    <ul>
      <li>Seluruh pihak terkait diharapkan menyelesaikan tindak lanjut sebelum batas waktu yang ditentukan.</li>
      <li>Koordinasi teknis lanjutan akan dilakukan secara bertahap pada masing-masing unit kerja.</li>
    </ul>
    <p></p>
  `
  if (form.content && !confirm('Konten yang ada akan ditambahkan dengan template. Lanjutkan?')) return
  form.content = (form.content ? form.content + '<br/>' : '') + templateHtml
  toast.add({ severity: 'success', summary: 'Template Digunakan', detail: 'Template format notulensi berhasil diterapkan', life: 2500 })
}

async function fetchUsers() {
  try {
    users.value = await api.get<any[]>('/users?limit=200')
  } catch (e) {
    console.error('Failed to fetch users', e)
  }
}

async function loadExistingMinute(id: number) {
  try {
    const data = await api.get<any>(`/meeting/minutes/${id}`)
    if (!data) return

    form.scope = data.scope || 'unit'
    form.unit_id = data.unit_id || null
    form.meeting_type = data.meeting_type || 'rapat_unit'
    form.title = data.title || ''
    form.nomor_notulen = data.nomor_notulen || ''
    form.meeting_date = data.meeting_date ? String(data.meeting_date).substring(0, 10) : new Date().toISOString().substring(0, 10)
    form.start_time = data.start_time || '08:30'
    form.end_time = data.end_time || '11:00'
    form.location = data.location || 'Ruang Rapat Utama'
    form.notulis_id = data.notulis_id || authStore.user?.id || null
    form.content = autoHealNotulenTableHtml(data.content || '')

    if (Array.isArray(data.attendees)) {
      form.attendees = data.attendees.map((a: any) => typeof a === 'object' ? a.id : a)
    }
    if (Array.isArray(data.absent_members)) {
      form.absent_members = data.absent_members.map((a: any) => typeof a === 'object' ? a.id : a)
    }
    if (Array.isArray(data.agenda) && data.agenda.length > 0) {
      form.agenda = [...data.agenda]
    }
    if (Array.isArray(data.decisions) && data.decisions.length > 0) {
      form.decisions = [...data.decisions]
    }
    if (Array.isArray(data.action_items)) {
      form.action_items = data.action_items.map((ai: any) => ({
        id: ai.id,
        task_description: ai.task_description || '',
        pic_user_id: ai.pic_user_id || ai.pic?.id || null,
        deadline: ai.deadline ? String(ai.deadline).substring(0, 10) : '',
        notes: ai.notes || '',
        status: ai.status || 'pending'
      }))
    }
    if (Array.isArray(data.attachment_urls) && data.attachment_urls.length > 0) {
      gdriveUrl.value = data.attachment_urls[0] || ''
    }
  } catch (e: any) {
    console.error('Failed to load existing minute', e)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data notulen untuk diedit', life: 3000 })
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
      agenda: form.agenda.filter(a => a && a.trim().length > 0),
      decisions: form.decisions.filter(d => d && d.trim().length > 0),
      attachment_urls: gdriveUrl.value.trim() ? [gdriveUrl.value.trim()] : [],
    }

    let targetId = editId.value

    if (isEditing.value && targetId) {
      await api.put(`/meeting/minutes/${targetId}`, payload)
      if (submitNow) {
        await api.post(`/meeting/minutes/${targetId}/submit`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Notulen berhasil diperbarui & diajukan', life: 3000 })
      } else {
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Perubahan notulen berhasil disimpan', life: 3000 })
      }
    } else {
      const res = await api.post<{ id: number; nomor_notulen: string }>('/meeting/minutes', payload)
      targetId = res.id

      if (submitNow) {
        await api.post(`/meeting/minutes/${res.id}/submit`)
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Notulen berhasil dibuat & diajukan untuk disahkan', life: 3000 })
      } else {
        toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Draf notulen berhasil disimpan', life: 3000 })
      }
    }

    router.push(`/dashboard/internal/notulen/${targetId}`)
  } catch (e: any) {
    console.error('Save minute failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: e.data?.detail || e.message || 'Gagal menyimpan notulen', life: 4000 })
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchUsers()
  if (editId.value) {
    await loadExistingMinute(editId.value)
  }
})
</script>

<style scoped>
.rich-editor-wrapper :deep(.p-editor-content) {
  border-bottom-left-radius: 0.75rem;
  border-bottom-right-radius: 0.75rem;
}
.rich-editor-wrapper :deep(.p-editor-toolbar) {
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
  background-color: #f8fafc;
}
:deep(.dark) .rich-editor-wrapper :deep(.p-editor-toolbar) {
  background-color: #1e293b;
  border-color: #334155;
}

/* Rich Editor Table Styling - Crisp visible borders and clear column layout */
.rich-editor-wrapper :deep(.ql-editor) {
  font-family: inherit;
  font-size: 0.875rem;
  line-height: 1.6;
}

.rich-editor-wrapper :deep(.ql-editor table) {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 1rem 0 !important;
  table-layout: auto !important;
  border: 1px solid #94a3b8 !important;
}

.rich-editor-wrapper :deep(.ql-editor table td),
.rich-editor-wrapper :deep(.ql-editor table th) {
  border: 1px solid #94a3b8 !important; /* Clearly visible, distinct line between cells */
  padding: 8px 12px !important;
  min-height: 40px !important;
  vertical-align: top !important;
  box-sizing: border-box !important;
  color: #1e293b !important;
}

/* Column 1 (No) narrow and centered */
.rich-editor-wrapper :deep(.ql-editor table td:first-child),
.rich-editor-wrapper :deep(.ql-editor table th:first-child) {
  width: 50px !important;
  text-align: center !important;
  font-weight: 600 !important;
}

/* Header row with light slate background & bold text */
.rich-editor-wrapper :deep(.ql-editor table tr:first-child td),
.rich-editor-wrapper :deep(.ql-editor table tr:first-child th) {
  background-color: #f1f5f9 !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  border-bottom: 2px solid #64748b !important;
}

/* Focus and hover cues so users clearly see the active cell and column boundaries */
.rich-editor-wrapper :deep(.ql-editor table td:hover) {
  background-color: #f8fafc !important;
}

.rich-editor-wrapper :deep(.ql-editor table td:focus),
.rich-editor-wrapper :deep(.ql-editor table td:focus-within) {
  outline: 2px solid #3b82f6 !important;
  outline-offset: -2px !important;
}

/* Dark mode styling */
:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table) {
  border-color: #475569 !important;
}

:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table td),
:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table th) {
  border-color: #475569 !important;
  color: #f1f5f9 !important;
}

:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table tr:first-child td),
:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table tr:first-child th) {
  background-color: #1e293b !important;
  color: #f8fafc !important;
  border-bottom-color: #94a3b8 !important;
}

:deep(.dark) .rich-editor-wrapper :deep(.ql-editor table td:hover) {
  background-color: rgba(30, 41, 59, 0.7) !important;
}
</style>
