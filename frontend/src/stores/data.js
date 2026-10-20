import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';
import { buildSeedVentas, seedCategorias, seedClientes, seedProductos } from '../lib/seed';
import { genCAE, uid } from '../lib/format';
const KEY = 'papelera-la-plata:data:v6';
function demo() {
    const { ventas, cajas } = buildSeedVentas();
    return {
        categorias: structuredClone(seedCategorias),
        productos: structuredClone(seedProductos),
        clientes: structuredClone(seedClientes),
        ventas,
        cajas,
    };
}
function initial() {
    const raw = localStorage.getItem(KEY);
    if (raw) {
        try {
            return JSON.parse(raw);
        }
        catch {
            /* datos corruptos: se regenera la demo */
        }
    }
    return demo();
}
const upsert = (list, item) => {
    const i = list.findIndex((x) => x.id === item.id);
    if (i >= 0)
        list.splice(i, 1, item);
    else
        list.push(item);
};
export const useDataStore = defineStore('data', () => {
    const init = initial();
    const categorias = ref(init.categorias);
    const productos = ref(init.productos);
    const clientes = ref(init.clientes);
    const ventas = ref(init.ventas);
    const cajas = ref(init.cajas);
    watch([categorias, productos, clientes, ventas, cajas], () => localStorage.setItem(KEY, JSON.stringify({
        categorias: categorias.value, productos: productos.value, clientes: clientes.value, ventas: ventas.value, cajas: cajas.value,
    })), { deep: true });
    const cajaAbierta = computed(() => cajas.value.find((c) => !c.cerradaEn));
    const guardarCategoria = (c) => upsert(categorias.value, { ...c, id: c.id || uid() });
    const eliminarCategoria = (id) => (categorias.value = categorias.value.filter((c) => c.id !== id));
    const guardarProducto = (p) => upsert(productos.value, { ...p, id: p.id || uid() });
    const eliminarProducto = (id) => (productos.value = productos.value.filter((p) => p.id !== id));
    const guardarCliente = (c) => upsert(clientes.value, { ...c, id: c.id || uid() });
    const eliminarCliente = (id) => (clientes.value = clientes.value.filter((c) => c.id !== id));
    /** Oculta o vuelve a mostrar un registro sin eliminarlo. Devuelve el nuevo estado. */
    const alternarOculto = (tipo, id) => {
        const list = tipo === 'categoria' ? categorias.value : tipo === 'producto' ? productos.value : clientes.value;
        const item = list.find((x) => x.id === id);
        if (item)
            item.oculto = !item.oculto;
        return !!item?.oculto;
    };
    const abrirCaja = (montoInicial, usuario) => cajas.value.push({ id: uid(), abiertaEn: new Date().toISOString(), montoInicial, usuario, movimientos: [] });
    const cerrarCaja = (montoCierre) => {
        const c = cajaAbierta.value;
        if (c)
            Object.assign(c, { cerradaEn: new Date().toISOString(), montoCierre });
    };
    const agregarMovimiento = (m) => cajaAbierta.value?.movimientos.push({ ...m, id: uid(), fecha: new Date().toISOString() });
    const registrarVenta = (v) => {
        const total = v.items.reduce((acc, it) => acc + it.cantidad * it.precioUnitario, 0);
        const subtotal = +v.items.reduce((acc, it) => acc + (it.cantidad * it.precioUnitario) / (1 + it.iva / 100), 0).toFixed(2);
        const ultimo = ventas.value.reduce((m, x) => Math.max(m, parseInt(x.numero.split('-')[1], 10)), 0);
        const ahora = new Date();
        const vto = new Date(ahora);
        vto.setDate(vto.getDate() + 10);
        const venta = {
            id: uid(),
            numero: `0001-${String(ultimo + 1).padStart(8, '0')}`,
            fecha: ahora.toISOString(),
            clienteId: v.cliente.id,
            clienteNombre: v.cliente.razonSocial,
            tipo: v.tipo,
            medioPago: v.medioPago,
            items: v.items.map((i) => ({ ...i })),
            subtotal,
            ivaTotal: +(total - subtotal).toFixed(2),
            total,
            cae: genCAE(),
            caeVto: vto.toISOString(),
            estadoARCA: 'Aprobado',
            cajaId: cajaAbierta.value?.id ?? '',
        };
        ventas.value.push(venta);
        v.items.forEach((it) => {
            const p = productos.value.find((x) => x.id === it.productoId);
            if (p)
                p.stock = Math.max(0, p.stock - it.cantidad);
        });
        return venta;
    };
    const reiniciarDemo = () => {
        const d = demo();
        categorias.value = d.categorias;
        productos.value = d.productos;
        clientes.value = d.clientes;
        ventas.value = d.ventas;
        cajas.value = d.cajas;
    };
    return {
        categorias, productos, clientes, ventas, cajas, cajaAbierta,
        guardarCategoria, eliminarCategoria, guardarProducto, eliminarProducto, guardarCliente, eliminarCliente, alternarOculto,
        abrirCaja, cerrarCaja, agregarMovimiento, registrarVenta, reiniciarDemo,
    };
});
