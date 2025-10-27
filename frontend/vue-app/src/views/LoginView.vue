<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>Вход в систему</h1>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Логин</label>
          <input
            id="username"
            v-model="loginData.username"
            type="text"
            required
            :disabled="isLoading"
          >
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <input
            id="password"
            v-model="loginData.password"
            type="password"
            required
            :disabled="isLoading"
          >
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button 
          type="submit" 
          class="login-button"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Вход...' : 'Войти' }}
        </button>

        <div class="register-link">
          Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginData = reactive({
  username: '',
  password: ''
})

const isLoading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    await authStore.login(loginData)
    router.push('/dashboard')
  } catch (error) {
    if (error.response?.status === 400 || error.response?.status === 401) {
      errorMessage.value = 'Неверный логин или пароль'
    } else if (error.response?.status === 500) {
      errorMessage.value = 'Ошибка сервера. Попробуйте позже'
    } else if (error.message?.includes('Network Error')) {
      errorMessage.value = 'Нет соединения с сервером'
    } else {
      errorMessage.value = 'Произошла ошибка при входе'
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

.register-link {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.register-link a {
  color: #2e7d32;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>