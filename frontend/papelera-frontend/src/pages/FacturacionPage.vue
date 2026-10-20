<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronLeft, ChevronRight, Download, Printer, Receipt, DollarSign, TrendingUp, Percent, FileText } from 'lucide-vue-next'
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, ArcElement, Tooltip, type ChartOptions } from 'chart.js'
import { useDataStore } from '../stores/data'
import { seccion } from '../lib/sections'
import { dayKey, fmtDate, fmtMoney, fmtTime } from '../lib/format'
import { COLOR_MEDIO, tipoBadge } from '../lib/ui'
import type { MedioPago, Venta } from '../types'
import PageHeader from '../components/PageHeader.vue'
import SearchInput from '../components/SearchInput.vue'
import Modal from '../components/Modal.vue'
import EmptyState from '../components/EmptyState.vue'
import StatCard from '../components/StatCard.vue'
import Comprobante from '../components/Comprobante.vue'
import EstadoARCA from '../components/EstadoARCA.vue'

ChartJS.register(BarElement, CategoryScale, LinearScale, ArcElement, Tooltip)
ChartJS.defaults.font.family = 'Inter, system-ui, sans-serif'

const data = useDataStore()
const dia = ref(dayKey(new Date()))
const q = ref('')
const ver = ref<Venta | null>(null)

const esHoy = computed(() => dia.value === dayKey(new Date()))
const delDia = computed(() => data.ventas.filter((v) => dayKey(v.fecha) === dia.value).sort((a, b) => b.fecha.localeCompare(a.fecha)))
const filtradas = computed(() => {
  const t = q.value.toLowerCase()
  return delDia.value.filter((v) => !t || v.numero.includes(t) || v.clienteNombre.toLowerCase().includes(t) || v.cae.includes(t))
})

const total = computed(() => delDia.value.reduce((s, v) => s + v.total, 0))
const iva = computed(() => delDia.value.reduce((s, v) => s + v.ivaTotal, 0))
const promedio = computed(() => (delDia.value.length ? total.value / delDia.value.length : 0))
const pendientes = computed(() => delDia.value.filter((v) => v.estadoARCA !== 'Aprobado').length)

const tooltipMoney = { callbacks: { label: (ctx: { raw: unknown }) => ` ${fmtMoney(Number(ctx.raw))}` } }
const barOptions: ChartOptions<'bar'> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: tooltipMoney },
  scales: {
    x: { grid: { display: false }, border: { display: false } },
    y: { grid: { color: '#ececec' }, border: { display: false }, ticks: { callback: (v) => `$${Number(v) / 1000}k` } },
  },
}

const porHora = computed(() => {
  const vals = Array(12).fill(0)
  delDia.value.forEach((v) => {
    const h = new Date(v.fecha).getHours() - 8
    if (h >= 0 && h < 12) vals[h] += v.total
  })
  return {
    labels: vals.map((_, i) => `${8 + i}h`),
    datasets: [{ data: vals, backgroundColor: '#7fdcdc', hoverBackgroundColor: '#5ccaca', borderRadius: 8 }],
  }
})

const porMedio = computed(() => {
  const m: Partial<Record<MedioPago, number>> = {}
  delDia.value.forEach((v) => (m[v.medioPago] = (m[v.medioPago] ?? 0) + v.total))
  return (Object.entries(m) as [MedioPago, number][]).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)
})
const medioChart = computed(() => ({
  labels: porMedio.value.map((m) => m.name),
  datasets: [{ data: porMedio.value.map((m) => m.value), backgroundColor: porMedio.value.map((m) => COLOR_MEDIO[m.name]), borderWidth: 3, borderColor: '#fff' }],
}))
const doughnutOptions: ChartOptions<'doughnut'> = { responsive: true, maintainAspectRatio: false, cutout: '62%', plugins: { legend: { display: false }, tooltip: tooltipMoney } }

const top = computed(() => {
  const m: Record<string, { nombre: string; cant: number; total: number }> = {}
  delDia.value.forEach((v) => v.items.forEach((i) => {
    m[i.productoId] ??= { nombre: i.nombre, cant: 0, total: 0 }
    m[i.productoId].cant += i.cantidad
    m[i.productoId].total += i.cantidad * i.precioUnitario
  }))
  return Object.values(m).sort((a, b) => b.cant - a.cant).slice(0, 5)
})

const ultimos7 = computed(() => Array.from({ length: 7 }, (_, i) => {
  const d = new Date(dia.value + 'T12:00')
  d.setDate(d.getDate() - (6 - i))
  const k = dayKey(d)
  return { label: d.toLocaleDateString('es-AR', { weekday: 'short', day: 'numeric' }), k, total: data.ventas.filter((v) => dayKey(v.fecha) === k).reduce((s, v) => s + v.total, 0) }
}))
const semanaChart = computed(() => ({
  labels: ultimos7.value.map((d) => d.label),
  datasets: [{ data: ultimos7.value.map((d) => d.total), backgroundColor: ultimos7.value.map((d) => (d.k === dia.value ? '#f58f88' : '#c9ccd6')), borderRadius: 8 }],
}))
const semanaOptions = computed<ChartOptions<'bar'>>(() => ({
  ...barOptions,
  onClick: (_e, els) => { if (els[0]) dia.value = ultimos7.value[els[0].index].k },
  onHover: (e, els) => { (e.native?.target as HTMLElement | null)?.style.setProperty('cursor', els.length ? 'pointer' : 'default') },
}))

const cajasDia = computed(() => data.cajas.filter((c) => dayKey(c.abiertaEn) === dia.value))

function mover(n: number) {
  const d = new Date(dia.value + 'T12:00')
  d.setDate(d.getDate() + n)
  dia.value = dayKey(d)
}

function exportar() {
  const filas = [['Numero', 'Fecha', 'Hora', 'Tipo', 'Cliente', 'Medio de pago', 'Neto', 'IVA', 'Total', 'CAE', 'Estado ARCA']]
  delDia.value.forEach((v) => filas.push([v.numero, fmtDate(v.fecha), fmtTime(v.fecha), v.tipo, v.clienteNombre, v.medioPago, v.subtotal.toFixed(2), v.ivaTotal.toFixed(2), v.total.toFixed(2), v.cae, v.estadoARCA]))
  const csv = filas.map((f) => f.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(';')).join('\n')
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' }))
  a.download = `ventas-${dia.value}.csv`
  a.click()
}

const print = () => window.print()
</script>

<template>
  <PageHeader :seccion="seccion('/facturacion')">
    <template #actions>
      <div class="flex items-center rounded-xl border border-tinta-100 bg-white">
        <button class="p-2.5 hover:bg-tinta-50" @click="mover(-1)"><ChevronLeft class="h-4 w-4" /></button>
        <input v-model="dia" type="date" class="border-x border-tinta-100 px-3 py-2 text-sm font-semibold outline-none" :max="dayKey(new Date())" />
        <button class="p-2.5 hover:bg-tinta-50 disabled:opacity-30" :disabled="esHoy" @click="mover(1)"><ChevronRight class="h-4 w-4" /></button>
      </div>
      <button v-if="!esHoy" class="btn-ghost" @click="dia = dayKey(new Date())">Hoy</button>
      <button class="btn-ghost no-print" @click="exportar"><Download class="h-4 w-4" />CSV</button>
      <button class="btn-primary no-print" @click="print"><Printer class="h-4 w-4" />Imprimir reporte</button>
    </template>
  </PageHeader>

  <div class="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <StatCard :label="esHoy ? 'Vendido hoy' : 'Vendido en el día'" :value="fmtMoney(total)" :icon="DollarSign" tone="bg-turquesa-400 text-tinta" :hint="fmtDate(dia + 'T12:00')" />
    <StatCard label="Comprobantes" :value="String(delDia.length)" :icon="FileText" tone="bg-tinta-200 text-tinta" :hint="pendientes ? `${pendientes} pendiente(s) en ARCA` : 'Todos autorizados'" />
    <StatCard label="Ticket promedio" :value="fmtMoney(promedio)" :icon="TrendingUp" tone="bg-rojo-200 text-rojo-800" />
    <StatCard label="IVA débito fiscal" :value="fmtMoney(iva)" :icon="Percent" tone="bg-amarillo-400 text-tinta" />
  </div>

  <div class="mb-6 grid gap-6 xl:grid-cols-3">
    <div class="card p-5 xl:col-span-2">
      <h3 class="mb-4 text-lg font-semibold">Ventas por hora</h3>
      <div class="h-64"><Bar :data="porHora" :options="barOptions" /></div>
    </div>
    <div class="card p-5">
      <h3 class="mb-4 text-lg font-semibold">Medios de pago</h3>
      <template v-if="porMedio.length">
        <div class="h-44"><Doughnut :data="medioChart" :options="doughnutOptions" /></div>
        <ul class="mt-4 space-y-2 text-sm">
          <li v-for="m in porMedio" :key="m.name" class="flex items-center gap-2">
            <span class="h-3 w-3 rounded" :style="{ background: COLOR_MEDIO[m.name] }" />
            <span class="flex-1">{{ m.name }}</span>
            <span class="text-tinta-500">{{ ((m.value / total) * 100).toFixed(0) }}%</span>
            <b class="w-28 text-right">{{ fmtMoney(m.value) }}</b>
          </li>
        </ul>
      </template>
      <p v-else class="py-10 text-center text-sm text-tinta-300">Sin datos</p>
    </div>
  </div>

  <div class="mb-6 grid gap-6 xl:grid-cols-3">
    <div class="card p-5">
      <h3 class="mb-4 text-lg font-semibold">Más vendidos</h3>
      <ol v-if="top.length" class="space-y-3">
        <li v-for="(t, i) in top" :key="t.nombre" class="flex items-center gap-3">
          <span :class="['grid h-8 w-8 place-items-center rounded-lg font-display font-bold', i === 0 ? 'bg-rojo-200 text-rojo-800' : i === 1 ? 'bg-turquesa-200 text-turquesa-800' : 'bg-tinta-50']">{{ i + 1 }}</span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium">{{ t.nombre }}</p>
            <p class="text-xs text-tinta-500">{{ t.cant }} unidades</p>
          </div>
          <b class="text-sm">{{ fmtMoney(t.total) }}</b>
        </li>
      </ol>
      <p v-else class="py-10 text-center text-sm text-tinta-300">Sin datos</p>
    </div>
    <div class="card p-5 xl:col-span-2">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h3 class="text-lg font-semibold">Últimos 7 días</h3>
        <div class="flex gap-2">
          <span v-for="c in cajasDia" :key="c.id" :class="['inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold', c.cerradaEn ? 'bg-tinta-50 text-tinta-500' : 'bg-turquesa-50 text-turquesa-700']">
            Caja {{ fmtTime(c.abiertaEn) }} – {{ c.cerradaEn ? fmtTime(c.cerradaEn) : 'abierta' }}
          </span>
        </div>
      </div>
      <div class="h-56"><Bar :data="semanaChart" :options="semanaOptions" /></div>
    </div>
  </div>

  <div class="card overflow-hidden">
    <div class="flex flex-wrap items-center gap-3 border-b border-tinta-100 p-4">
      <h3 class="text-lg font-semibold">Comprobantes emitidos</h3>
      <div class="ml-auto"><SearchInput v-model="q" placeholder="N°, cliente o CAE..." /></div>
    </div>
    <EmptyState v-if="!filtradas.length" :icon="Receipt" title="Sin comprobantes" text="No hay ventas registradas para esta fecha." />
    <div v-else class="scroll-thin overflow-x-auto">
      <table class="w-full min-w-[900px]">
        <thead class="bg-tinta-50">
          <tr><th class="th">Hora</th><th class="th">Comprobante</th><th class="th">Cliente</th><th class="th">Medio</th><th class="th">CAE</th><th class="th">ARCA</th><th class="th text-right">Total</th></tr>
        </thead>
        <tbody class="divide-y divide-tinta-100">
          <tr v-for="v in filtradas" :key="v.id" class="cursor-pointer hover:bg-tinta-50/60" @click="ver = v">
            <td class="td text-tinta-500">{{ fmtTime(v.fecha) }}</td>
            <td class="td">
              <div class="flex items-center gap-2">
                <span :class="['grid h-7 w-7 place-items-center rounded-lg font-display text-sm font-bold', tipoBadge(v.tipo)]">{{ v.tipo.slice(-1) }}</span>
                <span class="font-mono text-xs">{{ v.numero }}</span>
              </div>
            </td>
            <td class="td font-medium">{{ v.clienteNombre }}</td>
            <td class="td"><span class="inline-flex items-center gap-2 text-sm"><span class="h-2.5 w-2.5 rounded-full" :style="{ background: COLOR_MEDIO[v.medioPago] }" />{{ v.medioPago }}</span></td>
            <td class="td font-mono text-xs text-tinta-500">{{ v.cae }}</td>
            <td class="td"><EstadoARCA :estado="v.estadoARCA" /></td>
            <td class="td text-right font-semibold">{{ fmtMoney(v.total) }}</td>
          </tr>
        </tbody>
        <tfoot class="bg-tinta-100 text-tinta">
          <tr>
            <td class="td font-display uppercase" colspan="6">Total del día · {{ delDia.length }} comprobantes</td>
            <td class="td text-right font-display text-lg font-semibold">{{ fmtMoney(total) }}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>

  <Modal :open="!!ver" :title="ver ? `${ver.tipo} ${ver.numero}` : ''" size="lg" accent="bg-tinta" @close="ver = null">
    <Comprobante v-if="ver" :venta="ver" />
    <template #footer><button class="btn-primary" @click="print"><Printer class="h-4 w-4" />Imprimir</button></template>
  </Modal>
</template>
