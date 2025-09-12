<template>
  <div class="admin-publications">
    <div class="filters-section">
      <select v-model="selectedAuthor" class="filter-select">
        <option value="">Все авторы</option>
        <option v-for="author in authors" :key="author.id" :value="author.id">
          {{ author.first_name }} {{ author.middle_name }} {{ author.last_name }}
        </option>
      </select>
      <button @click="loadPublications" class="btn-refresh">Обновить</button>
    </div>

    <div v-if="loading" class="loading">Загрузка публикаций...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="publications-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Автор</th>
            <th>Год</th>
            <th>Тип</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="publication in filteredPublications" :key="publication.id">
            <td>{{ publication.id }}</td>
            <td>{{ publication.title }}</td>
            <td>{{ publication.authors }}</td>
            <td>{{ publication.year }}</td>
            <td>{{ publication.type }}</td>
            <td>{{ publication.status }}</td>
            <td class="actions">
              <button class="btn-edit" @click="editPublication(publication)">
                ✏️
              </button>
              <button class="btn-delete" @click="deletePublication(publication)">
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
import { publicationsAPI, usersAPI } from '../../services/api.js'

const selectedAuthor = ref('')
const publications = ref([])
const authors = ref([])
const loading = ref(false)
const error = ref('')

const loadPublications = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await publicationsAPI.getAll()
    console.log(response.data)
    publications.value = response.data
  } catch (err) {
    console.error('Ошибка загрузки публикаций:', err)
    error.value = 'Не удалось загрузить публикации'
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const response = await usersAPI.getAll()
    authors.value = response.data
  } catch (err) {
    console.error('Ошибка загрузки пользователей:', err)
  }
}

const filteredPublications = computed(() => {
  if (!selectedAuthor.value) return publications.value
  return publications.value.filter(pub => 
    pub.author === parseInt(selectedAuthor.value)
  )
})

const editPublication = (publication) => {
  console.log('Редактировать публикацию:', publication)
}

const deletePublication = async (publication) => {
  if (confirm(`Удалить публикацию "${publication.title}"?`)) {
    try {
      await loadPublications()
      console.log('Публикация удалена:', publication)
    } catch (err) {
      console.error('Ошибка удаления публикации:', err)
      alert('Не удалось удалить публикацию')
    }
  }
}

onMounted(() => {
  loadPublications()
  loadUsers()
})
</script>

<style scoped>
.admin-publications {
  padding: 1rem;
}

.filters-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: center;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  min-width: 200px;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: #f8f9fa;
  cursor: pointer;
}

.btn-refresh:hover {
  background: #e9ecef;
}

.loading, .error {
  padding: 2rem;
  text-align: center;
  font-size: 1.1rem;
}

.error {
  color: #dc3545;
}

.publications-table {
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
  display: flex;
  gap: 0.5rem;
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
  background-color: #ffebee;
}
</style>