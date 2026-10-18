<script setup>
import { useCategoriasView } from '../composables/useCategoriasView'

const {
  categorias, busqueda, estadoFiltro, cargando, error, modal, categoriaSeleccionada, categoriaAEliminar, formulario,
  esDueno, categoriasVisibles, abrirCrear, abrirEditar, guardarCategoria, cambiarEstado, eliminarCategoria, confirmarEliminacionCategoria
} = useCategoriasView()
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">Categorías</h2>
        <p class="mt-1 text-sm text-slate-500">Organizá el catálogo y su disponibilidad.</p>
      </div>
      <button
        class="rounded-lg bg-teal-400 px-4 py-2 font-medium text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="!esDueno"
        @click="abrirCrear"
      >
        + Nueva Categoría
      </button>
    </div>

    <div v-if="error" class="flex items-center justify-between rounded-xl border border-rose-100 bg-rose-50 p-4 text-sm text-rose-700">
      <span>{{ error }}</span>
      <button class="font-bold" @click="error = ''">×</button>
    </div>

    <section class="rounded-xl bg-white p-4 shadow-sm">
      <div class="grid gap-3 md:grid-cols-[1fr_220px]">
        <input
          v-model="busqueda"
          class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
          placeholder="Buscar por nombre o descripción..."
        />
        <select
          v-model="estadoFiltro"
          class="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 outline-none focus:border-teal-300"
        >
          <option value="">Todas</option>
          <option value="true">Activas</option>
          <option value="false">Ocultas/Inactivas</option>
        </select>
      </div>
    </section>

    <section class="overflow-hidden rounded-xl bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px] text-left text-sm">
          <thead class="border-b border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="px-5 py-4">Nombre</th>
              <th class="px-5 py-4">Descripción</th>
              <th class="px-5 py-4">Estado</th>
              <th class="px-5 py-4">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="categoria in categoriasVisibles" :key="categoria.id" class="text-slate-600">
              <td class="px-5 py-4 font-medium text-slate-800">{{ categoria.nombre }}</td>
              <td class="px-5 py-4">{{ categoria.descripcion || 'Sin descripción' }}</td>
              <td class="px-5 py-4">
                <span
                  :class="categoria.activo ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                  class="rounded-full px-2.5 py-1 text-xs font-medium"
                >
                  {{ categoria.activo ? 'Activa' : 'Oculta' }}
                </span>
              </td>
              <td class="px-5 py-4">
                <div class="flex gap-2">
                  <button
                    class="text-slate-900 hover:text-slate-700 disabled:opacity-40"
                    :disabled="!esDueno"
                    @click="abrirEditar(categoria)"
                  >
                    Editar
                  </button>
                  <button
                    :class="categoria.activo ? 'text-amber-600 hover:text-amber-800' : 'text-teal-700 hover:text-teal-900'"
                    class="disabled:opacity-40"
                    :disabled="!esDueno"
                    @click="cambiarEstado(categoria)"
                  >
                    {{ categoria.activo ? 'Ocultar' : 'Activar' }}
                  </button>
                  <button
                    class="text-rose-700 hover:text-rose-900 disabled:opacity-40"
                    :disabled="!esDueno"
                    @click="eliminarCategoria(categoria)"
                  >
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!cargando && !categoriasVisibles.length">
              <td colspan="4" class="px-5 py-12 text-center text-slate-400">No hay categorías que coincidan con los filtros.</td>
            </tr>
            <tr v-if="cargando">
              <td colspan="4" class="px-5 py-12 text-center text-slate-400">Cargando categorías...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="modal" class="fixed inset-0 z-10 flex items-center justify-center bg-slate-900/30 p-4">
      <form class="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl" @submit.prevent="guardarCategoria">
        <div class="mb-5 flex items-center justify-between">
          <h3 class="text-xl font-bold text-slate-800">{{ categoriaSeleccionada ? 'Editar categoría' : 'Nueva categoría' }}</h3>
          <button type="button" class="text-2xl text-slate-400" @click="modal = false">×</button>
        </div>
        <div class="space-y-4">
          <label>
            Nombre
            <input v-model="formulario.nombre" required maxlength="150" class="campo" />
          </label>
          <label>
            Descripción
            <textarea v-model="formulario.descripcion" maxlength="250" class="campo" rows="3"></textarea>
          </label>
          <label class="flex items-center gap-2">
            <input v-model="formulario.activo" type="checkbox" class="h-4 w-4 accent-teal-500" />
            Categoría activa
          </label>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100" @click="modal = false">Cancelar</button>
          <button type="submit" class="rounded-lg bg-teal-400 px-4 py-2 font-medium text-white hover:bg-teal-500">Guardar categoría</button>
        </div>
      </form>
    </div>

    <div v-if="categoriaAEliminar" class="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/30 p-4">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="text-xl font-bold text-slate-800">Eliminar categoría</h3>
        <p class="mt-3 text-sm text-slate-600">¿Querés eliminar definitivamente la categoría <strong>{{ categoriaAEliminar.nombre }}</strong>? Esta acción no se puede deshacer.</p>
        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100" @click="categoriaAEliminar = null">Cancelar</button>
          <button type="button" class="rounded-lg bg-rose-600 px-4 py-2 font-medium text-white hover:bg-rose-700" @click="confirmarEliminacionCategoria">Eliminar definitivamente</button>
        </div>
      </div>
    </div>
  </div>
</template>
