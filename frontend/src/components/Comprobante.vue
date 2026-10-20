<script setup>import BrandLogo from './BrandLogo.vue';
import { computed } from 'vue';
import { fmtDate, fmtDateTime, fmtMoney } from '../lib/format';
import { tipoBadge } from '../lib/ui';
import EstadoARCA from './EstadoARCA.vue';
const props = defineProps({ venta: Object });
const letra = computed(() => props.venta.tipo.replace('Factura ', '').slice(0, 1));
const codigo = computed(() => (letra.value === 'A' ? '01' : letra.value === 'B' ? '06' : '11'));
</script>

<template>
  <div class="rounded-2xl border border-tinta-100 bg-white">
    <div class="grid grid-cols-[1fr_auto_1fr] border-b border-tinta-100">
      <div class="p-5">
        <BrandLogo size="sm" class="mb-2" />
        <p class="text-xs text-tinta-500">Calle 50 N° 123, La Plata · IVA Responsable Inscripto</p>
      </div>
      <div class="flex flex-col items-center border-x border-tinta-100 px-5 pt-5">
        <div :class="['grid h-14 w-14 place-items-center rounded-xl font-display text-3xl font-bold', tipoBadge(venta.tipo)]">{{ letra }}</div>
        <p class="mt-1 text-[10px] text-tinta-500">COD. {{ codigo }}</p>
      </div>
      <div class="p-5 text-right text-sm">
        <p class="font-display text-xl font-semibold uppercase">{{ venta.tipo }}</p>
        <p class="font-mono">N° {{ venta.numero }}</p>
        <p class="text-tinta-500">{{ fmtDateTime(venta.fecha) }}</p>
        <p class="mt-2 text-xs text-tinta-500">CUIT 30-12345678-9</p>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-2 border-b border-tinta-100 px-5 py-3 text-sm">
      <p><span class="text-tinta-500">Cliente: </span><b>{{ venta.clienteNombre }}</b></p>
      <p class="text-right"><span class="text-tinta-500">Pago: </span><b>{{ venta.medioPago }}</b></p>
    </div>
    <table class="w-full">
      <thead class="bg-tinta-50">
        <tr><th class="th">Producto</th><th class="th text-right">Cant.</th><th class="th text-right">P. Unit.</th><th class="th text-right">Importe</th></tr>
      </thead>
      <tbody class="divide-y divide-tinta-100">
        <tr v-for="(it, i) in venta.items" :key="i">
          <td class="td">{{ it.nombre }}</td>
          <td class="td text-right">{{ it.cantidad }}</td>
          <td class="td text-right">{{ fmtMoney(it.precioUnitario) }}</td>
          <td class="td text-right font-medium">{{ fmtMoney(it.cantidad * it.precioUnitario) }}</td>
        </tr>
      </tbody>
    </table>
    <div class="flex flex-wrap items-end justify-between gap-4 border-t border-tinta-100 p-5">
      <div class="space-y-1 text-xs">
        <EstadoARCA :estado="venta.estadoARCA" />
        <p><span class="text-tinta-500">CAE:</span> <span class="font-mono font-semibold">{{ venta.cae }}</span></p>
        <p><span class="text-tinta-500">Vto. CAE:</span> {{ fmtDate(venta.caeVto) }}</p>
      </div>
      <div class="min-w-[220px] space-y-1 text-sm">
        <template v-if="venta.tipo === 'Factura A'">
          <div class="flex justify-between"><span class="text-tinta-500">Neto gravado</span><span>{{ fmtMoney(venta.subtotal) }}</span></div>
          <div class="flex justify-between"><span class="text-tinta-500">IVA 21%</span><span>{{ fmtMoney(venta.ivaTotal) }}</span></div>
        </template>
        <div class="flex justify-between border-t border-tinta-100 pt-2 font-display text-2xl font-semibold">
          <span>Total</span><span>{{ fmtMoney(venta.total) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
