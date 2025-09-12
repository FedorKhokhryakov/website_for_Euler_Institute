<template>
  <div class="admin-users">
    <div class="search-section">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Поиск по ФИО"
        class="search-input"
      >
    </div>

    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>ФИО</th>
            <th>Email</th>
            <th>Лаборатория</th>
            <th>Роль</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ getUserFullName(user) }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.department }}</td>
            <td>{{ user.role }}</td>
            <td class="actions">
              <button class="btn-edit" @click="editUser(user)" title="Редактировать пользователя">
                ✏️
              </button>
              <button class="btn-delete" @click="deleteUser(user)" title="Удалить пользователя">
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersAPI } from '../../services/api'

const searchQuery = ref('')
const loading = ref(false)
const error = ref('')
const users = ref([])

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  return users.value.filter(user =>
    getUserFullName(user).toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const getUserFullName = (user) => {
  return `${user.last_name || ''} ${user.first_name || ''} ${user.middle_name || ''}`.trim()
}

const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await usersAPI.getAll()
    console.log(response.data)
    users.value = response.data
  } catch (err) {
    error.value = 'Ошибка загрузки пользователей'
    console.error('Error fetching users:', err)
  } finally {
    loading.value = false
  }
}

const editUser = (user) => {
  console.log('Редактировать пользователя:', user)
}

const deleteUser = (user) => {
  console.log('Удалить пользователя:', user)
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.admin-users {
  padding: 1rem;
}

.search-section {
  margin-bottom: 1rem;
}

.search-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  width: 300px;
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
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.actions {
  gap: 0.5rem;
  display: flex
}

.btn-edit, .btn-delete {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.btn-edit:hover {
  background-color: #e3f2fd;
}

.btn-delete:hover {
  background-color: #f3e5f5;
}
</style>