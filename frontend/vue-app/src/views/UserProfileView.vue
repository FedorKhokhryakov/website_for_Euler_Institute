<template>
  <div class="user-profile">
    <div class="profile-header">
      <h1>Профиль сотрудника</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="userData" class="profile-content">
      <div class="profile-main">
        <div class="info-container">
          <div class="section-title">ФИО на русском</div>
          <div class="info-row triple-fields">
            <div class="field-group">
              <label class="info-label">Фамилия</label>
              <input 
                class="info-input"
                v-model="formData.second_name_rus"
              >
            </div>
            <div class="field-group">
              <label class="info-label">Имя</label>
              <input 
                class="info-input"
                v-model="formData.first_name_rus"
              >
            </div>
            <div class="field-group">
              <label class="info-label">Отчество</label>
              <input 
                class="info-input"
                v-model="formData.middle_name_rus"
              >
            </div>
          </div>

          <div class="section-title">ФИО на английском</div>
          <div class="info-row triple-fields">
            <div class="field-group">
              <label class="info-label">Фамилия</label>
              <input 
                class="info-input"
                v-model="formData.second_name_eng"
              >
            </div>
            <div class="field-group">
              <label class="info-label">Имя</label>
              <input 
                class="info-input"
                v-model="formData.first_name_eng"
              >
            </div>
            <div class="field-group">
              <label class="info-label">Отчество</label>
              <input 
                class="info-input"
                v-model="formData.middle_name_eng"
              >
            </div>
          </div>

          <div class="info-row">
            <label class="info-label">Email</label>
            <input 
              class="info-input"
              v-model="formData.email"
            >
          </div>
          
          <div class="info-row">
            <label class="info-label">Год рождения</label>
            <input 
              class="info-input"
              v-model="formData.year_of_birth"
            >
          </div>
          
          <div class="info-row">
            <label class="info-label">Год окончания вуза</label>
            <input 
              class="info-input"
              v-model="formData.year_of_graduation"
            >
          </div>
          
          <div class="info-row">
            <label class="info-label">Ученая степень</label>
            <input 
              class="info-input"
              v-model="formData.academic_degree"
            >
          </div>
          
          <div class="info-row">
            <label class="info-label">Год получения степени</label>
            <input 
              class="info-input"
              v-model="formData.year_of_degree"
            >
          </div>
          
          <div class="info-row">
            <label class="info-label">Должность</label>
            <input 
              class="info-input"
              v-model="formData.position"
            >
          </div>
        </div>
      </div>

      <div class="save-section">
        <button 
          class="save-button" 
          @click="saveUserData"
          :disabled="saving"
        >
          {{ saving ? 'Сохранение...' : 'Сохранить' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { usersAPI } from '../services/api.js'

const userData = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)

const formData = reactive({
  second_name_rus: '',
  first_name_rus: '',
  middle_name_rus: '',
  second_name_eng: '',
  first_name_eng: '',
  middle_name_eng: '',
  email: '',
  year_of_birth: null,
  year_of_graduation: null,
  academic_degree: '',
  year_of_degree: null,
  position: ''
})

const loadUserData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await usersAPI.getUserInfo()
    userData.value = response.data

    console.log(userData.value);
    
    Object.assign(formData, userData.value.user_info)
    
  } catch (err) {
    console.error('Ошибка загрузки данных пользователя:', err)
    if (err.response?.status === 404) {
      error.value = 'Пользователь не найден'
    } else if (err.response?.status === 401) {
      error.value = 'Требуется авторизация'
    } else if (err.response?.status === 403) {
      error.value = 'Недостаточно прав для просмотра'
    } else {
      error.value = 'Не удалось загрузить данные пользователя'
    }
  } finally {
    loading.value = false
  }
}

const saveUserData = async () => {
  try {
    saving.value = true
    error.value = ''

    const updateData = { ...formData }

    const numericFields = ['year_of_birth', 'year_of_graduation', 'year_of_degree']
    numericFields.forEach(field => {
      if (updateData[field] === '' || updateData[field] === null) {
        updateData[field] = null
      } else {
        updateData[field] = parseInt(updateData[field])
      }
    })

    await usersAPI.updateUser(userData.value.user_info.id, updateData)
    
    alert('Данные успешно сохранены!')
    
  } catch (err) {
    console.error('Ошибка сохранения данных:', err)
    if (err.response?.status === 400) {
      error.value = 'Ошибка валидации данных: ' + JSON.stringify(err.response.data)
    } else if (err.response?.status === 403) {
      error.value = 'Недостаточно прав для изменения данных'
    } else {
      error.value = 'Не удалось сохранить данные пользователя'
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.user-profile {
  padding: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.profile-header {
  margin-bottom: 1.5rem;
}

.profile-header h1 {
  color: var(--color-primary);
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.error-state {
  color: var(--color-secondary);
}

.profile-main {
  display: flex;
  align-items: flex-start;
}

.info-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--color-primary);
}

.info-row {
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
}

.info-row.triple-fields {
  flex-direction: row;
  gap: 0.5rem;
}

.field-group {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.info-label {
  font-weight: 600;
  color: var(--color-primary);
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.info-input {
  color: var(--color-text-primary);
  font-size: 1rem;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-background);
  outline: none;
  width: 100%;
}

.info-input:focus {
  border-color: var(--color-primary);
}

/* Стили для секции сохранения */
.save-section {
  margin-top: 2rem;
  padding: 1rem;
  display: flex;
  justify-content: center;
}

.save-button {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  padding: 0.75rem 2rem;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.save-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.save-button:disabled {
  background-color: var(--color-text-secondary);
  cursor: not-allowed;
}
</style>