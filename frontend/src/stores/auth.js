import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../lib/axios';
import { apiErrorMessage } from '../lib/apiError';
const KEY = 'papelera-la-plata:auth';
export const useAuthStore = defineStore('auth', () => {
    let stored = {};
    try {
        stored = JSON.parse(sessionStorage.getItem(KEY) || '{}');
    }
    catch {
        sessionStorage.removeItem(KEY);
    }
    const user = ref(stored.user || null);
    const initialized = ref(false);
    const error = ref('');
    async function login(usuario, pass) {
        error.value = '';
        try {
            const { data } = await api.post('/token/', { username: usuario.trim(), password: pass });
            const tokens = { access: data.access, refresh: data.refresh, user: null };
            sessionStorage.setItem(KEY, JSON.stringify(tokens));
            const current = await api.get('/me/');
            tokens.user = current.data;
            sessionStorage.setItem(KEY, JSON.stringify(tokens));
            user.value = tokens.user;
            initialized.value = true;
            return true;
        }
        catch (requestError) {
            sessionStorage.removeItem(KEY);
            user.value = null;
            error.value = requestError.response?.status === 401 ? 'Usuario o contraseña incorrectos' : apiErrorMessage(requestError, 'No se pudo conectar con el servidor.');
            return false;
        }
    }
    function logout() {
        sessionStorage.removeItem(KEY);
        user.value = null;
        initialized.value = true;
    }
    if (typeof window !== 'undefined')
        window.addEventListener('auth:expired', logout);
    async function initialize() {
        if (initialized.value)
            return !!user.value;
        const tokens = JSON.parse(sessionStorage.getItem(KEY) || '{}');
        if (!tokens.access || !tokens.refresh) {
            initialized.value = true;
            return false;
        }
        try {
            const { data } = await api.get('/me/');
            user.value = data;
            sessionStorage.setItem(KEY, JSON.stringify({ ...tokens, user: data }));
        }
        catch {
            logout();
        }
        initialized.value = true;
        return !!user.value;
    }
    return { user, initialized, error, login, logout, initialize };
});
