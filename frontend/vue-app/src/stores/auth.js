import { defineStore } from "pinia"
import { ref } from 'vue'

export const useAuthStore = defineStore("auth", () => {
  const token = ref('')
  const user = ref(null)

  const initialize = async () => {
    try {
      const savedToken = localStorage.getItem('token')
      if (savedToken) {
        token.value = savedToken
        await fetchUserData()
      }
    } catch (error) {
      console.error('Initialization error:', error)
    }
    
  }

  const fetchUserData = async () => {
    if (!token.value) return

    try {
      const response = await axios.get('http://localhost:8000/api/user/', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
      user.value = response.fetchUserData
    } catch (error) {
      console.error("Failed to fetch user data:", error)
      clearToken()
    }
  }

  const setToken = async (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)

    await fetchUserData()
  }

  const clearToken = () => {
    token.value = ''
    localStorage.removeItem('token')
    user.value = null
  }

  const isAuthenticated = () => {
    return !!token.value && !!user.value
  }

  return { token, 
    user,
    initialize,
    setToken, 
    clearToken, 
    isAuthenticated,
    fetchUserData }
})

