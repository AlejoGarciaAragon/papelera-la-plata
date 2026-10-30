import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import api from '../lib/axios';
import { useAuthStore } from './auth';

const asList = (data) => Array.isArray(data) ? data : data.results || [];
const normalizeProducto = (item) => ({ ...item, precioCosto: Number(item.precioCosto), ganancia: Number(item.ganancia), precioVenta: Number(item.precioVenta), iva: Number(item.iva), stock: Number(item.stock), stockMinimo: Number(item.stockMinimo) });
const normalizeVenta = (item) => ({ ...item, total: Number(item.total), subtotal: Number(item.subtotal), ivaTotal: Number(item.ivaTotal), items: item.items.map((line) => ({ ...line, precioUnitario: Number(line.precioUnitario), cantidad: Number(line.cantidad), iva: Number(line.iva) })) });
const normalizeMovimiento = (movement) => ({ ...movement, monto: Number(movement.monto) });
const normalizeCaja = (item) => ({ ...item, montoInicial: Number(item.montoInicial), montoCierre: item.montoCierre == null ? null : Number(item.montoCierre), movimientos: (item.movimientos ?? []).map(normalizeMovimiento) });
const upsert = (list, item) => {
    const index = list.findIndex((current) => current.id === item.id);
    if (index < 0)
        list.push(item);
    else
        list.splice(index, 1, item);
};

export const useDataStore = defineStore('data', () => {
    const auth = useAuthStore();
    const categorias = ref([]);
    const productos = ref([]);
    const clientes = ref([]);
    const ventas = ref([]);
    const cajas = ref([]);
    const loading = ref(false);
    const loaded = ref(false);
    const error = ref('');
    let loadedRole = null;
    const cajaAbierta = computed(() => cajas.value.find((caja) => !caja.cerradaEn));

    async function cargar(force = false) {
        const role = auth.user?.rol ?? null;
        if (loadedRole !== role) {
            categorias.value = [];
            productos.value = [];
            clientes.value = [];
            ventas.value = [];
            cajas.value = [];
            loaded.value = false;
            loadedRole = role;
        }
        if (loading.value || (loaded.value && !force))
            return;
        loading.value = true;
        error.value = '';
        try {
            if (auth.user?.rol === 'Empleado') {
                const [categoriasResponse, productosResponse, cajaActualResponse] = await Promise.all([
                    api.get('categorias/'), api.get('productos/'), api.get('cajas/actual/'),
                ]);
                categorias.value = asList(categoriasResponse.data);
                productos.value = asList(productosResponse.data).map(normalizeProducto);
                clientes.value = [];
                ventas.value = [];
                cajas.value = cajaActualResponse.data ? [normalizeCaja(cajaActualResponse.data)] : [];
                loaded.value = true;
                return;
            }
            const [categoriasResponse, productosResponse, clientesResponse, ventasResponse, cajasResponse] = await Promise.all([
                api.get('categorias/'), api.get('productos/'), api.get('clientes/'), api.get('ventas/'), api.get('cajas/'),
            ]);
            categorias.value = asList(categoriasResponse.data);
            productos.value = asList(productosResponse.data).map(normalizeProducto);
            clientes.value = asList(clientesResponse.data);
            ventas.value = asList(ventasResponse.data).map(normalizeVenta);
            cajas.value = asList(cajasResponse.data).map(normalizeCaja);
            loaded.value = true;
        }
        catch (requestError) {
            error.value = requestError.response?.data?.detail || 'No se pudieron cargar los datos del servidor.';
        }
        finally {
            loading.value = false;
        }
    }

    async function guardar(tipo, item) {
        const base = { categoria: 'categorias/', producto: 'productos/', cliente: 'clientes/' }[tipo];
        const { data } = item.id ? await api.patch(`${base}${item.id}/`, item) : await api.post(base, item);
        const list = { categoria: categorias, producto: productos, cliente: clientes }[tipo].value;
        const normalized = tipo === 'producto' ? normalizeProducto(data) : data;
        upsert(list, normalized);
        await cargar(true);
        return normalized;
    }

    async function eliminar(tipo, id) {
        const base = { categoria: 'categorias/', producto: 'productos/', cliente: 'clientes/' }[tipo];
        await api.delete(`${base}${id}/`);
        const list = { categoria: categorias, producto: productos, cliente: clientes }[tipo];
        list.value = list.value.filter((item) => item.id !== id);
        await cargar(true);
    }

    async function alternarOculto(tipo, id) {
        const list = { categoria: categorias, producto: productos, cliente: clientes }[tipo];
        const item = list.value.find((record) => record.id === id);
        if (!item)
            return false;
        const base = { categoria: 'categorias/', producto: 'productos/', cliente: 'clientes/' }[tipo];
        const { data } = await api.patch(`${base}${id}/`, { oculto: !item.oculto });
        upsert(list.value, data);
        await cargar(true);
        return data.oculto;
    }

    const guardarCategoria = (item) => guardar('categoria', item);
    const eliminarCategoria = (id) => eliminar('categoria', id);
    const guardarProducto = (item) => guardar('producto', item);
    const eliminarProducto = (id) => eliminar('producto', id);
    const guardarCliente = (item) => guardar('cliente', item);
    const eliminarCliente = (id) => eliminar('cliente', id);

    async function abrirCaja(montoInicial) {
        const { data } = await api.post('cajas/abrir/', { montoInicial });
        const caja = normalizeCaja(data);
        upsert(cajas.value, caja);
        await cargar(true);
        return caja;
    }

    async function cerrarCaja(montoCierre) {
        const caja = cajaAbierta.value;
        if (!caja)
            return;
        const { data } = await api.post(`cajas/${caja.id}/cerrar/`, { montoCierre });
        const cajaCerrada = normalizeCaja(data);
        upsert(cajas.value, cajaCerrada);
        await cargar(true);
        return cajaCerrada;
    }

    async function agregarMovimiento(movimiento) {
        const caja = cajaAbierta.value;
        if (!caja)
            return;
        const { data } = await api.post(`cajas/${caja.id}/movimientos/`, movimiento);
        const movimientoGuardado = normalizeMovimiento(data);
        caja.movimientos.push(movimientoGuardado);
        await cargar(true);
        return movimientoGuardado;
    }

    async function registrarVenta(venta) {
        const payload = {
            items: venta.items.map((item) => ({ productoId: item.productoId, cantidad: item.cantidad })),
        };
        const { data } = await api.post('ventas/', payload);
        const ventaCreada = normalizeVenta(data);
        upsert(ventas.value, ventaCreada);
        await cargar(true);
        return ventaCreada;
    }

    async function cobrarVenta(id, medioPago, pagaCon, clienteId, tipo) {
        const payload = { medioPago, tipo };
        if (pagaCon !== undefined)
            payload.pagaCon = pagaCon;
        payload.clienteId = clienteId || null;
        const { data } = await api.post(`ventas/${id}/cobrar_y_facturar/`, payload);
        const ventaCobrada = normalizeVenta(data);
        upsert(ventas.value, ventaCobrada);
        await cargar(true);
        return ventaCobrada;
    }

    async function tipoComprobanteSugerido(clienteId) {
        const params = clienteId ? { clienteId } : {};
        const { data } = await api.get('ventas/tipo-comprobante-sugerido/', { params });
        return data.tipo;
    }

    return {
        categorias, productos, clientes, ventas, cajas, cajaAbierta, loading, loaded, error, cargar,
        guardarCategoria, eliminarCategoria, guardarProducto, eliminarProducto, guardarCliente, eliminarCliente, alternarOculto,
        abrirCaja, cerrarCaja, agregarMovimiento, registrarVenta, cobrarVenta, tipoComprobanteSugerido,
    };
});
