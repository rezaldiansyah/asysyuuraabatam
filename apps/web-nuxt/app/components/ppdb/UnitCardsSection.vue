<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h3 v-if="title" class="text-xl lg:text-2xl font-bold text-center text-slate-800 dark:text-white mb-8">{{ title }}</h3>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 lg:gap-6">
      <NuxtLink
        v-for="unit in displayUnits"
        :key="unit.code"
        :to="`/unit/${unit.code.toLowerCase()}`"
        class="group p-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 text-center hover:border-primary hover:shadow-lg transition-all"
      >
        <div class="w-16 h-16 mx-auto mb-4 rounded-xl flex items-center justify-center text-white text-2xl font-bold"
          :style="{ backgroundColor: themeHex }">
          {{ unit.code.charAt(0) }}
        </div>
        <h4 class="text-lg font-bold text-slate-800 dark:text-white group-hover:text-primary transition">{{ unit.name }}</h4>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">{{ unit.desc }}</p>
        <div class="mt-3 text-sm font-medium group-hover:underline" :style="{ color: themeHex }">
          Lihat Detail <i class="pi pi-arrow-right text-xs ml-1"></i>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title?: string
  units?: string[]
  themeHex?: string
}>()

const allUnits = [
  { code: 'RA', name: 'RA (TK Islam)', desc: 'Raudhatul Athfal — Pendidikan anak usia dini Islami' },
  { code: 'SDIT', name: 'SDIT', desc: 'Sekolah Dasar Islam Terpadu — Kelas 1 s.d. 6' },
  { code: 'SMPIT', name: 'SMPIT', desc: 'SMP Islam Terpadu — Kelas 7 s.d. 9' },
]

const displayUnits = computed(() => {
  if (props.units && props.units.length > 0) {
    return allUnits.filter(u => props.units!.includes(u.code))
  }
  return allUnits
})
</script>
