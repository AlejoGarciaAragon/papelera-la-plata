<script setup>
import { computed, onMounted, ref } from 'vue'

const productos = ref([])
const categorias = ref([])
const busqueda = ref('')
const categoriaFiltro = ref('')
const estadoFiltro = ref('')
const cargando = ref(false)
const error = ref('')
const modal = ref(null)
const productoSeleccionado = ref(null)
const formulario = ref(formularioVacio())

function formularioVacio() {
  return {
    nombre: '',
    descripcion: '',
    categoria: '',
    precio_actual: 0,
    porcentaje_ganancia: 0,
    stock_inicial: 0,
    stock_fisico: 0,
    codigo_barra: '',
    activo: true
  }
}

function tokenPayload() {
  try {
    const token = localStorage.getItem('access')
    return token ? JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))) : {}
  } catch {
    return {}
  }
}

const esDueno = computed(() => {
  const payload = tokenPayload()
  const rol = String(localStorage.getItem('rol') || localStorage.getItem('role') || payload.rol || payload.role || '').toLowerCase()
  const grupos = payload.groups || payload.grupos || []
  return ['dueño', 'dueno', 'owner'].includes(rol) || grupos.some((grupo) => ['dueño', 'dueno', 'owner'].includes(String(grupo).toLowerCase()))
})

const productosVisibles = computed(() => {
  const texto = busqueda.value.trim().toLowerCase()
  return productos.value.filter((producto) => {
    const coincideTexto = !texto || [producto.nombre, producto.codigo_barra, producto.descripcion].some((valor) => String(valor || '').toLowerCase().includes(texto))
    const coincideCategoria = !categoriaFiltro.value || String(producto.categoria || '') === categoriaFiltro.value
    const coincideEstado = !estadoFiltro.value || String(producto.activo) === estadoFiltro.value
    return coincideTexto && coincideCategoria && coincideEstado
  })
})

async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access')}`,
      ...(options.headers || {})
    }
  })
  const data = response.status === 204 ? null : await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(data.error || data.detail || 'No se pudo completar la operación.')
  return data
}

async function cargarDatos() {
  cargando.value = true
  error.value = ''
  try {
    const [productosData, categoriasData] = await Promise.all([
      apiFetch('/api/productos/'),
      apiFetch('/api/categorias/?activo=true')
    ])
    productos.value = productosData.results || productosData
    categorias.value = (categoriasData.results || categoriasData).filter((categoria) => categoria.activo)
  } catch (err) {
    error.value = err.message
  } finally {
    cargando.value = false
  }
}

function abrirCrear() {
  if (!esDueno.value) return alert('Solo el rol Dueño puede gestionar productos.')
  productoSeleccionado.value = null
  formulario.value = formularioVacio()
  modal.value = 'formulario'
}

function abrirEditar(producto) {
  if (!esDueno.value) return alert('Solo el rol Dueño puede gestionar productos.')
  productoSeleccionado.value = producto
  formulario.value = {
    nombre: producto.nombre,
    descripcion: producto.descripcion || '',
    categoria: producto.categoria || '',
    precio_actual: producto.precio_actual,
    porcentaje_ganancia: producto.porcentaje_ganancia,
    stock_fisico: producto.inventario?.stock_fisico ?? 0,
    codigo_barra: producto.codigo_barra,
    activo: producto.activo
  }
  modal.value = 'formulario'
}

async function guardarProducto() {
  try {
    const esNuevo = !productoSeleccionado.value
    const payload = { ...formulario.value, categoria: formulario.value.categoria || null }
    if (esNuevo) delete payload.stock_fisico
    await apiFetch(esNuevo ? '/api/productos/' : `/api/productos/${productoSeleccionado.value.id}/`, {
      method: esNuevo ? 'POST' : 'PATCH',
      body: JSON.stringify(payload)
    })
    await cargarDatos()
    modal.value = null
  } catch (err) {
    error.value = err.message
  }
}

async function cambiarEstado(producto) {
  if (!esDueno.value) return alert('Solo el rol Dueño puede gestionar productos.')
  try {
    Object.assign(producto, await apiFetch(`/api/productos/${producto.id}/`, {
      method: 'PATCH',
      body: JSON.stringify({ activo: !producto.activo })
    }))
  } catch (err) {
    error.value = err.message
  }
}

function precio(valor) {
  return Number(valor || 0).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })
}

function precioVenta(producto) {
  return precio(Number(producto.precio_actual || 0) * (1 + Number(producto.porcentaje_ganancia || 0) / 100))
}

onMounted(cargarDatos)
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">Productos</h2>
        <p class="mt-1 text-sm text-slate-500">Administrá el catálogo y su disponibilidad.</p>
      </div>
      <button class="rounded-lg bg-teal-400 px-4 py-2 font-medium text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!esDueno" @click="abrirCrear">+ Nuevo Producto</button>
    </div>

    <div v-if="error" class="flex items-center justify-between rounded-xl border border-rose-100 bg-rose-50 p-4 text-sm text-rose-700">
      <span>{{ error }}</span><button class="font-bold" @click="error = ''">×</button>
    </div>

    <section class="rounded-xl bg-white p-4 shadow-sm">
      <div class="grid gap-3 md:grid-cols-[1fr_220px_180px]">
        <input v-model="busqueda" class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-300 focus:ring-2 focus:ring-teal-100" placeholder="Buscar por nombre, código o descripción..." />
        <select v-model="categoriaFiltro" class="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 outline-none focus:border-teal-300"><option value="">Todas las categorías</option><option v-for="categoria in categorias" :key="categoria.id" :value="String(categoria.id)">{{ categoria.nombre }}</option></select>
        <select v-model="estadoFiltro" class="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 outline-none focus:border-teal-300"><option value="">Todos los estados</option><option value="true">Activos</option><option value="false">Ocultos/Inactivos</option></select>
      </div>
    </section>

    <section class="overflow-hidden rounded-xl bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1000px] text-left text-sm">
          <thead class="border-b border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr><th class="px-5 py-4">Código</th><th class="px-5 py-4">Nombre</th><th class="px-5 py-4">Categoría</th><th class="px-5 py-4">Costo</th><th class="px-5 py-4">Ganancia</th><th class="px-5 py-4">Precio de venta</th><th class="px-5 py-4">Stock</th><th class="px-5 py-4">Estado</th><th class="px-5 py-4">Acciones</th></tr></thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="producto in productosVisibles" :key="producto.id" class="text-slate-600"><td class="px-5 py-4 font-mono text-xs">{{ producto.codigo_barra }}</td><td class="px-5 py-4 font-medium text-slate-800">{{ producto.nombre }}<div class="max-w-xs truncate text-xs font-normal text-slate-400">{{ producto.descripcion }}</div></td><td class="px-5 py-4">{{ producto.categoria_nombre || 'Sin categoría' }}</td><td class="px-5 py-4">{{ precio(producto.precio_actual) }}</td><td class="px-5 py-4">{{ producto.porcentaje_ganancia }}%</td><td class="px-5 py-4">{{ precioVenta(producto) }}</td><td class="px-5 py-4">{{ producto.inventario?.stock_fisico ?? 0 }}</td><td class="px-5 py-4"><span :class="producto.activo ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'" class="rounded-full px-2.5 py-1 text-xs font-medium">{{ producto.activo ? 'Activo' : 'Oculto' }}</span></td><td class="px-5 py-4"><div class="flex gap-2"><button class="text-teal-700 hover:text-teal-900 disabled:opacity-40" :disabled="!esDueno" @click="abrirEditar(producto)">Editar</button><button :class="producto.activo ? 'text-rose-600 hover:text-rose-800' : 'text-teal-700 hover:text-teal-900'" class="disabled:opacity-40" :disabled="!esDueno" @click="cambiarEstado(producto)">{{ producto.activo ? 'Ocultar' : 'Activar' }}</button></div></td></tr>
            <tr v-if="!cargando && !productosVisibles.length"><td colspan="9" class="px-5 py-12 text-center text-slate-400">No hay productos que coincidan con los filtros.</td></tr>
            <tr v-if="cargando"><td colspan="9" class="px-5 py-12 text-center text-slate-400">Cargando productos...</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="modal === 'formulario'" class="fixed inset-0 z-10 flex items-center justify-center bg-slate-900/30 p-4">
      <form class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white p-6 shadow-xl" @submit.prevent="guardarProducto">
        <div class="mb-5 flex items-center justify-between"><h3 class="text-xl font-bold text-slate-800">{{ productoSeleccionado ? 'Editar producto' : 'Nuevo producto' }}</h3><button type="button" class="text-2xl text-slate-400" @click="modal = null">×</button></div>
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="sm:col-span-2">Nombre<input v-model="formulario.nombre" required class="campo" /></label>
          <label class="sm:col-span-2">Descripción<textarea v-model="formulario.descripcion" class="campo" rows="2"></textarea></label>
          <label>Código de barras<input v-model="formulario.codigo_barra" required class="campo" /></label>
          <label>Categoría<select v-model="formulario.categoria" class="campo"><option value="">Sin categoría</option><option v-for="categoria in categorias" :key="categoria.id" :value="categoria.id">{{ categoria.nombre }}</option></select></label>
          <label>Precio de costo<input v-model.number="formulario.precio_actual" type="number" min="0" step="0.01" class="campo" /></label>
          <label>Porcentaje de ganancia<input v-model.number="formulario.porcentaje_ganancia" type="number" min="0" step="0.01" class="campo" /></label>
          <label>{{ productoSeleccionado ? 'Stock' : 'Stock inicial' }}<input v-model.number="formulario[productoSeleccionado ? 'stock_fisico' : 'stock_inicial']" type="number" min="0" class="campo" /></label>
          <label class="flex items-center gap-2 pt-7"><input v-model="formulario.activo" type="checkbox" class="h-4 w-4 accent-teal-500" /> Producto activo</label>
        </div>
        <div class="mt-6 flex justify-end gap-3"><button type="button" class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100" @click="modal = null">Cancelar</button><button type="submit" class="rounded-lg bg-teal-400 px-4 py-2 font-medium text-white hover:bg-teal-500">Guardar producto</button></div>
      </form>
    </div>

  </div>
</template>

<style scoped>
.campo { display: block; width: 100%; margin-top: 0.35rem; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.6rem 0.75rem; color: #475569; outline: none; }
.campo:focus { border-color: #5eead4; box-shadow: 0 0 0 3px #ccfbf1; }
label { color: #475569; font-size: 0.875rem; }
</style>
