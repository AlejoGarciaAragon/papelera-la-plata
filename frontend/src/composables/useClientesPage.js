import { computed, ref } from 'vue';
import { useDataStore } from '../stores/data';
import { useToastStore } from '../stores/toast';
export const CONDICIONES = ['Responsable Inscripto', 'Monotributista', 'Consumidor Final', 'Exento'];
export function useClientesPage() {
    const data = useDataStore();
    const { push: toast } = useToastStore();
    const q = ref('');
    const verOcultos = ref(false);
    const ocultos = computed(() => data.clientes.filter((c) => c.oculto).length);
    const base = computed(() => data.clientes.filter((c) => !!c.oculto === verOcultos.value));
    const cond = ref('');
    const form = ref(null);
    const borrar = ref(null);
    const iniciales = (n) => n.split(' ').slice(0, 2).map((x) => x[0]).join('').toUpperCase();
    const stats = computed(() => {
        const m = {};
        data.ventas.forEach((v) => {
            var _a;
            m[_a = v.clienteId] ?? (m[_a] = { n: 0, total: 0 });
            m[v.clienteId].n++;
            m[v.clienteId].total += v.total;
        });
        return m;
    });
    const lista = computed(() => base.value.filter((c) => {
        const t = q.value.toLowerCase();
        return (!t || c.razonSocial.toLowerCase().includes(t) || c.documento.includes(t)) && (!cond.value || c.condicionIVA === cond.value);
    }));
    const nuevo = () => (form.value = { id: '', razonSocial: '', documento: '', condicionIVA: 'Consumidor Final', email: '', telefono: '', direccion: '' });
    function alternar(c) {
        const oculto = data.alternarOculto('cliente', c.id);
        toast(oculto ? `"${c.razonSocial}" oculto. Lo encontrás en Ocultos.` : `"${c.razonSocial}" visible nuevamente`, 'info');
    }
    function guardar() {
        const f = form.value;
        if (!f)
            return;
        if (!f.razonSocial.trim() || !f.documento.trim())
            return toast('Razón social y CUIT/DNI son obligatorios', 'error');
        data.guardarCliente(f);
        toast(f.id ? 'Cliente actualizado' : 'Cliente creado');
        form.value = null;
    }
    return { data, q, verOcultos, ocultos, base, cond, form, borrar, iniciales, stats, lista, nuevo, alternar, guardar, toast };
}
