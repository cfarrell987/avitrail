import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Dashboard from '../views/Dashboard.vue'
import Flights from '../views/Flights.vue'
import { SessionManager } from '../utils/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/flights',
    name: 'Flights',
    component: Flights,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards with session validation
router.beforeEach((to, from, next) => {
  const isLoggedIn = SessionManager.isSessionValid()

  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/')
  } else if (to.meta.requiresGuest && isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
