<script setup>
import { useDashboardVentasView } from '../composables/useDashboardVentasView'

const {
  ventasFiltradas, resumen, fecha, metodoPago, estado, cargando, error, ventaSeleccionada,
  ventaAAnular, anulando, esDueno, totalTarjetaTransferencia, precio, fechaHora,
  etiquetaMetodo, etiquetaEstado, cargarDatos, abrirDetalle, abrirAnulacion, confirmarAnulacion
} = useDashboardVentasView()
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-slate-800">Dashboard y ventas realizadas</h2>
      <p class="mt-1 text-sm text-slate-500">Consultá la actividad financiera y gestioná los tickets del día.</p>
    </div>

    <div v-if="error" class="flex items-center justify-between rounded-xl border border-rose-100 bg-rose-50 p-4 text-sm text-rose-700">
      <span>{{ error }}</span><button class="font-bold" @click="error = ''">×</button>
    </div>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <article v-for="kpi in [
        { label: 'Recaudación total', value: precio(resumen.recaudacion_total) },
        { label: 'Total en efectivo', value: precio(resumen.recaudacion_por_metodo.efectivo) },
        { label: 'Tarjeta / transferencia', value: precio(totalTarjetaTransferencia) },
        { label: 'Operaciones', value: resumen.cantidad_ventas }
      ]" :key="kpi.label" class="rounded-xl bg-white p-5 shadow-sm">
        <p class="text-sm text-slate-500">{{ kpi.label }}</p>
        <p class="mt-2 text-2xl font-bold text-slate-800">{{ kpi.value }}</p>
      </article>
    </section>

    <section class="rounded-xl bg-white p-4 shadow-sm">
      <div class="grid gap-3 md:grid-cols-[1fr_1fr_1fr_auto]">
        <label class="text-sm text-slate-600">Fecha<input v-model="fecha" type="date" class="campo" @change="cargarDatos" /></label>
        <label class="text-sm text-slate-600">Método de pago<select v-model="metodoPago" class="campo" @change="cargarDatos"><option value="">Todos</option><option value="efectivo">Efectivo</option><option value="tarjeta">Tarjeta</option><option value="transferencia">Transferencia</option></select></label>
        <label class="text-sm text-slate-600">Estado<select v-model="estado" class="campo" @change="cargarDatos"><option value="">Todos</option><option value="completada">Completada</option><option value="cancelada">Cancelada</option></select></label>
        <button class="self-end rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-200" @click="cargarDatos">Actualizar</button>
      </div>
    </section>

    <section class="overflow-hidden rounded-xl bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[850px] text-left text-sm">
          <thead class="border-b border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr><th class="px-5 py-4">ID Venta</th><th class="px-5 py-4">Fecha/Hora</th><th class="px-5 py-4">Vendedor</th><th class="px-5 py-4">Método</th><th class="px-5 py-4">Total</th><th class="px-5 py-4">Estado</th><th class="px-5 py-4">Acciones</th></tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="venta in ventasFiltradas" :key="venta.id" :class="venta.estado === 'cancelada' ? 'opacity-50' : ''" class="text-slate-600">
              <td class="px-5 py-4 font-medium text-slate-800">#{{ venta.id }}</td>
              <td class="px-5 py-4">{{ fechaHora(venta.fecha) }}</td>
              <td class="px-5 py-4">{{ venta.vendedor_nombre }}</td>
              <td class="px-5 py-4">{{ etiquetaMetodo(venta.metodo_pago) }}</td>
              <td class="px-5 py-4 font-medium">{{ precio(venta.total) }}</td>
              <td class="px-5 py-4"><span :class="venta.estado === 'completada' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'" class="rounded-full px-2.5 py-1 text-xs font-medium">{{ etiquetaEstado(venta.estado) }}</span></td>
              <td class="px-5 py-4"><div class="flex gap-3"><button class="text-teal-700 hover:text-teal-900" @click="abrirDetalle(venta)">Ver detalle</button><button v-if="esDueno && venta.estado === 'completada'" class="text-rose-600 hover:text-rose-800" @click="abrirAnulacion(venta)">Anular</button></div></td>
            </tr>
            <tr v-if="!cargando && !ventasFiltradas.length"><td colspan="7" class="px-5 py-12 text-center text-slate-400">No hay ventas para los filtros seleccionados.</td></tr>
            <tr v-if="cargando"><td colspan="7" class="px-5 py-12 text-center text-slate-400">Cargando ventas...</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="ventaSeleccionada" class="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/30 p-4">
      <div class="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
        <div class="flex items-center justify-between"><h3 class="text-xl font-bold text-slate-800">Detalle de venta #{{ ventaSeleccionada.id }}</h3><button class="text-2xl text-slate-400" @click="ventaSeleccionada = null">×</button></div>
        <div class="mt-5 divide-y divide-slate-100">
          <div v-for="detalle in ventaSeleccionada.detalles" :key="detalle.id" class="flex justify-between py-3 text-sm"><span>{{ detalle.cantidad }} × {{ detalle.producto_nombre }}<small class="ml-2 text-slate-400">{{ precio(detalle.precio_unitario) }}</small></span><strong>{{ precio(detalle.subtotal) }}</strong></div>
        </div>
        <div class="mt-5 flex justify-between border-t border-slate-100 pt-4 text-lg font-bold text-slate-800"><span>Total</span><span>{{ precio(ventaSeleccionada.total) }}</span></div>
      </div>
    </div>

    <div v-if="ventaAAnular" class="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/30 p-4">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="text-xl font-bold text-slate-800">Anular venta #{{ ventaAAnular.id }}</h3>
        <p class="mt-3 text-sm text-slate-600">¿Querés anular esta venta? Se devolverá el stock al inventario.</p>
        <div class="mt-6 flex justify-end gap-3"><button class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100" @click="ventaAAnular = null">Cancelar</button><button class="rounded-lg bg-rose-600 px-4 py-2 font-medium text-white hover:bg-rose-700 disabled:opacity-50" :disabled="anulando" @click="confirmarAnulacion">{{ anulando ? 'Anulando...' : 'Anular venta' }}</button></div>
      </div>
    </div>
  </div>
</template>
