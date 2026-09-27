<template>
  <div class="min-h-screen flex">
    <Toast />
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-50 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transform transition-all duration-300 lg:translate-x-0 overflow-y-auto overflow-x-hidden flex flex-col justify-between"
      :class="[
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        isCollapsed ? 'w-20' : 'w-64'
      ]"
    >
      <div>
        <!-- Logo Header -->
        <div class="h-16 flex items-center border-b border-slate-200 dark:border-slate-700 px-4 transition-all"
          :class="isCollapsed ? 'justify-center' : 'justify-between'">
          
          <NuxtLink to="/dashboard" class="flex items-center gap-3 min-w-0" :title="isCollapsed ? 'SIST Asy-Syuuraa' : ''">
            <div class="w-9 h-9 bg-primary rounded-xl flex items-center justify-center shrink-0 shadow-sm shadow-primary/30">
              <span class="text-white font-bold text-sm">AS</span>
            </div>
            <div v-show="!isCollapsed" class="font-bold text-primary dark:text-white truncate text-base leading-tight">
              SIST Asy-Syuuraa
            </div>
          </NuxtLink>

          <!-- Toggle Minimize Desktop Button (in sidebar header) -->
          <button
            v-show="!isCollapsed"
            @click="toggleCollapse"
            class="hidden lg:flex items-center justify-center w-7 h-7 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            title="Kecilkan Sidebar"
          >
            <i class="pi pi-angle-left text-sm"></i>
          </button>
        </div>

        <!-- Navigation Menu -->
        <nav class="space-y-1.5 transition-all" :class="isCollapsed ? 'p-2' : 'p-3'">
          <template v-for="item in menuItems" :key="item.label">
            
            <!-- Single Item -->
            <NuxtLink
              v-if="!item.children"
              :to="item.to"
              class="flex items-center rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition group"
              :class="isCollapsed ? 'justify-center p-3' : 'gap-3 px-3.5 py-2.5'"
              active-class="!bg-primary/10 !text-primary font-semibold"
              :title="item.label"
            >
              <i :class="item.icon" class="text-lg shrink-0 transition-transform group-hover:scale-110"></i>
              <span v-show="!isCollapsed" class="truncate text-sm">{{ item.label }}</span>
            </NuxtLink>

            <!-- Submenu Item -->
            <div v-else class="relative">
              <button
                @click="handleSubmenuClick(item.label)"
                class="w-full flex items-center rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition group"
                :class="isCollapsed ? 'justify-center p-3' : 'justify-between px-3.5 py-2.5'"
                :title="item.label"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <i :class="item.icon" class="text-lg shrink-0 transition-transform group-hover:scale-110"></i>
                  <span v-show="!isCollapsed" class="truncate text-sm">{{ item.label }}</span>
                </div>
                <i v-show="!isCollapsed" :class="openSubmenus.includes(item.label) ? 'pi pi-chevron-up' : 'pi pi-chevron-down'" class="text-[10px] text-slate-400"></i>
              </button>

              <!-- Submenu Links when expanded -->
              <div v-show="!isCollapsed && openSubmenus.includes(item.label)" class="ml-7 pl-2 mt-1 space-y-1 border-l-2 border-slate-100 dark:border-slate-700">
                <NuxtLink
                  v-for="child in item.children"
                  :key="child.label"
                  :to="child.to"
                  class="flex items-center px-3 py-2 rounded-lg text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 transition"
                  active-class="!bg-primary/10 !text-primary font-semibold"
                >
                  <span class="truncate">{{ child.label }}</span>
                </NuxtLink>
              </div>

              <!-- Collapsed Popover/Tooltip Menu -->
              <div 
                v-if="isCollapsed && activeHoverMenu === item.label"
                class="fixed left-20 ml-2 py-2 px-1 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 z-50 min-w-48 space-y-1"
                @mouseenter="activeHoverMenu = item.label"
                @mouseleave="activeHoverMenu = null"
              >
                <div class="px-3 py-1 text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 dark:border-slate-700 mb-1">
                  {{ item.label }}
                </div>
                <NuxtLink
                  v-for="child in item.children"
                  :key="child.label"
                  :to="child.to"
                  class="flex items-center px-3 py-1.5 rounded-lg text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
                  active-class="!bg-primary/10 !text-primary font-semibold"
                  @click="activeHoverMenu = null"
                >
                  {{ child.label }}
                </NuxtLink>
              </div>
            </div>

          </template>
        </nav>
      </div>

      <!-- Bottom Sidebar Collapse Toggle Bar (Always Accessible) -->
      <div class="p-3 border-t border-slate-200 dark:border-slate-700 hidden lg:block">
        <button
          @click="toggleCollapse"
          class="w-full flex items-center rounded-xl p-2.5 text-slate-500 hover:text-slate-800 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 transition"
          :class="isCollapsed ? 'justify-center' : 'justify-start gap-3'"
          :title="isCollapsed ? 'Perbesar Sidebar' : 'Kecilkan Sidebar'"
        >
          <i :class="isCollapsed ? 'pi pi-arrow-right' : 'pi pi-arrow-left'" class="text-sm"></i>
          <span v-show="!isCollapsed" class="text-xs font-medium">Kecilkan Menu</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div 
      class="flex-1 min-h-screen bg-slate-50 dark:bg-slate-900 transition-all duration-300 flex flex-col"
      :class="isCollapsed ? 'lg:ml-20' : 'lg:ml-64'"
    >
      <!-- Top Header -->
      <header class="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-4 lg:px-6 sticky top-0 z-30 shadow-sm">
        <div class="flex items-center gap-3">
          <!-- Mobile Toggle -->
          <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300">
            <i class="pi pi-bars text-lg"></i>
          </button>

          <!-- Desktop Quick Sidebar Toggle -->
          <button 
            @click="toggleCollapse" 
            class="hidden lg:flex items-center justify-center w-9 h-9 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 hover:text-slate-800 dark:hover:text-white transition"
            :title="isCollapsed ? 'Perbesar Sidebar' : 'Kecilkan Sidebar'"
          >
            <i class="pi pi-bars text-base"></i>
          </button>

          <!-- Breadcrumb placeholder -->
          <div class="text-xs lg:text-sm font-medium text-slate-500 dark:text-slate-400">
            SIST Asy-Syuuraa Dashboard
          </div>
        </div>

        <!-- User Menu (client-only to prevent hydration mismatch) -->
        <ClientOnly>
          <div class="flex items-center gap-3">
            <div class="hidden sm:flex flex-col text-right">
              <span class="text-xs font-bold text-slate-800 dark:text-white">{{ authStore.user?.full_name || authStore.user?.name || 'Super Administrator' }}</span>
              <span class="text-[10px] text-slate-400 uppercase tracking-wider">{{ authStore.user?.role?.name || 'Administrator' }}</span>
            </div>
            <Button severity="secondary" size="small" outlined class="!py-1.5 !px-3 text-xs" @click="handleLogout">
              <i class="pi pi-sign-out mr-1.5 text-xs"></i>
              Keluar
            </Button>
          </div>
          <template #fallback>
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400">Memuat...</span>
            </div>
          </template>
        </ClientOnly>
      </header>

      <!-- Page Content -->
      <main class="p-4 lg:p-6 flex-1">
        <slot />
      </main>
    </div>

    <!-- Mobile Overlay -->
    <div
      v-show="sidebarOpen"
      @click="sidebarOpen = false"
      class="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { navigation, type MenuItem } from '~/config/navigation'

const authStore = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)
const isCollapsed = ref(false)
const activeHoverMenu = ref<string | null>(null)
const openSubmenus = ref<string[]>(['Akademik', 'Keuangan'])

onMounted(() => {
  if (process.client) {
    const saved = localStorage.getItem('sidebar_collapsed')
    if (saved === 'true') {
      isCollapsed.value = true
    }
  }
})

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
  if (process.client) {
    localStorage.setItem('sidebar_collapsed', isCollapsed.value ? 'true' : 'false')
  }
}

function handleSubmenuClick(label: string) {
  if (isCollapsed.value) {
    // If collapsed, uncollapse so user sees submenus clearly
    isCollapsed.value = false
    openSubmenus.value = [label]
    if (process.client) {
      localStorage.setItem('sidebar_collapsed', 'false')
    }
  } else {
    toggleSubmenu(label)
  }
}

// Filter menu based on user role permissions
const menuItems = computed(() => {
  const role = authStore.user?.role
  const userRole = (role && typeof role === 'object' ? role.code : role) || 'guest'
  
  // Superadmin sees everything
  if (userRole === 'superadmin') return navigation
  
  // Get permissions from role object (loaded at login)
  const permissions: string[] = (role && typeof role === 'object' && (role as any).permissions) 
    ? (role as any).permissions 
    : []
  
  // If no permissions configured yet, show only Dashboard
  if (!permissions.length) {
    return navigation.filter(item => item.key === 'dashboard')
  }
  
  // Filter by permissions
  return navigation.filter(item => {
    if (item.key === 'dashboard') return true // Dashboard always visible
    return permissions.includes(item.key || '')
  })
})

function toggleSubmenu(label: string) {
  if (openSubmenus.value.includes(label)) {
    openSubmenus.value = openSubmenus.value.filter(s => s !== label)
  } else {
    openSubmenus.value.push(label)
  }
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>
