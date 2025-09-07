import { createRouter, createWebHistory } from "vue-router"
import Login from "../views/Login.vue"
import Main from "../views/Main.vue"
import NotFound from "../views/NotFound.vue"
import { useAuthStore } from "../stores/auth"

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login, meta: {requiresAuth: false} },
  { path: "/main", component: Main, meta: {requiresAuth: true} },
  { path: "/:pathMatch(.*)*", component: NotFound }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

let authStore = null

/*router.beforeEach(async (to, from, next) => {
  if (!authStore) {
    authStore = useAuthStore()
    await authStore.initialize()
  }

  const isAuthenticated = authStore.isAuthenticated()

  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login")
  } else if (to.path === "/login" && isAuthenticated) {
    next("/main")
  } else {
    next()
  }
})*/

export default router

