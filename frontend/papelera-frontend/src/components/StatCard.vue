<script setup lang="ts">
import type { Component } from 'vue'
defineProps<{ label: string; value: string; icon: Component; tone: string; hint?: string }>()
</script>

<template>
  <div class="card flex h-full items-center gap-4 p-5">
    <div :class="['grid h-12 w-12 shrink-0 place-items-center rounded-xl', tone]"><component :is="icon" class="h-6 w-6" /></div>
    <div class="min-w-0">
      <p class="text-xs font-semibold uppercase tracking-wider text-tinta-500">{{ label }}</p>
      <p class="truncate font-display text-2xl font-semibold">{{ value }}</p>
      <p v-if="hint" class="text-xs text-tinta-500">{{ hint }}</p>
    </div>
  </div>
</template>
