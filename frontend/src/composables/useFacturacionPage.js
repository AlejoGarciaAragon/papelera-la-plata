import { computed, ref } from 'vue';
import { ChevronLeft, ChevronRight, Download, Printer, Receipt, DollarSign } from 'lucide-vue-next';
import { useDataStore } from '../stores/data';
import { seccion } from '../lib/sections';
import { dayKey, fmtDate, fmtDateTime, fmtMoney, fmtTime } from '../lib/format';
import { COLOR_MEDIO, tipoBadge } from '../lib/ui';
import PageHeader from '../components/PageHeader.vue';
import SearchInput from '../components/SearchInput.vue';
import Modal from '../components/Modal.vue';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';
import Comprobante from '../components/Comprobante.vue';
import EstadoARCA from '../components/EstadoARCA.vue';
export function useFacturacionPage() {
    const data = useDataStore();
    const dia = ref(dayKey(new Date()));
    const q = ref('');
    const ver = ref(null);
    const fechaCaja = ref('');
    const detalleCaja = ref(null);
    const esHoy = computed(() => dia.value === dayKey(new Date()));
    const delDia = computed(() => data.ventas.filter((v) => v.estado !== 'pendiente_cobro' && dayKey(v.fecha) === dia.value).sort((a, b) => b.fecha.localeCompare(a.fecha)));
    const filtradas = computed(() => {
        const t = q.value.toLowerCase();
        return delDia.value.filter((v) => !t || v.numero.includes(t) || v.clienteNombre.toLowerCase().includes(t) || v.vendedorNombre.toLowerCase().includes(t) || v.cae.includes(t));
    });
    const total = computed(() => delDia.value.reduce((s, v) => s + v.total, 0));
    const mediosCaja = ['Efectivo', 'Débito', 'Crédito', 'Cuenta DNI', 'Mercado Pago'];
    const fechaDeCaja = (caja) => caja.fechaOperativa || dayKey(caja.abiertaEn);
    const fechasRecientes = computed(() => Array.from({ length: 3 }, (_, index) => {
        const fecha = new Date();
        fecha.setDate(fecha.getDate() - index);
        return dayKey(fecha);
    }));
    const cajasDia = computed(() => {
        const fechas = fechaCaja.value ? [fechaCaja.value] : fechasRecientes.value;
        return data.cajas
            .filter((caja) => caja.cerradaEn && fechas.includes(fechaDeCaja(caja)))
            .sort((a, b) => `${fechaDeCaja(b)}${b.abiertaEn}`.localeCompare(`${fechaDeCaja(a)}${a.abiertaEn}`));
    });
    const ventasDeCaja = (caja) => data.ventas.filter((venta) => venta.estado !== 'pendiente_cobro' && String(venta.cajaId) === String(caja.id));
    const resumenCaja = (caja) => {
        const ventas = ventasDeCaja(caja);
        const ventasPorMedio = Object.fromEntries(mediosCaja.map((medio) => [medio, 0]));
        ventas.forEach((venta) => {
            ventasPorMedio[venta.medioPago] = (ventasPorMedio[venta.medioPago] || 0) + Number(venta.total || 0);
        });
        const ventasEfectivo = ventas
            .filter((venta) => venta.medioPago === 'Efectivo')
            .reduce((total, venta) => total + Number(venta.total || 0), 0);
        const ingresos = caja.movimientos
            .filter((movimiento) => movimiento.tipo === 'Ingreso')
            .reduce((total, movimiento) => total + Number(movimiento.monto || 0), 0);
        const egresos = caja.movimientos
            .filter((movimiento) => movimiento.tipo === 'Egreso')
            .reduce((total, movimiento) => total + Number(movimiento.monto || 0), 0);
        const efectivoEsperado = Number(caja.montoInicial || 0) + ventasEfectivo + ingresos - egresos;
        const montoCierre = caja.montoCierre === null ? null : Number(caja.montoCierre);
        return {
            cantidadVentas: ventas.length,
            totalVentas: ventas.reduce((total, venta) => total + Number(venta.total || 0), 0),
            ventasPorMedio,
            ingresos,
            egresos,
            efectivoEsperado,
            montoCierre,
            diferencia: montoCierre === null ? null : montoCierre - efectivoEsperado,
        };
    };
    const resumenDetalleCaja = computed(() => detalleCaja.value ? resumenCaja(detalleCaja.value) : null);
    function mover(n) {
        const d = new Date(dia.value + 'T12:00');
        d.setDate(d.getDate() + n);
        dia.value = dayKey(d);
    }
    function exportarVentasCaja(caja) {
        const ventas = ventasDeCaja(caja);
        const filas = [['Numero', 'Fecha', 'Hora', 'Tipo', 'Cliente', 'Empleado', 'Medio de pago', 'Neto', 'IVA', 'Total', 'Estado ARCA']];
        ventas.forEach((v) => filas.push([v.numero, fmtDate(v.fecha), fmtTime(v.fecha), v.tipo, v.clienteNombre, v.vendedorNombre, v.medioPago, v.subtotal.toFixed(2), v.ivaTotal.toFixed(2), v.total.toFixed(2), v.estadoARCA]));
        const csv = filas.map((f) => f.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(';')).join('\n');
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
        a.download = `ventas-${fechaDeCaja(caja)}.csv`;
        a.click();
    }
    const print = () => window.print();
    return {
        ChevronLeft, ChevronRight, Download, Printer, Receipt, DollarSign,
        PageHeader, SearchInput, Modal, EmptyState, StatCard, Comprobante, EstadoARCA,
        seccion, dayKey, fmtDate, fmtDateTime, fmtMoney, fmtTime, COLOR_MEDIO, tipoBadge,
        data, dia, q, ver, esHoy, delDia, filtradas, total,
        cajasDia, resumenCaja, mediosCaja, fechaCaja, fechaDeCaja, detalleCaja, resumenDetalleCaja, mover, exportarVentasCaja, print,
    };
}
