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
  const isImpersonating = ref(false)
  const impersonator = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  const isAdmin = computed(() => {
    if (!user.value) return false
    const adminRoles = ['MasterAdmin', 'SPbUAdmin', 'POMIAdmin']
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
        setAuthToken(savedToken)

        const statusResponse = await authAPI.impersonateStatus()
        if (statusResponse.data.is_impersonating) {
          isImpersonating.value = true
          impersonator.value = statusResponse.data.impersonator
        }

        const response = await usersAPI.getUserInfo()
        user.value = {
          ...response.data.user_info,
          roles: response.data.roles
        }
        token.value = savedToken

        console.log('Initialized user roles:', response.data.roles)
        
        console.log('Успешная инициализация, пользователь:', user.value)
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

  const startImpersonation = async (targetUserId) => {
    try {
      const response = await authAPI.impersonateStart({ user_id: targetUserId })
      
      const { token: newToken, user_info, roles, impersonator: impersonatorData } = response.data

      console.log('Impersonation response roles:', roles)
      
      localStorage.setItem('context_token', response.data.context_token)
      
      setAuthToken(newToken)
      user.value = {
        ...user_info,
        roles: roles
      }
      token.value = newToken
      isImpersonating.value = true
      impersonator.value = impersonatorData
      
      localStorage.setItem('auth_token', newToken)
      localStorage.setItem('user_data', JSON.stringify(user.value))
      localStorage.setItem('is_impersonating', 'true')
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
      
      return response.data
    } catch (error) {
      console.error('Ошибка имперсонализации:', error)
      throw error
    }
  }

  const stopImpersonation = async () => {
    try {
      const contextToken = localStorage.getItem('context_token')
      if (!contextToken) {
        throw new Error('Контекстный токен не найден')
      }

      const response = await authAPI.impersonateStop({ context_token: contextToken })
      
      const { token: originalToken, user_info, roles } = response.data
      
      setAuthToken(originalToken)
      user.value = {
        ...user_info,
        roles: roles
      }
      token.value = originalToken
      isImpersonating.value = false
      impersonator.value = null
      
      localStorage.setItem('auth_token', originalToken)
      localStorage.setItem('user_data', JSON.stringify(user.value))
      localStorage.removeItem('context_token')
      localStorage.removeItem('is_impersonating')
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${originalToken}`
      
      return response.data
    } catch (error) {
      console.error('Ошибка завершения имперсонализации:', error)
      throw error
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    isImpersonating.value = false
    impersonator.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    localStorage.removeItem('context_token')
    localStorage.removeItem('is_impersonating')
    delete axios.defaults.headers.common['Authorization']
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    isInitialized,
    isAdmin,
    isImpersonating,
    impersonator,
    login,
    logout,
    initialize,
    startImpersonation,
    stopImpersonation
  }
})