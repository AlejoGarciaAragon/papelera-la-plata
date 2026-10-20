<script setup lang="ts">
import { CheckCircle2, AlertTriangle, Info } from 'lucide-vue-next'
import { useToastStore } from '../stores/toast'
const store = useToastStore()
const styles = { ok: 'border-turquesa-400', error: 'border-rojo-500', info: 'border-tinta' }
const icons = { ok: CheckCircle2, error: AlertTriangle, info: Info }
const iconCls = { ok: 'text-turquesa-600', error: 'text-rojo-500', info: '' }
</script>

<template>
  <div class="no-print fixed bottom-5 right-5 z-[60] flex flex-col gap-2">
    <TransitionGroup enter-from-class="translate-y-2 opacity-0" leave-to-class="opacity-0" enter-active-class="transition" leave-active-class="transition">
      <div v-for="t in store.toasts" :key="t.id" :class="['flex items-center gap-3 rounded-xl border-l-4 bg-white px-4 py-3 text-sm font-medium shadow-pop', styles[t.tipo]]">
        <component :is="icons[t.tipo]" :class="['h-5 w-5', iconCls[t.tipo]]" />
        {{ t.texto }}
      </div>
    </TransitionGroup>
  </div>
</template>
