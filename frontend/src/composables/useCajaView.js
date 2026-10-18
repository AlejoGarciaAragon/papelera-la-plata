import { computed, onMounted, ref } from 'vue'
import { apiFetch } from '../services/api'

export function useCajaView() {
  const productos = ref([])
  const clientes = ref([])
  const carrito = ref([])
  const busqueda = ref('')
  const clienteId = ref(null)
  const busquedaCliente = ref('')
  const mostrarClientes = ref(false)
  const metodoPago = ref('efectivo')
  const cargando = ref(false)
  const procesandoVenta = ref(false)
  const error = ref('')
  const exito = ref('')

  const productosFiltrados = computed(() => {
    const texto = busqueda.value.trim().toLowerCase()
    return productos.value.filter((producto) => {
      if (!texto) return true
      return [producto.nombre, producto.codigo_barra]
        .some((valor) => String(valor || '').toLowerCase().includes(texto))
    })
  })

  const clientesFiltrados = computed(() => {
    const texto = busquedaCliente.value.trim().toLowerCase()
    if (!texto) return clientes.value.slice(0, 8)
    return clientes.value.filter((cliente) => [
      cliente.nombre_o_razon_social,
      cliente.numero_documento
    ].some((valor) => String(valor || '').toLowerCase().includes(texto))).slice(0, 8)
  })

  const clienteSeleccionado = computed(() =>
    clientes.value.find((cliente) => cliente.id === clienteId.value) || null
  )

  const total = computed(() => carrito.value.reduce(
    (acumulado, item) => acumulado + Number(item.precio_venta) * item.cantidad,
    0
  ))

  function stockDisponible(producto) {
    return Math.max(0, Number(producto.inventario?.stock_fisico || 0) - Number(producto.inventario?.stock_reservado || 0))
  }

  function precio(valor) {
    return Number(valor || 0).toLocaleString('es-AR', { style: 'currency', currency: 'ARS' })
  }

  function agregarProducto(producto) {
    const stock = stockDisponible(producto)
    const existente = carrito.value.find((item) => item.id === producto.id)
    if (!stock) {
      error.value = `El producto "${producto.nombre}" no tiene stock disponible.`
      return
    }
    if (existente) {
      if (existente.cantidad >= stock) {
        error.value = `No hay más stock disponible para "${producto.nombre}".`
        return
      }
      existente.cantidad += 1
      return
    }
    carrito.value.push({
      id: producto.id,
      nombre: producto.nombre,
      codigo_barra: producto.codigo_barra,
      precio_venta: Number(producto.precio_venta),
      cantidad: 1,
      stock
    })
    busqueda.value = ''
  }

  function buscarYAgregar() {
    const texto = busqueda.value.trim().toLowerCase()
    if (!texto) return
    const exacto = productos.value.find((producto) => String(producto.codigo_barra).toLowerCase() === texto)
    if (exacto) {
      agregarProducto(exacto)
      return
    }
    if (productosFiltrados.value.length === 1) agregarProducto(productosFiltrados.value[0])
  }

  function cambiarCantidad(item, incremento) {
    const nuevaCantidad = item.cantidad + incremento
    if (nuevaCantidad < 1) {
      eliminarItem(item)
      return
    }
    if (nuevaCantidad > item.stock) {
      error.value = `No hay más stock disponible para "${item.nombre}".`
      return
    }
    item.cantidad = nuevaCantidad
  }

  function eliminarItem(item) {
    carrito.value = carrito.value.filter((actual) => actual.id !== item.id)
  }

  async function cargarProductos() {
    cargando.value = true
    error.value = ''
    try {
      const data = await apiFetch('/api/productos/?activo=true')
      productos.value = (data.results || data).filter((producto) => producto.activo)
    } catch (err) {
      error.value = err.message
    } finally {
      cargando.value = false
    }
  }

  async function cargarClientes() {
    try {
      const data = await apiFetch('/api/clientes/?activo=true')
      clientes.value = (data.results || data).filter((cliente) => cliente.activo)
    } catch (err) {
      error.value = err.message
    }
  }

  function seleccionarCliente(cliente) {
    clienteId.value = cliente.id
    busquedaCliente.value = ''
    mostrarClientes.value = false
  }

  function seleccionarConsumidorFinal() {
    clienteId.value = null
    busquedaCliente.value = ''
    mostrarClientes.value = false
  }

  function alternarClientes() {
    mostrarClientes.value = !mostrarClientes.value
    if (mostrarClientes.value) busquedaCliente.value = ''
  }

  async function confirmarVenta() {
    if (!carrito.value.length) {
      error.value = 'Agregá al menos un producto al carrito.'
      return
    }
    procesandoVenta.value = true
    error.value = ''
    exito.value = ''
    try {
      await apiFetch('/api/ventas/', {
        method: 'POST',
        body: JSON.stringify({
          metodo_pago: metodoPago.value,
          cliente: clienteId.value,
          items: carrito.value.map((item) => ({
            producto_id: item.id,
            cantidad: item.cantidad
          }))
        })
      })
      carrito.value = []
      clienteId.value = null
      busquedaCliente.value = ''
      mostrarClientes.value = false
      exito.value = 'Venta registrada correctamente.'
      await cargarProductos()
    } catch (err) {
      error.value = err.message
    } finally {
      procesandoVenta.value = false
    }
  }

  onMounted(() => {
    cargarProductos()
    cargarClientes()
  })

  return {
    productosFiltrados,
    clientes,
    carrito,
    busqueda,
    clienteId,
    busquedaCliente,
    mostrarClientes,
    metodoPago,
    cargando,
    procesandoVenta,
    error,
    exito,
    total,
    precio,
    stockDisponible,
    clientesFiltrados,
    clienteSeleccionado,
    agregarProducto,
    buscarYAgregar,
    cambiarCantidad,
    eliminarItem,
    seleccionarCliente,
    seleccionarConsumidorFinal,
    alternarClientes,
    confirmarVenta
  }
}
