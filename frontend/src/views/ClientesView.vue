<script setup>
import { useClientesView } from '../composables/useClientesView'

const {
  busqueda, condicionFiltro, estadoFiltro, cargando, guardando, error, modal,
  clienteSeleccionado, clienteAEliminar, formulario, tiposDocumento, condicionesIva, esDueno,
  puedeEditar, advertenciaDocumento, clientesVisibles, etiquetaTipoDocumento,
  etiquetaCondicion, abrirCrear, abrirEditar, guardarCliente, cambiarEstado,
  eliminarCliente, confirmarEliminacionCliente
} = useClientesView()
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h2 class="text-2xl font-bold text-slate-800">Clientes</h2>
        <p class="mt-1 text-sm text-slate-500">Administrá los datos fiscales para la facturación.</p>
      </div>
      <button
        class="rounded-lg bg-teal-400 px-4 py-2 font-medium text-white transition hover:bg-teal-500 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="!puedeEditar"
        @click="abrirCrear"
      >
        + Nuevo Cliente
      </button>
    </div>

    <div v-if="error" class="flex items-center justify-between rounded-xl border border-rose-100 bg-rose-50 p-4 text-sm text-rose-700">
      <span>{{ error }}</span>
      <button class="font-bold" @click="error = ''">×</button>
    </div>

    <section class="rounded-xl bg-white p-4 shadow-sm">
      <div class="grid gap-3 md:grid-cols-[1fr_220px_180px]">
        <input
          v-model="busqueda"
          class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
          placeholder="Buscar por nombre, DNI o CUIT..."
        />
        <select v-model="condicionFiltro" class="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 outline-none focus:border-teal-300">
          <option value="">Todas las condiciones</option>
          <option v-for="condicion in condicionesIva" :key="condicion.value" :value="condicion.value">{{ condicion.label }}</option>
        </select>
        <select v-model="estadoFiltro" class="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 outline-none focus:border-teal-300">
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Ocultos</option>
        </select>
      </div>
    </section>

    <section class="overflow-hidden rounded-xl bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[850px] text-left text-sm">
          <thead class="border-b border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="px-5 py-4">Razón Social</th>
              <th class="px-5 py-4">CUIT/DNI</th>
              <th class="px-5 py-4">Cond. IVA</th>
              <th class="px-5 py-4">Teléfono</th>
              <th class="px-5 py-4">Estado</th>
              <th class="px-5 py-4">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="cliente in clientesVisibles" :key="cliente.id" :class="cliente.activo ? '' : 'opacity-50'" class="text-slate-600">
              <td class="px-5 py-4 font-medium text-slate-800">{{ cliente.nombre_o_razon_social }}</td>
              <td class="px-5 py-4">{{ etiquetaTipoDocumento(cliente.tipo_documento) }}: {{ cliente.numero_documento }}</td>
              <td class="px-5 py-4">{{ etiquetaCondicion(cliente.condicion_iva) }}</td>
              <td class="px-5 py-4">{{ cliente.telefono || 'Sin teléfono' }}</td>
              <td class="px-5 py-4">
                <span :class="cliente.activo ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'" class="rounded-full px-2.5 py-1 text-xs font-medium">
                  {{ cliente.activo ? 'Activo' : 'Oculto' }}
                </span>
              </td>
              <td class="px-5 py-4">
                <div class="flex gap-3">
                  <button class="text-slate-900 hover:text-slate-700 disabled:opacity-40" :disabled="!puedeEditar" @click="abrirEditar(cliente)">Editar</button>
                  <button
                    v-if="esDueno"
                    :class="cliente.activo ? 'text-amber-600 hover:text-amber-800' : 'text-teal-700 hover:text-teal-900'"
                    @click="cambiarEstado(cliente)"
                  >
                    {{ cliente.activo ? 'Ocultar' : 'Activar' }}
                  </button>
                  <button
                    v-if="esDueno"
                    class="text-rose-700 hover:text-rose-900"
                    @click="eliminarCliente(cliente)"
                  >
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!cargando && !clientesVisibles.length">
              <td colspan="6" class="px-5 py-12 text-center text-slate-400">No hay clientes que coincidan con los filtros.</td>
            </tr>
            <tr v-if="cargando">
              <td colspan="6" class="px-5 py-12 text-center text-slate-400">Cargando clientes...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="modal" class="fixed inset-0 z-10 flex items-center justify-center bg-slate-900/30 p-4">
      <form class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white p-6 shadow-xl" @submit.prevent="guardarCliente">
        <div class="mb-5 flex items-center justify-between">
          <h3 class="text-xl font-bold text-slate-800">{{ clienteSeleccionado ? 'Editar cliente' : 'Nuevo cliente' }}</h3>
          <button type="button" class="text-2xl text-slate-400" @click="modal = false">×</button>
        </div>
        <div class="grid gap-4 md:grid-cols-2">
          <label>Nombre/Razón Social<input v-model.trim="formulario.nombre_o_razon_social" required maxlength="200" class="campo" /></label>
          <label>Condición IVA<select v-model="formulario.condicion_iva" class="campo"><option v-for="condicion in condicionesIva" :key="condicion.value" :value="condicion.value">{{ condicion.label }}</option></select></label>
          <label>Tipo de documento<select v-model="formulario.tipo_documento" class="campo"><option v-for="tipo in tiposDocumento" :key="tipo.value" :value="tipo.value">{{ tipo.label }}</option></select></label>
          <label>Dirección<input v-model.trim="formulario.direccion" maxlength="250" class="campo" /></label>
          <label>Número de documento<input v-model.trim="formulario.numero_documento" required maxlength="50" class="campo" /></label>
          <label>Teléfono<input v-model.trim="formulario.telefono" maxlength="50" class="campo" /></label>
          <label class="md:col-span-2">Email<input v-model.trim="formulario.email" type="email" maxlength="254" class="campo" /></label>
        </div>
        <p v-if="advertenciaDocumento" class="mt-3 text-sm text-amber-700">Para Responsable Inscripto se recomienda utilizar CUIT.</p>
        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100" @click="modal = false">Cancelar</button>
          <button type="submit" class="rounded-lg bg-teal-400 px-4 py-2 font-medium text-white hover:bg-teal-500 disabled:opacity-50" :disabled="guardando">
            {{ guardando ? 'Guardando...' : 'Guardar cliente' }}
          </button>
        </div>
      </form>
    </div>

    <div v-if="clienteAEliminar" class="fixed inset-0 z-20 flex items-center justify-center bg-slate-900/30 p-4">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h3 class="text-xl font-bold text-slate-800">Eliminar cliente</h3>
        <p class="mt-3 text-sm text-slate-600">
          ¿Querés eliminar definitivamente a
          <strong>{{ clienteAEliminar.nombre_o_razon_social }}</strong>?
          Solo será posible si no tiene ventas, pedidos u otras operaciones asociadas.
        </p>
        <div class="mt-6 flex justify-end gap-3">
          <button type="button" class="rounded-lg px-4 py-2 text-slate-600 hover:bg-slate-100" @click="clienteAEliminar = null">Cancelar</button>
          <button type="button" class="rounded-lg bg-rose-600 px-4 py-2 font-medium text-white hover:bg-rose-700" @click="confirmarEliminacionCliente">
            Eliminar definitivamente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
