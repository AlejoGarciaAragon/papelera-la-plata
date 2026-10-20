<script setup lang="ts">
defineProps<{ label: string }>()
</script>

<template>
  <label class="block">
    <span class="label">{{ label }}</span>
    <slot />
  </label>
</template>
