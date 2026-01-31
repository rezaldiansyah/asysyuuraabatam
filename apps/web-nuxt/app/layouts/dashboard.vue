<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transform transition-transform duration-200 lg:translate-x-0"
      :class="{ '-translate-x-full': !sidebarOpen }"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-700">
        <NuxtLink to="/dashboard" class="flex items-center gap-3">
          <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span class="text-white font-bold">AS</span>
          </div>
          <span class="font-bold text-primary dark:text-white">SIST Asy-Syuuraa</span>
        </NuxtLink>
      </div>

      <!-- Navigation Menu -->
      <nav class="p-4 space-y-2">
        <template v-for="item in menuItems" :key="item.label">
          <!-- Single Item -->
          <NuxtLink
            v-if="!item.children"
            :to="item.to"
            class="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            active-class="!bg-primary/10 !text-primary font-medium"
          >
            <i :class="item.icon" class="text-lg"></i>
            <span>{{ item.label }}</span>
          </NuxtLink>

          <!-- Submenu -->
          <div v-else>
            <button
              @click="toggleSubmenu(item.label)"
              class="w-full flex items-center justify-between px-4 py-3 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            >
              <div class="flex items-center gap-3">
                <i :class="item.icon" class="text-lg"></i>
                <span>{{ item.label }}</span>
              </div>
              <i :class="openSubmenus.includes(item.label) ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" class="text-xs"></i>
            </button>
            <div v-show="openSubmenus.includes(item.label)" class="ml-6 mt-1 space-y-1">
              <NuxtLink
                v-for="child in item.children"
                :key="child.label"
                :to="child.to"
                class="flex items-center gap-3 px-4 py-2 rounded-lg text-sm text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
                active-class="!bg-primary/10 !text-primary font-medium"
              >
                <span>{{ child.label }}</span>
              </NuxtLink>
            </div>
          </div>
        </template>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="lg:ml-64 flex-1 min-h-screen bg-slate-50 dark:bg-slate-900">
      <!-- Top Header -->
      <header class="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-6">
        <!-- Mobile Toggle -->
        <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700">
          <i class="pi pi-bars text-lg"></i>
        </button>

        <!-- Breadcrumb placeholder -->
        <div class="hidden lg:block text-slate-500 dark:text-slate-400">
          Dashboard
        </div>

        <!-- User Menu -->
        <div class="flex items-center gap-4">
          <span class="text-sm text-slate-600 dark:text-slate-300">{{ authStore.user?.name || 'User' }}</span>
          <Button severity="secondary" size="small" @click="handleLogout">
            <i class="pi pi-sign-out mr-2"></i>
            Logout
          </Button>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-6">
        <slot />
      </main>
    </div>

    <!-- Mobile Overlay -->
    <div
      v-show="sidebarOpen"
      @click="sidebarOpen = false"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)
const openSubmenus = ref<string[]>(['Akademik', 'Keuangan'])

const menuItems = [
  { label: 'Dashboard', icon: 'pi pi-home', to: '/dashboard' },
  {
    label: 'Akademik',
    icon: 'pi pi-book',
    children: [
      { label: 'Data Siswa', to: '/dashboard/siswa' },
      { label: 'Data Guru', to: '/dashboard/guru' },
      { label: 'Jadwal Pelajaran', to: '/dashboard/jadwal' },
      { label: 'Nilai Siswa', to: '/dashboard/nilai' },
    ],
  },
  {
    label: 'Absensi',
    icon: 'pi pi-check-square',
    children: [
      { label: 'Absensi Siswa', to: '/dashboard/absensi' },
    ],
  },
  {
    label: 'Tahfidz',
    icon: 'pi pi-bookmark',
    children: [
      { label: 'Setoran Harian', to: '/dashboard/tahfidz' },
    ],
  },
  {
    label: 'Keuangan',
    icon: 'pi pi-wallet',
    children: [
      { label: 'SPP & Tagihan', to: '/dashboard/keuangan' },
    ],
  },
  {
    label: 'CMS Website',
    icon: 'pi pi-send',
    children: [
      { label: 'Konten Landing Page', to: '/dashboard/cms/konten' },
      { label: 'Berita Sekolah', to: '/dashboard/berita' },
    ],
  },
  {
    label: 'Settings',
    icon: 'pi pi-cog',
    children: [
      { label: 'Manajemen User', to: '/dashboard/users' },
      { label: 'Konfigurasi Sekolah', to: '/dashboard/settings' },
    ],
  },
]

function toggleSubmenu(label: string) {
  if (openSubmenus.value.includes(label)) {
    openSubmenus.value = openSubmenus.value.filter((l) => l !== label)
  } else {
    openSubmenus.value.push(label)
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
