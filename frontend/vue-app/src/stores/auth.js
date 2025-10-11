import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, usersAPI } from '../services/api.js'
import axios from 'axios'
import { setAuthToken } from '../services/axiosConfig.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isInitialized = ref(false)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const isAdmin = computed(() => {
    if (!user.value) return false
    const adminRoles = ['MasterAdmin', 'AdminSPbU', 'AdminPOMI']
    return user.value.roles?.some(role => adminRoles.includes(role)) || false
  })

  const login = async (credentials) => {
    isLoading.value = true
    try {
      const response = await authAPI.login(credentials)
      setAuthToken(response.data.token)

      console.log('Login response:', response.data)
      
      const { token: authToken, user_info, roles } = response.data
      
      user.value = {
        ...user_info,
        roles: roles
      }
      token.value = authToken
      
      localStorage.setItem('auth_token', authToken)
      localStorage.setItem('user_data', JSON.stringify(user.value))
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`
      
      return response.data
    } catch (error) {
      console.error('Ошибка инициализации:', error)
      console.error('Статус ошибки:', error.response?.status)
      console.error('Данные ошибки:', error.response?.data)
      
      if (error.response?.status === 401 || error.response?.status === 403) {
        logout()
      }
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
        setAuthToken(savedToken)

        const response = await usersAPI.getUserInfo()
        user.value = {
          ...response.data.user_info,
          roles: response.data.roles
        }
        token.value = savedToken
        
        console.log('Успешная инициализация, пользователь:', user.value)
        console.log('Is admin:', isAdmin.value)
        localStorage.setItem('user_data', JSON.stringify(user.value))
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
    isAdmin,
    login,
    logout,
    initialize
  }
})