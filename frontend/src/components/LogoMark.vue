<script setup lang="ts">
withDefaults(defineProps<{ aqua?: string; aquaBorde?: string; rojo?: string; rojoBorde?: string }>(), {
  aqua: '#7fdcdc',
  aquaBorde: '#5ccaca',
  rojo: '#f58f88',
  rojoBorde: '#ea7770',
})
</script>

<template>
  <svg viewBox="0 0 340 390" role="img" aria-label="Símbolo de Papelera La Plata" xmlns="http://www.w3.org/2000/svg">
    <path d="M25 34C120 3 232 0 279 42c36 32 43 91 18 139-17 33-48 55-91 73L57 316z" :fill="aqua" :stroke="aquaBorde" stroke-width="14" stroke-linejoin="round" />
    <path d="M23 366 148 229v137z" :fill="rojo" :stroke="rojoBorde" stroke-width="12" stroke-linejoin="round" />
  </svg>
</template>
