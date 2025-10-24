<template>
  <div class="user-profile">
    <div class="profile-header">
      <h1>Создать пользователя</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <p>Создание пользователя...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>

    <div v-else class="profile-content">
      <div class="profile-main">
        <div class="info-container">
          <div class="section-title">Учётные данные *</div>
          
          <div class="info-row">
            <label class="info-label">Логин *</label>
            <input 
              class="info-input"
              v-model="formData.login"
              placeholder="Введите логин"
              :class="{ 'error-input': fieldErrors.login }"
            >
            <span v-if="fieldErrors.login" class="error-text">{{ fieldErrors.login }}</span>
          </div>
          
          <div class="info-row">
            <label class="info-label">Пароль *</label>
            <div class="password-wrapper">
              <input 
                class="info-input"
                :type="showPassword ? 'text' : 'password'"
                v-model="formData.password"
                placeholder="Введите пароль"
                :class="{ 'error-input': fieldErrors.password }"
              >
              <div class="password-buttons">
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  {{ showPassword ? '🔓' : '🔒' }}
                </button>
                <button type="button" class="generate-password" @click="generatePassword">
                  Сгенерировать
                </button>
              </div>
            </div>
            <span v-if="fieldErrors.password" class="error-text">{{ fieldErrors.password }}</span>
          </div>

          <div class="section-title">ФИО на русском *</div>
          <div class="info-row triple-fields">
            <div class="field-group">
              <label class="info-label">Фамилия *</label>
              <input 
                class="info-input"
                v-model="formData.second_name_rus"
                placeholder="Введите фамилию"
                :class="{ 'error-input': fieldErrors.second_name_rus }"
              >
              <span v-if="fieldErrors.second_name_rus" class="error-text">{{ fieldErrors.second_name_rus }}</span>
            </div>
            <div class="field-group">
              <label class="info-label">Имя *</label>
              <input 
                class="info-input"
                v-model="formData.first_name_rus"
                placeholder="Введите имя"
                :class="{ 'error-input': fieldErrors.first_name_rus }"
              >
              <span v-if="fieldErrors.first_name_rus" class="error-text">{{ fieldErrors.first_name_rus }}</span>
            </div>
            <div class="field-group">
              <label class="info-label">Отчество</label>
              <input 
                class="info-input"
                v-model="formData.middle_name_rus"
                placeholder="Введите отчество"
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
                placeholder="Введите фамилию"
              >
            </div>
            <div class="field-group">
              <label class="info-label">Имя</label>
              <input 
                class="info-input"
                v-model="formData.first_name_eng"
                placeholder="Введите имя"
              >
            </div>
            <div class="field-group">
              <label class="info-label">Отчество</label>
              <input 
                class="info-input"
                v-model="formData.middle_name_eng"
                placeholder="Введите отчество"
              >
            </div>
          </div>

          <div class="info-row">
            <label class="info-label">Email</label>
            <input 
              class="info-input"
              v-model="formData.email"
              placeholder="Введите email"
              type="email"
            >
          </div>

          <div v-if="isMasterAdmin" class="section-title admin-title">Назначенные роли</div>
          <div v-if="isMasterAdmin" class="info-row roles-section">
            <div class="roles-checkbox-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="selectedRoles"
                  value="SPbUUser"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                Сотрудник СПбГУ
              </label>
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="selectedRoles"
                  value="POMIUser"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                Сотрудник ПОМИ
              </label>
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="selectedRoles"
                  value="SPbUAdmin"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                Администратор СПбГУ
              </label>
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="selectedRoles"
                  value="POMIAdmin"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                Администратор ПОМИ
              </label>
            </div>
          </div>

          <div v-if="!isMasterAdmin" class="info-row">
            <div class="auto-role-info">
              <p>Будет назначена роль: {{ autoAssignedRole }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="save-section">
        <button 
          class="save-button" 
          @click="createUser"
          :disabled="loading"
        >
          {{ loading ? 'Создание...' : 'Создать пользователя' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { adminAPI } from '../../services/api.js'

const authStore = useAuthStore()

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const selectedRoles = ref([])

const userRoles = computed(() => authStore.user?.roles || [])
const isMasterAdmin = computed(() => userRoles.value.includes('MasterAdmin'))
const isSPbUAdmin = computed(() => userRoles.value.includes('SPbUAdmin'))
const isPOMIAdmin = computed(() => userRoles.value.includes('POMIAdmin'))

const autoAssignedRole = computed(() => {
  if (isSPbUAdmin.value) return 'SPbUUser'
  if (isPOMIAdmin.value) return 'POMIUser'
  return ''
})

const formData = reactive({
  login: '',
  password: '',
  second_name_rus: '',
  first_name_rus: '',
  middle_name_rus: '',
  second_name_eng: '',
  first_name_eng: '',
  middle_name_eng: '',
  email: '',
  roles: []
})

const fieldErrors = reactive({
  login: '',
  password: '',
  second_name_rus: '',
  first_name_rus: ''
})

const validateForm = () => {
  let isValid = true
  
  Object.keys(fieldErrors).forEach(key => fieldErrors[key] = '')
  
  if (!formData.login.trim()) {
    fieldErrors.login = 'Логин обязателен для заполнения'
    isValid = false
  }
  
  if (!formData.password) {
    fieldErrors.password = 'Пароль обязателен для заполнения'
    isValid = false
  } else if (formData.password.length < 6) {
    fieldErrors.password = 'Пароль должен содержать не менее 6 символов'
    isValid = false
  }
  
  if (!formData.second_name_rus.trim()) {
    fieldErrors.second_name_rus = 'Фамилия обязательна для заполнения'
    isValid = false
  }
  
  if (!formData.first_name_rus.trim()) {
    fieldErrors.first_name_rus = 'Имя обязательно для заполнения'
    isValid = false
  }
  
  return isValid
}

const generatePassword = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
  let password = ''
  for (let i = 0; i < 12; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  formData.password = password
  showPassword.value = true
}

const createUser = async () => {
  if (!validateForm()) {
    return
  }

  try {
    loading.value = true
    error.value = ''

    const userData = {
      login: formData.login,
      password: formData.password,
      second_name_rus: formData.second_name_rus,
      first_name_rus: formData.first_name_rus,
      roles: isMasterAdmin.value ? selectedRoles.value : [autoAssignedRole.value]
    }

    if (formData.middle_name_rus.trim()) {
      userData.middle_name_rus = formData.middle_name_rus
    }
    if (formData.second_name_eng.trim()) {
      userData.second_name_eng = formData.second_name_eng
    }
    if (formData.first_name_eng.trim()) {
      userData.first_name_eng = formData.first_name_eng
    }
    if (formData.middle_name_eng.trim()) {
      userData.middle_name_eng = formData.middle_name_eng
    }
    if (formData.email.trim()) {
      userData.email = formData.email
    }

    const response = await adminAPI.createUser(userData)
    
    alert(`Пользователь успешно создан! ID: ${response.data.user_id}`)
    
    resetForm()
    
  } catch (err) {
    if (err.response?.data?.error) {
      error.value = err.response.data.error
      if (err.response.data.details) {
        const details = err.response.data.details
        Object.keys(details).forEach(field => {
          if (fieldErrors[field] !== undefined) {
            fieldErrors[field] = Array.isArray(details[field]) ? details[field].join(', ') : details[field]
          }
        })
        console.log(details)
      }
    } else {
      error.value = 'Не удалось создать пользователя'
    }
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.keys(formData).forEach(key => {
    if (key !== 'roles') {
      formData[key] = ''
    }
  })
  selectedRoles.value = []
  Object.keys(fieldErrors).forEach(key => fieldErrors[key] = '')
  showPassword.value = false
}

onMounted(() => {
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

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-buttons {
  position: absolute;
  right: 0.5rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.toggle-password {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0.25rem;
}

.generate-password {
  background-color: var(--color-primary);
  color: var(--color-text-light);
  border: none;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  cursor: pointer;
}

.generate-password:hover {
  background-color: var(--color-primary-dark);
}

.error-text {
  color: var(--color-secondary);
  font-size: 0.85rem;
  margin-top: 0.25rem;
  display: block;
}

.error-input {
  border-color: var(--color-secondary);
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
  color: var(--color-secondary);
  border-bottom-color: var(--color-secondary);
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

.roles-section {
  background-color: var(--color-surface);
  padding: 1rem;
}

.roles-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 1.2rem;
  height: 1.2rem;
  border: 2px solid var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox-input:checked + .checkbox-custom {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  color: var(--color-text-light);
  font-size: 0.8rem;
  font-weight: bold;
}

.auto-role-info {
  background-color: var(--color-surface);
  padding: 0.75rem;
}

.auto-role-info p {
  margin: 0;
  color: var(--color-primary);
  font-weight: 500;
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
</style>