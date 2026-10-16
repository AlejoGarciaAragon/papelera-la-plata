<script setup>
import { useLoginView } from '../composables/useLoginView'

const { username, password, error, loading, login } = useLoginView()
</script>

<template>
  <div class="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#f8fbfa] px-4 py-8 sm:px-6">
    <div class="pointer-events-none absolute inset-x-0 top-0 h-2 bg-gradient-to-r from-teal-200 via-[#f7d8cf] to-teal-200"></div>
    <div class="pointer-events-none absolute -left-24 top-1/4 h-64 w-64 rounded-full bg-teal-100/35 blur-3xl"></div>
    <div class="pointer-events-none absolute -right-24 bottom-1/4 h-64 w-64 rounded-full bg-rose-100/35 blur-3xl"></div>

    <main class="relative w-full max-w-lg rounded-[2rem] border border-white/80 bg-white/90 px-7 py-9 shadow-[0_24px_80px_rgba(92,133,128,0.16)] backdrop-blur-sm sm:px-12 sm:py-12">
      <div class="mb-10 text-center">
        <img src="../assets/logo.png" alt="Logo de Papelera La Plata" class="mx-auto h-auto w-56 max-w-full mix-blend-multiply sm:w-64" />
        <h1 class="mt-7 text-3xl font-semibold leading-tight tracking-tight text-slate-700 sm:text-4xl">Bienvenido al sistema</h1>
        <p class="mx-auto mt-3 max-w-sm text-sm leading-6 text-slate-400">Gestioná tu stock y tus operaciones de manera simple, clara y ordenada.</p>
      </div>

      <form @submit.prevent="login" class="space-y-5">
        <div v-if="error" class="rounded-xl border border-rose-100 bg-rose-50/80 p-3 text-center text-sm text-rose-700">
          {{ error }}
        </div>

        <div>
          <label for="username" class="mb-2 block text-sm font-medium text-slate-600">Usuario</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            autocomplete="username"
            class="w-full rounded-xl border border-teal-100 bg-[#f4fbfa] px-4 py-3.5 text-slate-700 outline-none transition-all placeholder:text-slate-300 focus:border-teal-300 focus:bg-white focus:ring-4 focus:ring-teal-100"
            placeholder="Ingresá tu usuario"
          />
        </div>

        <div>
          <label for="password" class="mb-2 block text-sm font-medium text-slate-600">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full rounded-xl border border-teal-100 bg-[#f4fbfa] px-4 py-3.5 text-slate-700 outline-none transition-all placeholder:text-slate-300 focus:border-teal-300 focus:bg-white focus:ring-4 focus:ring-teal-100"
            placeholder="Ingresá tu contraseña"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="flex w-full items-center justify-center rounded-xl bg-[#a9dcd3] px-4 py-3.5 font-semibold text-[#245f5a] shadow-[0_8px_20px_rgba(137,199,190,0.24)] transition-all hover:-translate-y-0.5 hover:bg-[#94d2c7] hover:shadow-[0_10px_24px_rgba(137,199,190,0.32)] focus:outline-none focus:ring-4 focus:ring-teal-100 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
        >
          <span v-if="loading" class="animate-pulse">Ingresando...</span>
          <span v-else>Ingresar al sistema</span>
        </button>
      </form>

      <p class="mt-8 text-center text-xs text-slate-300">Un espacio simple para que el trabajo siga avanzando.</p>
    </main>
  </div>
</template>