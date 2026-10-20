<script setup>import { onBeforeUnmount, watch } from 'vue';
import { X } from 'lucide-vue-next';
const props = defineProps({
    open: Boolean,
    title: String,
    size: { type: String, default: 'md' },
    accent: { type: String, default: 'bg-turquesa-400' },
});
const emit = defineEmits();
const widths = { sm: 'max-w-md', md: 'max-w-xl', lg: 'max-w-3xl', xl: 'max-w-5xl' };
const onKey = (e) => e.key === 'Escape' && emit('close');
watch(() => props.open, (o) => (o ? window.addEventListener('keydown', onKey) : window.removeEventListener('keydown', onKey)), { immediate: true });
onBeforeUnmount(() => window.removeEventListener('keydown', onKey));
</script>

<template>
  <Teleport to="body">
    <Transition enter-from-class="opacity-0" leave-to-class="opacity-0" enter-active-class="transition duration-150" leave-active-class="transition duration-150">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-tinta/50 p-4 backdrop-blur-sm" @mousedown.self="emit('close')">
        <div :class="['card relative flex max-h-[92vh] w-full flex-col overflow-hidden', widths[size]]">
          <div :class="['h-1.5 w-full', accent]" />
          <div class="flex items-center justify-between border-b border-tinta-100 px-6 py-4">
            <h2 class="text-xl font-semibold">{{ title }}</h2>
            <button class="rounded-lg p-1.5 text-tinta-500 hover:bg-tinta-50" aria-label="Cerrar" @click="emit('close')"><X class="h-5 w-5" /></button>
          </div>
          <div class="scroll-thin overflow-y-auto px-6 py-5"><slot /></div>
          <div v-if="$slots.footer" class="flex justify-end gap-2 border-t border-tinta-100 bg-tinta-50 px-6 py-4"><slot name="footer" /></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
