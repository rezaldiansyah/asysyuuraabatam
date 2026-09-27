<template>
  <div>
    <div :class="containerClass">
      <img
        v-for="(img, i) in images"
        :key="i"
        :src="img"
        :alt="`Section ${i + 1}`"
        class="w-full object-cover"
        :class="radiusClass"
        loading="lazy"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  images: string[]
  gap?: string
  borderRadius?: string
}>()

const containerClass = computed(() => {
  const classes = ['flex', 'flex-col']
  switch (props.gap) {
    case 'small':
      classes.push('gap-1')
      break
    case 'medium':
      classes.push('gap-4')
      break
    default:
      // no gap
      break
  }
  return classes.join(' ')
})

const radiusClass = computed(() => {
  switch (props.borderRadius) {
    case 'rounded':
      return 'rounded-lg'
    case 'full-rounded':
      return 'rounded-2xl'
    default:
      return ''
  }
})
</script>
