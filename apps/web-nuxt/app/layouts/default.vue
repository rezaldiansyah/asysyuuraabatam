<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900">
    <!-- Public Navbar -->
    <nav class="sticky top-0 z-50 bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <NuxtLink to="/" class="flex items-center gap-3">
              <div class="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">AS</span>
              </div>
              <span class="font-bold text-lg text-primary dark:text-white">Asy-Syuuraa</span>
            </NuxtLink>
          </div>

          <!-- Navigation Links (Desktop) -->
          <div class="hidden md:flex items-center gap-6">
            <NuxtLink to="/" class="text-slate-600 dark:text-slate-300 hover:text-primary transition">
              Beranda
            </NuxtLink>
            <NuxtLink to="/profil" class="text-slate-600 dark:text-slate-300 hover:text-primary transition">
              Profil
            </NuxtLink>
            <NuxtLink to="/unit" class="text-slate-600 dark:text-slate-300 hover:text-primary transition">
              Unit Pendidikan
            </NuxtLink>
            <NuxtLink to="/ppdb" class="text-slate-600 dark:text-slate-300 hover:text-primary transition">
              PPDB
            </NuxtLink>
            <NuxtLink to="/berita" class="text-slate-600 dark:text-slate-300 hover:text-primary transition">
              Berita
            </NuxtLink>
          </div>

          <!-- Auth Button (Desktop) + Mobile Toggle -->
          <div class="flex items-center gap-4">
            <NuxtLink
              to="/login"
              class="hidden md:inline-block px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium"
            >
              Login
            </NuxtLink>

            <!-- Mobile Hamburger -->
            <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700">
              <svg v-if="!mobileMenuOpen" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-600 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-600 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Menu Dropdown -->
      <div v-show="mobileMenuOpen" class="md:hidden border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-lg">
        <div class="px-4 py-4 space-y-3">
          <NuxtLink to="/" class="block text-slate-600 dark:text-slate-300 hover:text-primary transition py-2" @click="mobileMenuOpen = false">
            Beranda
          </NuxtLink>
          <NuxtLink to="/profil" class="block text-slate-600 dark:text-slate-300 hover:text-primary transition py-2" @click="mobileMenuOpen = false">
            Profil
          </NuxtLink>
          <NuxtLink to="/unit" class="block text-slate-600 dark:text-slate-300 hover:text-primary transition py-2" @click="mobileMenuOpen = false">
            Unit Pendidikan
          </NuxtLink>
          <NuxtLink to="/ppdb" class="block text-slate-600 dark:text-slate-300 hover:text-primary transition py-2" @click="mobileMenuOpen = false">
            PPDB
          </NuxtLink>
          <NuxtLink to="/berita" class="block text-slate-600 dark:text-slate-300 hover:text-primary transition py-2" @click="mobileMenuOpen = false">
            Berita
          </NuxtLink>
          <div class="pt-2 border-t border-slate-200 dark:border-slate-700">
            <NuxtLink
              to="/login"
              class="block w-full text-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium"
              @click="mobileMenuOpen = false"
            >
              Login
            </NuxtLink>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <footer class="bg-slate-800 text-white py-12 mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-8">
          <!-- About -->
          <div>
            <h3 class="font-bold text-lg mb-4">Asy-Syuuraa Batam</h3>
            <p class="text-slate-400 text-sm">
              {{ footer.about }}
            </p>
          </div>

          <!-- Quick Links -->
          <div>
            <h3 class="font-bold text-lg mb-4">Unit Pendidikan</h3>
            <ul class="space-y-2 text-slate-400 text-sm">
              <li><NuxtLink to="/unit/ra" class="hover:text-secondary">RA (TK Islam)</NuxtLink></li>
              <li><NuxtLink to="/unit/sdit" class="hover:text-secondary">SDIT</NuxtLink></li>
              <li><NuxtLink to="/unit/smpit" class="hover:text-secondary">SMPIT</NuxtLink></li>
            </ul>
          </div>

          <!-- Contact -->
          <div>
            <h3 class="font-bold text-lg mb-4">Kontak</h3>
            <ul class="space-y-2 text-slate-400 text-sm">
              <li>📍 {{ footer.address }}</li>
              <li>📞 {{ footer.phone }}</li>
              <li>✉️ {{ footer.email }}</li>
            </ul>
          </div>

          <!-- Social -->
          <div>
            <h3 class="font-bold text-lg mb-4">Media Sosial</h3>
            <div class="flex gap-4">
              <a v-if="footer.instagram" :href="footer.instagram" target="_blank" class="text-slate-400 hover:text-secondary">Instagram</a>
              <a v-if="footer.facebook" :href="footer.facebook" target="_blank" class="text-slate-400 hover:text-secondary">Facebook</a>
              <span v-if="!footer.instagram && !footer.facebook" class="text-slate-400 text-sm">Belum ada link</span>
            </div>
          </div>
        </div>

        <div class="border-t border-slate-700 mt-8 pt-8 text-center text-slate-400 text-sm">
          © 2026 Yayasan Asy-Syuuraa Batam. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const mobileMenuOpen = ref(false)

// Close mobile menu on route change
const route = useRoute()
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

const { public: { apiBase } } = useRuntimeConfig()

// Default Footer Data
const defaultFooter = {
  about: 'Sekolah Islam Terpadu yang mengedepankan pendidikan akademik dan karakter Islami.',
  address: 'Batam, Kepulauan Riau',
  phone: '(0778) xxx-xxxx',
  email: 'info@asy-syuuraa.sch.id',
  instagram: '',
  facebook: ''
}

// Fetch Footer Data globally
const { data: footerData } = await useAsyncData('layout-footer', async () => {
  try {
    const res = await $fetch<any>(`${apiBase}/public/content/settings_footer`)
    if (res && res.content_json) {
      return JSON.parse(res.content_json)
    }
  } catch (e) {
    // Ignore error if not set yet
  }
  return defaultFooter
})

const footer = computed(() => {
  return { ...defaultFooter, ...(footerData.value || {}) }
})
</script>
