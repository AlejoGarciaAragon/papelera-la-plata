const money = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', minimumFractionDigits: 2 });
export const fmtMoney = (n) => money.format(n);
export const fmtDate = (iso) => new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' });
export const fmtTime = (iso) => new Date(iso).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
export const fmtDateTime = (iso) => `${fmtDate(iso)} ${fmtTime(iso)}`;
export const dayKey = (d) => {
    const x = new Date(d);
    return `${x.getFullYear()}-${String(x.getMonth() + 1).padStart(2, '0')}-${String(x.getDate()).padStart(2, '0')}`;
};
export const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
export const genCAE = () => Array.from({ length: 14 }, () => Math.floor(Math.random() * 10)).join('');
export const tipoPorCondicion = (cond) => cond === 'Responsable Inscripto' ? 'Factura A' : 'Factura B';
// Los precios de venta se redondean siempre hacia arriba a este múltiplo
export const REDONDEO = 10;
export const precioVentaDe = (costo, ganancia, iva) => Math.ceil(Math.round((Number(costo) || 0) * (1 + (Number(ganancia) || 0) / 100) * (1 + iva / 100) * 100) / 100 / REDONDEO) * REDONDEO;
