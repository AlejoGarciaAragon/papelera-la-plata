import { computed, onMounted, ref } from 'vue'
import { apiFetch } from '../services/api'

function hoy() {
  return new Date().toISOString().slice(0, 10)
}

function tokenPayload() {
  try {
    const token = localStorage.getItem('access')
    return token ? JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))) : {}
  } catch {
    return {}
  }
}

export function useDashboardVentasView() {
  const ventas = ref([])
  const resumen = ref({
    cantidad_ventas: 0,
    recaudacion_total: 0,
    recaudacion_por_metodo: { efectivo: 0, tarjeta: 0, transferencia: 0 }
  })
  const fecha = ref(hoy())
  const metodoPago = ref('')
  const estado = ref('')
  const cargando = ref(false)
  const error = ref('')
  const ventaSeleccionada = ref(null)
  const ventaAAnular = ref(null)
  const anulando = ref(false)

  const esDueno = computed(() => {
    const payload = tokenPayload()
    const rol = String(localStorage.getItem('role') || payload.role || '').toLowerCase()
    return ['dueño', 'dueno', 'owner'].includes(rol)
  })

  const totalTarjetaTransferencia = computed(() =>
    Number(resumen.value.recaudacion_por_metodo.tarjeta || 0) +
    Number(resumen.value.recaudacion_por_metodo.transferencia || 0)
  )

  const ventasFiltradas = computed(() => ventas.value)

  function precio(valor) {
    return Number(valor || 0).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })
  }

  function fechaHora(valor) {
    return new Date(valor).toLocaleString('es-AR', {
      dateStyle: 'short',
      timeStyle: 'short'
    })
  }

  function etiquetaMetodo(metodo) {
    return { efectivo: 'Efectivo', tarjeta: 'Tarjeta', transferencia: 'Transferencia' }[metodo] || metodo
  }

  function etiquetaEstado(valor) {
    return { completada: 'Completada', cancelada: 'Cancelada', pendiente: 'Pendiente' }[valor] || valor
  }

  async function cargarDatos() {
    cargando.value = true
    error.value = ''
    try {
      const params = new URLSearchParams()
      if (fecha.value) params.set('fecha', fecha.value)
      if (metodoPago.value) params.set('metodo_pago', metodoPago.value)
      if (estado.value) params.set('estado', estado.value)
      const [ventasData, resumenData] = await Promise.all([
        apiFetch(`/api/ventas/?${params}`),
        apiFetch(`/api/ventas/resumen_diario/?fecha=${fecha.value}`)
      ])
      ventas.value = ventasData.results || ventasData
      resumen.value = resumenData
    } catch (err) {
      error.value = err.message
    } finally {
      cargando.value = false
    }
  }

  function abrirDetalle(venta) {
    ventaSeleccionada.value = venta
  }

  function abrirAnulacion(venta) {
    if (esDueno.value && venta.estado === 'completada') ventaAAnular.value = venta
  }

  async function confirmarAnulacion() {
    if (!ventaAAnular.value) return
    anulando.value = true
    error.value = ''
    try {
      const actualizada = await apiFetch(`/api/ventas/${ventaAAnular.value.id}/anular/`, { method: 'POST' })
      Object.assign(ventaAAnular.value, actualizada)
      ventaAAnular.value = null
      await cargarDatos()
    } catch (err) {
      error.value = err.message
    } finally {
      anulando.value = false
    }
  }

  onMounted(cargarDatos)

  return {
    ventasFiltradas,
    resumen,
    fecha,
    metodoPago,
    estado,
    cargando,
    error,
    ventaSeleccionada,
    ventaAAnular,
    anulando,
    esDueno,
    totalTarjetaTransferencia,
    precio,
    fechaHora,
    etiquetaMetodo,
    etiquetaEstado,
    cargarDatos,
    abrirDetalle,
    abrirAnulacion,
    confirmarAnulacion
  }
}
