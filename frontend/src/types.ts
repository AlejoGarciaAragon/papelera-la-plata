export type CondicionIVA = 'Responsable Inscripto' | 'Monotributista' | 'Consumidor Final' | 'Exento'
export type TipoComprobante = 'Factura A' | 'Factura B' | 'Factura C' | 'Ticket'
export type MedioPago = 'Efectivo' | 'Débito' | 'Crédito' | 'Cuenta DNI' | 'Mercado Pago'
export type EstadoARCA = 'Aprobado' | 'Pendiente' | 'Rechazado'

export interface Categoria {
  id: string
  nombre: string
  descripcion: string
  color: string
  oculto?: boolean
}

export interface Producto {
  id: string
  codigo: string
  nombre: string
  categoriaId: string
  precioCosto: number
  ganancia: number
  precioVenta: number
  iva: 21 | 11 | 0
  stock: number
  stockMinimo: number
  oculto?: boolean
}

export interface Cliente {
  id: string
  razonSocial: string
  documento: string
  condicionIVA: CondicionIVA
  email: string
  telefono: string
  direccion: string
  oculto?: boolean
}

export interface ItemVenta {
  productoId: string
  nombre: string
  cantidad: number
  precioUnitario: number
  iva: number
}

export interface Venta {
  id: string
  numero: string
  fecha: string
  clienteId: string
  clienteNombre: string
  tipo: TipoComprobante
  medioPago: MedioPago
  items: ItemVenta[]
  subtotal: number
  ivaTotal: number
  total: number
  cae: string
  caeVto: string
  estadoARCA: EstadoARCA
  cajaId: string
}

export interface MovimientoCaja {
  id: string
  fecha: string
  tipo: 'Ingreso' | 'Egreso'
  concepto: string
  monto: number
}

export interface Caja {
  id: string
  abiertaEn: string
  cerradaEn?: string
  montoInicial: number
  montoCierre?: number
  usuario: string
  movimientos: MovimientoCaja[]
}

export interface Usuario {
  usuario: string
  nombre: string
  rol: 'Administrador' | 'Cajero'
}
