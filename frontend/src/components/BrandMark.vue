<script setup>
defineProps({ size: { type: Number, default: 40 } })
</script>

<template>
  <div class="relative shrink-0" :style="{ width: `${size}px`, height: `${size}px` }">
    <div class="absolute left-[8%] top-[4%] h-[72%] w-[86%] rounded-[18%_50%_50%_18%] bg-turquesa-400" />
    <div class="absolute bottom-[4%] left-0 h-[62%] w-[60%] bg-rojo-500" style="clip-path: polygon(100% 0, 100% 100%, 0 100%)" />
    <span class="absolute inset-0 grid place-items-center font-display font-bold text-tinta" :style="{ fontSize: `${size * 0.5}px` }">P</span>
  </div>
</template>
