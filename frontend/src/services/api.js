let refreshRequest = null

function tokenExpiraPronto() {
  try {
    const token = localStorage.getItem('access')
    if (!token) return false
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return Number(payload.exp) <= Math.floor(Date.now() / 1000) + 60
  } catch {
    return true
  }
}

async function renovarToken() {
  const refresh = localStorage.getItem('refresh')
  if (!refresh) return false

  if (!refreshRequest) {
    refreshRequest = fetch('/api/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    })
      .then(async (response) => {
        const data = await response.json().catch(() => ({}))
        if (!response.ok || !data.access) return false
        localStorage.setItem('access', data.access)
        if (data.refresh) localStorage.setItem('refresh', data.refresh)
        return true
      })
      .finally(() => {
        refreshRequest = null
      })
  }

  return refreshRequest
}

export async function apiFetch(url, options = {}, reintentar = true) {
  if (reintentar && tokenExpiraPronto()) await renovarToken()

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access')}`,
      ...(options.headers || {})
    }
  })

  if (response.status === 401 && reintentar && await renovarToken()) {
    return apiFetch(url, options, false)
  }

  const data = response.status === 204 ? null : await response.json().catch(() => ({}))
  if (!response.ok) {
    const detalle = data.error || data.detail || data.stock || data.items
    const detalleTexto = Array.isArray(detalle) ? detalle.join(' ') : typeof detalle === 'object'
      ? Object.values(detalle).flat().join(' ')
      : detalle
    const mensaje = response.status === 401
      ? 'La sesión expiró, volvé a iniciar sesión.'
      : detalleTexto || 'No se pudo completar la operación.'
    throw new Error(mensaje)
  }
  return data
}
