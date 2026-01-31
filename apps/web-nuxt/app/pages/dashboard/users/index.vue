<template>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-slate-800 dark:text-white">Manajemen User</h1>
          <p class="text-slate-500 dark:text-slate-400">Kelola akun pengguna dan hak akses sistem</p>
        </div>
        <Button label="Tambah User" icon="pi pi-plus" @click="openDialog()" />
      </div>

      <!-- Table -->
      <div class="card bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl overflow-hidden">
        <DataTable 
          :value="users" 
          :loading="loading" 
          paginator 
          :rows="10"
          tableStyle="min-width: 50rem"
        >
          <template #empty>Tidak ada data user.</template>
          
          <Column field="nik" header="NIK / Username" sortable></Column>
          
          <Column field="full_name" header="Nama Lengkap" sortable>
            <template #body="slotProps">
               <div class="flex items-center gap-2">
                  <Avatar :label="slotProps.data.full_name?.charAt(0)" shape="circle" size="small" class="bg-primary/10 text-primary" />
                  <span class="font-medium">{{ slotProps.data.full_name }}</span>
               </div>
            </template>
          </Column>
          
          <Column field="email" header="Email" sortable></Column>
          
          <Column field="role.name" header="Role" sortable>
             <template #body="slotProps">
                <Tag 
                  :value="slotProps.data.role?.name || '-'" 
                  :severity="getRoleSeverity(slotProps.data.role?.code)" 
                />
             </template>
          </Column>
          
          <Column field="is_active" header="Status" sortable>
            <template #body="slotProps">
               <Tag 
                :value="slotProps.data.is_active ? 'Aktif' : 'Non-Aktif'" 
                :severity="slotProps.data.is_active ? 'success' : 'danger'" 
                icon="pi pi-circle-fill"
                class="bg-opacity-10"
              />
            </template>
          </Column>
          
           <Column header="Aksi" style="width: 100px">
              <template #body="slotProps">
                 <div class="flex gap-1 justify-end">
                    <Button icon="pi pi-pencil" text rounded size="small" @click="openDialog(slotProps.data)" v-tooltip.top="'Edit'" />
                    <Button icon="pi pi-trash" text rounded severity="danger" size="small" @click="confirmDelete(slotProps.data)" v-tooltip.top="'Hapus'" />
                 </div>
              </template>
          </Column>
        </DataTable>
      </div>
      
      <!-- Dialog -->
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

definePageMeta({
    layout: 'dashboard'
    // middleware: ['auth'] - Handled by auth.global.ts
})

const api = useApi()
const confirm = useConfirm()
const toast = useToast()

const users = ref([])
const roles = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const selectedUser = ref(null)

onMounted(() => {
    fetchUsers()
    fetchRoles()
})

async function fetchUsers() {
    loading.value = true
    try {
        const data = await api.get('/users')
        users.value = data
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Gagal memuat data users' })
    } finally {
        loading.value = false
    }
}

async function fetchRoles() {
    try {
        const data = await api.get('/roles')
        roles.value = data
    } catch (e) {
        console.error('Failed to fetch roles', e)
    }
}

function openDialog(user = null) {
    selectedUser.value = user
    dialogVisible.value = true
}

function confirmDelete(user: any) {
    confirm.require({
        message: `Apakah Anda yakin ingin menghapus user ${user.full_name}?`,
        header: 'Konfirmasi Hapus',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: async () => {
            try {
                await api.delete(`/users/${user.id}`)
                toast.add({ severity: 'success', summary: 'Sukses', detail: 'User berhasil dihapus' })
                fetchUsers()
            } catch (e) {
                toast.add({ severity: 'error', summary: 'Gagal', detail: 'Gagal menghapus user' })
            }
        }
    })
}

function getRoleSeverity(code: string) {
    switch (code) {
        case 'superadmin': return 'danger'
        case 'yayasan': return 'warning'
        case 'guru': return 'info'
        case 'siswa': return 'success'
        default: return 'secondary'
    }
}
</script>
