<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>Регистрация сотрудника</h1>
      </div>

      <form @submit.prevent="handleRegister" class="login-form">
        <div class="form-group">
          <label for="lastName">Фамилия *</label>
          <input
            id="lastName"
            v-model="registerData.last_name"
            type="text"
            required
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="firstName">Имя *</label>
          <input
            id="firstName"
            v-model="registerData.first_name"
            type="text"
            required
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="middleName">Отчество</label>
          <input
            id="middleName"
            v-model="registerData.middle_name"
            type="text"
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="username">Логин *</label>
          <input
            id="username"
            v-model="registerData.username"
            type="text"
            required
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="email">Email *</label>
          <input
            id="email"
            v-model="registerData.email"
            type="email"
            required
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="password">Пароль *</label>
          <input
            id="password"
            v-model="registerData.password"
            type="password"
            required
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="confirmPassword">Подтверждение пароля *</label>
          <input
            id="confirmPassword"
            v-model="registerData.confirmPassword"
            type="password"
            required
            :disabled="isLoading"
          >
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>

        <button 
          type="submit" 
          class="login-button"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>

        <div class="login-link">
          Уже есть аккаунт? <router-link to="/login">Войти</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../services/api.js'

const router = useRouter()

const registerData = reactive({
  last_name: '',
  first_name: '',
  middle_name: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const validateForm = () => {
  if (registerData.password !== registerData.confirmPassword) {
    errorMessage.value = 'Пароли не совпадают'
    return false
  }
  
  if (registerData.password.length < 6) {
    errorMessage.value = 'Пароль должен содержать минимум 6 символов'
    return false
  }
  
  return true
}

const handleRegister = async () => {
  if (!validateForm()) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authAPI.register(registerData)
    console.log('Registration success:', response.data)

    successMessage.value = 'Регистрация успешна! Вы будете перенаправлены на страницу входа.'
    
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (error) {
    console.error('Registration error:', error.response?.data)
    
    if (error.response?.status === 400) {
      const errorData = error.response.data
      
      if (errorData.error === 'Username already exists') {
        errorMessage.value = 'Пользователь с таким логином уже существует'
      } else if (errorData.error === 'Email already registered') {
        errorMessage.value = 'Пользователь с таким email уже существует'
      } else if (errorData.details) {
        errorMessage.value = `Ошибка валидации: ${JSON.stringify(errorData.details)}`
      } else if (errorData.error) {
        errorMessage.value = errorData.error
      } else {
        errorMessage.value = 'Неверные данные для регистрации'
      }
    } else {
      errorMessage.value = error.message || 'Ошибка при регистрации'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  padding: 20px;
}

.login-card {
  background-color: white;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
  border: 1px solid #e0e0e0;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  color: #2e7d32;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  color: #333;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.form-group input {
  padding: 8px 12px;
  border: 1px solid #ccc;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #2e7d32;
}

.form-group input:disabled {
  background-color: #f5f5f5;
}

.error-message {
  color: #d32f2f;
  padding: 4px 0;
  font-size: 0.9rem;
}

.success-message {
  color: #2e7d32;
  padding: 4px 0;
  font-size: 0.9rem;
}

.login-button {
  background-color: #2e7d32;
  color: white;
  padding: 10px;
  border: none;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 1rem;
}

.login-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.login-link a {
  color: #2e7d32;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>