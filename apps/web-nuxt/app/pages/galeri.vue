<template>
  <div class="min-h-screen bg-white dark:bg-slate-900">
    <!-- Hero -->
    <section class="bg-gradient-to-r from-emerald-700 to-emerald-900 text-white py-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h1 class="text-4xl font-bold mb-3">Galeri Asy-Syuuraa</h1>
        <p class="text-emerald-100 text-lg max-w-2xl mx-auto">Dokumentasi kegiatan dan prestasi siswa/siswi Yayasan Asy-Syuuraa Batam</p>
      </div>
    </section>

    <!-- Tabs -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-center gap-2 mb-8">
        <button 
          v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          class="px-6 py-2.5 rounded-full font-medium text-sm transition-all"
          :class="activeTab === tab.key 
            ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-200 dark:shadow-none' 
            : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'"
        >
          <i :class="tab.icon" class="mr-2"></i>{{ tab.label }}
        </button>
      </div>

      <!-- Albums Grid -->
      <div v-if="filteredAlbums.length" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="album in filteredAlbums" :key="album.id" 
          class="group cursor-pointer"
          @click="openAlbum(album)"
        >
          <div class="relative rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-shadow aspect-[4/3]">
            <img v-if="album.cover_url" :src="album.cover_url" :alt="album.title" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
            <div v-else class="w-full h-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              <i class="pi pi-images text-6xl text-slate-300"></i>
            </div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
            <div class="absolute bottom-0 left-0 right-0 p-4 text-white">
              <h3 class="font-bold text-lg">{{ album.title }}</h3>
              <p class="text-sm text-white/80">{{ album.photo_count }} foto</p>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-20 text-slate-400">
        <i class="pi pi-images text-6xl mb-4 block"></i>
        <p class="text-lg">Belum ada album di kategori ini.</p>
      </div>
    </div>

    <!-- Lightbox Dialog -->
    <Dialog v-model:visible="lightboxVisible" :header="selectedAlbum?.title || 'Album'" modal class="w-full max-w-4xl">
      <div v-if="selectedPhotos.length" class="space-y-4">
        <!-- Main Image -->
        <div class="relative bg-black rounded-lg overflow-hidden" style="min-height: 300px; max-height: 500px;">
          <img :src="selectedPhotos[currentIndex]?.image_url" :alt="selectedPhotos[currentIndex]?.caption" class="w-full h-full object-contain mx-auto" style="max-height: 500px;" />
          <!-- Nav Arrows -->
          <button v-if="selectedPhotos.length > 1" @click="prevPhoto" class="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/20 hover:bg-white/40 text-white flex items-center justify-center backdrop-blur-sm transition">
            <i class="pi pi-chevron-left"></i>
          </button>
          <button v-if="selectedPhotos.length > 1" @click="nextPhoto" class="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-white/20 hover:bg-white/40 text-white flex items-center justify-center backdrop-blur-sm transition">
            <i class="pi pi-chevron-right"></i>
          </button>
        </div>
        <p v-if="selectedPhotos[currentIndex]?.caption" class="text-center text-slate-600 dark:text-slate-300">{{ selectedPhotos[currentIndex]?.caption }}</p>
        <p class="text-center text-xs text-slate-400">{{ currentIndex + 1 }} / {{ selectedPhotos.length }}</p>

        <!-- Thumbnail Strip -->
        <div class="flex gap-2 overflow-x-auto pb-2">
          <button v-for="(photo, idx) in selectedPhotos" :key="photo.id" @click="currentIndex = idx"
            class="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-all"
            :class="idx === currentIndex ? 'border-emerald-500 opacity-100' : 'border-transparent opacity-60 hover:opacity-80'"
          >
            <img :src="photo.image_url" :alt="photo.caption" class="w-full h-full object-cover" />
          </button>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'default' })

useHead({ title: 'Galeri - Asy-Syuuraa Batam' })

const config = useRuntimeConfig()

const tabs = [
  { key: 'kegiatan', label: 'Kegiatan', icon: 'pi pi-calendar' },
  { key: 'prestasi', label: 'Prestasi', icon: 'pi pi-trophy' },
]

const activeTab = ref('kegiatan')
const albums = ref<any[]>([])
const lightboxVisible = ref(false)
const selectedAlbum = ref<any>(null)
const selectedPhotos = ref<any[]>([])
const currentIndex = ref(0)

const filteredAlbums = computed(() => albums.value.filter(a => a.category === activeTab.value))

onMounted(async () => {
  try {
    albums.value = await $fetch<any[]>(`${config.public.apiBase}/marketing/gallery/albums?published_only=true`)
  } catch (e) {
    console.error('Failed to load gallery', e)
  }
})

async function openAlbum(album: any) {
  selectedAlbum.value = album
  currentIndex.value = 0
  try {
    const data = await $fetch<any>(`${config.public.apiBase}/marketing/gallery/albums/${album.id}`)
    selectedPhotos.value = data.photos || []
    lightboxVisible.value = true
  } catch (e) { console.error('Failed to load photos', e) }
}

function prevPhoto() { currentIndex.value = (currentIndex.value - 1 + selectedPhotos.value.length) % selectedPhotos.value.length }
function nextPhoto() { currentIndex.value = (currentIndex.value + 1) % selectedPhotos.value.length }
</script>
