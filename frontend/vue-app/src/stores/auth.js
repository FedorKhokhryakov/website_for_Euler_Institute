import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api.js'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isInitialized = ref(false)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await authAPI.login(credentials)

      console.log('Login response:', response.data)
      
      const { token: authToken, user: userData } = response.data
      
      user.value = userData
      token.value = authToken
      
      localStorage.setItem('auth_token', authToken)
      localStorage.setItem('user_data', JSON.stringify(userData))
      
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
    } finally {
      isLoading.value = false
    }
  }

  const register = async (userData) => {
    isLoading.value = true
    
    try {
      const response = await authAPI.register(userData)
      
      if (response.data) {
        return { 
          success: true, 
          message: 'Регистрация успешна',
          user: response.data
        }
      }
      
      return { success: true, message: 'Регистрация успешна' }
      
    } catch (error) {
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const initialize = async () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user_data')
    
    if (savedToken) {
      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
        
        const response = await authAPI.getUserProfile()
        user.value = response.data
        
        localStorage.setItem('user_data', JSON.stringify(response.data))
      } catch (error) {
        console.error('Ошибка инициализации:', error)
        logout()
      }
    }
    isInitialized.value = true
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    delete axios.defaults.headers.common['Authorization']
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    isInitialized,
    register,
    login,
    logout,
    initialize
  }
})

// файл с заглушкой для постоянного входа
// stores/auth.js
/*import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const isLoading = ref(false)
  const isAuthenticated = ref(false)

  const login = async (credentials) => {
    isLoading.value = true
    
    await new Promise(resolve => setTimeout(resolve, 1000))
    
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
    
    localStorage.setItem('auth_token', token.value)
    localStorage.setItem('user_data', JSON.stringify(user.value))
    
    // Устанавливаем заголовок для axios
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    
    isLoading.value = false
    return { success: true }
  }

  const logout = () => {
    user.value = null
    token.value = null
    isAuthenticated.value = false
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    delete axios.defaults.headers.common['Authorization']
  }

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
})*/