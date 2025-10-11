import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "../stores/auth"

import AppLayout from "../components/layout/AppLayout.vue"

import LoginView from "../views/LoginView.vue"
import RegisterView from "../views/RegisterView.vue"
import DashboardView from "../views/DashboardView.vue"
import UserProfileView from '../views/UserProfileView.vue'
import YearReportView from '../views/YearReportView.vue'
import PostFormView from '../views/PostFormView.vue'

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
        path: "/year_report/:year",
        name: "YearReport",
        component: YearReportView
      },
      {
        path: "/posts/create",
        name: "CreatePost",
        component: PostFormView,
        props: { mode: 'create' }
      },
      {
        path: "/posts/edit/:id",
        name: "EditPost",
        component: PostFormView,
        props: { mode: 'edit' }
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
        path: "generate-report", 
        name: "AdminGenerateReport",
        component: AdminReportsView
      },
      { 
        path: "add-users", 
        name: "AdminUsers",
        component: AdminUsersView
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
  const isAdmin = authStore.isAdmin
  
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