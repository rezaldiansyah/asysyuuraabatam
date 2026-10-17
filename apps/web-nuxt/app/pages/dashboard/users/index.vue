<template>
  <div class="space-y-4 text-sm">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
      <div>
        <h1 class="text-xl font-semibold text-slate-800 dark:text-white">Manajemen Pengguna</h1>
        <p class="text-xs text-slate-500 dark:text-slate-400">
          Kelola akun pengguna, hak akses, dan status login sistem.
          <span class="font-medium text-slate-700 dark:text-slate-200 ml-1">
            Total: {{ users.length }} akun ({{ activeUsersCount }} aktif)
          </span>
        </p>
      </div>
      <div class="flex items-center gap-2">
        <Button 
          icon="pi pi-refresh" 
          severity="secondary" 
          outlined 
          size="small" 
          :loading="loading" 
          @click="fetchUsers" 
          title="Segarkan data"
        />
        <Button 
          label="Tambah Pengguna" 
          icon="pi pi-plus" 
          size="small" 
          @click="openDialog()" 
        />
      </div>
    </div>

    <!-- Filter Bar (Smart Search & Role Filter) -->
    <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl p-3 border border-slate-200 dark:border-slate-800">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        <!-- Smart Search Input -->
        <div class="relative w-full lg:col-span-2">
          <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
          <InputText 
            v-model="searchQuery" 
            placeholder="Cari nama, NIK/username, atau email..." 
            size="small" 
            class="w-full !pl-8 text-xs" 
          />
          <button 
            v-if="searchQuery" 
            @click="searchQuery = ''" 
            class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs"
            title="Hapus pencarian"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>

        <!-- Role Filter Dropdown -->
        <div class="w-full">
          <Select 
            v-model="selectedRole" 
            :options="roleFilterOptions" 
            optionLabel="label" 
            optionValue="value" 
            placeholder="Semua Role" 
            showClear 
            size="small" 
            class="w-full text-xs" 
          />
        </div>

        <!-- Status Filter Dropdown -->
        <div class="w-full">
          <Select 
            v-model="selectedStatus" 
            :options="statusFilterOptions" 
            optionLabel="label" 
            optionValue="value" 
            placeholder="Semua Status" 
            showClear 
            size="small" 
            class="w-full text-xs" 
          />
        </div>
      </div>

      <!-- Active Filter Status & Reset -->
      <div v-if="hasActiveFilters" class="flex items-center justify-between mt-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-500">
        <span>
          Menampilkan <b>{{ filteredUsers.length }}</b> dari total <b>{{ users.length }}</b> pengguna
        </span>
        <button 
          @click="resetFilters" 
          class="text-primary hover:underline font-medium flex items-center gap-1"
        >
          <i class="pi pi-filter-slash text-[10px]"></i> Reset Filter
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="card bg-white dark:bg-slate-900 shadow-sm rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden p-1">
      <DataTable 
        :value="filteredUsers" 
        :loading="loading" 
        dataKey="id"
        class="p-datatable-sm text-xs" 
        stripedRows 
        responsiveLayout="scroll"
        paginator 
        :rows="rowsPerPage" 
        :rowsPerPageOptions="[10, 20, 50, 100]"
        paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
        currentPageReportTemplate="Menampilkan {first}–{last} dari {totalRecords} pengguna"
      >
        <template #empty>
          <div class="text-center py-8 text-slate-400">
            <i class="pi pi-users text-3xl mb-2 opacity-50 block"></i>
            <span v-if="hasActiveFilters">Tidak ada pengguna yang cocok dengan kriteria filter.</span>
            <span v-else>Belum ada data pengguna di sistem.</span>
          </div>
        </template>
        
        <!-- NIK / Username Column -->
        <Column field="nik" header="NIK / Username" sortable style="min-width: 130px">
          <template #body="{ data }">
            <span class="font-mono text-slate-700 dark:text-slate-300 font-medium">
              {{ data.nik || '-' }}
            </span>
          </template>
        </Column>
        
        <!-- Full Name & Avatar Column -->
        <Column field="full_name" header="Nama Lengkap" sortable style="min-width: 220px">
          <template #body="{ data }">
            <div class="flex items-center gap-2.5 py-0.5">
              <Avatar 
                :label="getInitials(data.full_name)" 
                shape="circle" 
                class="w-7 h-7 text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/50" 
              />
              <div class="flex flex-col">
                <span class="font-medium text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
                  {{ data.full_name }}
                  <span v-if="data.id === currentUserId" class="text-[10px] text-primary bg-primary/10 px-1.5 py-0.2 rounded font-normal">
                    Anda
                  </span>
                </span>
                <span class="text-[11px] text-slate-400 sm:hidden">{{ data.email }}</span>
              </div>
            </div>
          </template>
        </Column>
        
        <!-- Email Column -->
        <Column field="email" header="Email" sortable style="min-width: 200px">
          <template #body="{ data }">
            <span class="text-slate-600 dark:text-slate-300">{{ data.email }}</span>
          </template>
        </Column>
        
        <!-- Role Column -->
        <Column field="role.name" header="Role / Akses" sortable style="min-width: 150px">
          <template #body="{ data }">
            <Tag 
              :value="data.role?.name || '-'" 
              :severity="getRoleSeverity(data.role?.code)" 
              class="text-[11px] font-medium py-0.5 px-2"
            />
          </template>
        </Column>
        
        <!-- Status Column -->
        <Column field="is_active" header="Status" sortable style="min-width: 110px">
          <template #body="{ data }">
            <Tag 
              :value="data.is_active ? 'Aktif' : 'Non-Aktif'" 
              :severity="data.is_active ? 'success' : 'danger'" 
              class="text-[11px] py-0.5 px-2"
            />
          </template>
        </Column>
        
        <!-- Action Column -->
        <Column header="Aksi" style="width: 110px" :exportable="false">
          <template #body="{ data }">
            <div class="flex items-center justify-end gap-1">
              <Button 
                icon="pi pi-pencil" 
                text 
                rounded 
                size="small" 
                severity="secondary"
                @click="openDialog(data)" 
                title="Edit data / reset password" 
              />
              
              <Button 
                v-if="data.role?.code !== 'superadmin' && data.id !== currentUserId" 
                icon="pi pi-trash" 
                text 
                rounded 
                severity="danger" 
                size="small" 
                @click="confirmDelete(data)" 
                title="Hapus akun" 
              />

              <Tag 
                v-else-if="data.role?.code === 'superadmin'" 
                value="Dilindungi" 
                severity="secondary" 
                class="text-[10px] py-0.5 px-1.5 opacity-75" 
                title="Akun Superadmin dilindungi dari penghapusan" 
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
    
    <!-- User Form Dialog -->
    <DashboardUsersUserFormDialog 
      v-if="dialogVisible" 
      v-model:visible="dialogVisible" 
      :user="selectedUser" 
      :roles="roles"
      @saved="fetchUsers" 
      @close="dialogVisible = false"
    />
    
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { useConfirm } from "primevue/useconfirm"
import { useToast } from "primevue/usetoast"
import { useAuthStore } from "~/stores/auth"

definePageMeta({
  layout: 'dashboard'
})

const api = useApi()
const confirm = useConfirm()
const toast = useToast()
const authStore = useAuthStore()

const currentUserId = computed(() => authStore.user?.id)

const users = ref<any[]>([])
const roles = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const selectedUser = ref<any>(null)

// Filter states
const searchQuery = ref('')
const selectedRole = ref<number | null>(null)
const selectedStatus = ref<boolean | null>(null)
const rowsPerPage = ref(10)

onMounted(() => {
  fetchUsers()
  fetchRoles()
})

async function fetchUsers() {
  loading.value = true
  try {
    const data = await api.get<any[]>('/users?limit=1000')
    users.value = data || []
  } catch (e) {
    console.error('Failed to fetch users', e)
    toast.add({ 
      severity: 'error', 
      summary: 'Gagal', 
      detail: 'Gagal memuat data pengguna dari server', 
      life: 3000 
    })
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  try {
    const data = await api.get<any[]>('/roles')
    roles.value = data || []
  } catch (e) {
    console.error('Failed to fetch roles', e)
  }
}

// Role filter dropdown options
const roleFilterOptions = computed(() => {
  return roles.value.map(r => ({
    label: r.name,
    value: r.id
  }))
})

// Status filter dropdown options
const statusFilterOptions = [
  { label: 'Aktif', value: true },
  { label: 'Non-Aktif', value: false }
]

// Active filter check
const hasActiveFilters = computed(() => {
  return !!searchQuery.value.trim() || selectedRole.value !== null || selectedStatus.value !== null
})

function resetFilters() {
  searchQuery.value = ''
  selectedRole.value = null
  selectedStatus.value = null
}

// Smart Filtered Users
const filteredUsers = computed(() => {
  let list = users.value || []

  // 1. Search Query Filter
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(u => {
      const name = (u.full_name || '').toLowerCase()
      const email = (u.email || '').toLowerCase()
      const nik = (u.nik || '').toLowerCase()
      const roleName = (u.role?.name || '').toLowerCase()
      const roleCode = (u.role?.code || '').toLowerCase()

      return name.includes(q) || email.includes(q) || nik.includes(q) || roleName.includes(q) || roleCode.includes(q)
    })
  }

  // 2. Role Filter
  if (selectedRole.value !== null) {
    list = list.filter(u => u.role_id === selectedRole.value || u.role?.id === selectedRole.value)
  }

  // 3. Status Filter
  if (selectedStatus.value !== null) {
    list = list.filter(u => Boolean(u.is_active) === selectedStatus.value)
  }

  return list
})

// Active users count
const activeUsersCount = computed(() => {
  return users.value.filter(u => u.is_active).length
})

function openDialog(user: any = null) {
  selectedUser.value = user
  dialogVisible.value = true
}

function confirmDelete(user: any) {
  if (user.role?.code === 'superadmin') {
    toast.add({ 
      severity: 'warn', 
      summary: 'Dilindungi', 
      detail: 'Akun Super Administrator dilindungi dan tidak dapat dihapus',
      life: 3000
    })
    return
  }

  if (user.id === currentUserId.value) {
    toast.add({ 
      severity: 'warn', 
      summary: 'Ditolak', 
      detail: 'Anda tidak dapat menghapus akun Anda sendiri yang sedang digunakan',
      life: 3000
    })
    return
  }

  confirm.require({
    message: `Apakah Anda yakin ingin menghapus akun pengguna "${user.full_name}" (${user.email})?`,
    header: 'Konfirmasi Hapus Pengguna',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger p-button-sm',
    rejectClass: 'p-button-text p-button-sm',
    acceptLabel: 'Ya, Hapus',
    rejectLabel: 'Batal',
    accept: async () => {
      try {
        await api.delete(`/users/${user.id}`)
        toast.add({ 
          severity: 'success', 
          summary: 'Berhasil', 
          detail: `Pengguna ${user.full_name} berhasil dihapus`,
          life: 3000
        })
        fetchUsers()
      } catch (e: any) {
        console.error('Delete user error:', e)
        toast.add({ 
          severity: 'error', 
          summary: 'Gagal Menghapus', 
          detail: e?.data?.detail || e?.message || 'Gagal menghapus user',
          life: 4000
        })
      }
    }
  })
}

function getRoleSeverity(code?: string) {
  switch (code) {
    case 'superadmin': return 'danger'
    case 'ketua_yayasan':
    case 'wakil_ketua_yayasan': return 'warn'
    case 'kabid_umum':
    case 'kabid_keuangan': return 'info'
    case 'kepala_unit':
    case 'wakil_kepala': return 'success'
    case 'guru': return 'info'
    default: return 'secondary'
  }
}

function getInitials(name?: string) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase()
  return (parts[0][0] + parts[1][0]).toUpperCase()
}
</script>
