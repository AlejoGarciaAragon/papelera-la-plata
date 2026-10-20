import { defineStore } from 'pinia';
import { ref } from 'vue';
export const useToastStore = defineStore('toast', () => {
    const toasts = ref([]);
    function push(texto, tipo = 'ok') {
        const id = Date.now() + Math.random();
        toasts.value.push({ id, tipo, texto });
        setTimeout(() => (toasts.value = toasts.value.filter((t) => t.id !== id)), 3200);
    }
    return { toasts, push };
});
