import { Store, Package, Tags, Users, Receipt } from 'lucide-vue-next';
export const SECCIONES = [
    { path: '/caja', label: 'Caja', descripcion: 'Ventas y movimientos del día', icon: Store, tile: 'bg-turquesa-300 text-turquesa-900', soft: 'bg-turquesa-50', text: 'text-turquesa-700' },
    { path: '/productos', label: 'Productos', descripcion: 'Alta, baja y modificación de stock', icon: Package, tile: 'bg-rojo-300 text-rojo-900', soft: 'bg-rojo-50', text: 'text-rojo-700' },
    { path: '/categorias', label: 'Categorías', descripcion: 'Organizá tus productos', icon: Tags, tile: 'bg-amarillo-400 text-amarillo-700', soft: 'bg-amarillo-50', text: 'text-amarillo-700' },
    { path: '/clientes', label: 'Clientes', descripcion: 'Datos fiscales y contacto', icon: Users, tile: 'bg-violeta-400 text-violeta-700', soft: 'bg-violeta-50', text: 'text-violeta-700' },
    { path: '/facturacion', label: 'Facturación', descripcion: 'Reporte diario y comprobantes ARCA', icon: Receipt, tile: 'bg-tinta-200 text-tinta', soft: 'bg-tinta-100', text: 'text-tinta' },
];
export const seccion = (path) => SECCIONES.find((s) => s.path === path);
