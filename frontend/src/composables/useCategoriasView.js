import { computed, onMounted, ref } from 'vue'
import { apiFetch } from '../services/api'

function formularioVacio() {
  return { nombre: '', descripcion: '', activo: true }
}

function tokenPayload() {
  try {
    const token = localStorage.getItem('access')
    if (!token) return {}
    return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
  } catch {
    return {}
  }
}

export function useCategoriasView() {
  const categorias = ref([])
  const busqueda = ref('')
  const estadoFiltro = ref('')
  const cargando = ref(false)
  const error = ref('')
  const modal = ref(false)
  const categoriaSeleccionada = ref(null)
  const formulario = ref(formularioVacio())

  const esDueno = computed(() => {
    const payload = tokenPayload()
    const rol = String(localStorage.getItem('rol') || localStorage.getItem('role') || payload.rol || payload.role || '').toLowerCase()
    const grupos = payload.groups || payload.grupos || []
    return ['dueño', 'dueno', 'owner'].includes(rol) ||
      grupos.some((grupo) => ['dueño', 'dueno', 'owner'].includes(String(grupo).toLowerCase()))
  })

  const categoriasVisibles = computed(() => {
    const texto = busqueda.value.trim().toLowerCase()
    return categorias.value.filter((categoria) => {
      const coincideTexto = !texto || [categoria.nombre, categoria.descripcion]
        .some((valor) => String(valor || '').toLowerCase().includes(texto))
      const coincideEstado = !estadoFiltro.value || String(categoria.activo) === estadoFiltro.value
      return coincideTexto && coincideEstado
    })
  })

  async function cargarCategorias() {
    cargando.value = true
    error.value = ''
    try {
      const data = await apiFetch('/api/categorias/')
      categorias.value = data.results || data
    } catch (err) {
      error.value = err.message
    } finally {
      cargando.value = false
    }
  }

  function abrirCrear() {
    if (!esDueno.value) return
    categoriaSeleccionada.value = null
    formulario.value = formularioVacio()
    modal.value = true
  }

  function abrirEditar(categoria) {
    if (!esDueno.value) return
    categoriaSeleccionada.value = categoria
    formulario.value = {
      nombre: categoria.nombre,
      descripcion: categoria.descripcion || '',
      activo: categoria.activo
    }
    modal.value = true
  }

  async function guardarCategoria() {
    if (!esDueno.value) return
    try {
      const esNueva = !categoriaSeleccionada.value
      const categoria = await apiFetch(
        esNueva ? '/api/categorias/' : `/api/categorias/${categoriaSeleccionada.value.id}/`,
        {
          method: esNueva ? 'POST' : 'PATCH',
          body: JSON.stringify(formulario.value)
        }
      )
      if (esNueva) categorias.value.push(categoria)
      else Object.assign(categoriaSeleccionada.value, categoria)
      modal.value = false
    } catch (err) {
      error.value = err.message
    }
  }

  async function cambiarEstado(categoria) {
    if (!esDueno.value) return
    try {
      Object.assign(categoria, await apiFetch(`/api/categorias/${categoria.id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ activo: !categoria.activo })
      }))
    } catch (err) {
      error.value = err.message
    }
  }

  onMounted(cargarCategorias)

  return {
    categorias,
    busqueda,
    estadoFiltro,
    cargando,
    error,
    modal,
    categoriaSeleccionada,
    formulario,
    esDueno,
    categoriasVisibles,
    abrirCrear,
    abrirEditar,
    guardarCategoria,
    cambiarEstado
  }
}
