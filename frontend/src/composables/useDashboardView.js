import { ref } from 'vue'
import { useRouter } from 'vue-router'

export function useDashboardView() {
  const router = useRouter()
  const usuario = ref(localStorage.getItem('username') || 'Usuario: dueno_test')

  function cerrarSesion() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('username')
    router.push('/login')
  }

  return { router, usuario, cerrarSesion }
}
