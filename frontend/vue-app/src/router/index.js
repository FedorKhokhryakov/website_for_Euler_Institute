import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "../stores/auth"

import AppLayout from "../components/layout/AppLayout.vue"

import LoginView from "../views/LoginView.vue"
//import RegisterView from "../views/RegisterView.vue"
import DashboardView from "../views/DashboardView.vue"
import ScientificActivityView from '../views/ScientificActivityView.vue'
import AddPublicationView from '../views/AddPublicationView.vue'
import MyPublicationsView from '../views/MyPublicationsView.vue'
import PublicationDetailedView from '../views/PublicationDetailedView.vue'
import UserProfileView from '../views/UserProfileView.vue'

/*import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminUsersView from '../views/admin/AdminUsersView.vue'
import AdminPublicationsView from '../views/admin/AdminPublicationsView.vue'
import AdminReportsView from '../views/admin/AdminReportsView.vue'*/
import NotFoundView from "../views/NotFoundView.vue"


const routes = [
  { 
    path: "/", 
    redirect: "/dashboard",
    meta: { requiresAuth: true }
  },
  { 
    path: "/login", 
    name: "Login",
    component: LoginView, 
    meta: { requiresAuth: false } 
  },
  /*{ 
    path: "/register", 
    name: "Register",
    component: RegisterView, 
    meta: { requiresAuth: false } 
  },*/
  {
    path: '',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { 
        path: "/dashboard", 
        name: "Dashboard",
        component: DashboardView
      },
      { 
        path: "/activity", 
        name: "ScientificActivity",
        component: ScientificActivityView
      },
      { 
        path: "/add-publication", 
        name: "AddPublication",
        component: AddPublicationView
      },
      { 
        path: "/my-publications", 
        name: "MyPublications",
        component: MyPublicationsView
      },
      {
        path:"/publication/:id",
        name: "PublicationDetail",
        component: PublicationDetailedView
      },
      {
        path: '/user/:id/profile',
        name: 'UserProfileView',
        component: UserProfileView
      }
    ]
  },
  // Admin routes
  /*{ 
    path: "/admin", 
    name: "AdminDashboard",
    component: AdminDashboardView, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: "/admin/users", 
    name: "AdminUsers",
    component: AdminUsersView, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: "/admin/publications", 
    name: "AdminPublications",
    component: AdminPublicationsView, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },
  { 
    path: "/admin/reports", 
    name: "AdminReports",
    component: AdminReportsView, 
    meta: { requiresAuth: true, requiresAdmin: true } 
  },*/
  { 
    path: "/:pathMatch(.*)*", 
    name: "NotFound",
    component: NotFoundView,
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


// Навигационный гард
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Если store еще не инициализирован, инициализируем его
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }
  
  const isAuthenticated = authStore.isAuthenticated
  const isAdmin = authStore.user?.role === 'admin' // Предполагаем, что в user есть поле role
  
  // Если маршрут требует авторизации, а пользователь не авторизован
  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login")
  } 
  // Если пользователь авторизован и пытается попасть на login/register
  else if ((to.path === "/login" || to.path === "/register") && isAuthenticated) {
    next("/dashboard")
  }
  // Если маршрут требует прав администратора, а у пользователя их нет
  else if (to.meta.requiresAdmin && !isAdmin) {
    next("/dashboard") // Или на страницу 403 Forbidden
  }
  // Во всех остальных случаях разрешаем переход
  else {
    next()
  }
})

export default router