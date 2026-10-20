<script setup>import { Plus, Pencil, Trash2, Tags, Eye, EyeOff } from 'lucide-vue-next';
import { seccion } from '../lib/sections';
import { useCategoriasPage } from '../composables/useCategoriasPage';
import PageHeader from '../components/PageHeader.vue';
import SearchInput from '../components/SearchInput.vue';
import Modal from '../components/Modal.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import EmptyState from '../components/EmptyState.vue';
import Field from '../components/Field.vue';
const { COLORES, data, q, verOcultas, ocultas, form, borrar, lista, nueva, editar, alternar, guardar, pedirBorrar, confirmarBorrar } = useCategoriasPage();
</script>

<template>
  <PageHeader :seccion="seccion('/categorias')">
    <template #actions>
      <SearchInput v-model="q" placeholder="Buscar categoría..." />
      <button :class="['flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition', verOcultas ? 'bg-tinta-200 text-tinta' : 'bg-tinta-50 text-tinta-500 hover:text-tinta']" @click="verOcultas = !verOcultas"><EyeOff class="h-4 w-4" />Ocultos ({{ ocultas }})</button>
      <button class="btn bg-amarillo-400 text-tinta hover:bg-amarillo-500" @click="nueva"><Plus class="h-4 w-4" />Nueva categoría</button>
    </template>
  </PageHeader>

  <div v-if="!lista.length" class="card"><EmptyState :icon="Tags" :title="verOcultas ? 'No hay categorías ocultas' : 'Sin categorías'" :text="verOcultas ? 'Las categorías que ocultes aparecen acá.' : 'Creá tu primera categoría para organizar los productos.'" /></div>
  <div v-else class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
    <div v-for="c in lista" :key="c.id" class="card group relative overflow-hidden transition hover:-translate-y-0.5 hover:shadow-pop">
      <div class="absolute -right-8 -top-8 h-28 w-28 rounded-full opacity-20" :style="{ background: c.color }" />
      <div class="h-2" :style="{ background: c.color }" />
      <div class="p-5">
        <div class="flex items-start gap-3">
          <div class="grid h-12 w-12 place-items-center rounded-xl text-tinta/70" :style="{ background: c.color }"><Tags class="h-6 w-6" /></div>
          <div class="min-w-0 flex-1">
            <h3 class="truncate text-xl font-semibold">{{ c.nombre }}</h3>
            <p class="truncate text-sm text-tinta-500">{{ c.descripcion || 'Sin descripción' }}</p>
          </div>
        </div>
        <div class="mt-5 grid grid-cols-3 gap-2 text-center">
          <div class="rounded-xl bg-tinta-50 py-2"><p class="font-display text-xl font-semibold">{{ c.cant }}</p><p class="text-[11px] uppercase text-tinta-500">Productos</p></div>
          <div class="rounded-xl bg-tinta-50 py-2"><p class="font-display text-xl font-semibold">{{ c.unidades }}</p><p class="text-[11px] uppercase text-tinta-500">Unidades</p></div>
          <div :class="['rounded-xl py-2', c.bajos ? 'bg-rojo-50 text-rojo-700' : 'bg-tinta-50']"><p class="font-display text-xl font-semibold">{{ c.bajos }}</p><p class="text-[11px] uppercase opacity-70">Stock bajo</p></div>
        </div>
        <div class="mt-4 flex items-center justify-end border-t border-tinta-100 pt-3">
          <div class="flex gap-1">
            <button class="rounded-lg p-2 text-tinta-500 hover:bg-tinta-50 hover:text-tinta disabled:opacity-30" :title="c.oculto ? 'Mostrar' : 'Ocultar'" @click="alternar(c)"><Eye v-if="c.oculto" class="h-4 w-4" /><EyeOff v-else class="h-4 w-4" /></button>
            <button class="rounded-lg p-2 text-tinta-500 hover:bg-tinta-50 hover:text-tinta" title="Editar" @click="editar(c)"><Pencil class="h-4 w-4" /></button>
            <button class="rounded-lg p-2 text-tinta-500 hover:bg-rojo-50 hover:text-rojo-700" title="Eliminar" @click="pedirBorrar(c)"><Trash2 class="h-4 w-4" /></button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <Modal :open="!!form" :title="form?.id ? 'Editar categoría' : 'Nueva categoría'" accent="bg-amarillo-400" @close="form = null">
    <div v-if="form" class="space-y-4">
      <Field label="Nombre"><input v-model="form.nombre" class="input" autofocus /></Field>
      <Field label="Descripción"><textarea v-model="form.descripcion" maxlength="120" rows="2" class="input h-[72px] resize-none" /></Field>
      <div>
        <span class="label">Color identificatorio</span>
        <div class="flex flex-wrap gap-2">
          <button v-for="col in COLORES" :key="col" type="button" :style="{ background: col }"
            :class="['h-10 w-10 rounded-xl transition', form.color === col ? 'scale-110 ring-4 ring-tinta/20 ring-offset-2' : 'hover:scale-105']" @click="form.color = col" />
        </div>
      </div>
    </div>
    <template #footer>
      <button class="btn-ghost" @click="form = null">Cancelar</button>
      <button class="btn bg-amarillo-400 text-tinta hover:bg-amarillo-500" @click="guardar">Guardar</button>
    </template>
  </Modal>

  <ConfirmDialog :open="!!borrar" title="Eliminar categoría" @close="borrar = null" @confirm="confirmarBorrar">
    ¿Seguro que querés eliminar <b>{{ borrar?.nombre }}</b>? Esta acción no se puede deshacer.
  </ConfirmDialog>
</template>
