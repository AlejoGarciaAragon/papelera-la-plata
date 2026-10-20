<script setup>
defineProps({ label: String })
</script>

<template>
  <label class="block">
    <span class="label">{{ label }}</span>
    <slot />
  </label>
</template>
