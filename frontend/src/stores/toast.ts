import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastTipo = 'ok' | 'error' | 'info'

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<{ id: number; tipo: ToastTipo; texto: string }[]>([])
  function push(texto: string, tipo: ToastTipo = 'ok') {
    const id = Date.now() + Math.random()
    toasts.value.push({ id, tipo, texto })
    setTimeout(() => (toasts.value = toasts.value.filter((t) => t.id !== id)), 3200)
  }
  return { toasts, push }
})
