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
    console.log('Начало инициализации auth store')
    const savedToken = localStorage.getItem('auth_token')
    
    console.log('Сохраненный токен:', savedToken)
    
    if (savedToken) {
      try {

        axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`

        const response = await authAPI.getUserProfile()
        user.value = response.data
        token.value = savedToken
        
        console.log('Успешная инициализация, пользователь:', response.data)
        localStorage.setItem('user_data', JSON.stringify(response.data))
      } catch (error) {
        console.error('Ошибка инициализации:', error)
        console.error('Статус ошибки:', error.response?.status)
        console.error('Данные ошибки:', error.response?.data)
        
        if (error.response?.status === 401 || error.response?.status === 403) {
          logout()
        }
      }
    } else {
      console.log('Токен не найден в localStorage')
    }
    isInitialized.value = true
    console.log('Инициализация завершена')
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
