<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>Институт им. Эйлера</h2>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-link">Главная</router-link>
        
        <div v-if="showReportsSection" class="reports-section">
          <div class="reports-label" @click="toggleReports">
            <span>Отчеты</span>
            <span class="dropdown-arrow" :class="{ rotated: isReportsOpen }">▶</span>
          </div>
          <div class="years-list" v-show="isReportsOpen">
            <router-link 
              v-for="year in years" 
              :key="year"
              :to="'/year_report/' + year" 
              class="year-link"
            >
              {{ year }}
            </router-link>
          </div>
        </div>

        <router-link 
            :to="userProfilePath" 
            class="nav-link"
        >
            Моя учетная запись
        </router-link>
        
        <div v-if="isAdmin" class="admin-section">
          <router-link to="/admin/add-users" class="nav-link admin-link">
            Добавить пользователя
          </router-link>
          <router-link to="/admin/generate-report" class="nav-link admin-link">
            Сгенерировать отчет
          </router-link>
        </div>
      </nav>

      <button @click="logout" class="logout-button">Выйти</button>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const isReportsOpen = ref(false)

const currentYear = new Date().getFullYear()
const years = computed(() => {
  const yearsList = []
  for (let year = 2014; year <= currentYear; year++) {
    yearsList.push(year)
  }
  return yearsList.reverse()
})

const isAdmin = computed(() => {
  const adminRoles = ['MasterAdmin', 'AdminPOMI', 'AdminSPbU']
  return user.value?.roles?.some(role => adminRoles.includes(role)) || false
})

const showReportsSection = computed(() => {
  const userRolesList = ['UserSPbU', 'UserPOMI']
  return user.value?.roles?.some(role => userRolesList.includes(role)) || false
})

const userProfilePath = computed(() => {
  if (user.value?.id) {
    return `/user/${user.value.id}/profile`
  }
  return '/dashboard'
})

const toggleReports = () => {
  isReportsOpen.value = !isReportsOpen.value
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  overflow: visible;
}

.sidebar {
  width: 270px;
  background-color: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 0rem;
}

.sidebar-header {
  padding: 1rem 0;
  background-color: var(--color-primary);
}

.sidebar-header h2 {
  color: var(--color-text-light);
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  text-align: center;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0rem;
}

.nav-link {
  padding: 8px 12px;
  color: var(--color-text-primary);
  text-decoration: none;
  border: 1px solid transparent;
  font-size: 0.95rem;
}

.nav-link:hover {
  background-color: var(--color-hover);
}

.nav-link.router-link-active {
  background-color: var(--color-primary);
  color: var(--color-text-light);
}

.reports-section {
  display: flex;
  flex-direction: column;
}

.reports-label {
  padding: 8px 12px;
  color: var(--color-text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  background-color: var(--color-surface);
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.reports-label:hover {
  background-color: var(--color-hover);
}

.dropdown-arrow {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
}

.dropdown-arrow.rotated {
  transform: rotate(90deg);
}

.years-list {
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.year-link {
  padding: 2px 12px 2px 24px;
  color: var(--color-text-primary);
  text-decoration: none;
  border: 1px solid transparent;
  font-size: 0.9rem;
  background-color: var(--color-surface);
}

.year-link:hover {
  background-color: var(--color-hover);
}

.year-link.router-link-active {
  background-color: var(--color-primary);
  color: var(--color-text-light);
}

.admin-section {
  display: flex;
  flex-direction: column;
}

.admin-link {
  color: var(--color-secondary);
  font-weight: 500;
}

.admin-link.router-link-active {
  background-color: var(--color-secondary);
  color: var(--color-text-light);
}

.logout-button {
  background-color: var(--color-secondary);
  color: var(--color-text-light);
  padding: 8px;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: auto;
}

.logout-button:hover {
  background-color: var(--color-secondary-dark);
}

.main-content {
  align-content: right;
  flex: 1;
  padding: 1rem;
  background-color: var(--color-background);
  z-index: 1;
}
</style>