import { computed, onMounted, ref } from 'vue'
import { apiFetch } from '../services/api'

const tiposDocumento = [
  { value: 'dni', label: 'DNI' },
  { value: 'cuit', label: 'CUIT' },
  { value: 'cuil', label: 'CUIL' },
  { value: 'pasaporte', label: 'Pasaporte' },
  { value: 'otro', label: 'Otro' }
]

const condicionesIva = [
  { value: 'consumidor_final', label: 'Consumidor Final' },
  { value: 'responsable_inscripto', label: 'Responsable Inscripto' },
  { value: 'monotributo', label: 'Monotributo' },
  { value: 'exento', label: 'Exento' }
]

function formularioVacio() {
  return {
    nombre_o_razon_social: '',
    tipo_documento: 'dni',
    numero_documento: '',
    condicion_iva: 'consumidor_final',
    direccion: '',
    telefono: '',
    email: '',
    activo: true
  }
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

function rolesUsuario() {
  const payload = tokenPayload()
  const roles = [
    localStorage.getItem('rol'),
    localStorage.getItem('role'),
    payload.rol,
    payload.role,
    ...(payload.groups || payload.grupos || [])
  ]
  return roles.filter(Boolean).map((rol) => String(rol).toLowerCase())
}

export function useClientesView() {
  const clientes = ref([])
  const busqueda = ref('')
  const condicionFiltro = ref('')
  const estadoFiltro = ref('')
  const cargando = ref(false)
  const guardando = ref(false)
  const error = ref('')
  const modal = ref(false)
  const clienteSeleccionado = ref(null)
  const clienteAEliminar = ref(null)
  const formulario = ref(formularioVacio())

  const esDueno = computed(() => rolesUsuario()
    .some((rol) => ['dueño', 'dueno', 'owner'].includes(rol)))
  const puedeEditar = computed(() => esDueno.value || rolesUsuario().includes('empleado'))
  const advertenciaDocumento = computed(() =>
    formulario.value.condicion_iva === 'responsable_inscripto' &&
    formulario.value.tipo_documento !== 'cuit'
  )

  const clientesVisibles = computed(() => {
    const texto = busqueda.value.trim().toLowerCase()
    return clientes.value.filter((cliente) => {
      const coincideTexto = !texto || [
        cliente.nombre_o_razon_social,
        cliente.numero_documento
      ].some((valor) => String(valor || '').toLowerCase().includes(texto))
      const coincideCondicion = !condicionFiltro.value ||
        cliente.condicion_iva === condicionFiltro.value
      const coincideEstado = !estadoFiltro.value ||
        String(cliente.activo) === estadoFiltro.value
      return coincideTexto && coincideCondicion && coincideEstado
    })
  })

  function etiquetaTipoDocumento(tipo) {
    return tiposDocumento.find((item) => item.value === tipo)?.label || tipo
  }

  function etiquetaCondicion(condicion) {
    return condicionesIva.find((item) => item.value === condicion)?.label || condicion
  }

  async function cargarClientes() {
    cargando.value = true
    error.value = ''
    try {
      const data = await apiFetch('/api/clientes/')
      clientes.value = data.results || data
    } catch (err) {
      error.value = err.message
    } finally {
      cargando.value = false
    }
  }

  function abrirCrear() {
    if (!puedeEditar.value) return
    clienteSeleccionado.value = null
    formulario.value = formularioVacio()
    modal.value = true
  }

  function abrirEditar(cliente) {
    if (!puedeEditar.value) return
    clienteSeleccionado.value = cliente
    formulario.value = {
      nombre_o_razon_social: cliente.nombre_o_razon_social,
      tipo_documento: cliente.tipo_documento,
      numero_documento: cliente.numero_documento,
      condicion_iva: cliente.condicion_iva,
      direccion: cliente.direccion || '',
      telefono: cliente.telefono || '',
      email: cliente.email || '',
      activo: cliente.activo
    }
    modal.value = true
  }

  async function guardarCliente() {
    if (!puedeEditar.value || guardando.value) return
    guardando.value = true
    error.value = ''
    try {
      const esNuevo = !clienteSeleccionado.value
      const payload = { ...formulario.value }
      if (!esNuevo) delete payload.activo
      const cliente = await apiFetch(
        esNuevo ? '/api/clientes/' : `/api/clientes/${clienteSeleccionado.value.id}/`,
        { method: esNuevo ? 'POST' : 'PATCH', body: JSON.stringify(payload) }
      )
      if (esNuevo) clientes.value.push(cliente)
      else Object.assign(clienteSeleccionado.value, cliente)
      modal.value = false
    } catch (err) {
      error.value = err.message
    } finally {
      guardando.value = false
    }
  }

  async function cambiarEstado(cliente) {
    if (!esDueno.value) return
    error.value = ''
    try {
      Object.assign(cliente, await apiFetch(`/api/clientes/${cliente.id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ activo: !cliente.activo })
      }))
    } catch (err) {
      error.value = err.message
    }
  }

  function eliminarCliente(cliente) {
    if (!esDueno.value) return
    clienteAEliminar.value = cliente
  }

  async function confirmarEliminacionCliente() {
    if (!clienteAEliminar.value) return
    error.value = ''
    try {
      const id = clienteAEliminar.value.id
      await apiFetch(`/api/clientes/${id}/`, { method: 'DELETE' })
      clientes.value = clientes.value.filter((cliente) => cliente.id !== id)
      clienteAEliminar.value = null
    } catch (err) {
      error.value = err.message
    }
  }

  onMounted(cargarClientes)

  return {
    clientes,
    busqueda,
    condicionFiltro,
    estadoFiltro,
    cargando,
    guardando,
    error,
    modal,
    clienteSeleccionado,
    clienteAEliminar,
    formulario,
    tiposDocumento,
    condicionesIva,
    esDueno,
    puedeEditar,
    advertenciaDocumento,
    clientesVisibles,
    etiquetaTipoDocumento,
    etiquetaCondicion,
    abrirCrear,
    abrirEditar,
    guardarCliente,
    cambiarEstado,
    eliminarCliente,
    confirmarEliminacionCliente
  }
}
