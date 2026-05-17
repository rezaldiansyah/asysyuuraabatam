<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Role & Permissions</h1>
      <p class="text-slate-500 dark:text-slate-400">Atur menu dan halaman yang dapat diakses oleh setiap role.</p>
    </div>

    <!-- Permission Matrix -->
    <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
              <th class="text-left py-4 px-5 font-semibold text-slate-700 dark:text-slate-300 sticky left-0 bg-slate-50 dark:bg-slate-800 min-w-[220px] z-10">
                Menu / Halaman
              </th>
              <th 
                v-for="role in roles" 
                :key="role.id" 
                class="text-center py-4 px-3 font-semibold text-slate-700 dark:text-slate-300 min-w-[100px]"
              >
                <div class="flex flex-col items-center gap-1">
                  <span>{{ role.name }}</span>
                  <span class="text-xs font-normal text-slate-400">{{ role.code }}</span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-for="menu in menuDefinitions" :key="menu.key">
              <!-- Parent Menu -->
              <tr class="bg-slate-50/50 dark:bg-slate-800/30 border-b border-slate-100 dark:border-slate-700/50">
                <td class="py-3 px-5 font-semibold text-slate-700 dark:text-slate-200 sticky left-0 bg-slate-50/50 dark:bg-slate-800/30 z-10">
                  <div class="flex items-center gap-2">
                    <i :class="menu.icon" class="text-primary"></i>
                    {{ menu.label }}
                  </div>
                </td>
                <td v-for="role in roles" :key="role.id" class="text-center py-3 px-3">
                  <Checkbox 
                    v-if="role.code !== 'superadmin'"
                    :modelValue="hasPermission(role, menu.key)"
                    @update:modelValue="togglePermission(role, menu.key)" 
                    :binary="true"
                  />
                  <i v-else class="pi pi-check-circle text-green-500 text-lg" title="Superadmin memiliki akses penuh"></i>
                </td>
              </tr>
              <!-- Children -->
              <tr 
                v-for="child in menu.children" 
                :key="child.key" 
                class="border-b border-slate-100 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-800/20 transition-colors"
              >
                <td class="py-2.5 px-5 pl-12 text-slate-500 dark:text-slate-400 sticky left-0 bg-white dark:bg-slate-900 z-10">
                  {{ child.label }}
                </td>
                <td v-for="role in roles" :key="role.id" class="text-center py-2.5 px-3">
                  <span v-if="role.code === 'superadmin'" class="text-green-400">—</span>
                  <span v-else :class="hasPermission(role, menu.key) ? 'text-green-400' : 'text-slate-300 dark:text-slate-600'">
                    <i :class="hasPermission(role, menu.key) ? 'pi pi-check' : 'pi pi-minus'"></i>
                  </span>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Info & Save -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800 flex-1">
        <p class="text-sm text-blue-700 dark:text-blue-400">
          <i class="pi pi-info-circle mr-1"></i>
          <strong>Superadmin</strong> selalu memiliki akses penuh ke semua menu. Centang menu di setiap kolom role untuk memberikan akses.
        </p>
      </div>
      <Button 
        label="Simpan Semua Perubahan" 
        icon="pi pi-save" 
        :loading="saving" 
        @click="saveAll" 
        class="whitespace-nowrap"
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

// Define the menu structure that maps to navigation.ts
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
      { key: 'tahfidz.laporan', label: 'Laporan' },
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
    key: 'ppdb', label: 'Manajemen PPDB', icon: 'pi pi-id-card',
    children: [
      { key: 'ppdb.pendaftar', label: 'Data Pendaftar' },
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
