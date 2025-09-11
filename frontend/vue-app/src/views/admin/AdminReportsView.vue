<template>
  <div class="admin-reports">
    <div class="create-report-section">
      <h3>Создать новый отчет</h3>
      <div class="form-group">
        <div class="searchable-select">
          <input
            type="text"
            v-model="userSearch"
            placeholder="Поиск сотрудника..."
            class="form-select search-input"
            @focus="showDropdown = true"
          />
          <div v-if="showDropdown" class="dropdown">
            <div
              v-for="user in filteredUsers"
              :key="user.id"
              class="dropdown-item"
              @click="selectUser(user)"
            >
              {{ user.full_name || user.fullName }}
            </div>
            <div v-if="filteredUsers.length === 0" class="dropdown-item no-results">
              Сотрудники не найдены
            </div>
          </div>
        </div>
      </div>
      <div class="form-group">
        <select v-model="newReport.year" class="form-select">
          <option value="">Выберите год</option>
          <option v-for="year in years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>
      <button @click="generateReport" class="btn-generate" :disabled="isGenerating">
        {{ isGenerating ? 'Генерация...' : 'Сгенерировать' }}
      </button>
    </div>

    <div class="saved-reports-section">
      <h3>Сохраненные отчеты</h3>
      <div v-if="isLoading" class="loading">Загрузка отчетов...</div>
      <div v-else-if="reports.length === 0" class="no-reports">Нет сохраненных отчетов</div>
      <table v-else>
        <thead>
          <tr>
            <th>Название отчета</th>
            <th>Дата создания</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="report in reports" :key="report.id">
            <td>{{ report.name }}</td>
            <td>{{ formatDate(report.created_at || report.date) }}</td>
            <td>
              <button @click="downloadReport(report)" class="btn-download" :disabled="isDownloading">
                ⬇️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usersAPI, reportsAPI } from '../../services/api.js'

const newReport = ref({
  userId: '',
  year: '',
})

const userSearch = ref('')
const showDropdown = ref(false)
const selectedUser = ref(null)
const isGenerating = ref(false)
const isLoading = ref(false)
const isDownloading = ref(false)

const users = ref([])
const years = ref([2024, 2023, 2022, 2021])
const reports = ref([])

const loadUsers = async () => {
  try {
    const response = await usersAPI.getAll()
    users.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
  }
}

const loadReports = async () => {
  isLoading.value = true
  try {
    const response = await reportsAPI.getAll()
    reports.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки отчетов:', error)
  } finally {
    isLoading.value = false
  }
}

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const searchTerm = userSearch.value.toLowerCase()
  return users.value.filter(user => {
    const userName = user.full_name || user.fullName || ''
    return userName.toLowerCase().includes(searchTerm)
  })
})

const selectUser = (user) => {
  selectedUser.value = user
  newReport.value.userId = user.id
  userSearch.value = user.full_name || user.fullName
  showDropdown.value = false
}

const handleClickOutside = (event) => {
  const searchContainer = document.querySelector('.searchable-select')
  if (searchContainer && !searchContainer.contains(event.target)) {
    showDropdown.value = false
  }
}

const generateReport = async () => {
  if (!newReport.value.userId || !newReport.value.year) {
    alert('Выберите сотрудника и год')
    return
  }

  isGenerating.value = true
  try {
    const reportData = {
      user_id: newReport.value.userId,
      year: newReport.value.year,
      format: 'rtf',
      type: 'annual_user'
    }
    
    await reportsAPI.generate(reportData)
    
    newReport.value.userId = ''
    newReport.value.year = ''
    userSearch.value = ''
    selectedUser.value = null
    
    await loadReports()
    alert('Отчет успешно сгенерирован')
    
  } catch (error) {
    console.error('Ошибка генерации отчета:', error)
    alert('Не удалось сгенерировать отчет')
  } finally {
    isGenerating.value = false
  }
}

const downloadReport = async (report) => {
  isDownloading.value = true
  try {
    const response = await reportsAPI.download(report.id)
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    const fileName = `${report.name}.rtf` || `report_${report.id}.rtf`
    link.setAttribute('download', fileName)
    
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('Ошибка скачивания отчета:', error)
    alert('Не удалось скачать отчет')
  } finally {
    isDownloading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}

onMounted(() => {
  loadUsers()
  loadReports()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.admin-reports {
  padding: 1rem;
}

.create-report-section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid #ddd;
}

.create-report-section h3 {
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
  position: relative;
}

.form-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  margin-right: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.searchable-select {
  position: relative;
}

.search-input {
  width: 100%;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-item {
  padding: 0.5rem;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f0f0f0;
}

.no-results {
  color: #999;
  font-style: italic;
}

.btn-generate {
  padding: 0.5rem 1rem;
  background-color: #2e7d32;
  color: white;
  border: none;
  cursor: pointer;
}

.btn-generate:hover:not(:disabled) {
  background-color: #1b5e20;
}

.btn-generate:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.saved-reports-section {
  margin-top: 2rem;
}

.saved-reports-section table {
  width: 100%;
  border-collapse: collapse;
}

.saved-reports-section th,
.saved-reports-section td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.saved-reports-section th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.btn-download {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.btn-download:hover:not(:disabled) {
  background-color: #e8f5e8;
}

.btn-download:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading, .no-reports {
  text-align: center;
  padding: 2rem;
  color: #666;
}
</style>