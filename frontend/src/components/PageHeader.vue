<script setup>
defineProps({ seccion: Object })
</script>

<template>
  <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-4">
      <div :class="['grid h-14 w-14 place-items-center rounded-2xl shadow-card', seccion.tile]">
        <component :is="seccion.icon" class="h-7 w-7" :stroke-width="2.2" />
      </div>
      <div>
        <h1 class="text-3xl font-bold leading-none">{{ seccion.label }}</h1>
        <p class="mt-1 text-sm text-tinta-500">{{ seccion.descripcion }}</p>
      </div>
      <slot name="info" />
    </div>
    <div v-if="$slots.actions" class="flex flex-wrap items-center gap-2"><slot name="actions" /></div>
  </div>
</template>
