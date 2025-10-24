<template>
  <div class="app-layout">
    <div v-if="isImpersonating" class="impersonation-banner">
      <div class="banner-content">
        <span class="banner-text">
          Режим супервизора: Вы вошли как 
          <strong>{{ user?.second_name_rus }} {{ user?.first_name_rus }}</strong>
        </span>
        <button @click="stopImpersonation" class="banner-button">
          Вернуться к себе
        </button>
      </div>
    </div>

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
        
        <div v-if="isAdmin && !isImpersonating" class="admin-section">
          <router-link to="/admin/user-view" class="nav-link admin-link">
            Пользователи
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
const { user, isAdmin, isImpersonating, impersonator } = storeToRefs(authStore)

const isReportsOpen = ref(false)

const years = computed(() => {
  const yearsList = []
  for (let year = 2023; year <= 2031; year++) {
    yearsList.push(year)
  }
  return yearsList.reverse()
})

const showReportsSection = computed(() => {
  const userRolesList = ['SPbUUser', 'POMIUser']
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

const stopImpersonation = async () => {
  try {
    await authStore.stopImpersonation()
    router.push('/dashboard')
  } catch (error) {
    console.error('Ошибка при завершении имперсонализации:', error)
    alert('Не удалось завершить режим имперсонализации')
  }
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
}

.impersonation-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 30px;
  background-color: var(--color-primary-dark);
  color: var(--color-text-light);
  padding: 0.5rem;
  z-index: 1000;
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--color-primary-dark);
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 0 1rem;
}

.banner-text {
  font-weight: 500;
}

.banner-button {
  background-color: var(--color-secondary);
  color: var(--color-text-light);
  border: none;
  padding: 0.25rem 0.75rem;
  cursor: pointer;
  font-size: 0.8rem;
}

.banner-button:hover {
  background-color: var(--color-secondary-dark);
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
  flex: 1;
  padding: 1rem;
  background-color: var(--color-background);
  z-index: 1;
}
</style>
