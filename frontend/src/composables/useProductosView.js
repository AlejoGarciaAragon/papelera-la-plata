import { computed, onMounted, ref } from 'vue'
import { apiFetch } from '../services/api'

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

export function useProductosView() {
  const productos = ref([])
  const categorias = ref([])
  const busqueda = ref('')
  const categoriaFiltro = ref('')
  const estadoFiltro = ref('')
  const cargando = ref(false)
  const error = ref('')
  const modal = ref(null)
  const productoSeleccionado = ref(null)
  const productoAEliminar = ref(null)
  const formulario = ref(formularioVacio())

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
      if (!formulario.value.categoria || Number(formulario.value.precio_actual) <= 0 || Number(formulario.value.porcentaje_ganancia) <= 0) {
        error.value = 'Seleccioná una categoría e ingresá un precio de costo y porcentaje de ganancia mayores que cero.'
        return
      }
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

  async function eliminarProducto(producto) {
    if (!esDueno.value) return
    productoAEliminar.value = producto
  }

  async function confirmarEliminacionProducto() {
    if (!productoAEliminar.value) return
    try {
      await apiFetch(`/api/productos/${productoAEliminar.value.id}/`, { method: 'DELETE' })
      productos.value = productos.value.filter((item) => item.id !== productoAEliminar.value.id)
      productoAEliminar.value = null
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

  return {
    productos,
    categorias,
    busqueda,
    categoriaFiltro,
    estadoFiltro,
    cargando,
    error,
    modal,
    productoSeleccionado,
    productoAEliminar,
    formulario,
    esDueno,
    productosVisibles,
    abrirCrear,
    abrirEditar,
    guardarProducto,
    cambiarEstado,
    eliminarProducto,
    confirmarEliminacionProducto,
    precio,
    precioVenta
  }
}
