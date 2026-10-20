<script setup>import { Search } from 'lucide-vue-next';
const model = defineModel({ required: true });
defineProps({ placeholder: { type: String, default: 'Buscar...' } })
</script>

<template>
  <div class="relative w-full sm:w-72">
    <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-tinta-300" />
    <input v-model="model" class="input pl-9" :placeholder="placeholder" />
  </div>
</template>
