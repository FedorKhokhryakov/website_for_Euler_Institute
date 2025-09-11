<template>
  <div class="admin-publications">
    <div class="filters-section">
      <select v-model="selectedAuthor" class="filter-select">
        <option value="">Все авторы</option>
        <option v-for="author in authors" :key="author.id" :value="author.id">
          {{ author.name }}
        </option>
      </select>
    </div>

    <div class="publications-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Автор</th>
            <th>Год</th>
            <th>Тип</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="publication in filteredPublications" :key="publication.id">
            <td>{{ publication.id }}</td>
            <td>{{ publication.title }}</td>
            <td>{{ publication.author }}</td>
            <td>{{ publication.year }}</td>
            <td>{{ publication.type }}</td>
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
import { ref, computed } from 'vue'

const selectedAuthor = ref('')

// Заглушка данных
const publications = ref([
  { id: 1, title: 'Математический анализ', author: 'Иванов И.И.', year: 2024, type: 'Монография' },
  { id: 2, title: 'Физика частиц', author: 'Петров П.П.', year: 2023, type: 'Статья' },
  { id: 3, title: 'Алгоритмы машинного обучения', author: 'Сидорова А.В.', year: 2024, type: 'Доклад' }
])

const authors = ref([
  { id: 1, name: 'Иванов И.И.' },
  { id: 2, name: 'Петров П.П.' },
  { id: 3, name: 'Сидорова А.В.' }
])

const filteredPublications = computed(() => {
  if (!selectedAuthor.value) return publications.value
  return publications.value.filter(pub => 
    pub.author === authors.value.find(a => a.id === parseInt(selectedAuthor.value))?.name
  )
})

const editPublication = (publication) => {
  console.log('Редактировать публикацию:', publication)
}

const deletePublication = (publication) => {
  if (confirm(`Удалить публикацию "${publication.title}"?`)) {
    console.log('Удалить публикацию:', publication)
  }
}
</script>

<style scoped>
.admin-publications {
  padding: 1rem;
}

.filters-section {
  margin-bottom: 1rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
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