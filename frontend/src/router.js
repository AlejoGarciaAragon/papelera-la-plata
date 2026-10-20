import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { useDataStore } from './stores/data';
import AppLayout from './components/AppLayout.vue';
const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: '/login', component: () => import('./pages/LoginPage.vue'), meta: { publica: true } },
        {
            path: '/',
            component: AppLayout,
            children: [
                { path: '', redirect: '/caja' },
                { path: 'caja', component: () => import('./pages/CajaPage.vue'), meta: { roles: ['Dueno', 'Empleado'] } },
                { path: 'productos', component: () => import('./pages/ProductosPage.vue'), meta: { roles: ['Dueno', 'Empleado'] } },
                { path: 'categorias', component: () => import('./pages/CategoriasPage.vue'), meta: { roles: ['Dueno'] } },
                { path: 'clientes', component: () => import('./pages/ClientesPage.vue'), meta: { roles: ['Dueno'] } },
                { path: 'facturacion', component: () => import('./pages/FacturacionPage.vue'), meta: { roles: ['Dueno'] } },
            ],
        },
        { path: '/:pathMatch(.*)*', redirect: '/caja' },
    ],
});
router.beforeEach(async (to) => {
    const auth = useAuthStore();
    if (!to.meta.publica && !(await auth.initialize()))
        return '/login';
    if (to.path === '/login' && auth.user)
        return '/caja';
    if (!to.meta.publica) {
        if (to.meta.roles && !to.meta.roles.includes(auth.user?.rol))
            return '/caja';
        await useDataStore().cargar();
    }
});
export default router;
