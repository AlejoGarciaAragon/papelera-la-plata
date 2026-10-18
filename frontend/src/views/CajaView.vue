<script setup>
import { useCajaView } from '../composables/useCajaView'

const {
  productosFiltrados, carrito, busqueda, metodoPago, cargando, procesandoVenta, error, exito,
  total, precio, stockDisponible, agregarProducto, buscarYAgregar, cambiarCantidad,
  eliminarItem, confirmarVenta
} = useCajaView()
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-slate-800">Caja</h2>
      <p class="mt-1 text-sm text-slate-500">Registrá ventas y controlá el stock en tiempo real.</p>
    </div>

    <div v-if="error" class="rounded-xl border border-rose-100 bg-rose-50 p-4 text-sm text-rose-700">{{ error }}</div>
    <div v-if="exito" class="rounded-xl border border-emerald-100 bg-emerald-50 p-4 text-sm text-emerald-700">{{ exito }}</div>

    <div class="grid gap-6 lg:grid-cols-[1.35fr_1fr]">
      <section class="rounded-xl bg-white p-5 shadow-sm">
        <div class="flex gap-3">
          <input
            v-model="busqueda"
            autofocus
            class="w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
            placeholder="Buscar por nombre o escanear código de barras..."
            @keyup.enter="buscarYAgregar"
          />
          <button class="rounded-lg bg-teal-100 px-4 font-medium text-teal-800 hover:bg-teal-200" @click="buscarYAgregar">Agregar</button>
        </div>

        <div v-if="cargando" class="py-12 text-center text-sm text-slate-400">Cargando productos...</div>
        <div v-else class="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <button
            v-for="producto in productosFiltrados"
            :key="producto.id"
            type="button"
            class="rounded-xl border border-slate-100 p-4 text-left transition hover:border-teal-200 hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!stockDisponible(producto)"
            @click="agregarProducto(producto)"
          >
            <span class="block font-medium text-slate-800">{{ producto.nombre }}</span>
            <span class="mt-1 block text-xs text-slate-400">{{ producto.codigo_barra }}</span>
            <span class="mt-3 block font-semibold text-teal-700">{{ precio(producto.precio_venta) }}</span>
            <span class="mt-1 block text-xs text-slate-500">Stock: {{ stockDisponible(producto) }}</span>
          </button>
        </div>
        <p v-if="!cargando && !productosFiltrados.length" class="py-12 text-center text-sm text-slate-400">No se encontraron productos.</p>
      </section>

      <section class="flex flex-col rounded-xl bg-white p-5 shadow-sm">
        <h3 class="text-lg font-bold text-slate-800">Ticket de venta</h3>
        <div class="mt-4 flex-1 divide-y divide-slate-100">
          <div v-for="item in carrito" :key="item.id" class="flex items-center gap-3 py-4">
            <div class="min-w-0 flex-1">
              <p class="truncate font-medium text-slate-800">{{ item.nombre }}</p>
              <p class="text-xs text-slate-400">{{ precio(item.precio_venta) }} c/u</p>
            </div>
            <div class="flex items-center gap-2">
              <button class="h-7 w-7 rounded bg-slate-100 text-slate-700 hover:bg-slate-200" @click="cambiarCantidad(item, -1)">−</button>
              <span class="w-5 text-center text-sm">{{ item.cantidad }}</span>
              <button class="h-7 w-7 rounded bg-slate-100 text-slate-700 hover:bg-slate-200" @click="cambiarCantidad(item, 1)">+</button>
            </div>
            <span class="w-20 text-right text-sm font-medium text-slate-700">{{ precio(item.precio_venta * item.cantidad) }}</span>
            <button class="text-rose-600 hover:text-rose-800" title="Eliminar del carrito" @click="eliminarItem(item)">×</button>
          </div>
          <p v-if="!carrito.length" class="py-12 text-center text-sm text-slate-400">El carrito está vacío.</p>
        </div>

        <div class="mt-5 border-t border-slate-100 pt-5">
          <label class="block text-sm font-medium text-slate-600">
            Método de pago
            <select v-model="metodoPago" class="campo">
              <option value="efectivo">Efectivo</option>
              <option value="tarjeta">Tarjeta</option>
              <option value="transferencia">Transferencia</option>
            </select>
          </label>
          <div class="mt-5 flex items-center justify-between">
            <span class="text-lg font-medium text-slate-600">Total</span>
            <span class="text-3xl font-bold text-slate-800">{{ precio(total) }}</span>
          </div>
          <button
            class="mt-5 w-full rounded-xl bg-teal-400 px-4 py-4 text-lg font-bold text-white hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="procesandoVenta || !carrito.length"
            @click="confirmarVenta"
          >
            {{ procesandoVenta ? 'Procesando...' : 'Confirmar Venta' }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>
