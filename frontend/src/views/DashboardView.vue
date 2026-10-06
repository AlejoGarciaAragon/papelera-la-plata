<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const usuario = ref(localStorage.getItem('username') || 'Usuario: dueno_test')

const cerrarSesion = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<template>
  <main class="min-h-screen bg-slate-50 text-slate-700">
    <div class="min-h-screen w-full bg-white">
      <header class="flex flex-col gap-4 border-b border-slate-200 px-5 py-5 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <div class="flex min-w-0 items-center gap-5">
          <img src="../assets/logo-mark.svg" alt="Símbolo de Papelera La Plata" class="h-14 w-14 shrink-0 object-contain sm:h-16 sm:w-16" />
          <h1 class="truncate text-3xl font-bold leading-tight text-slate-800 sm:text-4xl">Papelera La Plata</h1>
        </div>

        <div class="flex items-center justify-between gap-4 sm:justify-end">
          <button
            type="button"
            class="truncate rounded-lg px-3 py-1.5 text-sm font-medium text-slate-500 transition-colors hover:bg-teal-50 hover:text-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-100"
            @click="router.push('/perfil')"
          >
            {{ usuario }}
          </button>
          <button
            type="button"
            class="shrink-0 rounded px-3 py-1.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-200"
            @click="cerrarSesion"
          >
            Cerrar Sesión
          </button>
        </div>
      </header>

      <nav class="overflow-x-auto border-b border-slate-200" aria-label="Navegación principal">
        <div class="flex min-w-[58rem] divide-x divide-slate-200 md:min-w-0">
          <router-link to="/productos" active-class="router-link-active bg-teal-50 text-teal-800" class="flex-1 whitespace-nowrap px-3 py-3 text-center text-sm font-medium text-slate-600 transition-colors hover:bg-teal-50 hover:text-teal-800">Productos</router-link>
          <router-link to="/categorias" active-class="router-link-active bg-teal-50 text-teal-800" class="flex-1 whitespace-nowrap px-3 py-3 text-center text-sm font-medium text-slate-600 transition-colors hover:bg-teal-50 hover:text-teal-800">Categorías</router-link>
          <router-link to="/clientes" active-class="router-link-active bg-teal-50 text-teal-800" class="flex-1 whitespace-nowrap px-3 py-3 text-center text-sm font-medium text-slate-600 transition-colors hover:bg-teal-50 hover:text-teal-800">Clientes</router-link>
          <router-link to="/facturacion" active-class="router-link-active bg-teal-50 text-teal-800" class="flex-1 whitespace-nowrap px-3 py-3 text-center text-sm font-medium text-slate-600 transition-colors hover:bg-teal-50 hover:text-teal-800">Facturación y ARCA</router-link>
          <router-link to="/caja" active-class="router-link-active bg-teal-50 text-teal-800" class="flex-1 whitespace-nowrap px-3 py-3 text-center text-sm font-medium text-slate-600 transition-colors hover:bg-teal-50 hover:text-teal-800">Caja y turnos</router-link>
          <router-link to="/stock" active-class="router-link-active bg-teal-50 text-teal-800" class="flex-1 whitespace-nowrap px-3 py-3 text-center text-sm font-medium text-slate-600 transition-colors hover:bg-teal-50 hover:text-teal-800">Stock y proveedores</router-link>
          <router-link to="/dashboard" exact-active-class="router-link-active bg-teal-50 text-teal-800" class="flex-1 whitespace-nowrap px-3 py-3 text-center text-sm font-medium text-slate-600 transition-colors hover:bg-teal-50 hover:text-teal-800">Dashboard</router-link>
        </div>
      </nav>

      <section class="min-h-[60vh] bg-slate-50/40 px-5 py-6 sm:px-8 sm:py-8">
        <router-view />
      </section>
    </div>
  </main>
</template>
