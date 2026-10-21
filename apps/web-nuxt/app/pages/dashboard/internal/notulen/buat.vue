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

      <!-- 4. Jalannya Rapat & Notulensi (Google Docs Style Editor) -->
      <div class="card p-5 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h2 class="font-bold text-base text-slate-800 dark:text-white flex items-center gap-2">
              <i class="pi pi-file-edit text-primary"></i> 4. Catatan Pembahasan / Isi Notulensi *
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">
              Tulis catatan rapat secara fleksibel layaknya <b>Google Docs</b>. Gunakan tombol tabel untuk format resmi yayasan, serta daftar butir (bullet) atau nomor dengan mudah.
            </p>
          </div>

          <!-- Quick Template & Table Action Buttons -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <Button 
              type="button" 
              label="+ Tabel 4 Kolom (Yayasan)" 
              icon="pi pi-table" 
              size="small" 
              class="!text-xs !py-1 !px-2.5 font-bold !bg-emerald-600 hover:!bg-emerald-700 !text-white !border-emerald-600"
              @click="insertTable(4)" 
              title="Sisipkan format tabel resmi yayasan: No, Perihal, Pembahasan/Arahan, Tindak Lanjut"
            />
            <Button 
              type="button" 
              label="+ Tabel 3 Kolom" 
              icon="pi pi-table" 
              size="small" 
              outlined
              severity="secondary"
              class="!text-xs !py-1 !px-2.5 font-medium"
              @click="insertTable(3)" 
              title="Sisipkan tabel 3 kolom: No, Masukan, Kesepakatan"
            />
            <Button 
              type="button" 
              label="+ Tambah Baris" 
              icon="pi pi-plus" 
              size="small" 
              severity="success" 
              outlined
              class="!text-xs !py-1 !px-2 font-semibold"
              @click="addTableRow" 
              title="Tambah baris baru ke tabel (atau tekan Tab di kolom terakhir)"
            />
            <Button 
              type="button" 
              label="Template Notulen" 
              icon="pi pi-file" 
              size="small" 
              severity="info" 
              outlined 
              class="!text-xs !py-1 !px-2 font-semibold"
              @click="insertNotulenTemplate" 
              title="Gunakan format template lengkap notulen resmi"
            />
          </div>
        </div>

        <!-- Google Docs Workspace Container -->
        <div class="gdocs-workspace">
          <!-- Google Docs Ruler Bar -->
          <div class="gdocs-ruler select-none">
            <div class="gdocs-ruler-track">
              <div class="gdocs-ruler-marker-left"></div>
              <div class="flex justify-between w-full px-8 text-[9px] font-mono text-slate-400">
                <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span>
              </div>
              <div class="gdocs-ruler-marker-right"></div>
            </div>
          </div>

          <!-- PrimeVue Editor with Google Docs Toolbar -->
          <div class="gdocs-editor-sheet-wrapper">
            <Editor 
              ref="editorRef"
              v-model="form.content" 
              :modules="editorModules"
              @load="onEditorLoad"
              placeholder="Mulai ketik isi notulensi rapat di sini layaknya Google Docs...">
              <template #toolbar>
                <!-- Undo / Redo / Print -->
                <button type="button" class="gdocs-icon-btn" @click="undo" title="Urungkan (Ctrl+Z)">
                  <i class="pi pi-undo text-xs"></i>
                </button>
                <button type="button" class="gdocs-icon-btn" @click="redo" title="Ulangi (Ctrl+Y)">
                  <i class="pi pi-refresh text-xs"></i>
                </button>
                <button type="button" class="gdocs-icon-btn" @click="printDoc" title="Cetak Dokumen">
                  <i class="pi pi-print text-xs"></i>
                </button>

                <div class="gdocs-divider"></div>

                <!-- Text Style / Heading -->
                <span class="ql-formats">
                  <select class="ql-header" title="Gaya Teks">
                    <option selected>Teks Normal</option>
                    <option value="1">Judul Utama (H1)</option>
                    <option value="2">Sub Judul (H2)</option>
                    <option value="3">Poin Bahasan (H3)</option>
                  </select>
                </span>

                <!-- Font Family -->
                <span class="ql-formats">
                  <select class="ql-font" title="Jenis Font">
                    <option selected>Arial</option>
                    <option value="serif">Times New Roman</option>
                    <option value="monospace">Courier New</option>
                  </select>
                </span>

                <!-- Font Size -->
                <span class="ql-formats">
                  <select class="ql-size" title="Ukuran Font">
                    <option value="small">Kecil (9pt)</option>
                    <option selected>Normal (11pt)</option>
                    <option value="large">Sedang (14pt)</option>
                    <option value="huge">Besar (18pt)</option>
                  </select>
                </span>

                <div class="gdocs-divider"></div>

                <!-- Bold, Italic, Underline, Strike -->
                <span class="ql-formats">
                  <button class="ql-bold" type="button" title="Tebal (Ctrl+B)"></button>
                  <button class="ql-italic" type="button" title="Miring (Ctrl+I)"></button>
                  <button class="ql-underline" type="button" title="Garis Bawah (Ctrl+U)"></button>
                  <button class="ql-strike" type="button" title="Coret"></button>
                </span>

                <!-- Colors -->
                <span class="ql-formats">
                  <select class="ql-color" title="Warna Teks"></select>
                  <select class="ql-background" title="Warna Sorotan (Stabilo)"></select>
                </span>

                <div class="gdocs-divider"></div>

                <!-- Alignment -->
                <span class="ql-formats">
                  <select class="ql-align" title="Perataan Paragraf"></select>
                </span>

                <!-- Lists & Indent -->
                <span class="ql-formats">
                  <button class="ql-list" value="bullet" type="button" title="Daftar Butir (Bullet •)"></button>
                  <button class="ql-list" value="ordered" type="button" title="Daftar Bernomor (1, 2, 3)"></button>
                  <button class="ql-list" value="check" type="button" title="Daftar Centang (Checklist)"></button>
                  <button class="ql-indent" value="-1" type="button" title="Kurangi Indentasi"></button>
                  <button class="ql-indent" value="+1" type="button" title="Tambah Indentasi"></button>
                </span>

                <div class="gdocs-divider"></div>

                <!-- Links & Code & Clean -->
                <span class="ql-formats">
                  <button class="ql-link" type="button" title="Sisipkan Link"></button>
                  <button class="ql-blockquote" type="button" title="Kutipan"></button>
                  <button class="ql-clean" type="button" title="Bersihkan Format"></button>
                </span>

                <div class="gdocs-divider"></div>

                <!-- Inline Table Actions inside Toolbar -->
                <div class="flex items-center gap-1">
                  <button
                    type="button"
                    @click="addTableRow"
                    class="gdocs-custom-pill text-blue-700 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800"
                    title="Tambah baris baru ke tabel aktif"
                  >
                    <i class="pi pi-plus text-[10px]"></i>
                    <span>+ Baris</span>
                  </button>
                  <button
                    type="button"
                    @click="deleteTableRow"
                    class="gdocs-custom-pill text-rose-700 bg-rose-50 hover:bg-rose-100 dark:bg-rose-950/40 dark:text-rose-300 border border-rose-200 dark:border-rose-800"
                    title="Hapus baris terakhir dari tabel"
                  >
                    <i class="pi pi-minus text-[10px]"></i>
                    <span>- Baris</span>
                  </button>
                  <button
                    type="button"
                    @click="mergeTables"
                    class="gdocs-custom-pill text-purple-700 bg-purple-50 hover:bg-purple-100 dark:bg-purple-950/40 dark:text-purple-300 border border-purple-200 dark:border-purple-800"
                    title="Gabungkan tabel terpisah menjadi 1 tabel bersambung"
                  >
                    <i class="pi pi-link text-[10px]"></i>
                    <span>Gabung</span>
                  </button>
                </div>
              </template>
            </Editor>
          </div>
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

// =========================================================================
// GOOGLE DOCS STYLE NOTULEN EDITOR
// =========================================================================
const editorRef = ref<any>(null)
const quillInstance = ref<any>(null)
const editorModules = {
  table: true
}

function onEditorLoad(event: any) {
  const instance = event?.instance || event
  quillInstance.value = instance

  const editorEl = (instance?.root || document.querySelector('.gdocs-workspace .ql-editor')) as HTMLElement | null
  if (editorEl) {
    editorEl.removeEventListener('keydown', handleEditorKeyDown)
    editorEl.addEventListener('keydown', handleEditorKeyDown)
  }
}

function undo() {
  if (quillInstance.value?.history) {
    quillInstance.value.history.undo()
  }
}

function redo() {
  if (quillInstance.value?.history) {
    quillInstance.value.history.redo()
  }
}

function printDoc() {
  window.print()
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
  const sel = window.getSelection()
  const node = sel?.anchorNode
  const currentCell = (node instanceof HTMLElement ? node : node?.parentElement)?.closest('td') as HTMLElement | null

  // In Word/Doc mode: Intercept Enter inside <td> so it does NOT jump out of cell
  if (e.key === 'Enter' && !e.shiftKey && currentCell) {
    e.preventDefault()
    e.stopPropagation()
    const range = sel?.getRangeAt(0)
    if (range) {
      range.deleteContents()
      const br = document.createElement('br')
      range.insertNode(br)
      const textNode = document.createTextNode('')
      br.after(textNode)
      range.setStartAfter(br)
      range.setEndAfter(br)
      sel?.removeAllRanges()
      sel?.addRange(range)
    }
    return
  }

  // Handle Tab navigation inside table
  if (e.key === 'Tab') {
    if (currentCell) {
      e.preventDefault()
      const table = currentCell.closest('table')
      if (table) {
        const allCells = Array.from(table.querySelectorAll('td')) as HTMLElement[]
        const currentIndex = allCells.indexOf(currentCell)
        if (currentIndex !== -1) {
          if (!e.shiftKey) {
            if (currentIndex < allCells.length - 1) {
              focusCell(allCells[currentIndex + 1])
            } else {
              addTableRow()
            }
          } else {
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
  let cleaned = raw.replace(/<th\b([^>]*)>(.*?)<\/th>/gis, '<td$1><b>$2</b></td>')
  cleaned = cleaned.replace(/<\/?thead\b[^>]*>/gi, '')
  cleaned = cleaned.replace(/<table\b([^>]*)>/gi, (m, attrs) => {
    if (!attrs.includes('border-collapse')) {
      return `<table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">`
    }
    return m
  })
  return cleaned
}

// Helper: Insert formatted table into content (supports 2, 3, or 4 columns)
function insertTable(cols: 2 | 3 | 4) {
  let tableHtml = ''
  if (cols === 4) {
    tableHtml = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 35px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="width: 22%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Perihal / Topik</b></td>
            <td style="width: 48%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Pembahasan / Arahan Pimpinan</b></td>
            <td style="padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Tindak Lanjut</b></td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">1</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">Topik bahasan pertama...</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">a. Poin arahan pertama...<br/>b. Poin arahan kedua...</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;">a. PIC dan batas waktu...</td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 8px; border: 1px solid #94a3b8;">2</td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
            <td style="padding: 8px; border: 1px solid #94a3b8;"></td>
          </tr>
        </tbody>
      </table>
      <p><br></p>
    `
  } else if (cols === 2) {
    tableHtml = `
      <table class="notulen-table" style="width: 100%; border-collapse: collapse; margin: 12px 0;" border="1">
        <tbody>
          <tr style="background-color: #f1f5f9; font-weight: bold;">
            <td style="width: 40px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
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
            <td style="width: 35px; text-align: center; padding: 8px; border: 1px solid #94a3b8;"><b>No</b></td>
            <td style="width: 30%; padding: 8px; border: 1px solid #94a3b8; text-align: left;"><b>Topik / Masukan Peserta</b></td>
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
/* =========================================================================
   GOOGLE DOCS STYLE WORKSPACE & CANVAS
   ========================================================================= */
.gdocs-workspace {
  background-color: #f0f4f9;
  border-radius: 1rem;
  border: 1px solid #e2e8f0;
  padding: 1.25rem 0.75rem 2rem 0.75rem;
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.03);
}
:deep(.dark) .gdocs-workspace {
  background-color: #0b1329;
  border-color: #1e293b;
}

/* Sticky Google Docs Toolbar */
.gdocs-workspace :deep(.p-editor-toolbar) {
  position: sticky;
  top: 0.5rem;
  z-index: 25;
  background-color: #ffffff;
  border-radius: 9999px;
  border: 1px solid #cbd5e1;
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.08);
  padding: 0.35rem 0.85rem;
  margin-bottom: 0.75rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25rem;
}
:deep(.dark) .gdocs-workspace :deep(.p-editor-toolbar) {
  background-color: #1e293b;
  border-color: #334155;
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.3);
}

/* Toolbar Divider */
.gdocs-divider {
  width: 1px;
  height: 1.25rem;
  background-color: #e2e8f0;
  margin: 0 0.25rem;
}
:deep(.dark) .gdocs-divider {
  background-color: #475569;
}

/* Toolbar icon buttons (Undo, Redo, Print) */
.gdocs-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 0.375rem;
  color: #475569;
  transition: all 0.15s;
}
.gdocs-icon-btn:hover {
  background-color: #f1f5f9;
  color: #0f172a;
}
:deep(.dark) .gdocs-icon-btn {
  color: #94a3b8;
}
:deep(.dark) .gdocs-icon-btn:hover {
  background-color: #334155;
  color: #f8fafc;
}

/* Toolbar Custom Pill Buttons */
.gdocs-custom-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.55rem;
  border-radius: 0.375rem;
  transition: all 0.15s;
}

/* Google Docs Ruler Bar */
.gdocs-ruler {
  max-width: 820px;
  margin: 0 auto 0.6rem auto;
  height: 16px;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 2px;
  position: relative;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
:deep(.dark) .gdocs-ruler {
  background-color: #1e293b;
  border-color: #334155;
}
.gdocs-ruler-track {
  width: 100%;
  display: flex;
  align-items: center;
  position: relative;
}
.gdocs-ruler-marker-left {
  position: absolute;
  left: 20px;
  top: 1px;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #2563eb;
}
.gdocs-ruler-marker-right {
  position: absolute;
  right: 20px;
  top: 1px;
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #2563eb;
}

/* The Document Page (Sheet of paper) */
.gdocs-workspace :deep(.p-editor-content) {
  border: none !important;
  background: transparent !important;
  display: flex;
  justify-content: center;
  padding: 0;
}

.gdocs-workspace :deep(.ql-editor) {
  background-color: #ffffff;
  width: 100%;
  max-width: 820px;
  min-height: 720px;
  margin: 0 auto;
  padding: 48px 56px !important;
  border-radius: 2px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(60,64,67,.15), 0 2px 6px 2px rgba(60,64,67,.1);
  font-family: Arial, 'Plus Jakarta Sans', system-ui, sans-serif;
  font-size: 11pt;
  line-height: 1.65;
  color: #1e293b;
}
:deep(.dark) .gdocs-workspace :deep(.ql-editor) {
  background-color: #0f172a;
  border-color: #1e293b;
  box-shadow: 0 4px 14px rgba(0,0,0,0.4);
  color: #f1f5f9;
}

/* Headings inside the document */
.gdocs-workspace :deep(.ql-editor h1) {
  font-size: 1.6rem;
  font-weight: 700;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
}
.gdocs-workspace :deep(.ql-editor h2) {
  font-size: 1.3rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #0f172a;
}
.gdocs-workspace :deep(.ql-editor h3) {
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.35rem;
  color: #1e293b;
}
:deep(.dark) .gdocs-workspace :deep(.ql-editor h1),
:deep(.dark) .gdocs-workspace :deep(.ql-editor h2),
:deep(.dark) .gdocs-workspace :deep(.ql-editor h3) {
  color: #f8fafc;
}

/* Lists styling inside document */
.gdocs-workspace :deep(.ql-editor ul),
.gdocs-workspace :deep(.ql-editor ol) {
  padding-left: 1.75rem !important;
  margin: 0.5rem 0 !important;
}
.gdocs-workspace :deep(.ql-editor li) {
  padding-left: 0.35rem !important;
  margin-bottom: 0.25rem;
}

/* Table styling inside document */
.gdocs-workspace :deep(.ql-editor table) {
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 1rem 0 !important;
  table-layout: auto !important;
  border: 1px solid #94a3b8 !important;
}

.gdocs-workspace :deep(.ql-editor table td),
.gdocs-workspace :deep(.ql-editor table th) {
  border: 1px solid #94a3b8 !important;
  padding: 8px 12px !important;
  min-height: 40px !important;
  vertical-align: top !important;
  box-sizing: border-box !important;
  line-height: 1.6 !important;
  color: #1e293b !important;
}

.gdocs-workspace :deep(.ql-editor table td:first-child),
.gdocs-workspace :deep(.ql-editor table th:first-child) {
  width: 40px !important;
  text-align: center !important;
  font-weight: 600 !important;
}

.gdocs-workspace :deep(.ql-editor table tr:first-child td),
.gdocs-workspace :deep(.ql-editor table tr:first-child th) {
  background-color: #f1f5f9 !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  border-bottom: 2px solid #64748b !important;
}

.gdocs-workspace :deep(.ql-editor table td:hover) {
  background-color: #f8fafc !important;
}

.gdocs-workspace :deep(.ql-editor table td:focus),
.gdocs-workspace :deep(.ql-editor table td:focus-within) {
  outline: 2px solid #3b82f6 !important;
  outline-offset: -2px !important;
}

/* Dark mode tables */
:deep(.dark) .gdocs-workspace :deep(.ql-editor table) {
  border-color: #475569 !important;
}
:deep(.dark) .gdocs-workspace :deep(.ql-editor table td),
:deep(.dark) .gdocs-workspace :deep(.ql-editor table th) {
  border-color: #475569 !important;
  color: #f1f5f9 !important;
}
:deep(.dark) .gdocs-workspace :deep(.ql-editor table tr:first-child td),
:deep(.dark) .gdocs-workspace :deep(.ql-editor table tr:first-child th) {
  background-color: #1e293b !important;
  color: #f8fafc !important;
  border-bottom-color: #94a3b8 !important;
}
:deep(.dark) .gdocs-workspace :deep(.ql-editor table td:hover) {
  background-color: rgba(30, 41, 59, 0.7) !important;
}
</style>
