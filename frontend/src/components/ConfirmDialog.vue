<script setup>import { AlertTriangle } from 'lucide-vue-next';
import Modal from './Modal.vue';
defineProps({ open: Boolean, title: String })
const emit = defineEmits(['close', 'confirm'])
</script>

<template>
  <Modal :open="open" :title="title" size="sm" accent="bg-rojo-500" @close="emit('close')">
    <div class="flex gap-4">
      <div class="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-rojo-50 text-rojo-500"><AlertTriangle class="h-5 w-5" /></div>
      <p class="text-sm text-tinta-700"><slot /></p>
    </div>
    <template #footer>
      <button class="btn-ghost" @click="emit('close')">Cancelar</button>
      <button class="btn-rojo" @click="emit('confirm'); emit('close')">Eliminar</button>
    </template>
  </Modal>
</template>
