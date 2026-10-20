<script setup>import { useFacturacionPage } from '../composables/useFacturacionPage';
const { ChevronLeft, ChevronRight, Download, Printer, Receipt, DollarSign, PageHeader, SearchInput, Modal, EmptyState, StatCard, Comprobante, EstadoARCA, seccion, dayKey, fmtDate, fmtDateTime, fmtMoney, fmtTime, COLOR_MEDIO, tipoBadge, dia, q, ver, esHoy, delDia, filtradas, total, cajasDia, resumenCaja, mediosCaja, fechaCaja, fechaDeCaja, detalleCaja, resumenDetalleCaja, mover, exportarVentasCaja, print, } = useFacturacionPage();
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
    </template>
  </PageHeader>

  <div class="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <StatCard :label="esHoy ? 'Vendido hoy' : 'Vendido en el día'" :value="fmtMoney(total)" :icon="DollarSign" tone="bg-turquesa-400 text-tinta" :hint="fmtDate(dia + 'T12:00')" />
  </div>

  <div class="card mb-6 overflow-hidden">
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

  <section class="card mb-6 p-5">
    <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h3 class="text-lg font-semibold">Cajas del mes</h3>
        <p class="text-sm text-tinta-500">{{ fechaCaja ? `Cajas del ${fmtDate(fechaCaja + 'T12:00')}` : 'Últimos 3 días' }}</p>
      </div>
      <div class="flex flex-wrap items-end gap-2">
        <label class="block">
          <span class="label">Buscar por día</span>
          <input v-model="fechaCaja" class="input w-auto" type="date" :max="dayKey(new Date())" />
        </label>
        <button v-if="fechaCaja" class="btn-ghost" @click="fechaCaja = ''">Últimos 3 días</button>
        <span class="pb-2 text-sm text-tinta-500">{{ cajasDia.length }} {{ cajasDia.length === 1 ? 'caja' : 'cajas' }}</span>
      </div>
    </div>
    <EmptyState v-if="!cajasDia.length" :icon="Receipt" :title="fechaCaja ? 'Sin cajas para ese día' : 'Sin cajas recientes'" :text="fechaCaja ? 'No hay cajas registradas en la fecha seleccionada.' : 'No se abrieron cajas en los últimos tres días.'" />
    <div v-else class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      <button v-for="caja in cajasDia" :key="caja.id" class="rounded-xl border border-tinta-100 p-4 text-left transition hover:border-turquesa-300 hover:bg-turquesa-50/40" @click="detalleCaja = caja">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h4 class="font-display text-lg font-semibold uppercase">Caja día {{ fmtDate(fechaDeCaja(caja) + 'T12:00') }}</h4>
            <p class="mt-1 text-sm text-tinta-500">{{ fmtTime(caja.abiertaEn) }} · {{ caja.usuario }}</p>
          </div>
          <span :class="['shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold', caja.cerradaEn ? 'bg-tinta-50 text-tinta-500' : 'bg-turquesa-50 text-turquesa-700']">{{ caja.cerradaEn ? 'Cerrada' : 'Abierta' }}</span>
        </div>
        <div class="mt-4 flex items-end justify-between border-t border-tinta-100 pt-3">
          <div>
            <p class="text-xs text-tinta-500">Ventas ({{ resumenCaja(caja).cantidadVentas }})</p>
            <b class="font-display text-xl">{{ fmtMoney(resumenCaja(caja).totalVentas) }}</b>
          </div>
          <span class="text-sm font-semibold text-turquesa-700">Ver detalle</span>
        </div>
      </button>
    </div>
  </section>

  <Modal :open="!!detalleCaja" :title="detalleCaja ? `Caja día ${fmtDate(fechaDeCaja(detalleCaja) + 'T12:00')}` : ''" size="lg" accent="bg-rojo-400" @close="detalleCaja = null">
    <div v-if="detalleCaja && resumenDetalleCaja" class="space-y-4">
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div class="rounded-xl bg-turquesa-50 px-4 py-3"><p class="text-xs text-tinta-500">Ventas ({{ resumenDetalleCaja.cantidadVentas }})</p><p class="font-display text-xl font-bold">{{ fmtMoney(resumenDetalleCaja.totalVentas) }}</p></div>
        <div class="rounded-xl bg-tinta-50 px-4 py-3"><p class="text-xs text-tinta-500">Efectivo esperado</p><p class="font-display text-xl font-bold">{{ fmtMoney(resumenDetalleCaja.efectivoEsperado) }}</p></div>
        <div class="rounded-xl bg-tinta-50 px-4 py-3"><p class="text-xs text-tinta-500">Ingresos</p><p class="font-display text-xl font-bold">{{ fmtMoney(resumenDetalleCaja.ingresos) }}</p></div>
        <div class="rounded-xl bg-rojo-50 px-4 py-3"><p class="text-xs text-tinta-500">Egresos</p><p class="font-display text-xl font-bold">{{ fmtMoney(resumenDetalleCaja.egresos) }}</p></div>
      </div>

      <div class="grid grid-cols-2 gap-2 sm:grid-cols-3">
        <div v-for="medio in mediosCaja" :key="medio" class="flex items-center justify-between rounded-xl bg-tinta-50 px-4 py-3 text-sm">
          <span class="text-tinta-500">{{ medio }}</span><b>{{ fmtMoney(resumenDetalleCaja.ventasPorMedio[medio]) }}</b>
        </div>
      </div>

      <div class="rounded-xl border border-tinta-100 p-4 text-sm">
        <div class="flex justify-between"><span class="text-tinta-500">Monto inicial</span><span>{{ fmtMoney(detalleCaja.montoInicial) }}</span></div>
        <div class="flex justify-between"><span class="text-tinta-500">+ Ventas en efectivo</span><span>{{ fmtMoney(resumenDetalleCaja.ventasPorMedio.Efectivo) }}</span></div>
        <div class="flex justify-between"><span class="text-tinta-500">+ Ingresos</span><span>{{ fmtMoney(resumenDetalleCaja.ingresos) }}</span></div>
        <div class="flex justify-between"><span class="text-tinta-500">− Egresos</span><span>{{ fmtMoney(resumenDetalleCaja.egresos) }}</span></div>
        <div class="mt-2 flex justify-between border-t border-tinta-100 pt-2 font-semibold"><span>Efectivo esperado</span><span>{{ fmtMoney(resumenDetalleCaja.efectivoEsperado) }}</span></div>
        <template v-if="detalleCaja.cerradaEn">
          <div class="mt-2 flex justify-between"><span class="text-tinta-500">Efectivo contado</span><span>{{ fmtMoney(resumenDetalleCaja.montoCierre) }}</span></div>
          <div class="flex justify-between font-semibold"><span>Diferencia</span><span :class="resumenDetalleCaja.diferencia === 0 ? 'text-turquesa-700' : 'text-rojo-600'">{{ fmtMoney(resumenDetalleCaja.diferencia) }}</span></div>
        </template>
        <p class="mt-2 text-xs text-tinta-500">Abierta {{ fmtDateTime(detalleCaja.abiertaEn) }} · {{ detalleCaja.usuario }}<span v-if="detalleCaja.cerradaEn"> · Cerrada {{ fmtDateTime(detalleCaja.cerradaEn) }}</span></p>
      </div>

    </div>
    <template #footer>
      <button class="btn-ghost no-print" @click="exportarVentasCaja(detalleCaja)"><Download class="h-4 w-4" />Ventas del día</button>
    </template>
  </Modal>

  <Modal :open="!!ver" :title="ver ? `${ver.tipo} ${ver.numero}` : ''" size="lg" accent="bg-tinta" @close="ver = null">
    <Comprobante v-if="ver" :venta="ver" />
    <template #footer><button class="btn-primary" @click="print"><Printer class="h-4 w-4" />Imprimir</button></template>
  </Modal>
</template>
