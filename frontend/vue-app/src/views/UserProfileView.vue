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

          <div class="section-title">Учётные данные</div>
          <div class="info-row">
            <label class="info-label">Логин</label>
            <input 
              class="info-input"
              v-model="loginForm.username"
              placeholder="Введите логин"
            >
          </div>
          <div class="info-row">
            <label class="info-label">Новый пароль</label>
            <div class="password-wrapper">
              <input 
                class="info-input"
                :type="showPassword ? 'text' : 'password'"
                v-model="loginForm.password"
                placeholder="Введите новый пароль"
              >
              <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                {{ showPassword ? '🔓' : '🔒' }}
              </button>
            </div>
            <span v-if="passwordError" class="error-text">{{ passwordError }}</span>
          </div>

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

          <div v-if="isImpersonating">
            <div class="section-title">Административные поля</div>
            <div class="info-row">
              <label class="info-label">Номер договора</label>
              <input 
                class="info-input"
                v-model="adminFormData.contract_number"
                placeholder="Введите номер договора"
              >
            </div>
            <div class="info-row">
              <label class="info-label">Договор</label>
              <div class="file-upload-section">
                <input 
                  type="file"
                  ref="contractFileInput"
                  class="file-input"
                  @change="handleContractFile"
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                >
                <button 
                  class="file-upload-button"
                  @click="triggerFileInput"
                >
                  📎 Выбрать файл
                </button>
                <span v-if="adminFormData.contract_file" class="file-name">
                  {{ adminFormData.contract_file.name }}
                </span>
                <span v-else class="file-placeholder">
                  Файл не выбран
                </span>
              </div>
            </div>
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
import { usersAPI } from '../services/api.js'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const isImpersonating = ref(authStore.isImpersonating)

const userData = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const passwordError = ref('')
const showPassword = ref(false)
const contractFileInput = ref(null)

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

const loginForm = reactive({
  username: '',
  password: ''
})

const adminFormData = reactive({
  contract_number: '',
  contract_file: null
})

const loadUserData = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await usersAPI.getUserInfo()
    userData.value = response.data
    Object.assign(formData, userData.value.user_info)
    loginForm.username = userData.value.user_info.username
    
    if (userData.value.admin_info && isImpersonating.value) {
      Object.assign(adminFormData, userData.value.admin_info)
    }
  } catch (err) {
    error.value = 'Ошибка загрузки данных пользователя'
  } finally {
    loading.value = false
  }
}

const saveUserData = async () => {
  try {
    saving.value = true
    error.value = ''
    passwordError.value = ''
    const updateData = { ...formData, username: loginForm.username }

    if (loginForm.password.trim() !== '') {
      if (loginForm.password.length < 6) {
        passwordError.value = 'Пароль должен содержать не менее 6 символов'
        return
      }
      updateData.password = loginForm.password
    }

    const numericFields = ['year_of_birth', 'year_of_graduation', 'year_of_degree']
    numericFields.forEach(field => {
      updateData[field] = updateData[field] ? parseInt(updateData[field]) : null
    })

    await usersAPI.updateUser(userData.value.user_info.id, updateData)
    alert('Данные успешно сохранены!')
  } catch (err) {
    if (err.response?.status === 400) {
      if (err.response.data?.password) {
        passwordError.value = 'Ошибка пароля: ' + err.response.data.password.join(', ')
      } else {
        error.value = 'Ошибка валидации данных'
      }
    } else {
      error.value = 'Не удалось сохранить данные пользователя'
    }
  } finally {
    saving.value = false
  }
}

const triggerFileInput = () => contractFileInput.value?.click()

const handleContractFile = (event) => {
  const file = event.target.files[0]
  if (file) adminFormData.contract_file = file
}

onMounted(() => loadUserData())
</script>

<style scoped>
.user-profile {
  padding: 1rem;
  max-width: 900px;
  margin: 0 auto;
  background-color: var(--color-surface)
}

.profile-header {
  margin-bottom: 1.5rem;
  position: relative;
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

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.toggle-password {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
}

.error-text {
  color: var(--color-secondary);
  font-size: 0.85rem;
  margin-top: 0.25rem;
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

.admin-title {
  color: #dc3545;
  border-bottom-color: #dc3545;
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

.file-upload-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.file-input {
  display: none;
}

.file-upload-button {
  background-color: #6c757d;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
}

.file-upload-button:hover {
  background-color: #5a6268;
}

.file-name {
  color: var(--color-primary);
  font-weight: 500;
}

.file-placeholder {
  color: var(--color-text-secondary);
  font-style: italic;
}

.file-hint {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}

.save-section {
  margin-top: 2rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
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

.admin-save-button {
  background-color: #dc3545;
  color: white;
  padding: 0.75rem 2rem;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.admin-save-button:hover:not(:disabled) {
  background-color: #c82333;
}

.admin-save-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>