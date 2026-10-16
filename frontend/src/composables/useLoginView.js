import { ref } from 'vue'
import { useRouter } from 'vue-router'

export function useLoginView() {
  const router = useRouter()
  const username = ref('')
  const password = ref('')
  const error = ref('')
  const loading = ref(false)

  const login = async () => {
    if (!username.value || !password.value) {
      error.value = 'Por favor, completá todos los campos.'
      return
    }
    loading.value = true
    error.value = ''
    try {
      const response = await fetch('/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.value, password: password.value })
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(response.status === 401 ? 'Usuario o contraseña incorrectos.' : 'Ocurrió un error en el servidor.')
      }
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      localStorage.setItem('username', username.value)
      localStorage.setItem('role', data.role || '')
      router.push('/caja')
    } catch (err) {
      error.value = err.message || 'No se pudo conectar con el servidor.'
    } finally {
      loading.value = false
    }
  }

  return { username, password, error, loading, login }
}
