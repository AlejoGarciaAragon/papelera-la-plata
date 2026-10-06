import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: () => {
        return localStorage.getItem('access') ? '/dashboard' : '/login'
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/productos',
      name: 'productos',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/categorias',
      name: 'categorias',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/clientes',
      name: 'clientes',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/facturacion',
      name: 'facturacion',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/caja',
      name: 'caja',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/stock',
      name: 'stock',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/perfil',
      name: 'perfil',
      component: DashboardView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access')

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.name === 'login' && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
