// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from '@primevue/themes/aura'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  // Modules
  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/color-mode',
    '@primevue/nuxt-module',
    '@pinia/nuxt',
    '@vee-validate/nuxt',
  ],

  // App configuration
  app: {
    head: {
      title: 'Asy-Syuuraa Batam - Sistem Informasi Sekolah',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Sistem Informasi Sekolah Terpadu Asy-Syuuraa Batam' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      ],
    },
  },

  // Runtime config - environment variables
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },

  // PrimeVue configuration
  primevue: {
    options: {
      theme: {
        preset: Aura,
        options: {
          darkModeSelector: '.dark',
        },
      },
    },
  },

  // Color mode configuration
  colorMode: {
    classSuffix: '',
    preference: 'system',
    fallback: 'light',
  },

  // Tailwind configuration
  tailwindcss: {
    cssPath: '~/assets/css/main.css',
  },

  // VeeValidate configuration
  veeValidate: {
    autoImports: true,
  },

  // TypeScript configuration
  typescript: {
    strict: true,
  },
})
