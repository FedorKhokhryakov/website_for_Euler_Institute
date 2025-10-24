<template>
  <div class="admin-users">
    <div class="header-section">
      <h1>Панель управления пользователями</h1>
      <div class="header-controls">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по ФИО"
          class="search-input"
        >
        <button class="btn-add-user" @click="addUser">
          Добавить пользователя
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <p>Загрузка пользователей...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <div v-else class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>ФИО</th>
            <th>Email</th>
            <th>Группа</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ getUserFullName(user) }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.group }}</td>
            <td class="actions">
              <button 
                class="btn-impersonate" 
                @click="impersonateUser(user)" 
                title="Зайти от лица пользователя"
                :disabled="impersonating"
              >
                👤
              </button>
              <button 
                class="btn-delete" 
                @click="deleteUser(user)" 
                title="Удалить пользователя"
              >
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Подтверждение имперсонализации</h3>
        <p>Вы действительно хотите войти от лица пользователя <strong>{{ selectedUser ? getUserFullName(selectedUser) : '' }}</strong>?</p>
        <div class="modal-actions">
          <button @click="confirmImpersonation" class="btn-confirm">
            Подтвердить
          </button>
          <button @click="cancelImpersonation" class="btn-cancel">
            Отмена
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usersAPI } from '../../services/api'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const loading = ref(false)
const error = ref('')
const users = ref([])
const impersonating = ref(false)
const showConfirmModal = ref(false)
const selectedUser = ref(null)

const filteredUsers = computed(() => {
  let result = users.value

  if (searchQuery.value) {
    result = result.filter(user =>
      getUserFullName(user).toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  result = result.filter(user =>
    user.id != authStore.user?.id
  )
  
  return result.sort((a, b) => a.id - b.id)
})

const getUserFullName = (user) => {
  return `${user.second_name_rus} ${user.first_name_rus} ${user.middle_name_rus || ''}`.trim()
}

const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await usersAPI.getAllUsers()
    console.log(response.data)
    users.value = response.data.users
  } catch (err) {
    error.value = 'Ошибка загрузки пользователей'
    console.error('Error fetching users:', err)
  } finally {
    loading.value = false
  }
}

const impersonateUser = (user) => {
  selectedUser.value = user
  showConfirmModal.value = true
}

const confirmImpersonation = async () => {
  if (!selectedUser.value) return
  
  impersonating.value = true
  try {
    await authStore.startImpersonation(selectedUser.value.id)
    showConfirmModal.value = false
    selectedUser.value = null
    
    router.push('/dashboard')
  } catch (err) {
    console.error('Ошибка имперсонализации:', err)
    error.value = 'Не удалось войти от лица пользователя'
    alert('Ошибка имперсонализации: ' + (err.response?.data?.error || err.message))
  } finally {
    impersonating.value = false
  }
}

const cancelImpersonation = () => {
  showConfirmModal.value = false
  selectedUser.value = null
}

const deleteUser = (user) => {
  if (confirm(`Вы уверены, что хотите удалить пользователя "${getUserFullName(user)}"?`)) {
    console.log('Удалить пользователя:', user)
  }
}

const addUser = () => {
  router.push('/admin/add-user')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-users {
  padding: 1rem;
  position: relative;
}

.header-section {
  margin-bottom: 1.5rem;
}

.header-section h1 {
  color: var(--color-text-primary);
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  width: 300px;
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.btn-add-user {
  padding: 0.5rem 1rem;
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-add-user:hover {
  background-color: var(--color-primary-dark);
}

.users-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

th {
  background-color: var(--color-surface);
  font-weight: 600;
  color: var(--color-text-primary);
}

td {
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

.actions {
  gap: 0.5rem;
  display: flex;
}

.btn-impersonate, .btn-delete {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-background);
  cursor: pointer;
  color: var(--color-text-primary);
}

.btn-impersonate:hover:not(:disabled) {
  background-color: var(--color-hover);
  border-color: var(--color-primary);
}

.btn-impersonate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-delete:hover {
  background-color: var(--color-hover);
  border-color: var(--color-secondary);
}

.loading, .error-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.error-state {
  color: var(--color-secondary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-background);
  padding: 2rem;
  border: 1px solid var(--color-border);
  max-width: 400px;
  width: 90%;
  color: var(--color-text-primary);
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-confirm, .btn-cancel {
  padding: 0.5rem 1rem;
  border: none;
  cursor: pointer;
}

.btn-confirm {
  background-color: var(--color-primary);
  color: var(--color-text-light);
}

.btn-confirm:hover {
  background-color: var(--color-primary-dark);
}

.btn-cancel {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
}

.btn-cancel:hover {
  background-color: var(--color-hover);
}
</style>