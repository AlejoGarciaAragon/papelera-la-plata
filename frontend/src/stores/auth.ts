import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Usuario } from '../types'

// Usuarios de demostración. Reemplazar por el endpoint de login del backend.
const USUARIOS: Record<string, { pass: string; user: Usuario }> = {
  admin: { pass: 'admin', user: { usuario: 'admin', nombre: 'Administrador', rol: 'Administrador' } },
  caja: { pass: 'caja', user: { usuario: 'caja', nombre: 'Cajero/a', rol: 'Cajero' } },
}

const KEY = 'papelera-la-plata:session'

export const useAuthStore = defineStore('auth', () => {
  const raw = sessionStorage.getItem(KEY)
  const user = ref<Usuario | null>(raw ? JSON.parse(raw) : null)

  async function login(usuario: string, pass: string) {
    await new Promise((r) => setTimeout(r, 600))
    const found = USUARIOS[usuario.trim().toLowerCase()]
    if (!found || found.pass !== pass) return false
    sessionStorage.setItem(KEY, JSON.stringify(found.user))
    user.value = found.user
    return true
  }

  function logout() {
    sessionStorage.removeItem(KEY)
    user.value = null
  }

  return { user, login, logout }
})
