<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>Институт им. Эйлера</h2>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-link">Главная</router-link>
        <router-link to="/activity" class="nav-link">Научная деятельность</router-link>
        <router-link to="/add-publication" class="nav-link">Добавить публикацию</router-link>
        <router-link to="/my-publications" class="nav-link">Мои публикации</router-link>
        <router-link 
            :to="userProfilePath" 
            class="nav-link"
        >
            Моя учетная запись
        </router-link>
        
        <router-link 
          v-if="user?.is_admin" 
          to="/admin" 
          class="nav-link admin-link"
        >
          Панель администратора
        </router-link>
      </nav>

      <button @click="logout" class="logout-button">Выйти</button>
    </aside>

    <main class="main-content">

      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const userProfilePath = computed(() => {
  if (user.value?.id) {
    return `/user/${user.value.id}/profile`
  }
  return '/dashboard'
})

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