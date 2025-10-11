<template>
  <div class="admin-reports">
    <div class="create-report-section">
      <h2>Создать выгрузку из базы данных</h2>
      
      <div class="form-group">
        <label>Тип выгрузки:</label>
        <div class="radio-group">
          <label>
            <input 
              type="radio" 
              v-model="reportSettings.load_type" 
              value="yearly" 
            />
            Годовая
          </label>
          <label>
            <input 
              type="radio" 
              v-model="reportSettings.load_type" 
              value="quarterly" 
            />
            Квартальная
          </label>
        </div>
      </div>

      <div class="form-group">
        <div v-if="reportSettings.load_type === 'yearly'">
          <label>Год:</label>
          <select v-model="reportSettings.year" class="form-select">
            <option value="">Выберите год</option>
            <option v-for="year in years" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
        </div>
        
        <div v-else class="quarterly-period">
          <div class="period-row">
            <div class="period-item">
              <label>Начальный квартал:</label>
              <div class="quarter-inputs">
                <select v-model="reportSettings.start_quarter.quarter" class="form-select">
                  <option value="">Квартал</option>
                  <option value="1">1 квартал</option>
                  <option value="2">2 квартал</option>
                  <option value="3">3 квартал</option>
                  <option value="4">4 квартал</option>
                </select>
                <select v-model="reportSettings.start_quarter.year" class="form-select">
                  <option value="">Год</option>
                  <option v-for="year in years" :key="year" :value="year">
                    {{ year }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="period-item">
              <label>Конечный квартал:</label>
              <div class="quarter-inputs">
                <select v-model="reportSettings.end_quarter.quarter" class="form-select">
                  <option value="">Квартал</option>
                  <option value="1">1 квартал</option>
                  <option value="2">2 квартал</option>
                  <option value="3">3 квартал</option>
                  <option value="4">4 квартал</option>
                </select>
                <select v-model="reportSettings.end_quarter.year" class="form-select">
                  <option value="">Год</option>
                  <option v-for="year in years" :key="year" :value="year">
                    {{ year }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Пользователи для выгрузки:</label>
        <div class="radio-group">
          <label>
            <input 
              type="radio" 
              v-model="reportSettings.user_type" 
              value="all" 
              @change="handleUserTypeChange"
            />
            Все пользователи
          </label>
          <label>
            <input 
              type="radio" 
              v-model="reportSettings.user_type" 
              value="POMI" 
              @change="handleUserTypeChange"
            />
            Только ПOMИ
          </label>
          <label>
            <input 
              type="radio" 
              v-model="reportSettings.user_type" 
              value="SPbU" 
              @change="handleUserTypeChange"
            />
            Только СПбГУ
          </label>
          <label>
            <input 
              type="radio" 
              v-model="reportSettings.user_type" 
              value="certain" 
              @change="handleUserTypeChange"
            />
            Конкретный пользователь
          </label>
        </div>

        <div v-if="reportSettings.user_type === 'certain'" class="searchable-select">
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
              {{ getUserFullName(user) }}
            </div>
            <div v-if="filteredUsers.length === 0" class="dropdown-item no-results">
              Сотрудники не найдены
            </div>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Включить в выгрузку:</label>
        <div class="checkbox-group">
          <label>
            <input 
              type="checkbox" 
              v-model="reportSettings.publications" 
            />
            Публикации
          </label>
          <label v-if="reportSettings.publications">
            <input 
              type="checkbox" 
              v-model="reportSettings.only_printed_publications" 
            />
            Только опубликованные публикации
          </label>
          <label>
            <input 
              type="checkbox" 
              v-model="reportSettings.presentations" 
            />
            Доклады
          </label>
          <label v-if="reportSettings.load_type === 'yearly'">
            <input 
              type="checkbox" 
              v-model="reportSettings.science_reports" 
            />
            Научные отчеты
          </label>
        </div>
      </div>

      <button 
        @click="generateReport" 
        class="btn-generate" 
        :disabled="isGenerating || !isFormValid"
      >
        {{ isGenerating ? 'Генерация...' : 'Сгенерировать выгрузку' }}
      </button>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>

    <div v-if="previewContent" class="preview-section">
      <h4>Предпросмотр выгрузки:</h4>
      <div class="preview-content">
        <pre>{{ previewContent }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usersAPI, adminAPI } from '../../services/api.js'

const reportSettings = ref({
  load_type: 'yearly',
  year: '',
  start_quarter: {
    quarter: '',
    year: ''
  },
  end_quarter: {
    quarter: '',
    year: ''
  },
  user_type: 'all',
  user_id: '',
  publications: true,
  presentations: true,
  science_reports: false,
  only_printed_publications: false
})

const userSearch = ref('')
const showDropdown = ref(false)
const selectedUser = ref(null)
const isGenerating = ref(false)
const users = ref([])
const errorMessage = ref('')
const previewContent = ref('')

const years = computed(() => {
  const startYear = 2000
  const endYear = new Date().getFullYear()
  const yearList = []
  for (let year = endYear; year >= startYear; year--) {
    yearList.push(year)
  }
  return yearList
})

const loadUsers = async () => {
  try {
    const response = await usersAPI.getAllUsers()
    users.value = response.data.users || response.data
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
    errorMessage.value = 'Ошибка загрузки списка пользователей'
  }
}

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const searchTerm = userSearch.value.toLowerCase()
  return users.value.filter(user => {
    const userName = getUserFullName(user) || ''
    return userName.toLowerCase().includes(searchTerm)
  })
})

const isFormValid = computed(() => {
  const settings = reportSettings.value
  
  if (settings.load_type === 'yearly') {
    if (!settings.year) return false
  } else {
    if (!settings.start_quarter.quarter || !settings.start_quarter.year || 
        !settings.end_quarter.quarter || !settings.end_quarter.year) {
      return false
    }
    
    const startDate = new Date(settings.start_quarter.year, (settings.start_quarter.quarter - 1) * 3)
    const endDate = new Date(settings.end_quarter.year, (settings.end_quarter.quarter - 1) * 3 + 2)
    if (startDate > endDate) return false
  }
  
  if (settings.user_type === 'certain' && !settings.user_id) return false
  
  if (!settings.publications && !settings.presentations && 
      !(settings.load_type === 'yearly' && settings.science_reports)) {
    return false
  }
  
  return true
})

const handleUserTypeChange = () => {
  if (reportSettings.value.user_type !== 'certain') {
    reportSettings.value.user_id = ''
    selectedUser.value = null
    userSearch.value = ''
  }
}

const selectUser = (user) => {
  selectedUser.value = user
  reportSettings.value.user_id = user.id
  userSearch.value = getUserFullName(user)
  showDropdown.value = false
}

const getUserFullName = (user) => {
  return `${user.last_name || ''} ${user.first_name || ''} ${user.middle_name || ''}`.trim()
}

const handleClickOutside = (event) => {
  const searchContainer = document.querySelector('.searchable-select')
  if (searchContainer && !searchContainer.contains(event.target)) {
    showDropdown.value = false
  }
}

const generateReport = async () => {
  if (!isFormValid.value) {
    errorMessage.value = 'Заполните все обязательные поля корректно'
    return
  }

  isGenerating.value = true
  errorMessage.value = ''
  previewContent.value = ''

  try {
    const requestData = { ...reportSettings.value }
    
    if (requestData.user_type !== 'certain') {
      delete requestData.user_id
    }
    
    if (requestData.load_type === 'yearly') {
      delete requestData.start_quarter
      delete requestData.end_quarter
      requestData.year = parseInt(requestData.year)
    } else {
      delete requestData.year
      delete requestData.science_reports
      
      requestData.start_quarter = {
        quarter: parseInt(requestData.start_quarter.quarter),
        year: parseInt(requestData.start_quarter.year)
      }
      requestData.end_quarter = {
        quarter: parseInt(requestData.end_quarter.quarter),
        year: parseInt(requestData.end_quarter.year)
      }
    }

    requestData.publications = Boolean(requestData.publications)
    requestData.presentations = Boolean(requestData.presentations)
    requestData.only_printed_publications = Boolean(requestData.only_printed_publications)
    if (requestData.load_type === 'yearly') {
      requestData.science_reports = Boolean(requestData.science_reports)
    }

    const response = await adminAPI.getDBInfoBlob(requestData)

    const blob = response.data
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = generateFileName()
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    errorMessage.value = 'Выгрузка успешно сгенерирована'
    
  } catch (error) {
    console.error('Ошибка генерации выгрузки:', error)
    errorMessage.value = error.response?.data?.error || error.message || 'Не удалось сгенерировать выгрузку'
  } finally {
    isGenerating.value = false
  }
}

const generateFileName = () => {
  const settings = reportSettings.value
  let fileName = 'report_'
  
  if (settings.load_type === 'yearly') {
    fileName += `yearly_${settings.year}`
  } else {
    fileName += `quarterly_${settings.start_quarter.year}Q${settings.start_quarter.quarter}-${settings.end_quarter.year}Q${settings.end_quarter.quarter}`
  }
  
  fileName += `_${settings.user_type}`
  
  if (settings.user_type === 'certain' && selectedUser.value) {
    fileName += `_${selectedUser.value.username}`
  }
  
  fileName += '.rtf'
  
  return fileName
}

onMounted(() => {
  loadUsers()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.admin-reports {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.create-report-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
}

.create-report-section h2 {
  margin-bottom: 1.5rem;
  color: var(--color-text-primary);
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.radio-group,
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-group label,
.checkbox-group label {
  display: flex;
  align-items: center;
  font-weight: normal;
  cursor: pointer;
}

.radio-group input[type="radio"],
.checkbox-group input[type="checkbox"] {
  margin-right: 0.5rem;
}

.form-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  width: 100%;
  box-sizing: border-box;
  font-size: 14px;
  background-color: var(--color-background);
}

.quarterly-period .period-row {
  display: flex;
  gap: 1rem;
}

.period-item {
  flex: 1;
}

.quarter-inputs {
  display: flex;
  gap: 0.5rem;
}

.quarter-inputs .form-select {
  flex: 1;
}

.searchable-select {
  position: relative;
  margin-top: 0.5rem;
}

.search-input {
  width: 100%;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-top: none;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-item {
  padding: 0.5rem;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
}

.dropdown-item:hover {
  background-color: var(--color-hover);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.no-results {
  color: var(--color-text-secondary);
  font-style: italic;
}

.btn-generate {
  padding: 0.75rem 1.5rem;
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
}

.btn-generate:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.btn-generate:disabled {
  background-color: var(--color-text-secondary);
  cursor: not-allowed;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: var(--color-secondary);
  color: var(--color-text-light);
  font-weight: 600;
}

.preview-section {
  margin-top: 2rem;
  padding: 1.5rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-surface);
}

.preview-section h4 {
  margin-bottom: 1rem;
  color: var(--color-text-primary);
}

.preview-content {
  background-color: var(--color-background);
  padding: 1rem;
  border: 1px solid var(--color-border);
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}

</style>