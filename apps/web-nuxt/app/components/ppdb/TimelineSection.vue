<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h3 v-if="title" class="text-xl lg:text-2xl font-bold text-center text-slate-800 dark:text-white mb-8">{{ title }}</h3>
    <div class="relative">
      <!-- Timeline Line -->
      <div class="absolute left-5 top-0 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700"></div>

      <div v-for="(step, i) in steps" :key="i" class="relative flex items-start gap-4 mb-6 last:mb-0">
        <!-- Step Circle -->
        <div class="relative z-10 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm shrink-0 shadow-md"
          :style="{ backgroundColor: themeHex }">
          {{ i + 1 }}
        </div>

        <!-- Step Content -->
        <div class="flex-1 bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700 shadow-sm">
          <div class="font-bold text-slate-800 dark:text-white">{{ step.label }}</div>
          <div v-if="step.date" class="text-sm font-medium mt-1" :style="{ color: themeHex }">
            <i class="pi pi-calendar mr-1"></i>{{ step.date }}
          </div>
          <div v-if="step.description" class="text-sm text-slate-500 dark:text-slate-400 mt-1">{{ step.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface TimelineStep {
  label: string
  date: string
  description: string
}

defineProps<{
  title?: string
  steps: TimelineStep[]
  themeHex?: string
}>()
</script>
