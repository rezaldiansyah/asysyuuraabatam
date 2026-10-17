<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white flex items-center gap-2.5">
          <i class="pi pi-shield text-primary text-2xl"></i>
          Role & Permissions (Matriks CRUD)
        </h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Atur hak akses Create, Read, Update, dan Delete (C-R-U-D) secara fleksibel untuk setiap role pada seluruh modul dan sub-fitur.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <Button 
          :label="allCollapsed ? 'Buka Semua Submenu' : 'Tutup Semua Submenu'" 
          :icon="allCollapsed ? 'pi pi-angle-double-down' : 'pi pi-angle-double-up'" 
          severity="secondary" 
          outlined 
          size="small" 
          @click="toggleAllSections"
        />
        <Button 
          label="Simpan Perubahan" 
          icon="pi pi-save" 
          severity="primary" 
          size="small" 
          :loading="saving" 
          @click="saveAll" 
        />
      </div>
    </div>

    <!-- Legend Bar for CRUD -->
    <div class="bg-white dark:bg-slate-800 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
      <div class="flex items-center gap-4 flex-wrap">
        <span class="font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
          <i class="pi pi-info-circle text-primary"></i> Panduan Hak Akses CRUD:
        </span>
        <div class="flex items-center gap-1.5">
          <span class="w-5 h-5 rounded bg-emerald-600 text-white font-bold text-[10px] flex items-center justify-center">C</span>
          <span class="text-slate-600 dark:text-slate-300"><strong>Create:</strong> Tambah data / unggah baru</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-5 h-5 rounded bg-blue-600 text-white font-bold text-[10px] flex items-center justify-center">R</span>
          <span class="text-slate-600 dark:text-slate-300"><strong>Read:</strong> Lihat data / cetak / download</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-5 h-5 rounded bg-amber-600 text-white font-bold text-[10px] flex items-center justify-center">U</span>
          <span class="text-slate-600 dark:text-slate-300"><strong>Update:</strong> Edit & perbarui data</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-5 h-5 rounded bg-rose-600 text-white font-bold text-[10px] flex items-center justify-center">D</span>
          <span class="text-slate-600 dark:text-slate-300"><strong>Delete:</strong> Hapus berkas / data</span>
        </div>
      </div>

      <div class="text-[11px] text-slate-400">
        Klik masing-masing huruf untuk aktifkan/nonaktifkan.
      </div>
    </div>

    <!-- Permission Matrix Table -->
    <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800">
      <div class="overflow-x-auto max-h-[calc(100vh-250px)]">
        <table class="w-full text-sm border-collapse">
          <thead class="sticky top-0 z-20">
            <tr class="bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm">
              <th class="text-left py-3.5 px-4 font-semibold text-slate-700 dark:text-slate-300 sticky left-0 bg-slate-100 dark:bg-slate-800 min-w-[270px] z-30">
                <div class="flex items-center justify-between">
                  <span>Menu / Modul Fitur</span>
                  <span class="text-xs font-normal text-slate-400">{{ menuDefinitions.length }} Modul</span>
                </div>
              </th>
              
              <th 
                v-for="role in roles" 
                :key="role.id" 
                class="text-center py-3.5 px-3 font-semibold text-slate-700 dark:text-slate-300 min-w-[140px] align-top"
              >
                <div class="flex flex-col items-center gap-1">
                  <span class="font-bold text-xs text-slate-800 dark:text-slate-100">{{ role.name }}</span>
                  <span class="text-[10px] font-mono text-slate-400">{{ role.code }}</span>
                  
                  <span 
                    class="text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded-full"
                    :class="getScopeBadgeClass(role.scope)"
                  >
                    {{ role.scope || 'role' }}
                  </span>

                  <!-- Quick Select Actions -->
                  <div v-if="role.code !== 'superadmin'" class="flex items-center gap-1.5 mt-1 text-[10px]">
                    <button 
                      type="button" 
                      @click="setRoleFullCrud(role)" 
                      class="text-emerald-600 dark:text-emerald-400 hover:underline px-1 py-0.5 rounded hover:bg-emerald-50 dark:hover:bg-emerald-950/30 transition"
                      title="Berikan semua akses CRUD"
                    >
                      CRUD
                    </button>
                    <span class="text-slate-300 dark:text-slate-600">|</span>
                    <button 
                      type="button" 
                      @click="setRoleReadOnly(role)" 
                      class="text-blue-600 dark:text-blue-400 hover:underline px-1 py-0.5 rounded hover:bg-blue-50 dark:hover:bg-blue-950/30 transition"
                      title="Setel hanya Read (Lihat saja)"
                    >
                      Read
                    </button>
                    <span class="text-slate-300 dark:text-slate-600">|</span>
                    <button 
                      type="button" 
                      @click="clearAll(role)" 
                      class="text-rose-500 hover:underline px-1 py-0.5 rounded hover:bg-rose-50 dark:hover:bg-rose-950/30 transition"
                      title="Reset semua akses"
                    >
                      Reset
                    </button>
                  </div>
                  <div v-else class="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold mt-1">
                    Akses Penuh (Root)
                  </div>
                </div>
              </th>
            </tr>
          </thead>

          <tbody>
            <template v-for="menu in menuDefinitions" :key="menu.key">
              <!-- PARENT ROW (MODULE LEVEL) -->
              <tr class="bg-slate-50/90 dark:bg-slate-800/60 border-b border-slate-200/80 dark:border-slate-700/80 hover:bg-slate-100/70 dark:hover:bg-slate-800/80 transition-colors">
                <td class="py-3 px-4 font-semibold text-slate-800 dark:text-slate-100 sticky left-0 bg-slate-50/95 dark:bg-slate-800/95 backdrop-blur-sm z-10">
                  <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2.5">
                      <div class="w-7 h-7 rounded-lg bg-primary/10 dark:bg-primary/20 flex items-center justify-center text-primary">
                        <i :class="menu.icon" class="text-xs"></i>
                      </div>
                      <div>
                        <div class="font-bold text-slate-800 dark:text-slate-100 text-xs">{{ menu.label }}</div>
                        <div class="text-[10px] font-normal text-slate-400 font-mono">{{ menu.key }}</div>
                      </div>
                    </div>

                    <button 
                      v-if="menu.children && menu.children.length > 0"
                      @click="toggleSection(menu.key)"
                      type="button"
                      class="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 transition"
                      :title="isCollapsed(menu.key) ? 'Tampilkan Submenu' : 'Sembunyikan Submenu'"
                    >
                      <i :class="isCollapsed(menu.key) ? 'pi pi-chevron-down' : 'pi pi-chevron-up'"></i>
                    </button>
                  </div>
                </td>

                <!-- Parent Checkbox: Aktifkan Modul di Sidebar -->
                <td v-for="role in roles" :key="role.id" class="text-center py-2.5 px-3">
                  <div v-if="role.code === 'superadmin'" class="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded">
                    <i class="pi pi-check text-[10px]"></i> Aktif
                  </div>
                  <div v-else class="flex flex-col items-center justify-center">
                    <Checkbox 
                      :modelValue="hasModuleAccess(role, menu.key)"
                      @update:modelValue="toggleModuleAccess(role, menu)" 
                      :binary="true"
                    />
                    <span class="text-[9px] text-slate-400 mt-0.5">
                      {{ hasModuleAccess(role, menu.key) ? 'Aktif' : 'Tutup' }}
                    </span>
                  </div>
                </td>
              </tr>

              <!-- SUBMENU / FEATURE ROWS (CRUD LEVEL) -->
              <template v-if="!isCollapsed(menu.key) && menu.children && menu.children.length > 0">
                <tr 
                  v-for="child in menu.children" 
                  :key="child.key" 
                  class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <td class="py-2.5 px-4 pl-12 text-slate-600 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    <div class="flex items-center gap-2">
                      <span class="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-600"></span>
                      <span class="text-xs font-medium">{{ child.label }}</span>
                      <span class="text-[10px] text-slate-400 font-mono ml-auto mr-2">({{ child.key }})</span>
                    </div>
                  </td>

                  <td v-for="role in roles" :key="role.id" class="text-center py-2 px-2.5">
                    <!-- Superadmin always has full access -->
                    <div v-if="role.code === 'superadmin'" class="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-0.5 rounded">
                      <i class="pi pi-check text-[10px]"></i> CRUD
                    </div>

                    <!-- If Parent Module is not enabled for this role -->
                    <div v-else-if="!hasModuleAccess(role, menu.key)" class="text-slate-300 dark:text-slate-600 text-xs">
                      —
                    </div>

                    <!-- Interactive C R U D Badges -->
                    <div v-else class="inline-flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200/80 dark:border-slate-700 shadow-2xs">
                      <!-- CREATE -->
                      <button 
                        type="button"
                        @click="toggleCrud(role, child.key, 'create')"
                        class="w-5 h-5 rounded text-[10px] font-extrabold transition-all flex items-center justify-center cursor-pointer select-none"
                        :class="hasCrud(role, child.key, 'create') 
                          ? 'bg-emerald-600 text-white shadow-xs scale-105' 
                          : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700'"
                        title="Create (Tambah / Unggah baru)"
                      >
                        C
                      </button>

                      <!-- READ -->
                      <button 
                        type="button"
                        @click="toggleCrud(role, child.key, 'read')"
                        class="w-5 h-5 rounded text-[10px] font-extrabold transition-all flex items-center justify-center cursor-pointer select-none"
                        :class="hasCrud(role, child.key, 'read') 
                          ? 'bg-blue-600 text-white shadow-xs scale-105' 
                          : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700'"
                        title="Read (Lihat data / cetak / unduh)"
                      >
                        R
                      </button>

                      <!-- UPDATE -->
                      <button 
                        type="button"
                        @click="toggleCrud(role, child.key, 'update')"
                        class="w-5 h-5 rounded text-[10px] font-extrabold transition-all flex items-center justify-center cursor-pointer select-none"
                        :class="hasCrud(role, child.key, 'update') 
                          ? 'bg-amber-600 text-white shadow-xs scale-105' 
                          : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700'"
                        title="Update (Edit / Perbarui data)"
                      >
                        U
                      </button>

                      <!-- DELETE -->
                      <button 
                        type="button"
                        @click="toggleCrud(role, child.key, 'delete')"
                        class="w-5 h-5 rounded text-[10px] font-extrabold transition-all flex items-center justify-center cursor-pointer select-none"
                        :class="hasCrud(role, child.key, 'delete') 
                          ? 'bg-rose-600 text-white shadow-xs scale-105' 
                          : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700'"
                        title="Delete (Hapus data / berkas)"
                      >
                        D
                      </button>
                    </div>
                  </td>
                </tr>
              </template>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Bottom Actions & Explanation -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
      <div class="flex items-start gap-3">
        <i class="pi pi-info-circle text-blue-500 text-lg mt-0.5"></i>
        <div class="text-xs text-slate-600 dark:text-slate-300">
          <p class="font-bold text-slate-800 dark:text-slate-100">Prinsip Keamanan Sistem (Enterprise RBAC):</p>
          <ul class="list-disc list-inside mt-0.5 space-y-0.5 text-slate-500 dark:text-slate-400">
            <li><strong>Superadmin:</strong> Memiliki akses penuh (C-R-U-D) ke seluruh modul secara otomatis tanpa batasan.</li>
            <li><strong>Role Pengguna:</strong> Hanya tombol atau aksi yang dicentang yang akan tampil dan diizinkan oleh sistem.</li>
            <li>Klik tombol <strong>"Simpan Perubahan"</strong> untuk menyimpan konfigurasi ke database.</li>
          </ul>
        </div>
      </div>

      <Button 
        label="Simpan Perubahan" 
        icon="pi pi-save" 
        severity="primary" 
        size="small" 
        :loading="saving" 
        @click="saveAll" 
        class="whitespace-nowrap w-full sm:w-auto"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

definePageMeta({ layout: 'dashboard' })

const api = useApi()
const toast = useToast()

const roles = ref<any[]>([])
const saving = ref(false)
const collapsedSections = ref<Record<string, boolean>>({})

// Definisi Struktur Menu & Sub-fitur
const menuDefinitions = [
  { 
    key: 'dashboard', label: 'Dashboard', icon: 'pi pi-home',
    children: [
      { key: 'dashboard.ringkasan', label: 'Ringkasan Statistik' }
    ]
  },
  { 
    key: 'akademik', label: 'Akademik', icon: 'pi pi-book',
    children: [
      { key: 'akademik.siswa', label: 'Data Siswa' },
      { key: 'akademik.guru', label: 'Data Guru' },
      { key: 'akademik.rombel', label: 'Rombel (Kelas)' },
      { key: 'akademik.jadwal', label: 'Jadwal Pelajaran' },
      { key: 'akademik.kalender', label: 'Kalender Pendidikan' },
      { key: 'akademik.absensi', label: 'Absensi Siswa' },
      { key: 'akademik.nilai', label: 'Nilai & Rapor' },
    ]
  },
  { 
    key: 'tahfidz', label: 'Tahfidz', icon: 'pi pi-bookmark',
    children: [
      { key: 'tahfidz.setoran', label: 'Setoran Hafalan' },
      { key: 'tahfidz.ujian', label: 'Ujian Tahfidz' },
      { key: 'tahfidz.laporan', label: 'Laporan Tahfidz' },
    ]
  },
  { 
    key: 'kesiswaan', label: 'Kesiswaan', icon: 'pi pi-trophy',
    children: [
      { key: 'kesiswaan.prestasi', label: 'Prestasi Siswa' },
      { key: 'kesiswaan.pelanggaran', label: 'Catatan Pelanggaran' },
      { key: 'kesiswaan.bk', label: 'Konseling (BK)' },
      { key: 'kesiswaan.uks', label: 'UKS / Kesehatan' },
    ]
  },
  { 
    key: 'keuangan', label: 'Keuangan', icon: 'pi pi-wallet',
    children: [
      { key: 'keuangan.transaksi', label: 'Transaksi & Tagihan' },
      { key: 'keuangan.laporan', label: 'Laporan Keuangan' },
    ]
  },
  { 
    key: 'kepegawaian', label: 'Kepegawaian', icon: 'pi pi-users',
    children: [
      { key: 'kepegawaian.pegawai', label: 'Data Pegawai & SK' },
      { key: 'kepegawaian.presensi', label: 'Presensi Pegawai' },
    ]
  },
  { 
    key: 'internal', label: 'Manajemen Internal', icon: 'pi pi-folder',
    children: [
      { key: 'internal.tugas', label: 'Tugas Saya (Manajemen Tugas / Kanban)' },
      { key: 'internal.dokumen', label: 'Pusat Unduhan (SOP/SK/Juknis)' },
      { key: 'internal.notulen', label: 'Notulen Rapat' },
      { key: 'internal.mutabaah', label: 'Mutabaah Harian' },
      { key: 'internal.rekap_mutabaah', label: 'Rekap Mutabaah' },
    ]
  },
  { 
    key: 'ppdb', label: 'Manajemen PPDB', icon: 'pi pi-id-card',
    children: [
      { key: 'ppdb.pendaftar', label: 'Data Pendaftar' },
      { key: 'ppdb.pengaturan-lp', label: 'Setup Landing Page' },
      { key: 'ppdb.pengaturan', label: 'Pengaturan PPDB' },
    ]
  },
  { 
    key: 'cms', label: 'CMS Portal', icon: 'pi pi-globe',
    children: [
      { key: 'cms.konten', label: 'Konten Landing Page' },
      { key: 'cms.berita', label: 'Berita & Artikel' },
      { key: 'cms.pengumuman', label: 'Pengumuman / Mading' },
      { key: 'cms.testimoni', label: 'Testimoni' },
      { key: 'cms.galeri', label: 'Galeri Foto' },
      { key: 'cms.video', label: 'Galeri Video' },
      { key: 'cms.teacher-of-month', label: 'Teacher of the Month' },
    ]
  },
  { 
    key: 'pengaturan', label: 'Pengaturan', icon: 'pi pi-cog',
    children: [
      { key: 'pengaturan.sekolah', label: 'Identitas Sekolah' },
      { key: 'pengaturan.kop_surat', label: 'Kop Surat & Cetak PDF' },
      { key: 'pengaturan.users', label: 'Manajemen User' },
      { key: 'pengaturan.roles', label: 'Role & Permissions' },
      { key: 'pengaturan.backup', label: 'Backup & Restore' },
    ]
  },
]

function getScopeBadgeClass(scope?: string) {
  switch (scope) {
    case 'sistem':
      return 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300'
    case 'yayasan':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
    case 'unit':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300'
    case 'portal':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'
    default:
      return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
  }
}

function isCollapsed(key: string): boolean {
  return !!collapsedSections.value[key]
}

function toggleSection(key: string) {
  collapsedSections.value[key] = !collapsedSections.value[key]
}

const allCollapsed = computed(() => {
  return menuDefinitions.filter(m => m.children && m.children.length > 0).every(m => collapsedSections.value[m.key])
})

function toggleAllSections() {
  const shouldCollapse = !allCollapsed.value
  for (const m of menuDefinitions) {
    if (m.children && m.children.length > 0) {
      collapsedSections.value[m.key] = shouldCollapse
    }
  }
}

// Module Level Access (Sidebar visibility)
function hasModuleAccess(role: any, moduleKey: string): boolean {
  if (role.code === 'superadmin') return true
  const perms = role.permissions || []
  return perms.includes(moduleKey) || perms.some((p: string) => p.startsWith(`${moduleKey}.`))
}

function toggleModuleAccess(role: any, menu: any) {
  if (!role.permissions) role.permissions = []
  const hasAccess = hasModuleAccess(role, menu.key)

  if (hasAccess) {
    // Remove parent module and all its child permissions
    role.permissions = role.permissions.filter((p: string) => 
      p !== menu.key && !p.startsWith(`${menu.key}.`)
    )
  } else {
    // Add parent module and default Read-Only to its children
    role.permissions.push(menu.key)
    if (menu.children) {
      for (const child of menu.children) {
        const readToken = `${child.key}:read`
        if (!role.permissions.includes(readToken)) {
          role.permissions.push(readToken)
        }
      }
    }
  }
}

// Feature Level CRUD Access
function hasCrud(role: any, featureKey: string, action: 'create' | 'read' | 'update' | 'delete'): boolean {
  if (role.code === 'superadmin') return true
  const perms = role.permissions || []

  // Exact token check e.g. "internal.dokumen:read"
  if (perms.includes(`${featureKey}:${action}`)) return true
  if (perms.includes(`${featureKey}:*`)) return true

  // Legacy fallback: if featureKey is directly present
  if (perms.includes(featureKey)) {
    return true
  }

  // If parent module is present without child restriction, default Read to true
  const parentKey = featureKey.split('.')[0]
  if (action === 'read' && perms.includes(parentKey)) {
    const hasAnyChildAction = perms.some((p: string) => p.startsWith(`${featureKey}:`))
    if (!hasAnyChildAction) {
      return true
    }
  }

  return false
}

function toggleCrud(role: any, featureKey: string, action: 'create' | 'read' | 'update' | 'delete') {
  if (!role.permissions) role.permissions = []
  const token = `${featureKey}:${action}`
  const parentKey = featureKey.split('.')[0]

  // Ensure parent module is enabled
  if (!role.permissions.includes(parentKey)) {
    role.permissions.push(parentKey)
  }

  const tokenIdx = role.permissions.indexOf(token)
  if (tokenIdx >= 0) {
    role.permissions.splice(tokenIdx, 1)
  } else {
    // If transitioning from legacy bare key, remove it first
    const bareIdx = role.permissions.indexOf(featureKey)
    if (bareIdx >= 0) {
      role.permissions.splice(bareIdx, 1)
    }
    role.permissions.push(token)
  }
}

// Quick presets per role
function setRoleFullCrud(role: any) {
  role.permissions = []
  for (const menu of menuDefinitions) {
    role.permissions.push(menu.key)
    if (menu.children) {
      for (const child of menu.children) {
        role.permissions.push(`${child.key}:create`)
        role.permissions.push(`${child.key}:read`)
        role.permissions.push(`${child.key}:update`)
        role.permissions.push(`${child.key}:delete`)
      }
    }
  }
}

function setRoleReadOnly(role: any) {
  role.permissions = []
  for (const menu of menuDefinitions) {
    role.permissions.push(menu.key)
    if (menu.children) {
      for (const child of menu.children) {
        role.permissions.push(`${child.key}:read`)
      }
    }
  }
}

function clearAll(role: any) {
  role.permissions = ['dashboard', 'dashboard.ringkasan:read']
}

async function loadRoles() {
  try {
    const data = await api.get('/roles/permissions')
    roles.value = data
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data role', life: 3000 })
  }
}

async function saveAll() {
  saving.value = true
  try {
    for (const role of roles.value) {
      if (role.code === 'superadmin') continue // Skip superadmin
      await api.put(`/roles/${role.id}/permissions`, {
        permissions: role.permissions || []
      })
    }
    toast.add({ 
      severity: 'success', 
      summary: 'Berhasil Disimpan', 
      detail: 'Seluruh konfigurasi matriks CRUD berhasil diperbarui.', 
      life: 3500 
    })
  } catch (e) {
    console.error('Save failed', e)
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan konfigurasi permissions', life: 3000 })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadRoles()
})
</script>
