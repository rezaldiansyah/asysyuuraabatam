<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900">
    <!-- Public Navbar -->
    <nav class="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
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

          <!-- Navigation Links -->
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

          <!-- Auth Button -->
          <div class="flex items-center gap-4">
            <NuxtLink
              to="/login"
              class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition font-medium"
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
              Sekolah Islam Terpadu yang mengedepankan pendidikan akademik dan karakter Islami.
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
              <li>📍 Batam, Kepulauan Riau</li>
              <li>📞 (0778) xxx-xxxx</li>
              <li>✉️ info@asy-syuuraa.sch.id</li>
            </ul>
          </div>

          <!-- Social -->
          <div>
            <h3 class="font-bold text-lg mb-4">Media Sosial</h3>
            <div class="flex gap-4">
              <a href="#" class="text-slate-400 hover:text-secondary">Instagram</a>
              <a href="#" class="text-slate-400 hover:text-secondary">Facebook</a>
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
