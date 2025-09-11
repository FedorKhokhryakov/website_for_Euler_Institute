<template>
  <div class="admin-dashboard">
    <div class="admin-header">
      <h1>Панель администратора</h1>
    </div>

    <div class="admin-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="tab-content">
      <AdminUsersView v-if="activeTab === 'users'" />
      <AdminPublicationsView v-if="activeTab === 'publications'" />
      <AdminReportsView v-if="activeTab === 'reports'" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AdminUsersView from './AdminUsersView.vue'
import AdminPublicationsView from './AdminPublicationsView.vue'
import AdminReportsView from './AdminReportsView.vue'

const activeTab = ref('users')

const tabs = [
  { id: 'users', label: 'Пользователи' },
  { id: 'publications', label: 'Публикации' },
  { id: 'reports', label: 'Отчеты' }
]
</script>

<style scoped>
.admin-dashboard {
  padding: 1rem;
}

.admin-header {
  margin-bottom: 2rem;
}

.admin-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 600;
}

.admin-tabs {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 2rem;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: #666;
  border-bottom: 3px solid transparent;
}

.tab-button.active {
  color: #2e7d32;
  border-bottom-color: #2e7d32;
}

.tab-button:hover {
  background-color: #f5f5f5;
}
</style>