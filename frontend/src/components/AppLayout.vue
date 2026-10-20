<script setup>import { ref, watch } from 'vue';
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router';
import { LogOut, Menu, X, CircleDot, PanelLeftClose, PanelLeftOpen } from 'lucide-vue-next';
import { SECCIONES } from '../lib/sections';
import { useAuthStore } from '../stores/auth';
import { useDataStore } from '../stores/data';
import LogoMark from './LogoMark.vue';
const SIDEBAR_KEY = 'papelera-la-plata:sidebar-colapsado';
const auth = useAuthStore();
const data = useDataStore();
const route = useRoute();
const router = useRouter();
const open = ref(false);
const colapsado = ref(localStorage.getItem(SIDEBAR_KEY) === '1');
watch(colapsado, (v) => localStorage.setItem(SIDEBAR_KEY, v ? '1' : '0'));
const hoyRaw = new Date().toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long' });
const hoy = hoyRaw.charAt(0).toUpperCase() + hoyRaw.slice(1);
const alternarMenu = () => {
    if (window.matchMedia('(min-width: 1024px)').matches)
        colapsado.value = !colapsado.value;
    else
        open.value = true;
};
const salir = () => {
    auth.logout();
    router.push('/login');
};
</script>

<template>
  <div class="flex h-full">
    <div v-if="open" class="fixed inset-0 z-30 bg-tinta/30 lg:hidden" @click="open = false" />
    <aside
      :class="[
        'no-print fixed inset-y-0 left-0 z-40 flex w-72 shrink-0 flex-col border-r border-tinta-100 bg-white transition-all duration-300 lg:static lg:translate-x-0',
        open ? 'translate-x-0' : '-translate-x-full',
        colapsado ? 'lg:w-[88px]' : 'lg:w-72',
      ]"
    >
      <div :class="['flex items-center px-6 pb-5 pt-6', colapsado && 'lg:justify-center lg:px-3']">
        <RouterLink to="/caja" class="flex items-center gap-3" title="Papelera La Plata">
          <LogoMark class="h-12 w-auto shrink-0" />
          <span :class="['font-display text-[26px] font-bold uppercase leading-[0.88] tracking-tight text-tinta', colapsado && 'lg:hidden']">
            <span class="block">Papelera</span><span class="block">La Plata</span>
          </span>
        </RouterLink>
        <button class="ml-auto rounded-lg p-1 lg:hidden" @click="open = false"><X class="h-5 w-5" /></button>
      </div>
      <p :class="['px-6 pb-2 text-[11px] font-semibold uppercase tracking-widest text-tinta-300', colapsado && 'lg:hidden']">Menú</p>
      <nav class="flex flex-1 flex-col gap-1 px-3">
        <RouterLink v-for="s in SECCIONES" :key="s.path" :to="s.path" custom v-slot="{ navigate, isActive, href }">
          <a
            :href="href"
            :title="s.label"
            :class="['group flex items-center gap-3 rounded-xl px-3 py-2.5 transition', isActive ? `${s.soft} font-semibold` : 'hover:bg-tinta-50', colapsado && 'lg:justify-center lg:px-0']"
            @click="navigate($event); open = false"
          >
            <span :class="['relative grid h-10 w-10 shrink-0 place-items-center rounded-xl transition', isActive ? `${s.tile} shadow-card` : `${s.soft} ${s.text} group-hover:scale-105`]">
              <component :is="s.icon" class="h-5 w-5" />
              <span
                v-if="s.path === '/caja' && colapsado"
                :class="['absolute -right-1 -top-1 hidden h-3 w-3 rounded-full ring-2 ring-white lg:block', data.cajaAbierta ? 'bg-turquesa-400' : 'bg-rojo-400']"
              />
            </span>
            <span :class="['flex-1 text-[15px]', colapsado && 'lg:hidden']">{{ s.label }}</span>
            <span
              v-if="s.path === '/caja'"
              :class="['h-2.5 w-2.5 rounded-full', data.cajaAbierta ? 'bg-turquesa-400 ring-4 ring-turquesa-100' : 'bg-rojo-400 ring-4 ring-rojo-100', colapsado && 'lg:hidden']"
              :title="data.cajaAbierta ? 'Caja abierta' : 'Caja cerrada'"
            />
          </a>
        </RouterLink>
      </nav>
      <div :class="['m-3 rounded-2xl border border-tinta-100 bg-tinta-50 p-3', colapsado && 'lg:px-0']">
        <div :class="['flex items-center gap-3', colapsado && 'lg:flex-col lg:gap-2']">
          <div class="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-turquesa-200 font-display text-lg font-bold text-turquesa-800" :title="auth.user?.nombre">{{ auth.user?.nombre[0] }}</div>
          <div :class="['min-w-0 flex-1', colapsado && 'lg:hidden']">
            <p class="truncate text-sm font-semibold">{{ auth.user?.nombre }}</p>
            <p class="text-xs text-tinta-500">{{ auth.user?.rol }}</p>
          </div>
          <button class="rounded-lg p-2 text-tinta-500 hover:bg-white hover:text-tinta" title="Cerrar sesión" @click="salir"><LogOut class="h-4 w-4" /></button>
        </div>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col">
      <header class="no-print sticky top-0 z-20 flex items-center gap-3 border-b border-tinta-100 bg-white/80 px-5 py-3 backdrop-blur lg:px-8">
        <button class="rounded-lg p-2 text-tinta-500 hover:bg-tinta-50 hover:text-tinta" :title="colapsado ? 'Expandir menú' : 'Contraer menú'" @click="alternarMenu">
          <Menu class="h-5 w-5 lg:hidden" />
          <PanelLeftOpen v-if="colapsado" class="hidden h-5 w-5 lg:block" />
          <PanelLeftClose v-else class="hidden h-5 w-5 lg:block" />
        </button>
        <p class="text-sm text-tinta-500">{{ hoy }}</p>
        <div class="ml-auto flex items-center gap-3">
          <RouterLink to="/caja" :class="['flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold', data.cajaAbierta ? 'bg-turquesa-50 text-turquesa-700' : 'bg-rojo-50 text-rojo-700']">
            <CircleDot class="h-3.5 w-3.5" />{{ data.cajaAbierta ? 'Caja abierta' : 'Caja cerrada' }}
          </RouterLink>
          <span class="hidden items-center gap-2 rounded-full bg-tinta-50 px-3 py-1.5 text-xs font-semibold text-tinta-500 sm:flex">
            <span class="h-2 w-2 rounded-full bg-turquesa-400" /> ARCA conectado
          </span>
        </div>
      </header>
      <main :key="route.path" class="scroll-thin flex-1 overflow-y-auto px-5 py-6 animate-[fadein_.25s_ease-out] lg:px-8 lg:py-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>
