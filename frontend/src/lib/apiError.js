export function apiErrorMessage(error, fallback = 'No se pudo completar la operación.') {
    const payload = error.response?.data;
    if (typeof payload === 'string')
        return payload;
    if (payload?.detail)
        return payload.detail;
    const messages = Object.values(payload || {}).flatMap((value) => Array.isArray(value) ? value : [value]).filter((value) => typeof value === 'string');
    return messages.join(' ') || error.message || fallback;
}