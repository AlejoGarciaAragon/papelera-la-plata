import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import type { Caja, Categoria, Cliente, ItemVenta, MedioPago, MovimientoCaja, Producto, TipoComprobante, Venta } from '../types'
import { buildSeedVentas, seedCategorias, seedClientes, seedProductos } from '../lib/seed'
import { genCAE, uid } from '../lib/format'

/**
 * Estado de la app persistido en localStorage.
 * Para conectar al backend real, reemplazar estas acciones por llamadas
 * a la API (fetch/axios) manteniendo las mismas firmas.
 */
interface DataState {
  categorias: Categoria[]
  productos: Producto[]
  clientes: Cliente[]
  ventas: Venta[]
  cajas: Caja[]
}

const KEY = 'papelera-la-plata:data:v6'

function demo(): DataState {
  const { ventas, cajas } = buildSeedVentas()
  return {
    categorias: structuredClone(seedCategorias),
    productos: structuredClone(seedProductos),
    clientes: structuredClone(seedClientes),
    ventas,
    cajas,
  }
}

function initial(): DataState {
  const raw = localStorage.getItem(KEY)
  if (raw) {
    try {
      return JSON.parse(raw)
    } catch {
      /* datos corruptos: se regenera la demo */
    }
  }
  return demo()
}

const upsert = <T extends { id: string }>(list: T[], item: T) => {
  const i = list.findIndex((x) => x.id === item.id)
  if (i >= 0) list.splice(i, 1, item)
  else list.push(item)
}

export const useDataStore = defineStore('data', () => {
  const init = initial()
  const categorias = ref<Categoria[]>(init.categorias)
  const productos = ref<Producto[]>(init.productos)
  const clientes = ref<Cliente[]>(init.clientes)
  const ventas = ref<Venta[]>(init.ventas)
  const cajas = ref<Caja[]>(init.cajas)

  watch(
    [categorias, productos, clientes, ventas, cajas],
    () => localStorage.setItem(KEY, JSON.stringify({
      categorias: categorias.value, productos: productos.value, clientes: clientes.value, ventas: ventas.value, cajas: cajas.value,
    })),
    { deep: true },
  )

  const cajaAbierta = computed(() => cajas.value.find((c) => !c.cerradaEn))

  const guardarCategoria = (c: Categoria) => upsert(categorias.value, { ...c, id: c.id || uid() })
  const eliminarCategoria = (id: string) => (categorias.value = categorias.value.filter((c) => c.id !== id))
  const guardarProducto = (p: Producto) => upsert(productos.value, { ...p, id: p.id || uid() })
  const eliminarProducto = (id: string) => (productos.value = productos.value.filter((p) => p.id !== id))
  const guardarCliente = (c: Cliente) => upsert(clientes.value, { ...c, id: c.id || uid() })
  const eliminarCliente = (id: string) => (clientes.value = clientes.value.filter((c) => c.id !== id))

  /** Oculta o vuelve a mostrar un registro sin eliminarlo. Devuelve el nuevo estado. */
  const alternarOculto = (tipo: 'categoria' | 'producto' | 'cliente', id: string) => {
    const list: { id: string; oculto?: boolean }[] = tipo === 'categoria' ? categorias.value : tipo === 'producto' ? productos.value : clientes.value
    const item = list.find((x) => x.id === id)
    if (item) item.oculto = !item.oculto
    return !!item?.oculto
  }

  const abrirCaja = (montoInicial: number, usuario: string) =>
    cajas.value.push({ id: uid(), abiertaEn: new Date().toISOString(), montoInicial, usuario, movimientos: [] })

  const cerrarCaja = (montoCierre: number) => {
    const c = cajaAbierta.value
    if (c) Object.assign(c, { cerradaEn: new Date().toISOString(), montoCierre })
  }

  const agregarMovimiento = (m: Omit<MovimientoCaja, 'id' | 'fecha'>) =>
    cajaAbierta.value?.movimientos.push({ ...m, id: uid(), fecha: new Date().toISOString() })

  const registrarVenta = (v: { cliente: Cliente; tipo: TipoComprobante; medioPago: MedioPago; items: ItemVenta[] }): Venta => {
    const total = v.items.reduce((acc, it) => acc + it.cantidad * it.precioUnitario, 0)
    const subtotal = +v.items.reduce((acc, it) => acc + (it.cantidad * it.precioUnitario) / (1 + it.iva / 100), 0).toFixed(2)
    const ultimo = ventas.value.reduce((m, x) => Math.max(m, parseInt(x.numero.split('-')[1], 10)), 0)
    const ahora = new Date()
    const vto = new Date(ahora)
    vto.setDate(vto.getDate() + 10)
    const venta: Venta = {
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
    }
    ventas.value.push(venta)
    v.items.forEach((it) => {
      const p = productos.value.find((x) => x.id === it.productoId)
      if (p) p.stock = Math.max(0, p.stock - it.cantidad)
    })
    return venta
  }

  const reiniciarDemo = () => {
    const d = demo()
    categorias.value = d.categorias
    productos.value = d.productos
    clientes.value = d.clientes
    ventas.value = d.ventas
    cajas.value = d.cajas
  }

  return {
    categorias, productos, clientes, ventas, cajas, cajaAbierta,
    guardarCategoria, eliminarCategoria, guardarProducto, eliminarProducto, guardarCliente, eliminarCliente, alternarOculto,
    abrirCaja, cerrarCaja, agregarMovimiento, registrarVenta, reiniciarDemo,
  }
})
