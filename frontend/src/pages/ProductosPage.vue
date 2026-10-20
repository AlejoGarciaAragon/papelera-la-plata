<script setup>import { Plus, Pencil, Trash2, Package, AlertTriangle, PackageX, Eye, EyeOff } from 'lucide-vue-next';
import { seccion } from '../lib/sections';
import { fmtMoney } from '../lib/format';
import { stockInfo } from '../lib/ui';
import { FILTROS, IVAS, useProductosPage } from '../composables/useProductosPage';
import PageHeader from '../components/PageHeader.vue';
import SearchInput from '../components/SearchInput.vue';
import Modal from '../components/Modal.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import EmptyState from '../components/EmptyState.vue';
import Field from '../components/Field.vue';
import StatCard from '../components/StatCard.vue';
const { data, esEmpleado, q, cat, filtro, verOcultos, form, borrar, catDe, lista, bajos, sin, ocultos, precioForm, barra, toggle, nuevo, alternar, guardar, confirmarBorrar } = useProductosPage();
</script>

<template>
  <PageHeader :seccion="seccion('/productos')">
    <template #actions><button v-if="!esEmpleado" class="btn-rojo" @click="nuevo"><Plus class="h-4 w-4" />Nuevo producto</button></template>
  </PageHeader>

  <div v-if="!esEmpleado" class="mb-6 grid gap-4 sm:grid-cols-2">
    <button :class="['rounded-2xl text-left transition', filtro === 'sin' && 'ring-2 ring-rojo-300']" @click="toggle('sin')"><StatCard label="Sin stock" :value="String(sin)" :icon="PackageX" tone="bg-rojo-100 text-rojo-700" hint="Click para filtrar" /></button>
    <button :class="['rounded-2xl text-left transition', filtro === 'bajo' && 'ring-2 ring-amarillo-400']" @click="toggle('bajo')"><StatCard label="Stock bajo" :value="String(bajos)" :icon="AlertTriangle" tone="bg-amarillo-100 text-amarillo-700" hint="Click para filtrar" /></button>
  </div>

  <div class="card overflow-hidden">
    <div class="flex flex-wrap items-center gap-3 border-b border-tinta-100 p-4">
      <SearchInput v-model="q" :placeholder="esEmpleado ? 'Buscar precio por nombre o código...' : 'Buscar por nombre o código...'" />
      <select v-if="!esEmpleado" v-model="cat" class="input w-auto">
        <option value="">Todas las categorías</option>
        <option v-for="c in data.categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
      </select>
      <div v-if="!esEmpleado" class="flex rounded-xl bg-tinta-50 p-1 text-sm">
        <button v-for="[k, l] in FILTROS" :key="k" :class="['rounded-lg px-3 py-1.5 font-medium transition', filtro === k ? 'bg-white shadow-card' : 'text-tinta-500']" @click="filtro = k">{{ l }}</button>
      </div>
      <button v-if="!esEmpleado" :class="['flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition', verOcultos ? 'bg-tinta-200 text-tinta' : 'bg-tinta-50 text-tinta-500 hover:text-tinta']" @click="verOcultos = !verOcultos"><EyeOff class="h-4 w-4" />Ocultos ({{ ocultos }})</button>
      <span class="ml-auto text-sm text-tinta-500">{{ lista.length }} resultado(s)</span>
    </div>
    <EmptyState v-if="!lista.length" :icon="Package" :title="verOcultos ? 'No hay productos ocultos' : 'No hay productos'" :text="verOcultos ? 'Los productos que ocultes aparecen acá.' : 'Probá con otro filtro o agregá un producto nuevo.'" />
    <div v-else class="scroll-thin overflow-x-auto">
      <table class="w-full min-w-[860px]">
        <thead class="bg-tinta-50">
          <tr>
            <th class="th">Código</th><th class="th">Producto</th><th v-if="!esEmpleado" class="th">Categoría</th>
            <th v-if="!esEmpleado" class="th text-right">Costo</th><th v-if="!esEmpleado" class="th text-right">Ganancia</th><th class="th text-right">IVA</th><th class="th text-right">Venta</th>
            <th class="th">Stock</th><th v-if="!esEmpleado" class="th text-right">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-tinta-100">
          <tr v-for="p in lista" :key="p.id" :class="['transition hover:bg-tinta-50/60', p.stock === 0 && 'bg-rojo-50/40']">
            <td class="td font-mono text-xs text-tinta-500">{{ p.codigo }}</td>
            <td class="td font-medium">{{ p.nombre }}</td>
            <td v-if="!esEmpleado" class="td">
              <span v-if="catDe(p.categoriaId)" class="inline-flex items-center gap-2 text-sm">
                <span class="h-2.5 w-2.5 rounded-full" :style="{ background: catDe(p.categoriaId)?.color }" />{{ catDe(p.categoriaId)?.nombre }}
              </span>
            </td>
            <td v-if="!esEmpleado" class="td text-right text-tinta-500">{{ fmtMoney(p.precioCosto) }}</td>
            <td v-if="!esEmpleado" class="td text-right"><span :class="p.ganancia >= 40 ? 'text-turquesa-700' : 'text-amarillo-700'">{{ p.ganancia }}%</span></td>
            <td class="td text-right text-tinta-500">{{ p.iva }}%</td>
            <td class="td text-right font-semibold">{{ fmtMoney(p.precioVenta) }}</td>
            <td class="td">
              <div class="flex items-center gap-3">
                <span :class="['inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold', stockInfo(p).cls]">{{ stockInfo(p).label }}</span>
                <div class="hidden h-1.5 w-16 overflow-hidden rounded-full bg-tinta-100 xl:block">
                  <div :class="['h-full rounded-full', p.stock <= p.stockMinimo ? 'bg-amarillo-400' : 'bg-turquesa-400']" :style="{ width: `${barra(p)}%` }" />
                </div>
              </div>
            </td>
            <td v-if="!esEmpleado" class="td whitespace-nowrap text-right">
              <button class="rounded-lg p-2 text-tinta-500 hover:bg-tinta-50 hover:text-tinta disabled:opacity-30" :title="p.oculto ? 'Mostrar' : 'Ocultar'" @click="alternar(p)"><Eye v-if="p.oculto" class="h-4 w-4" /><EyeOff v-else class="h-4 w-4" /></button>
              <button class="rounded-lg p-2 text-tinta-500 hover:bg-tinta-50 hover:text-tinta" title="Editar" @click="form = { ...p }"><Pencil class="h-4 w-4" /></button>
              <button class="rounded-lg p-2 text-tinta-500 hover:bg-rojo-50 hover:text-rojo-700" title="Eliminar" @click="borrar = p"><Trash2 class="h-4 w-4" /></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <Modal :open="!!form" :title="form?.id ? 'Editar producto' : 'Nuevo producto'" accent="bg-rojo-500" size="md" @close="form = null">
    <div v-if="form" class="space-y-5">
      <Field label="Nombre"><input v-model="form.nombre" class="input text-base font-semibold" placeholder="Ej: Cuaderno Rivadavia 50 hojas" autofocus /></Field>
      <div class="grid gap-4 sm:grid-cols-2">
        <Field label="Código"><input v-model="form.codigo" class="input font-mono" /></Field>
        <Field label="Categoría">
          <select v-model="form.categoriaId" class="input">
            <option :value="null">Sin categoría</option>
            <option v-for="c in data.categorias.filter((categoria) => !categoria.oculto || (form.id && categoria.id === form.categoriaId))" :key="c.id" :value="c.id">{{ c.nombre }}{{ c.oculto ? ' (oculta)' : '' }}</option>
          </select>
        </Field>
      </div>

      <div class="rounded-2xl bg-tinta-50 p-4">
        <div class="grid gap-4 sm:grid-cols-3">
          <Field label="Costo">
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 font-semibold text-tinta-300">$</span>
              <input v-model.number="form.precioCosto" class="input bg-white pl-8" type="number" min="0" />
            </div>
          </Field>
          <Field label="Ganancia">
            <div class="relative">
              <input v-model.number="form.ganancia" class="input bg-white pr-9" type="number" min="0" />
              <span class="absolute right-3.5 top-1/2 -translate-y-1/2 font-semibold text-tinta-300">%</span>
            </div>
          </Field>
          <div>
            <span class="label">IVA</span>
            <div class="grid grid-cols-3 gap-1 rounded-xl bg-white p-1 ring-1 ring-tinta-100">
              <button v-for="v in IVAS" :key="v" type="button"
                :class="['rounded-lg py-1.5 text-sm font-semibold transition', form.iva === v ? 'bg-rojo-200 text-tinta' : 'text-tinta-500 hover:text-tinta']"
                @click="form.iva = v">{{ v }}%</button>
            </div>
          </div>
        </div>
        <div class="mt-4 flex items-center justify-between border-t border-tinta-200 pt-3">
          <span class="text-sm font-semibold text-tinta-500">Precio de venta</span>
          <span class="font-display text-3xl font-bold">{{ fmtMoney(precioForm) }}</span>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <Field label="Stock actual"><input v-model.number="form.stock" class="input" type="number" min="0" /></Field>
        <Field label="Stock mínimo"><input v-model.number="form.stockMinimo" class="input" type="number" min="0" /></Field>
      </div>
    </div>
    <template #footer>
      <button class="btn-ghost" @click="form = null">Cancelar</button>
      <button class="btn-rojo" @click="guardar">Guardar producto</button>
    </template>
  </Modal>

  <ConfirmDialog :open="!!borrar" title="Eliminar producto" @close="borrar = null" @confirm="confirmarBorrar">
    ¿Seguro que querés eliminar <b>{{ borrar?.nombre }}</b>? Esta acción no se puede deshacer.
  </ConfirmDialog>
</template>
