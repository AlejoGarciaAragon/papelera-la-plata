import { computed, ref } from 'vue';
import { Minus, Plus, Trash2, ShoppingCart, Banknote, CreditCard, Wallet, Smartphone, Lock, Unlock, History, ArrowDownCircle, ArrowUpCircle, Receipt, Printer, CheckCircle2, ScanBarcode, User, } from 'lucide-vue-next';
import { useDataStore } from '../stores/data';
import { useAuthStore } from '../stores/auth';
import { useToastStore } from '../stores/toast';
import { seccion } from '../lib/sections';
import { fmtDateTime, fmtMoney, fmtTime, tipoPorCondicion } from '../lib/format';
import { tipoBadge } from '../lib/ui';
import PageHeader from '../components/PageHeader.vue';
import Modal from '../components/Modal.vue';
import EmptyState from '../components/EmptyState.vue';
import Field from '../components/Field.vue';
import Comprobante from '../components/Comprobante.vue';
const MEDIOS = [
    { id: 'Efectivo', icon: Banknote },
    { id: 'Débito', icon: CreditCard },
    { id: 'Crédito', icon: CreditCard },
    { id: 'Cuenta DNI', icon: Wallet },
    { id: 'Mercado Pago', icon: Smartphone },
];
export function useCajaPage() {
    const data = useDataStore();
    const auth = useAuthStore();
    const { push: toast } = useToastStore();
    const montoInicial = ref('');
    const q = ref('');
    const cat = ref('');
    const carrito = ref([]);
    const clienteId = ref('cf');
    const tipo = ref('Factura B');
    const medio = ref('Efectivo');
    const pagaCon = ref('');
    const emitida = ref(null);
    const emitiendo = ref(false);
    const mov = ref(null);
    const movForm = ref({ concepto: '', monto: '' });
    const cierre = ref(false);
    const verMovs = ref(false);
    const contado = ref('');
    const buscador = ref(null);
    const caja = computed(() => data.cajaAbierta);
    const ventasCaja = computed(() => data.ventas.filter((v) => v.cajaId === caja.value?.id));
    const totalVentas = computed(() => ventasCaja.value.reduce((s, v) => s + v.total, 0));
    const efectivoVentas = computed(() => ventasCaja.value.filter((v) => v.medioPago === 'Efectivo').reduce((s, v) => s + v.total, 0));
    const ingresos = computed(() => caja.value?.movimientos.filter((m) => m.tipo === 'Ingreso').reduce((s, m) => s + m.monto, 0) ?? 0);
    const egresos = computed(() => caja.value?.movimientos.filter((m) => m.tipo === 'Egreso').reduce((s, m) => s + m.monto, 0) ?? 0);
    const efectivoEsperado = computed(() => (caja.value?.montoInicial ?? 0) + efectivoVentas.value + ingresos.value - egresos.value);
    const porMedio = (id) => ventasCaja.value.filter((v) => v.medioPago === id).reduce((s, v) => s + v.total, 0);
    const diferencia = computed(() => (Number(contado.value) || 0) - efectivoEsperado.value);
    const ultimaCerrada = computed(() => [...data.cajas].filter((c) => c.cerradaEn).sort((a, b) => b.cerradaEn.localeCompare(a.cerradaEn))[0]);
    const catDe = (id) => data.categorias.find((c) => c.id === id);
    const visibles = computed(() => data.productos.filter((p) => {
        const t = q.value.toLowerCase();
        return !p.oculto && !catDe(p.categoriaId)?.oculto && (!cat.value || p.categoriaId === cat.value) && (!t || p.nombre.toLowerCase().includes(t) || p.codigo.includes(t));
    }));
    const cantEnCarrito = (id) => carrito.value.find((i) => i.productoId === id)?.cantidad ?? 0;
    const total = computed(() => carrito.value.reduce((s, i) => s + i.cantidad * i.precioUnitario, 0));
    const neto = computed(() => carrito.value.reduce((s, i) => s + (i.cantidad * i.precioUnitario) / (1 + i.iva / 100), 0));
    const cliente = computed(() => data.clientes.find((c) => c.id === clienteId.value) ?? data.clientes[0]);
    const unidades = computed(() => carrito.value.reduce((s, i) => s + i.cantidad, 0));
    const falta = computed(() => (medio.value === 'Efectivo' && Number(pagaCon.value) > 0 && Number(pagaCon.value) < total.value ? total.value - Number(pagaCon.value) : 0));
    const vuelto = computed(() => (medio.value === 'Efectivo' && Number(pagaCon.value) > total.value ? Number(pagaCon.value) - total.value : 0));
    const movimientos = computed(() => [
        ...ventasCaja.value.map((v) => ({ id: v.id, fecha: v.fecha, tipo: 'Venta', concepto: `${v.tipo} ${v.numero} · ${v.clienteNombre}`, detalle: v.medioPago, monto: v.total, venta: v })),
        ...(caja.value?.movimientos ?? []).map((m) => ({ id: m.id, fecha: m.fecha, tipo: m.tipo, concepto: m.concepto, detalle: 'Efectivo', monto: m.monto, venta: undefined })),
    ].sort((a, b) => b.fecha.localeCompare(a.fecha)));
    function abrir() {
        data.abrirCaja(Number(montoInicial.value) || 0, auth.user?.usuario ?? '');
        toast('Caja abierta. ¡Buenas ventas!');
    }
    function agregar(id) {
        const p = data.productos.find((x) => x.id === id);
        if (!p)
            return;
        const item = carrito.value.find((i) => i.productoId === id);
        if ((item?.cantidad ?? 0) >= p.stock)
            return toast(`Sin stock suficiente de "${p.nombre}"`, 'error');
        if (item)
            item.cantidad++;
        else
            carrito.value.push({ productoId: p.id, nombre: p.nombre, cantidad: 1, precioUnitario: p.precioVenta, iva: p.iva });
    }
    function cambiarCant(id, d) {
        const p = data.productos.find((x) => x.id === id);
        const item = carrito.value.find((i) => i.productoId === id);
        if (!item)
            return;
        item.cantidad = Math.min(p?.stock ?? 999, item.cantidad + d);
        if (item.cantidad <= 0)
            quitar(id);
    }
    const quitar = (id) => (carrito.value = carrito.value.filter((i) => i.productoId !== id));
    function escanear() {
        const p = data.productos.find((x) => x.codigo === q.value.trim() && !x.oculto);
        if (p) {
            agregar(p.id);
            q.value = '';
        }
        else if (visibles.value.length === 1) {
            agregar(visibles.value[0].id);
            q.value = '';
        }
    }
    function elegirCliente(id) {
        clienteId.value = id;
        const c = data.clientes.find((x) => x.id === id);
        if (c)
            tipo.value = tipoPorCondicion(c.condicionIVA);
    }
    async function cobrar() {
        if (!carrito.value.length)
            return;
        emitiendo.value = true;
        await new Promise((r) => setTimeout(r, 900));
        emitida.value = data.registrarVenta({ cliente: cliente.value, tipo: tipo.value, medioPago: medio.value, items: carrito.value });
        emitiendo.value = false;
        carrito.value = [];
        pagaCon.value = '';
        elegirCliente('cf');
        medio.value = 'Efectivo';
    }
    function registrarMov() {
        if (!movForm.value.concepto || !Number(movForm.value.monto))
            return toast('Completá concepto y monto', 'error');
        data.agregarMovimiento({ tipo: mov.value, concepto: movForm.value.concepto, monto: Number(movForm.value.monto) });
        toast(`${mov.value} registrado`);
        movForm.value = { concepto: '', monto: '' };
        mov.value = null;
    }
    function abrirCierre() {
        contado.value = efectivoEsperado.value;
        cierre.value = true;
    }
    function confirmarCierre() {
        data.cerrarCaja(Number(contado.value) || 0);
        cierre.value = false;
        toast('Caja cerrada correctamente');
    }
    function cerrarComprobante() {
        emitida.value = null;
        buscador.value?.focus();
    }
    const print = () => window.print();
    return {
        Minus, Plus, Trash2, ShoppingCart, Banknote, CreditCard, Wallet, Smartphone, Lock, Unlock, History,
        ArrowDownCircle, ArrowUpCircle, Receipt, Printer, CheckCircle2, ScanBarcode, User, MEDIOS,
        PageHeader, Modal, EmptyState, Field, Comprobante, data, seccion, fmtDateTime, fmtMoney, fmtTime, tipoBadge,
        montoInicial, q, cat, carrito, clienteId, tipo, medio, pagaCon, emitida, emitiendo, mov, movForm, cierre,
        verMovs, contado, buscador, caja, ventasCaja, totalVentas, efectivoVentas, ingresos, egresos, efectivoEsperado,
        porMedio, diferencia, ultimaCerrada, visibles, catDe, cantEnCarrito, total, neto, cliente, unidades, falta,
        vuelto, movimientos, abrir, agregar, cambiarCant, quitar, escanear, elegirCliente, cobrar, registrarMov,
        abrirCierre, confirmarCierre, cerrarComprobante, print,
    };
}
