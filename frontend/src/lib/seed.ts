import type { Caja, Categoria, Cliente, MedioPago, Producto, TipoComprobante, Venta } from '../types'
import { dayKey, precioVentaDe } from './format'

export const seedCategorias: Categoria[] = [
  { id: 'c1', nombre: 'Escolar', descripcion: 'Cuadernos, carpetas, útiles', color: '#7fdcdc' },
  { id: 'c2', nombre: 'Oficina', descripcion: 'Resmas, abrochadoras, archivo', color: '#f58f88' },
  { id: 'c3', nombre: 'Arte y Dibujo', descripcion: 'Témperas, pinceles, block', color: '#f8db8f' },
  { id: 'c4', nombre: 'Escritura', descripcion: 'Lapiceras, lápices, marcadores', color: '#c9bbfb' },
  { id: 'c5', nombre: 'Embalaje', descripcion: 'Cintas, cajas, papel madera', color: '#c9ccd6' },
  { id: 'c6', nombre: 'Regalería', descripcion: 'Bolsas, moños, tarjetas', color: '#f7bdd5' },
]

const p = (id: string, codigo: string, nombre: string, categoriaId: string, costo: number, venta: number, stock: number, min = 5): Producto => {
  const ganancia = Math.round((venta / 1.21 / costo - 1) * 100)
  return { id, codigo, nombre, categoriaId, precioCosto: costo, ganancia, precioVenta: precioVentaDe(costo, ganancia, 21), iva: 21, stock, stockMinimo: min }
}

export const seedProductos: Producto[] = [
  p('p1', '7790001', 'Cuaderno Rivadavia ABC 50 hojas', 'c1', 1800, 2900, 64),
  p('p2', '7790002', 'Carpeta N°3 3 anillos', 'c1', 2500, 4200, 22),
  p('p3', '7790003', 'Repuesto hojas N°3 x96', 'c1', 1900, 3100, 3),
  p('p4', '7790004', 'Cartuchera 2 pisos', 'c1', 5200, 8900, 12),
  p('p5', '7790005', 'Regla 30cm transparente', 'c1', 350, 700, 80),
  p('p6', '7790010', 'Resma A4 75g Autor', 'c2', 5800, 8500, 40, 10),
  p('p7', '7790011', 'Abrochadora Mit 21/6', 'c2', 6400, 10500, 6),
  p('p8', '7790012', 'Broches 21/6 x1000', 'c2', 700, 1300, 2),
  p('p9', '7790013', 'Bibliorato A4 lomo ancho', 'c2', 2900, 4800, 18),
  p('p10', '7790020', 'Témperas Alba x6', 'c3', 2100, 3600, 25),
  p('p11', '7790021', 'Block El Nene N°5 blanco', 'c3', 1300, 2300, 30),
  p('p12', '7790022', 'Set pinceles x5', 'c3', 1700, 2900, 4),
  p('p13', '7790023', 'Lápices de colores Faber x12', 'c3', 3800, 6200, 15),
  p('p14', '7790030', 'Birome Bic Cristal azul', 'c4', 250, 550, 200, 30),
  p('p15', '7790031', 'Lápiz negro HB Faber', 'c4', 200, 450, 150, 20),
  p('p16', '7790032', 'Resaltador Stabilo amarillo', 'c4', 900, 1600, 35),
  p('p17', '7790033', 'Marcador permanente Sharpie', 'c4', 1100, 1900, 0),
  p('p18', '7790040', 'Cinta de embalar 48mm', 'c5', 900, 1500, 45),
  p('p19', '7790041', 'Papel madera pliego', 'c5', 250, 500, 120),
  p('p20', '7790042', 'Caja cartón 40x30x30', 'c5', 1200, 2100, 9),
  p('p21', '7790050', 'Bolsa de regalo mediana', 'c6', 600, 1200, 50),
  p('p22', '7790051', 'Moño autoadhesivo x10', 'c6', 500, 1000, 28),
  p('p23', '7790052', 'Tarjeta de cumpleaños', 'c6', 400, 900, 60),
]

export const seedClientes: Cliente[] = [
  { id: 'cf', razonSocial: 'Consumidor Final', documento: '0', condicionIVA: 'Consumidor Final', email: '', telefono: '', direccion: '' },
  { id: 'cl1', razonSocial: 'Colegio San Martín', documento: '30-71234567-8', condicionIVA: 'Exento', email: 'administracion@csm.edu.ar', telefono: '221 455-1234', direccion: 'Calle 7 N° 1234, La Plata' },
  { id: 'cl2', razonSocial: 'Estudio Contable Pérez SRL', documento: '30-70987654-3', condicionIVA: 'Responsable Inscripto', email: 'compras@estudioperez.com', telefono: '221 423-9876', direccion: 'Av. 51 N° 820, La Plata' },
  { id: 'cl3', razonSocial: 'María Gómez', documento: '27-34567890-1', condicionIVA: 'Monotributista', email: 'mariag@gmail.com', telefono: '221 15 555-0101', direccion: 'Calle 12 N° 560, La Plata' },
  { id: 'cl4', razonSocial: 'Juan Rodríguez', documento: '32456789', condicionIVA: 'Consumidor Final', email: 'juanr@hotmail.com', telefono: '221 15 444-2020', direccion: 'Diag. 74 N° 1500, La Plata' },
]

// Ventas de ejemplo para hoy y días anteriores (deterministas)
let seed = 42
const rnd = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646
const pick = <T,>(a: T[]) => a[Math.floor(rnd() * a.length)]

export function buildSeedVentas(): { ventas: Venta[]; cajas: Caja[] } {
  const ventas: Venta[] = []
  const cajas: Caja[] = []
  const medios: MedioPago[] = ['Efectivo', 'Efectivo', 'Débito', 'Crédito', 'Cuenta DNI', 'Mercado Pago']
  let nro = 1
  for (let d = 6; d >= 0; d--) {
    const base = new Date()
    base.setDate(base.getDate() - d)
    base.setHours(9, 0, 0, 0)
    const cajaId = `caja-${dayKey(base)}`
    const caja: Caja = { id: cajaId, abiertaEn: base.toISOString(), montoInicial: 20000, usuario: 'admin', movimientos: [] }
    const n = d === 0 ? 9 : 10 + Math.floor(rnd() * 12)
    for (let i = 0; i < n; i++) {
      const fecha = new Date(base)
      const maxHour = d === 0 ? Math.max(1, Math.min(10, new Date().getHours() - 9)) : 10
      fecha.setHours(9 + Math.floor(rnd() * maxHour), Math.floor(rnd() * 60))
      const cli = rnd() < 0.7 ? seedClientes[0] : pick(seedClientes.slice(1))
      const tipo: TipoComprobante = cli.condicionIVA === 'Responsable Inscripto' ? 'Factura A' : 'Factura B'
      const items = Array.from({ length: 1 + Math.floor(rnd() * 4) }, () => {
        const pr = pick(seedProductos)
        return { productoId: pr.id, nombre: pr.nombre, cantidad: 1 + Math.floor(rnd() * 3), precioUnitario: pr.precioVenta, iva: pr.iva }
      })
      const total = items.reduce((s, it) => s + it.cantidad * it.precioUnitario, 0)
      const subtotal = +(total / 1.21).toFixed(2)
      const vto = new Date(fecha)
      vto.setDate(vto.getDate() + 10)
      ventas.push({
        id: `v${nro}`,
        numero: `0001-${String(nro).padStart(8, '0')}`,
        fecha: fecha.toISOString(),
        clienteId: cli.id,
        clienteNombre: cli.razonSocial,
        tipo,
        medioPago: pick(medios),
        items,
        subtotal,
        ivaTotal: +(total - subtotal).toFixed(2),
        total,
        cae: String(74000000000000 + Math.floor(rnd() * 999999999)),
        caeVto: vto.toISOString(),
        estadoARCA: rnd() < 0.93 ? 'Aprobado' : 'Pendiente',
        cajaId,
      })
      nro++
    }
    if (d > 0) {
      const cierre = new Date(base)
      cierre.setHours(19, 30)
      caja.cerradaEn = cierre.toISOString()
      caja.movimientos.push({ id: `m${d}`, fecha: cierre.toISOString(), tipo: 'Egreso', concepto: 'Pago proveedor', monto: 8000 })
      const efectivo = ventas.filter((v) => v.cajaId === cajaId && v.medioPago === 'Efectivo').reduce((s, v) => s + v.total, 0)
      caja.montoCierre = caja.montoInicial + efectivo - 8000
    }
    cajas.push(caja)
  }
  ventas.sort((a, b) => a.fecha.localeCompare(b.fecha))
  return { ventas, cajas }
}
