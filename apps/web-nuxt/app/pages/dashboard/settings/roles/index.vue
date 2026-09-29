<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Role & Permissions</h1>
        <p class="text-slate-500 dark:text-slate-400">Atur hak akses menu dan fitur untuk setiap role pengguna.</p>
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
          :loading="saving" 
          @click="saveAll" 
        />
      </div>
    </div>

    <!-- Permission Matrix -->
    <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800">
      <div class="overflow-x-auto max-h-[calc(100vh-250px)]">
        <table class="w-full text-sm border-collapse">
          <thead class="sticky top-0 z-20">
            <tr class="bg-slate-100 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm">
              <th class="text-left py-4 px-5 font-semibold text-slate-700 dark:text-slate-300 sticky left-0 bg-slate-100 dark:bg-slate-800 min-w-[260px] z-30">
                <div class="flex items-center justify-between">
                  <span>Menu / Modul Fitur</span>
                  <span class="text-xs font-normal text-slate-400">{{ menuDefinitions.length }} Modul</span>
                </div>
              </th>
              <th 
                v-for="role in roles" 
                :key="role.id" 
                class="text-center py-4 px-3 font-semibold text-slate-700 dark:text-slate-300 min-w-[125px] align-top"
              >
                <div class="flex flex-col items-center gap-1.5">
                  <span class="font-bold text-xs text-slate-800 dark:text-slate-100">{{ role.name }}</span>
                  <span class="text-[10px] font-mono text-slate-400">{{ role.code }}</span>
                  
                  <span 
                    class="text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded-full"
                    :class="getScopeBadgeClass(role.scope)"
                  >
                    {{ role.scope || 'role' }}
                  </span>

                  <!-- Quick select buttons for non-superadmin -->
                  <div v-if="role.code !== 'superadmin'" class="flex items-center gap-1 mt-1">
                    <button 
                      type="button" 
                      @click="selectAll(role)" 
                      class="text-[10px] text-primary hover:underline px-1 py-0.5 rounded hover:bg-primary/10 transition"
                      title="Beri semua akses"
                    >
                      Semua
                    </button>
                    <span class="text-slate-300 dark:text-slate-600 text-[10px]">|</span>
                    <button 
                      type="button" 
                      @click="clearAll(role)" 
                      class="text-[10px] text-slate-400 hover:text-red-500 hover:underline px-1 py-0.5 rounded hover:bg-red-500/10 transition"
                      title="Hapus semua akses"
                    >
                      Reset
                    </button>
                  </div>
                  <div v-else class="text-[10px] text-green-600 dark:text-green-400 font-semibold mt-1">
                    Akses Penuh
                  </div>

                  <span v-if="role.code !== 'superadmin'" class="text-[10px] text-slate-400">
                    {{ (role.permissions || []).length }}/{{ menuDefinitions.length }} aktif
                  </span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-for="menu in menuDefinitions" :key="menu.key">
              <!-- Parent Menu -->
              <tr class="bg-slate-50/80 dark:bg-slate-800/40 border-b border-slate-200/70 dark:border-slate-700/60 hover:bg-slate-100/60 dark:hover:bg-slate-800/60 transition-colors">
                <td class="py-3 px-5 font-semibold text-slate-800 dark:text-slate-100 sticky left-0 bg-slate-50/90 dark:bg-slate-800/90 backdrop-blur-sm z-10">
                  <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2.5">
                      <div class="w-7 h-7 rounded-lg bg-primary/10 dark:bg-primary/20 flex items-center justify-center text-primary">
                        <i :class="menu.icon" class="text-xs"></i>
                      </div>
                      <div>
                        <div class="font-medium text-slate-800 dark:text-slate-100">{{ menu.label }}</div>
                        <div class="text-[11px] font-normal text-slate-400">{{ menu.key }}</div>
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
                <td v-for="role in roles" :key="role.id" class="text-center py-3 px-3">
                  <Checkbox 
                    v-if="role.code !== 'superadmin'"
                    :modelValue="hasPermission(role, menu.key)"
                    @update:modelValue="togglePermission(role, menu.key)" 
                    :binary="true"
                  />
                  <i v-else class="pi pi-check-circle text-green-500 text-base" title="Superadmin memiliki akses penuh"></i>
                </td>
              </tr>

              <!-- Children / Submenus -->
              <template v-if="!isCollapsed(menu.key)">
                <tr 
                  v-for="child in menu.children" 
                  :key="child.key" 
                  class="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <td class="py-2.5 px-5 pl-14 text-slate-600 dark:text-slate-300 sticky left-0 bg-white dark:bg-slate-900 z-10">
                    <div class="flex items-center gap-2">
                      <span class="w-1.5 h-1.5 rounded-full bg-slate-300 dark:bg-slate-600"></span>
                      <span>{{ child.label }}</span>
                    </div>
                  </td>
                  <td v-for="role in roles" :key="role.id" class="text-center py-2.5 px-3">
                    <span v-if="role.code === 'superadmin'" class="text-green-500 font-bold text-xs">—</span>
                    <span 
                      v-else 
                      :class="hasPermission(role, menu.key) ? 'text-green-500 dark:text-green-400' : 'text-slate-300 dark:text-slate-600'"
                    >
                      <i :class="hasPermission(role, menu.key) ? 'pi pi-check font-bold' : 'pi pi-minus'" class="text-xs"></i>
                    </span>
                  </td>
                </tr>
              </template>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Info & Save Bar -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-200 dark:border-slate-700">
      <div class="flex items-start gap-3">
        <i class="pi pi-info-circle text-blue-500 text-lg mt-0.5"></i>
        <div class="text-xs sm:text-sm text-slate-600 dark:text-slate-300">
          <p class="font-medium text-slate-800 dark:text-slate-100">Ketentuan Akses Menu:</p>
          <ul class="list-disc list-inside mt-0.5 space-y-0.5 text-slate-500 dark:text-slate-400">
            <li><strong>Superadmin</strong> selalu memiliki akses ke seluruh modul dan submenu secara otomatis.</li>
            <li>Centang modul utama untuk memberikan hak akses kepada role yang bersangkutan beserta seluruh sub-fiturnya.</li>
            <li>Klik tombol <strong>"Simpan Perubahan"</strong> setelah menyesuaikan hak akses agar perubahan tersimpan ke sistem.</li>
          </ul>
        </div>
      </div>
      <Button 
        label="Simpan Perubahan" 
        icon="pi pi-save" 
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

// Define complete menu structure matching navigation.ts
const menuDefinitions = [
  { 
    key: 'dashboard', label: 'Dashboard', icon: 'pi pi-home',
    children: []
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
      { key: 'kesiswaan.prestasi', label: 'Prestasi' },
      { key: 'kesiswaan.pelanggaran', label: 'Pelanggaran' },
      { key: 'kesiswaan.bk', label: 'Konseling (BK)' },
      { key: 'kesiswaan.uks', label: 'UKS / Kesehatan' },
    ]
  },
  { 
    key: 'keuangan', label: 'Keuangan', icon: 'pi pi-wallet',
    children: []
  },
  { 
    key: 'kepegawaian', label: 'Kepegawaian', icon: 'pi pi-users',
    children: [
      { key: 'kepegawaian.pegawai', label: 'Data Pegawai' },
      { key: 'kepegawaian.presensi', label: 'Presensi Pegawai' },
    ]
  },
  { 
    key: 'internal', label: 'Manajemen Internal', icon: 'pi pi-folder',
    children: [
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

function hasPermission(role: any, menuKey: string): boolean {
  if (role.code === 'superadmin') return true
  return (role.permissions || []).includes(menuKey)
}

function togglePermission(role: any, menuKey: string) {
  if (!role.permissions) role.permissions = []
  
  const idx = role.permissions.indexOf(menuKey)
  if (idx >= 0) {
    role.permissions.splice(idx, 1)
  } else {
    role.permissions.push(menuKey)
  }
}

function selectAll(role: any) {
  role.permissions = menuDefinitions.map(m => m.key)
}

function clearAll(role: any) {
  // Always keep dashboard by default
  role.permissions = ['dashboard']
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
    toast.add({ severity: 'success', summary: 'Berhasil', detail: 'Semua permissions berhasil disimpan', life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menyimpan permissions', life: 3000 })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadRoles()
})
</script>
