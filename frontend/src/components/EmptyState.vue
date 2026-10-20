<script setup lang="ts">
import type { Component } from 'vue'
defineProps<{ icon: Component; title: string; text: string }>()
</script>

<template>
  <div class="flex flex-col items-center justify-center px-6 py-14 text-center">
    <div class="mb-4 grid h-16 w-16 place-items-center rounded-2xl bg-tinta-50 text-tinta-300"><component :is="icon" class="h-8 w-8" /></div>
    <p class="font-display text-lg uppercase">{{ title }}</p>
    <p class="mt-1 max-w-sm text-sm text-tinta-500">{{ text }}</p>
    <div v-if="$slots.default" class="mt-4"><slot /></div>
  </div>
</template>
