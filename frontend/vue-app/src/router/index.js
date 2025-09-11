import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "../stores/auth"

import AppLayout from "../components/layout/AppLayout.vue"

import LoginView from "../views/LoginView.vue"
import RegisterView from "../views/RegisterView.vue"
import DashboardView from "../views/DashboardView.vue"
import ScientificActivityView from '../views/ScientificActivityView.vue'
import AddPublicationView from '../views/AddPublicationView.vue'
import MyPublicationsView from '../views/MyPublicationsView.vue'
import PublicationDetailedView from '../views/PublicationDetailedView.vue'
import UserProfileView from '../views/UserProfileView.vue'

import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import AdminUsersView from '../views/admin/AdminUsersView.vue'
import AdminPublicationsView from '../views/admin/AdminPublicationsView.vue'
import AdminReportsView from '../views/admin/AdminReportsView.vue'
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
  { 
    path: "/register", 
    name: "Register",
    component: RegisterView, 
    meta: { requiresAuth: false } 
  },
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
  {
    path: '/admin',
    component: AppLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { 
        path: "", 
        name: "AdminDashboard",
        component: AdminDashboardView
      },
      { 
        path: "users", 
        name: "AdminUsers",
        component: AdminUsersView
      },
      { 
        path: "publications", 
        name: "AdminPublications",
        component: AdminPublicationsView
      },
      { 
        path: "reports", 
        name: "AdminReports",
        component: AdminReportsView
      }
    ]
  },
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


router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (!authStore.isInitialized) {
    await authStore.initialize()
  }
  
  const isAuthenticated = authStore.isAuthenticated
  const isAdmin = authStore.user?.is_admin
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login")
  } 
  else if ((to.path === "/login" || to.path === "/register") && isAuthenticated) {
    next("/dashboard")
  }
  else if (to.meta.requiresAdmin && !isAdmin) {
    next("/dashboard")
  }
  else {
    next()
  }
})

export default router