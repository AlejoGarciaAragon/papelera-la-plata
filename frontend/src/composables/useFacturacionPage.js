import { computed, ref } from 'vue';
import { ChevronLeft, ChevronRight, Download, Printer, Receipt, DollarSign, TrendingUp, Percent, FileText } from 'lucide-vue-next';
import { Bar, Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, ArcElement, Tooltip } from 'chart.js';
import { useDataStore } from '../stores/data';
import { seccion } from '../lib/sections';
import { dayKey, fmtDate, fmtMoney, fmtTime } from '../lib/format';
import { COLOR_MEDIO, tipoBadge } from '../lib/ui';
import PageHeader from '../components/PageHeader.vue';
import SearchInput from '../components/SearchInput.vue';
import Modal from '../components/Modal.vue';
import EmptyState from '../components/EmptyState.vue';
import StatCard from '../components/StatCard.vue';
import Comprobante from '../components/Comprobante.vue';
import EstadoARCA from '../components/EstadoARCA.vue';
ChartJS.register(BarElement, CategoryScale, LinearScale, ArcElement, Tooltip);
ChartJS.defaults.font.family = 'Inter, system-ui, sans-serif';
export function useFacturacionPage() {
    const data = useDataStore();
    const dia = ref(dayKey(new Date()));
    const q = ref('');
    const ver = ref(null);
    const esHoy = computed(() => dia.value === dayKey(new Date()));
    const delDia = computed(() => data.ventas.filter((v) => dayKey(v.fecha) === dia.value).sort((a, b) => b.fecha.localeCompare(a.fecha)));
    const filtradas = computed(() => {
        const t = q.value.toLowerCase();
        return delDia.value.filter((v) => !t || v.numero.includes(t) || v.clienteNombre.toLowerCase().includes(t) || v.cae.includes(t));
    });
    const total = computed(() => delDia.value.reduce((s, v) => s + v.total, 0));
    const iva = computed(() => delDia.value.reduce((s, v) => s + v.ivaTotal, 0));
    const promedio = computed(() => (delDia.value.length ? total.value / delDia.value.length : 0));
    const pendientes = computed(() => delDia.value.filter((v) => v.estadoARCA === 'Pendiente').length);
    const tooltipMoney = { callbacks: { label: (ctx) => ` ${fmtMoney(Number(ctx.raw))}` } };
    const barOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: tooltipMoney },
        scales: {
            x: { grid: { display: false }, border: { display: false } },
            y: { grid: { color: '#ececec' }, border: { display: false }, ticks: { callback: (v) => `$${Number(v) / 1000}k` } },
        },
    };
    const porHora = computed(() => {
        const vals = Array(12).fill(0);
        delDia.value.forEach((v) => {
            const h = new Date(v.fecha).getHours() - 8;
            if (h >= 0 && h < 12)
                vals[h] += v.total;
        });
        return {
            labels: vals.map((_, i) => `${8 + i}h`),
            datasets: [{ data: vals, backgroundColor: '#7fdcdc', hoverBackgroundColor: '#5ccaca', borderRadius: 8 }],
        };
    });
    const porMedio = computed(() => {
        const m = {};
        delDia.value.forEach((v) => (m[v.medioPago] = (m[v.medioPago] ?? 0) + v.total));
        return Object.entries(m).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
    });
    const medioChart = computed(() => ({
        labels: porMedio.value.map((m) => m.name),
        datasets: [{ data: porMedio.value.map((m) => m.value), backgroundColor: porMedio.value.map((m) => COLOR_MEDIO[m.name]), borderWidth: 3, borderColor: '#fff' }],
    }));
    const doughnutOptions = { responsive: true, maintainAspectRatio: false, cutout: '62%', plugins: { legend: { display: false }, tooltip: tooltipMoney } };
    const top = computed(() => {
        const m = {};
        delDia.value.forEach((v) => v.items.forEach((i) => {
            var _a;
            m[_a = i.productoId] ?? (m[_a] = { nombre: i.nombre, cant: 0, total: 0 });
            m[i.productoId].cant += i.cantidad;
            m[i.productoId].total += i.cantidad * i.precioUnitario;
        }));
        return Object.values(m).sort((a, b) => b.cant - a.cant).slice(0, 5);
    });
    const ultimos7 = computed(() => Array.from({ length: 7 }, (_, i) => {
        const d = new Date(dia.value + 'T12:00');
        d.setDate(d.getDate() - (6 - i));
        const k = dayKey(d);
        return { label: d.toLocaleDateString('es-AR', { weekday: 'short', day: 'numeric' }), k, total: data.ventas.filter((v) => dayKey(v.fecha) === k).reduce((s, v) => s + v.total, 0) };
    }));
    const semanaChart = computed(() => ({
        labels: ultimos7.value.map((d) => d.label),
        datasets: [{ data: ultimos7.value.map((d) => d.total), backgroundColor: ultimos7.value.map((d) => (d.k === dia.value ? '#f58f88' : '#c9ccd6')), borderRadius: 8 }],
    }));
    const semanaOptions = computed(() => ({
        ...barOptions,
        onClick: (_e, els) => { if (els[0])
            dia.value = ultimos7.value[els[0].index].k; },
        onHover: (e, els) => { e.native?.target?.style.setProperty('cursor', els.length ? 'pointer' : 'default'); },
    }));
    const cajasDia = computed(() => data.cajas.filter((c) => dayKey(c.abiertaEn) === dia.value));
    function mover(n) {
        const d = new Date(dia.value + 'T12:00');
        d.setDate(d.getDate() + n);
        dia.value = dayKey(d);
    }
    function exportar() {
        const filas = [['Numero', 'Fecha', 'Hora', 'Tipo', 'Cliente', 'Medio de pago', 'Neto', 'IVA', 'Total', 'CAE', 'Estado ARCA']];
        delDia.value.forEach((v) => filas.push([v.numero, fmtDate(v.fecha), fmtTime(v.fecha), v.tipo, v.clienteNombre, v.medioPago, v.subtotal.toFixed(2), v.ivaTotal.toFixed(2), v.total.toFixed(2), v.cae, v.estadoARCA]));
        const csv = filas.map((f) => f.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(';')).join('\n');
        const a = document.createElement('a');
        a.href = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }));
        a.download = `ventas-${dia.value}.csv`;
        a.click();
    }
    const print = () => window.print();
    return {
        ChevronLeft, ChevronRight, Download, Printer, Receipt, DollarSign, TrendingUp, Percent, FileText,
        Bar, Doughnut, PageHeader, SearchInput, Modal, EmptyState, StatCard, Comprobante, EstadoARCA,
        seccion, dayKey, fmtDate, fmtMoney, fmtTime, COLOR_MEDIO, tipoBadge,
        data, dia, q, ver, esHoy, delDia, filtradas, total, iva, promedio, pendientes,
        barOptions, porHora, porMedio, medioChart, doughnutOptions, top, ultimos7, semanaChart, semanaOptions,
        cajasDia, mover, exportar, print,
    };
}
