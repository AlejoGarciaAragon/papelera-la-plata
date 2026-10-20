<script setup>import { CheckCircle2, Clock, XCircle } from 'lucide-vue-next';
defineProps({ estado: String });
const map = {
    Aprobado: { cls: 'bg-turquesa-50 text-turquesa-700', icon: CheckCircle2 },
    Pendiente: { cls: 'bg-amarillo-100 text-amarillo-700', icon: Clock },
    Rechazado: { cls: 'bg-rojo-50 text-rojo-600', icon: XCircle },
    'No aplica': { cls: 'bg-tinta-100 text-tinta-500', icon: Clock },
};
</script>

<template>
  <span :class="['inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold', (map[estado] || map.Pendiente).cls]">
    <component :is="(map[estado] || map.Pendiente).icon" class="h-3.5 w-3.5" />{{ estado || 'Pendiente' }}
  </span>
</template>
