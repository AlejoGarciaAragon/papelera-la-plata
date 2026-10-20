<script setup>import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Eye, EyeOff, Lock, User, Loader2, ShieldCheck } from 'lucide-vue-next';
import { useAuthStore } from '../stores/auth';
import { SECCIONES } from '../lib/sections';
import BrandLogo from '../components/BrandLogo.vue';
const auth = useAuthStore();
const router = useRouter();
const usuario = ref('');
const pass = ref('');
const ver = ref(false);
const error = ref('');
const cargando = ref(false);
const anio = new Date().getFullYear();
async function submit() {
    error.value = '';
    cargando.value = true;
    const ok = await auth.login(usuario.value, pass.value);
    cargando.value = false;
    if (ok)
        router.push('/caja');
    else
      error.value = auth.error;
}
</script>

<template>
  <div class="grid min-h-full lg:grid-cols-2">
    <div class="relative hidden items-center justify-center overflow-hidden bg-gradient-to-br from-turquesa-50 via-white to-rojo-50 lg:flex">
      <div class="absolute -left-40 -top-40 h-[34rem] w-[34rem] rounded-full bg-turquesa-200/70 blur-3xl" />
      <div class="absolute -bottom-48 -right-32 h-[32rem] w-[32rem] rounded-full bg-rojo-200/60 blur-3xl" />
      <div class="absolute right-1/4 top-6 h-40 w-40 rounded-full bg-amarillo-100 blur-2xl" />
      <div class="absolute left-16 top-16 h-20 w-20 rounded-full border-[10px] border-turquesa-300/70" />
      <div class="absolute bottom-0 left-0 h-56 w-56 bg-rojo-200/80" style="clip-path: polygon(0 0, 100% 100%, 0 100%)" />
      <div class="absolute bottom-16 right-16 h-14 w-14 rotate-12 rounded-xl bg-turquesa-200" />
      <div class="absolute right-20 top-24 grid grid-cols-5 gap-3 opacity-50">
        <span v-for="i in 25" :key="i" class="h-1.5 w-1.5 rounded-full bg-tinta-300" />
      </div>
      <div class="relative flex flex-col items-center">
        <div class="rounded-[2.5rem] bg-white/85 px-14 py-12 shadow-pop ring-1 ring-white backdrop-blur">
          <BrandLogo size="xl" />
        </div>
        <div class="mt-10 flex gap-3">
          <span v-for="s in SECCIONES" :key="s.path" :title="s.label" :class="['grid h-12 w-12 place-items-center rounded-2xl shadow-card', s.tile]">
            <component :is="s.icon" class="h-5 w-5" />
          </span>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-center bg-tinta-50 px-6 py-12">
      <div class="w-full max-w-md">
        <BrandLogo size="lg" class="mb-8 justify-center lg:hidden" />
        <div class="card overflow-hidden">
          <div class="flex h-2">
            <div class="flex-1 bg-turquesa-400" />
            <div class="w-1/3 bg-rojo-500" />
            <div class="w-10 bg-amarillo-400" />
          </div>
          <form class="space-y-5 p-8" @submit.prevent="submit">
            <div>
              <h2 class="text-3xl font-bold">Iniciar sesión</h2>
              <p class="mt-1 text-sm text-tinta-500">Ingresá con tu usuario para operar la caja.</p>
            </div>
            <label class="block">
              <span class="label">Usuario</span>
              <div class="relative">
                <User class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-tinta-300" />
                <input v-model="usuario" class="input pl-9" autocomplete="username" autofocus required />
              </div>
            </label>
            <label class="block">
              <span class="label">Contraseña</span>
              <div class="relative">
                <Lock class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-tinta-300" />
                <input v-model="pass" class="input px-9" :type="ver ? 'text' : 'password'" placeholder="••••••" required />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-tinta-300 hover:text-tinta" @click="ver = !ver">
                  <EyeOff v-if="ver" class="h-4 w-4" /><Eye v-else class="h-4 w-4" />
                </button>
              </div>
            </label>
            <p v-if="error" class="rounded-xl bg-rojo-50 px-4 py-2.5 text-sm font-medium text-rojo-600">{{ error }}</p>
            <button class="btn-primary w-full py-3 text-base" :disabled="cargando">
              <Loader2 v-if="cargando" class="h-5 w-5 animate-spin" /><template v-else>Ingresar</template>
            </button>
          </form>
        </div>
        <p class="mt-6 text-center text-xs text-tinta-300">© {{ anio }} Papelera La Plata · Gestión comercial</p>
      </div>
    </div>
  </div>
</template>
