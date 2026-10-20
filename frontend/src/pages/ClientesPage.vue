<script setup>import { Plus, Pencil, Trash2, Users, Mail, Phone, MapPin, Eye, EyeOff } from 'lucide-vue-next';
import { seccion } from '../lib/sections';
import { fmtMoney } from '../lib/format';
import { avatarColor, condColor } from '../lib/ui';
import { CONDICIONES, useClientesPage } from '../composables/useClientesPage';
import PageHeader from '../components/PageHeader.vue';
import SearchInput from '../components/SearchInput.vue';
import Modal from '../components/Modal.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import EmptyState from '../components/EmptyState.vue';
import Field from '../components/Field.vue';
const { data, q, verOcultos, ocultos, base, cond, form, borrar, iniciales, stats, lista, nuevo, alternar, guardar, toast } = useClientesPage();
</script>

<template>
  <PageHeader :seccion="seccion('/clientes')">
    <template #actions><button class="btn bg-violeta-400 text-tinta hover:bg-violeta-500" @click="nuevo"><Plus class="h-4 w-4" />Nuevo cliente</button></template>
  </PageHeader>

  <div class="mb-5 flex flex-wrap gap-2">
    <button :class="['rounded-full px-4 py-1.5 text-sm font-semibold transition', !cond ? 'bg-tinta text-white' : 'bg-white text-tinta-500 shadow-card']" @click="cond = ''">Todos ({{ base.length }})</button>
    <button v-for="c in CONDICIONES" :key="c" :class="['rounded-full px-4 py-1.5 text-sm font-semibold transition', cond === c ? avatarColor[c] : 'bg-white text-tinta-500 shadow-card hover:text-tinta']" @click="cond = cond === c ? '' : c">
      {{ c }} ({{ base.filter((x) => x.condicionIVA === c).length }})
    </button>
  </div>

  <div class="card overflow-hidden">
    <div class="flex items-center gap-3 border-b border-tinta-100 p-4">
      <SearchInput v-model="q" placeholder="Buscar por nombre o CUIT/DNI..." />
      <button :class="['flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition', verOcultos ? 'bg-tinta-200 text-tinta' : 'bg-tinta-50 text-tinta-500 hover:text-tinta']" @click="verOcultos = !verOcultos"><EyeOff class="h-4 w-4" />Ocultos ({{ ocultos }})</button>
      <span class="ml-auto text-sm text-tinta-500">{{ lista.length }} cliente(s)</span>
    </div>
    <EmptyState v-if="!lista.length" :icon="Users" :title="verOcultos ? 'No hay clientes ocultos' : 'Sin clientes'" :text="verOcultos ? 'Los clientes que ocultes aparecen acá.' : 'No se encontraron clientes con ese criterio.'" />
    <div v-else class="scroll-thin overflow-x-auto">
      <table class="w-full min-w-[900px]">
        <thead class="bg-tinta-50">
          <tr><th class="th">Cliente</th><th class="th">CUIT / DNI</th><th class="th">Condición IVA</th><th class="th">Contacto</th><th class="th text-right">Compras</th><th class="th text-right">Acciones</th></tr>
        </thead>
        <tbody class="divide-y divide-tinta-100">
          <tr v-for="c in lista" :key="c.id" class="hover:bg-tinta-50/60">
            <td class="td">
              <div class="flex items-center gap-3">
                <div :class="['grid h-10 w-10 shrink-0 place-items-center rounded-full font-display font-semibold', avatarColor[c.condicionIVA]]">{{ iniciales(c.razonSocial) }}</div>
                <div>
                  <p class="font-semibold">{{ c.razonSocial }}</p>
                  <p v-if="c.direccion" class="flex items-center gap-1 text-xs text-tinta-500"><MapPin class="h-3 w-3" />{{ c.direccion }}</p>
                </div>
              </div>
            </td>
            <td class="td font-mono text-xs">{{ c.documento }}</td>
            <td class="td"><span :class="['inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold', condColor[c.condicionIVA]]">{{ c.condicionIVA }}</span></td>
            <td class="td text-xs text-tinta-500">
              <p v-if="c.email" class="flex items-center gap-1.5"><Mail class="h-3.5 w-3.5" />{{ c.email }}</p>
              <p v-if="c.telefono" class="flex items-center gap-1.5"><Phone class="h-3.5 w-3.5" />{{ c.telefono }}</p>
              <template v-if="!c.email && !c.telefono">—</template>
            </td>
            <td class="td text-right">
              <p class="font-semibold">{{ fmtMoney(stats[c.id]?.total ?? 0) }}</p>
              <p class="text-xs text-tinta-500">{{ stats[c.id]?.n ?? 0 }} comprobantes</p>
            </td>
            <td class="td whitespace-nowrap text-right">
              <button class="rounded-lg p-2 text-tinta-500 hover:bg-tinta-50 hover:text-tinta disabled:opacity-30" :title="c.oculto ? 'Mostrar' : 'Ocultar'" :disabled="c.id === 'cf'" @click="alternar(c)"><Eye v-if="c.oculto" class="h-4 w-4" /><EyeOff v-else class="h-4 w-4" /></button>
              <button class="rounded-lg p-2 text-tinta-500 hover:bg-tinta-50 hover:text-tinta" title="Editar" @click="form = { ...c }"><Pencil class="h-4 w-4" /></button>
              <button class="rounded-lg p-2 text-tinta-500 hover:bg-rojo-50 hover:text-rojo-700 disabled:opacity-30" :disabled="c.id === 'cf'" title="Eliminar" @click="borrar = c"><Trash2 class="h-4 w-4" /></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <Modal :open="!!form" :title="form?.id ? 'Editar cliente' : 'Nuevo cliente'" accent="bg-violeta-500" size="lg" @close="form = null">
    <div v-if="form" class="grid gap-4 sm:grid-cols-2">
      <Field label="Razón social / Nombre" class="sm:col-span-2"><input v-model="form.razonSocial" class="input" autofocus /></Field>
      <Field label="CUIT / DNI"><input v-model="form.documento" class="input font-mono" placeholder="20-12345678-9" /></Field>
      <Field label="Condición frente al IVA">
        <select v-model="form.condicionIVA" class="input"><option v-for="c in CONDICIONES" :key="c">{{ c }}</option></select>
      </Field>
      <Field label="Email"><input v-model="form.email" class="input" type="email" /></Field>
      <Field label="Teléfono"><input v-model="form.telefono" class="input" /></Field>
      <Field label="Dirección" class="sm:col-span-2"><input v-model="form.direccion" class="input" /></Field>
      <p class="rounded-xl bg-violeta-50 px-4 py-3 text-xs text-violeta-700 sm:col-span-2">
        Se emitirá <b>{{ form.condicionIVA === 'Responsable Inscripto' ? 'Factura A' : 'Factura B' }}</b> a este cliente según su condición frente al IVA.
      </p>
    </div>
    <template #footer>
      <button class="btn-ghost" @click="form = null">Cancelar</button>
      <button class="btn bg-violeta-400 text-tinta hover:bg-violeta-500" @click="guardar">Guardar cliente</button>
    </template>
  </Modal>

  <ConfirmDialog :open="!!borrar" title="Eliminar cliente" @close="borrar = null" @confirm="borrar && (data.eliminarCliente(borrar.id), toast('Cliente eliminado'))">
    ¿Seguro que querés eliminar a <b>{{ borrar?.razonSocial }}</b>?
  </ConfirmDialog>
</template>
