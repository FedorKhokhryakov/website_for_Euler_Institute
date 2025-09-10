/*import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isInitialized = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  // TODO: добавить обработку входа, связать ее с бэком
  const login = async (credentials) => {
    try {
      // Отправляем POST запрос на эндпоинт бэкенда
      const response = await axios.post('/api/auth/login/', credentials)
      
      // Предполагаем, что бэкенд возвращает структуру:
      // { token: 'ваш_jwt_токен', user: { id: 1, username: 'user', ... } }
      const { token: authToken, user: userData } = response.data
      
      // Сохраняем данные
      user.value = userData
      token.value = authToken
      
      // Сохраняем токен в localStorage
      localStorage.setItem('auth_token', authToken)
      
      // Устанавливаем токен по умолчанию для всех последующих запросов
      axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
      
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('Неверный логин или пароль')
      } else if (error.response?.status === 400) {
        throw new Error('Некорректные данные')
      } else {
        throw new Error('Ошибка сервера. Попробуйте позже.')
      }
    }
  }

  const initialize = async () => {
    if (token.value) {
      try {
        const response = await fetch('/api/auth/user/', {
          headers: {
            'Authorization': `Bearer ${token.value}`
          }
        })
        if (response.ok) {
          user.value = await response.json()
        } else {
          logout()
        }
      } catch (error) {
        logout()
      }
    }
    isInitialized.value = true
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    delete axios.defaults.headers.common['Authorization']
  }

  return {
    user,
    token,
    isAuthenticated,
    isInitialized,
    login,
    logout,
    initialize
  }
})*/

// файл с заглушкой для постоянного входа
// stores/auth.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const isLoading = ref(false)

  const isAuthenticated = ref(false)

  // Заглушка для входа - всегда успешный вход
  const login = async (credentials) => {
    isLoading.value = true
    
    // Имитация задержки сети
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Создаем mock пользователя
    user.value = {
      id: 1,
      username: credentials.username,
      email: `${credentials.username}@institute.ru`,
      first_name: 'Имя',
      last_name: 'Фамилия',
      role: credentials.username === 'admin' ? 'admin' : 'user'
    }
    
    token.value = 'mock-token-' + Date.now()
    isAuthenticated.value = true
    
    // Сохраняем в localStorage для сохранения состояния при перезагрузке
    localStorage.setItem('auth_token', token.value)
    localStorage.setItem('user_data', JSON.stringify(user.value))
    
    // Устанавливаем заголовок для axios (если потом будете использовать)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    
    isLoading.value = false
    return { success: true }
  }

  // Выход из системы
  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    delete axios.defaults.headers.common['Authorization']
  }

  // Инициализация при загрузке приложения
  const initialize = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user_data')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
      isAuthenticated.value = true
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
    }
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    logout,
    initialize
  }
})