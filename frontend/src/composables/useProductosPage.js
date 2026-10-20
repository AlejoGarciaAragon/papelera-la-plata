import { computed, ref } from 'vue';
import { useDataStore } from '../stores/data';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';
import { precioVentaDe } from '../lib/format';
import { apiErrorMessage } from '../lib/apiError';
export const FILTROS = [['todos', 'Todos'], ['bajo', 'Stock bajo'], ['sin', 'Sin stock']];
export const IVAS = [21, 11, 0];
export function useProductosPage() {
    const data = useDataStore();
    const auth = useAuthStore();
    const { push: toast } = useToastStore();
    const esEmpleado = computed(() => auth.user?.rol === 'Empleado');
    const q = ref('');
    const cat = ref('');
    const filtro = ref('todos');
    const verOcultos = ref(false);
    const form = ref(null);
    const borrar = ref(null);
    const catDe = (id) => data.categorias.find((c) => c.id === id);
    const lista = computed(() => data.productos.filter((p) => {
        if (!!p.oculto !== verOcultos.value)
            return false;
        const t = q.value.toLowerCase();
        if (t && !p.nombre.toLowerCase().includes(t) && !p.codigo.includes(t))
            return false;
        if (cat.value && String(p.categoriaId) !== String(cat.value))
            return false;
        if (filtro.value === 'bajo' && !(p.stock > 0 && p.stock <= p.stockMinimo))
            return false;
        if (filtro.value === 'sin' && p.stock !== 0)
            return false;
        return true;
    }));
    const bajos = computed(() => data.productos.filter((p) => !p.oculto && p.stock > 0 && p.stock <= p.stockMinimo).length);
    const sin = computed(() => data.productos.filter((p) => !p.oculto && p.stock === 0).length);
    const ocultos = computed(() => data.productos.filter((p) => p.oculto).length);
    const precioForm = computed(() => (form.value ? precioVentaDe(form.value.precioCosto, form.value.ganancia, form.value.iva) : 0));
    const barra = (p) => Math.min(100, (p.stock / Math.max(p.stockMinimo * 4, 1)) * 100);
    const toggle = (f) => (filtro.value = filtro.value === f ? 'todos' : f);
    const nuevo = () => (form.value = { id: '', codigo: '', nombre: '', categoriaId: data.categorias.find((categoria) => !categoria.oculto)?.id ?? null, precioCosto: 0, ganancia: 40, precioVenta: 0, iva: 21, stock: 0, stockMinimo: 5 });
    async function alternar(p) {
        try {
            const oculto = await data.alternarOculto('producto', p.id);
            toast(oculto ? `"${p.nombre}" oculto. Lo encontrás en Ocultos.` : `"${p.nombre}" visible nuevamente`, 'info');
        }
        catch (error) {
            toast(apiErrorMessage(error), 'error');
        }
    }
    async function guardar() {
        const f = form.value;
        if (!f)
            return;
        if (!f.nombre.trim() || !f.codigo.trim())
            return toast('Código y nombre son obligatorios', 'error');
        if (data.productos.some((p) => p.codigo === f.codigo && p.id !== f.id))
            return toast('Ya existe un producto con ese código', 'error');
        if (!(Number(f.precioCosto) > 0))
            return toast('El costo debe ser mayor a 0', 'error');
        try {
            await data.guardarProducto({ ...f, precioCosto: Number(f.precioCosto) || 0, ganancia: Number(f.ganancia) || 0, precioVenta: precioForm.value, stock: Number(f.stock) || 0, stockMinimo: Number(f.stockMinimo) || 0 });
            toast(f.id ? 'Producto actualizado' : 'Producto creado');
            form.value = null;
        }
        catch (error) {
            toast(apiErrorMessage(error), 'error');
        }
    }
    async function confirmarBorrar() {
        if (!borrar.value)
            return;
        try {
            await data.eliminarProducto(borrar.value.id);
            toast('Producto eliminado');
            borrar.value = null;
        }
        catch (error) {
            toast(apiErrorMessage(error), 'error');
        }
    }
    return { data, esEmpleado, q, cat, filtro, verOcultos, form, borrar, catDe, lista, bajos, sin, ocultos, precioForm, barra, toggle, nuevo, alternar, guardar, confirmarBorrar, toast };
}
