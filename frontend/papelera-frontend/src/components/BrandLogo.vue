<script setup lang="ts">
import { computed } from 'vue'
import LogoMark from './LogoMark.vue'

const props = withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' | 'xl' }>(), { size: 'md' })

const TAMANIOS = {
  sm: { marca: 'h-10', texto: 'text-lg', gap: 'gap-2' },
  md: { marca: 'h-14', texto: 'text-2xl', gap: 'gap-3' },
  lg: { marca: 'h-20', texto: 'text-4xl', gap: 'gap-4' },
  xl: { marca: 'h-36', texto: 'text-7xl', gap: 'gap-6' },
}
const t = computed(() => TAMANIOS[props.size])
</script>

<template>
  <div :class="['flex items-center', t.gap]">
    <LogoMark :class="[t.marca, 'w-auto shrink-0']" />
    <div :class="['font-display font-bold uppercase leading-[0.88] tracking-tight text-tinta', t.texto]">
      <span class="block">Papelera</span>
      <span class="block">La Plata</span>
    </div>
  </div>
</template>
