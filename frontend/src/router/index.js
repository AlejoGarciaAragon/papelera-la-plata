import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProductosView from '../views/ProductosView.vue'
import CategoriasView from '../views/CategoriasView.vue'
import CajaView from '../views/CajaView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: () => {
        return localStorage.getItem('access') ? '/caja' : '/login'
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
      component: DashboardView,
      meta: { requiresAuth: true }
      , children: [
        {
          path: '',
          name: 'productos',
          component: ProductosView
        }
      ]
    },
    {
      path: '/categorias',
      component: DashboardView,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'categorias',
          component: CategoriasView
        }
      ]
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
      component: DashboardView,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'caja',
          component: CajaView
        }
      ]
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
    next('/caja')
  } else {
    next()
  }
})

export default router
