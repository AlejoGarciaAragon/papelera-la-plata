<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  Minus, Plus, Trash2, ShoppingCart, Banknote, CreditCard, Wallet, Smartphone, Lock, Unlock, History,
  ArrowDownCircle, ArrowUpCircle, Receipt, Printer, CheckCircle2, ScanBarcode, User,
} from 'lucide-vue-next'
import { useDataStore } from '../stores/data'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import { seccion } from '../lib/sections'
import { fmtDateTime, fmtMoney, fmtTime, tipoPorCondicion } from '../lib/format'
import { tipoBadge } from '../lib/ui'
import type { ItemVenta, MedioPago, TipoComprobante, Venta } from '../types'
import PageHeader from '../components/PageHeader.vue'
import Modal from '../components/Modal.vue'
import EmptyState from '../components/EmptyState.vue'
import Field from '../components/Field.vue'
import Comprobante from '../components/Comprobante.vue'

const MEDIOS = [
  { id: 'Efectivo' as MedioPago, icon: Banknote },
  { id: 'Débito' as MedioPago, icon: CreditCard },
  { id: 'Crédito' as MedioPago, icon: CreditCard },
  { id: 'Cuenta DNI' as MedioPago, icon: Wallet },
  { id: 'Mercado Pago' as MedioPago, icon: Smartphone },
]

const data = useDataStore()
const auth = useAuthStore()
const { push: toast } = useToastStore()

const montoInicial = ref<number | ''>('')
const q = ref('')
const cat = ref('')
const carrito = ref<ItemVenta[]>([])
const clienteId = ref('cf')
const tipo = ref<TipoComprobante>('Factura B')
const medio = ref<MedioPago>('Efectivo')
const pagaCon = ref<number | ''>('')
const emitida = ref<Venta | null>(null)
const emitiendo = ref(false)
const mov = ref<null | 'Ingreso' | 'Egreso'>(null)
const movForm = ref<{ concepto: string; monto: number | '' }>({ concepto: '', monto: '' })
const cierre = ref(false)
const verMovs = ref(false)
const contado = ref<number | ''>('')
const buscador = ref<HTMLInputElement | null>(null)

const caja = computed(() => data.cajaAbierta)
const ventasCaja = computed(() => data.ventas.filter((v) => v.cajaId === caja.value?.id))
const totalVentas = computed(() => ventasCaja.value.reduce((s, v) => s + v.total, 0))
const efectivoVentas = computed(() => ventasCaja.value.filter((v) => v.medioPago === 'Efectivo').reduce((s, v) => s + v.total, 0))
const ingresos = computed(() => caja.value?.movimientos.filter((m) => m.tipo === 'Ingreso').reduce((s, m) => s + m.monto, 0) ?? 0)
const egresos = computed(() => caja.value?.movimientos.filter((m) => m.tipo === 'Egreso').reduce((s, m) => s + m.monto, 0) ?? 0)
const efectivoEsperado = computed(() => (caja.value?.montoInicial ?? 0) + efectivoVentas.value + ingresos.value - egresos.value)
const porMedio = (id: MedioPago) => ventasCaja.value.filter((v) => v.medioPago === id).reduce((s, v) => s + v.total, 0)
const diferencia = computed(() => (Number(contado.value) || 0) - efectivoEsperado.value)

const ultimaCerrada = computed(() => [...data.cajas].filter((c) => c.cerradaEn).sort((a, b) => b.cerradaEn!.localeCompare(a.cerradaEn!))[0])

const visibles = computed(() => data.productos.filter((p) => {
  const t = q.value.toLowerCase()
  return !p.oculto && !catDe(p.categoriaId)?.oculto && (!cat.value || p.categoriaId === cat.value) && (!t || p.nombre.toLowerCase().includes(t) || p.codigo.includes(t))
}))
const catDe = (id: string) => data.categorias.find((c) => c.id === id)
const cantEnCarrito = (id: string) => carrito.value.find((i) => i.productoId === id)?.cantidad ?? 0

const total = computed(() => carrito.value.reduce((s, i) => s + i.cantidad * i.precioUnitario, 0))
const neto = computed(() => carrito.value.reduce((s, i) => s + (i.cantidad * i.precioUnitario) / (1 + i.iva / 100), 0))
const cliente = computed(() => data.clientes.find((c) => c.id === clienteId.value) ?? data.clientes[0])
const unidades = computed(() => carrito.value.reduce((s, i) => s + i.cantidad, 0))
const falta = computed(() => (medio.value === 'Efectivo' && Number(pagaCon.value) > 0 && Number(pagaCon.value) < total.value ? total.value - Number(pagaCon.value) : 0))
const vuelto = computed(() => (medio.value === 'Efectivo' && Number(pagaCon.value) > total.value ? Number(pagaCon.value) - total.value : 0))

const movimientos = computed(() => [
  ...ventasCaja.value.map((v) => ({ id: v.id, fecha: v.fecha, tipo: 'Venta' as const, concepto: `${v.tipo} ${v.numero} · ${v.clienteNombre}`, detalle: v.medioPago, monto: v.total, venta: v as Venta | undefined })),
  ...(caja.value?.movimientos ?? []).map((m) => ({ id: m.id, fecha: m.fecha, tipo: m.tipo, concepto: m.concepto, detalle: 'Efectivo', monto: m.monto, venta: undefined })),
].sort((a, b) => b.fecha.localeCompare(a.fecha)))

function abrir() {
  data.abrirCaja(Number(montoInicial.value) || 0, auth.user?.usuario ?? '')
  toast('Caja abierta. ¡Buenas ventas!')
}

function agregar(id: string) {
  const p = data.productos.find((x) => x.id === id)
  if (!p) return
  const item = carrito.value.find((i) => i.productoId === id)
  if ((item?.cantidad ?? 0) >= p.stock) return toast(`Sin stock suficiente de "${p.nombre}"`, 'error')
  if (item) item.cantidad++
  else carrito.value.push({ productoId: p.id, nombre: p.nombre, cantidad: 1, precioUnitario: p.precioVenta, iva: p.iva })
}

function cambiarCant(id: string, d: number) {
  const p = data.productos.find((x) => x.id === id)
  const item = carrito.value.find((i) => i.productoId === id)
  if (!item) return
  item.cantidad = Math.min(p?.stock ?? 999, item.cantidad + d)
  if (item.cantidad <= 0) quitar(id)
}
const quitar = (id: string) => (carrito.value = carrito.value.filter((i) => i.productoId !== id))

function escanear() {
  const p = data.productos.find((x) => x.codigo === q.value.trim() && !x.oculto)
  if (p) { agregar(p.id); q.value = '' }
  else if (visibles.value.length === 1) { agregar(visibles.value[0].id); q.value = '' }
}

function elegirCliente(id: string) {
  clienteId.value = id
  const c = data.clientes.find((x) => x.id === id)
  if (c) tipo.value = tipoPorCondicion(c.condicionIVA) as TipoComprobante
}

async function cobrar() {
  if (!carrito.value.length) return
  emitiendo.value = true
  await new Promise((r) => setTimeout(r, 900)) // simula la solicitud de CAE a ARCA
  emitida.value = data.registrarVenta({ cliente: cliente.value, tipo: tipo.value, medioPago: medio.value, items: carrito.value })
  emitiendo.value = false
  carrito.value = []
  pagaCon.value = ''
  elegirCliente('cf')
  medio.value = 'Efectivo'
}

function registrarMov() {
  if (!movForm.value.concepto || !Number(movForm.value.monto)) return toast('Completá concepto y monto', 'error')
  data.agregarMovimiento({ tipo: mov.value!, concepto: movForm.value.concepto, monto: Number(movForm.value.monto) })
  toast(`${mov.value} registrado`)
  movForm.value = { concepto: '', monto: '' }
  mov.value = null
}

function abrirCierre() {
  contado.value = efectivoEsperado.value
  cierre.value = true
}

function confirmarCierre() {
  data.cerrarCaja(Number(contado.value) || 0)
  cierre.value = false
  toast('Caja cerrada correctamente')
}

function cerrarComprobante() {
  emitida.value = null
  buscador.value?.focus()
}

const print = () => window.print()
</script>

<template>
  <!-- CAJA CERRADA -->
  <template v-if="!caja">
    <PageHeader :seccion="seccion('/caja')" />
    <div class="mx-auto mt-6 max-w-lg">
      <div class="card overflow-hidden">
        <div class="relative bg-turquesa-400 px-8 pb-10 pt-8">
          <div class="absolute bottom-0 right-0 h-24 w-24 bg-rojo-500" style="clip-path: polygon(100% 0, 100% 100%, 0 100%)" />
          <Lock class="h-10 w-10" />
          <h2 class="mt-3 text-4xl font-bold">Caja cerrada</h2>
          <p class="mt-1 text-tinta-700">Abrí la caja para comenzar a vender.</p>
        </div>
        <form class="space-y-4 p-8" @submit.prevent="abrir">
          <Field label="Monto inicial en efectivo">
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 font-semibold text-tinta-300">$</span>
              <input v-model.number="montoInicial" class="input pl-8 text-lg font-semibold" type="number" min="0" placeholder="0,00" autofocus />
            </div>
          </Field>
          <button class="btn-primary w-full py-3 text-base"><Unlock class="h-5 w-5" />Abrir caja</button>
          <p v-if="ultimaCerrada" class="text-center text-xs text-tinta-500">
            Último cierre: {{ fmtDateTime(ultimaCerrada.cerradaEn!) }} · {{ fmtMoney(ultimaCerrada.montoCierre ?? 0) }}
          </p>
        </form>
      </div>
    </div>
  </template>

  <!-- CAJA ABIERTA -->
  <template v-else>
    <PageHeader :seccion="seccion('/caja')">
      <template #info>
        <span class="hidden items-center gap-2 rounded-full bg-turquesa-50 px-3 py-1 text-xs font-semibold text-turquesa-700 md:inline-flex">
          <span class="h-2 w-2 rounded-full bg-turquesa-500" />Abierta {{ fmtTime(caja.abiertaEn) }} · {{ caja.usuario }}
        </span>
      </template>
      <template #actions>
        <button class="btn-ghost" @click="verMovs = true">
          <History class="h-4 w-4 text-tinta-500" />Movimientos
          <span class="rounded-full bg-tinta-50 px-2 text-xs text-tinta-500">{{ movimientos.length }}</span>
        </button>
        <button class="btn-ghost" @click="mov = 'Ingreso'"><ArrowDownCircle class="h-4 w-4 text-turquesa-600" />Ingreso</button>
        <button class="btn-ghost" @click="mov = 'Egreso'"><ArrowUpCircle class="h-4 w-4 text-rojo-500" />Egreso</button>
        <button class="btn-ghost text-rojo-700" @click="abrirCierre"><Lock class="h-4 w-4" />Cerrar caja</button>
      </template>
    </PageHeader>

    <div class="grid gap-6 xl:grid-cols-[1fr_440px]">
      <!-- Productos -->
      <section class="card flex min-h-[520px] flex-col overflow-hidden xl:h-[calc(100vh-11rem)]">
        <div class="space-y-3 border-b border-tinta-100 p-4">
          <form class="relative" @submit.prevent="escanear">
            <ScanBarcode class="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-turquesa-600" />
            <input ref="buscador" v-model="q" class="input py-3 pl-12 text-base" placeholder="Escaneá o buscá un producto y presioná Enter" autofocus />
          </form>
          <div class="scroll-thin flex gap-2 overflow-x-auto pb-1">
            <button :class="['shrink-0 rounded-full px-3.5 py-1.5 text-sm font-semibold transition', !cat ? 'bg-tinta text-white' : 'bg-tinta-50 text-tinta-500 hover:bg-tinta-100']" @click="cat = ''">Todos</button>
            <button v-for="c in data.categorias.filter((x) => !x.oculto)" :key="c.id" :class="['flex shrink-0 items-center gap-2 rounded-full px-3.5 py-1.5 text-sm font-semibold transition', cat === c.id ? 'bg-tinta text-white' : 'bg-tinta-50 text-tinta-700 hover:bg-tinta-100']" @click="cat = cat === c.id ? '' : c.id">
              <span class="h-2.5 w-2.5 rounded-full" :style="{ background: c.color }" />{{ c.nombre }}
            </button>
          </div>
        </div>
        <div class="scroll-thin grid flex-1 auto-rows-min grid-cols-2 gap-2.5 overflow-y-auto p-4 md:grid-cols-3 2xl:grid-cols-4">
          <button v-for="p in visibles" :key="p.id" :disabled="p.stock === 0"
            :class="['relative flex min-h-[88px] flex-col rounded-2xl border-2 p-3 text-left transition',
              p.stock === 0 ? 'cursor-not-allowed border-tinta-100 opacity-40'
              : cantEnCarrito(p.id) ? 'border-turquesa-400 bg-turquesa-50'
              : 'border-tinta-100 bg-white hover:border-turquesa-300 hover:shadow-card']"
            @click="agregar(p.id)">
            <span v-if="cantEnCarrito(p.id)" class="absolute -right-2 -top-2 grid h-7 min-w-7 place-items-center rounded-full bg-turquesa-500 px-2 text-sm font-bold text-white shadow-card">{{ cantEnCarrito(p.id) }}</span>
            <p class="line-clamp-2 flex-1 text-sm font-semibold leading-snug">
              <span class="mr-1.5 inline-block h-2 w-2 rounded-full align-middle" :style="{ background: catDe(p.categoriaId)?.color }" />{{ p.nombre }}
            </p>
            <div class="mt-2 flex items-end justify-between gap-2">
              <p class="font-display text-lg font-bold">{{ fmtMoney(p.precioVenta) }}</p>
              <span v-if="p.stock <= p.stockMinimo" :class="['shrink-0 rounded-md px-1.5 py-0.5 text-[11px] font-semibold', p.stock === 0 ? 'bg-rojo-50 text-rojo-600' : 'bg-amarillo-100 text-amarillo-700']">{{ p.stock === 0 ? 'Sin stock' : `Quedan ${p.stock}` }}</span>
            </div>
          </button>
          <div v-if="!visibles.length" class="col-span-full"><EmptyState :icon="ScanBarcode" title="Sin resultados" text="No hay productos que coincidan con la búsqueda." /></div>
        </div>
      </section>

      <!-- Cobro -->
      <section class="card flex flex-col overflow-hidden xl:sticky xl:top-20 xl:h-[calc(100vh-11rem)]">
        <div class="flex items-center gap-2 border-b border-tinta-100 p-3">
          <div class="relative min-w-0 flex-1">
            <User class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-tinta-300" />
            <select class="input py-2 pl-9" title="Cliente" :value="clienteId" @change="elegirCliente(($event.target as HTMLSelectElement).value)">
              <option v-for="c in data.clientes.filter((x) => !x.oculto || x.id === clienteId)" :key="c.id" :value="c.id">{{ c.razonSocial }}</option>
            </select>
          </div>
          <select v-model="tipo" title="Comprobante" :class="['input w-auto border-transparent py-2 font-semibold', tipoBadge(tipo)]">
            <option>Factura A</option><option>Factura B</option><option>Factura C</option>
          </select>
        </div>

        <div class="flex items-center justify-between px-4 pb-1 pt-2 text-xs font-semibold uppercase tracking-wider text-tinta-300">
          <span>{{ unidades }} {{ unidades === 1 ? 'artículo' : 'artículos' }}</span>
          <button v-if="carrito.length" class="normal-case tracking-normal text-tinta-500 hover:text-rojo-600" @click="carrito = []">Vaciar</button>
        </div>
        <div class="scroll-thin min-h-[140px] flex-1 overflow-y-auto">
          <EmptyState v-if="!carrito.length" :icon="ShoppingCart" title="Sin productos" text="Tocá un producto o escaneá su código para empezar." />
          <ul v-else class="divide-y divide-tinta-100">
            <li v-for="i in carrito" :key="i.productoId" class="flex items-center gap-2.5 px-4 py-1.5">
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold leading-tight">{{ i.nombre }}</p>
                <p class="text-[11px] text-tinta-500">{{ fmtMoney(i.precioUnitario) }} c/u</p>
              </div>
              <div class="flex items-center rounded-lg border border-tinta-100">
                <button class="p-1 text-tinta-500 hover:text-rojo-600" title="Restar" @click="cambiarCant(i.productoId, -1)"><Minus class="h-4 w-4" /></button>
                <span class="w-6 text-center text-sm font-bold">{{ i.cantidad }}</span>
                <button class="p-1 text-tinta-500 hover:text-turquesa-700" title="Sumar" @click="cambiarCant(i.productoId, 1)"><Plus class="h-4 w-4" /></button>
              </div>
              <p class="w-[5.5rem] text-right text-sm font-semibold">{{ fmtMoney(i.cantidad * i.precioUnitario) }}</p>
              <button class="text-tinta-300 hover:text-rojo-600" title="Quitar" @click="quitar(i.productoId)"><Trash2 class="h-4 w-4" /></button>
            </li>
          </ul>
        </div>

        <div class="space-y-2.5 border-t border-tinta-100 p-3">
          <div class="flex items-center justify-between gap-3 rounded-2xl bg-turquesa-100 px-4 py-2.5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-turquesa-800">Total a cobrar</p>
              <p class="text-[11px] text-tinta-500">Neto {{ fmtMoney(neto) }} · IVA {{ fmtMoney(total - neto) }}</p>
            </div>
            <p class="font-display text-4xl font-bold leading-none">{{ fmtMoney(total) }}</p>
          </div>

          <div>
                        <div class="grid grid-cols-5 gap-1.5">
              <button v-for="m in MEDIOS" :key="m.id" :title="m.id"
                :class="['flex flex-col items-center gap-0.5 rounded-xl border-2 px-1 py-1.5 text-[11px] font-semibold leading-tight transition', medio === m.id ? 'border-turquesa-500 bg-turquesa-50 text-tinta' : 'border-tinta-100 bg-white text-tinta-500 hover:text-tinta']"
                @click="medio = m.id">
                <component :is="m.icon" class="h-4 w-4" />{{ m.id }}
              </button>
            </div>
          </div>

          <div v-if="medio === 'Efectivo' && carrito.length" class="grid grid-cols-2 gap-2">
            <label class="relative">
              <span class="absolute left-3.5 top-1.5 text-[10px] font-semibold uppercase tracking-wider text-tinta-300">Paga con</span>
              <input v-model.number="pagaCon" class="input pb-1.5 pt-5 text-base font-semibold" type="number" min="0" placeholder="$ 0" />
            </label>
            <div :class="['rounded-xl px-3.5 py-1.5', falta > 0 ? 'bg-rojo-50' : vuelto > 0 ? 'bg-amarillo-100' : 'bg-tinta-50']">
              <p class="text-[10px] font-semibold uppercase tracking-wider text-tinta-500">{{ falta > 0 ? 'Falta' : 'Vuelto' }}</p>
              <p :class="['font-display text-xl font-bold', falta > 0 && 'text-rojo-700']">{{ fmtMoney(falta > 0 ? falta : vuelto) }}</p>
            </div>
          </div>

          <button class="btn-turquesa w-full py-3 text-lg" :disabled="!carrito.length || emitiendo || falta > 0" @click="cobrar">
            <template v-if="emitiendo"><span class="h-5 w-5 animate-spin rounded-full border-2 border-tinta border-t-transparent" />Autorizando en ARCA...</template>
            <template v-else><CheckCircle2 class="h-5 w-5" />{{ carrito.length ? `Cobrar ${fmtMoney(total)}` : 'Cobrar' }}</template>
          </button>
        </div>
      </section>
    </div>

    <!-- Movimientos -->
    <Modal :open="verMovs" title="Movimientos de la caja" size="lg" @close="verMovs = false">
      <div class="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div class="rounded-xl bg-turquesa-50 px-4 py-3"><p class="text-xs text-tinta-500">Ventas ({{ ventasCaja.length }})</p><p class="font-display text-xl font-bold">{{ fmtMoney(totalVentas) }}</p></div>
        <div class="rounded-xl bg-tinta-50 px-4 py-3"><p class="text-xs text-tinta-500">Efectivo en caja</p><p class="font-display text-xl font-bold">{{ fmtMoney(efectivoEsperado) }}</p></div>
        <div class="rounded-xl bg-tinta-50 px-4 py-3"><p class="text-xs text-tinta-500">Ingresos</p><p class="font-display text-xl font-bold">{{ fmtMoney(ingresos) }}</p></div>
        <div class="rounded-xl bg-rojo-50 px-4 py-3"><p class="text-xs text-tinta-500">Egresos</p><p class="font-display text-xl font-bold">{{ fmtMoney(egresos) }}</p></div>
      </div>
      <EmptyState v-if="!movimientos.length" :icon="Receipt" title="Sin movimientos" text="Las ventas e ingresos/egresos de esta caja aparecerán acá." />
      <ul v-else class="scroll-thin max-h-96 divide-y divide-tinta-100 overflow-y-auto">
        <li v-for="m in movimientos" :key="m.id" :class="['flex items-center gap-4 px-2 py-3', m.venta && 'cursor-pointer rounded-xl hover:bg-tinta-50']" @click="m.venta && ((verMovs = false), (emitida = m.venta))">
          <span :class="['grid h-9 w-9 place-items-center rounded-xl', m.tipo === 'Venta' ? 'bg-turquesa-50 text-turquesa-700' : m.tipo === 'Ingreso' ? 'bg-tinta-50 text-tinta' : 'bg-rojo-50 text-rojo-500']">
            <Receipt v-if="m.tipo === 'Venta'" class="h-4 w-4" />
            <ArrowDownCircle v-else-if="m.tipo === 'Ingreso'" class="h-4 w-4" />
            <ArrowUpCircle v-else class="h-4 w-4" />
          </span>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium">{{ m.concepto }}</p>
            <p class="text-xs text-tinta-500">{{ fmtTime(m.fecha) }} · {{ m.detalle }}</p>
          </div>
          <p :class="['font-semibold', m.tipo === 'Egreso' && 'text-rojo-500']">{{ m.tipo === 'Egreso' ? '−' : '+' }}{{ fmtMoney(m.monto) }}</p>
        </li>
      </ul>
    </Modal>

    <!-- Ingreso / egreso -->
    <Modal :open="!!mov" :title="`Registrar ${mov?.toLowerCase()}`" size="sm" :accent="mov === 'Egreso' ? 'bg-rojo-500' : 'bg-turquesa-400'" @close="mov = null">
      <div class="space-y-4">
        <Field label="Concepto"><input v-model="movForm.concepto" class="input" :placeholder="mov === 'Egreso' ? 'Ej: Pago a proveedor' : 'Ej: Cambio'" autofocus /></Field>
        <Field label="Monto"><input v-model.number="movForm.monto" class="input" type="number" min="0" /></Field>
      </div>
      <template #footer>
        <button class="btn-ghost" @click="mov = null">Cancelar</button>
        <button :class="mov === 'Egreso' ? 'btn-rojo' : 'btn-turquesa'" @click="registrarMov">Registrar</button>
      </template>
    </Modal>

    <!-- Cierre -->
    <Modal :open="cierre" title="Cierre de caja" accent="bg-rojo-500" @close="cierre = false">
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div v-for="m in MEDIOS" :key="m.id" class="flex items-center justify-between rounded-xl bg-tinta-50 px-4 py-3">
            <span class="flex items-center gap-2 text-tinta-500"><component :is="m.icon" class="h-4 w-4" />{{ m.id }}</span>
            <b>{{ fmtMoney(porMedio(m.id)) }}</b>
          </div>
          <div class="flex items-center justify-between rounded-xl bg-turquesa-400 px-4 py-3"><span class="font-semibold">Total ventas</span><b>{{ fmtMoney(totalVentas) }}</b></div>
        </div>
        <div class="rounded-xl border border-tinta-100 p-4 text-sm">
          <div class="flex justify-between"><span class="text-tinta-500">Monto inicial</span><span>{{ fmtMoney(caja.montoInicial) }}</span></div>
          <div class="flex justify-between"><span class="text-tinta-500">+ Ventas en efectivo</span><span>{{ fmtMoney(efectivoVentas) }}</span></div>
          <div class="flex justify-between"><span class="text-tinta-500">+ Ingresos</span><span>{{ fmtMoney(ingresos) }}</span></div>
          <div class="flex justify-between"><span class="text-tinta-500">− Egresos</span><span>{{ fmtMoney(egresos) }}</span></div>
          <div class="mt-2 flex justify-between border-t border-tinta-100 pt-2 font-semibold"><span>Efectivo esperado</span><span>{{ fmtMoney(efectivoEsperado) }}</span></div>
        </div>
        <Field label="Efectivo contado"><input v-model.number="contado" class="input text-lg font-semibold" type="number" /></Field>
        <div :class="['rounded-xl px-4 py-3 text-sm font-semibold', Math.abs(diferencia) < 0.01 ? 'bg-turquesa-50 text-turquesa-700' : diferencia > 0 ? 'bg-amarillo-100 text-amarillo-700' : 'bg-rojo-50 text-rojo-600']">
          {{ Math.abs(diferencia) < 0.01 ? 'La caja cuadra perfectamente' : diferencia > 0 ? `Sobrante: ${fmtMoney(diferencia)}` : `Faltante: ${fmtMoney(-diferencia)}` }}
        </div>
      </div>
      <template #footer>
        <button class="btn-ghost" @click="cierre = false">Cancelar</button>
        <button class="btn-rojo" @click="confirmarCierre"><Lock class="h-4 w-4" />Confirmar cierre</button>
      </template>
    </Modal>
  </template>

  <!-- Comprobante emitido -->
  <Modal :open="!!emitida" title="Comprobante emitido" size="lg" @close="cerrarComprobante">
    <template v-if="emitida">
      <div class="mb-4 flex items-center gap-3 rounded-xl bg-turquesa-50 px-4 py-3 text-sm text-turquesa-800">
        <CheckCircle2 class="h-5 w-5" /> Comprobante autorizado por ARCA · CAE <b class="font-mono">{{ emitida.cae }}</b>
      </div>
      <Comprobante :venta="emitida" />
    </template>
    <template #footer>
      <button class="btn-ghost" @click="print"><Printer class="h-4 w-4" />Imprimir</button>
      <button class="btn-primary" @click="cerrarComprobante">Nueva venta</button>
    </template>
  </Modal>
</template>
