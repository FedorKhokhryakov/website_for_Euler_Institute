import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

apiClient.interceptors.request.use(
  (config) => {
    if (config.url.includes('/api/auth/login/')) {
      return config
    }
    
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      const isImpersonating = localStorage.getItem('is_impersonating')
      const contextToken = localStorage.getItem('context_token')
      
      if (isImpersonating && contextToken) {
        console.warn('Сессия имперсонализации истекла, возвращаемся к оригинальному пользователю')
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
        localStorage.removeItem('context_token')
        localStorage.removeItem('is_impersonating')
        window.location.href = '/login'
      } else {
        localStorage.removeItem('authToken')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('authToken', token)
  } else {
    localStorage.removeItem('authToken')
  }
}

export const getAuthToken = () => {
  return localStorage.getItem('authToken')
}

export default apiClient