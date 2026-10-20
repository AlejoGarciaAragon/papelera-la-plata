export const tipoBadge = (tipo) => tipo === 'Factura A' ? 'bg-rojo-200 text-rojo-800' : tipo === 'Factura B' ? 'bg-turquesa-200 text-turquesa-800' : tipo === 'Factura C' ? 'bg-amarillo-200 text-amarillo-700' : 'bg-tinta-200 text-tinta';
export const COLOR_MEDIO = {
    Efectivo: '#7fdcdc', 'Débito': '#f58f88', 'Crédito': '#b9bcc8', 'Cuenta DNI': '#f8db8f', 'Mercado Pago': '#c9bbfb',
};
export const condColor = {
    'Responsable Inscripto': 'bg-rojo-50 text-rojo-700',
    Monotributista: 'bg-violeta-50 text-violeta-700',
    'Consumidor Final': 'bg-turquesa-50 text-turquesa-700',
    Exento: 'bg-amarillo-100 text-amarillo-700',
};
export const avatarColor = {
    'Responsable Inscripto': 'bg-rojo-200 text-rojo-800',
    Monotributista: 'bg-violeta-200 text-violeta-700',
    'Consumidor Final': 'bg-turquesa-200 text-turquesa-800',
    Exento: 'bg-amarillo-200 text-amarillo-700',
};
export const stockInfo = (p) => p.stock === 0
    ? { cls: 'bg-rojo-100 text-rojo-700', label: 'Sin stock' }
    : p.stock <= p.stockMinimo
        ? { cls: 'bg-amarillo-100 text-amarillo-700', label: `${p.stock} · Bajo` }
        : { cls: 'bg-turquesa-50 text-turquesa-700', label: `${p.stock} u.` };
