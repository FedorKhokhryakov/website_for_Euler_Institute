import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'

export const authAPI = {
  login: (credentials) => axios.post(`${API_BASE_URL}/api/auth/login/`, credentials),
  register: (userData) => axios.post(`${API_BASE_URL}/api/auth/register/`, {
    username: userData.username,
    email: userData.email,
    password: userData.password,
    first_name: userData.first_name,
    last_name: userData.last_name,
    middle_name: userData.middle_name || ''
  }),
  getUserProfile: () => axios.get(`${API_BASE_URL}/api/auth/user/`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    }
  }),
}

export const publicationsAPI = {
  getAll: () => axios.get(`${API_BASE_URL}/api/my_publications/`),
  getById: (id) => axios.get(`${API_BASE_URL}/api/publications/${id}/`),
  create: (data) => axios.post(`${API_BASE_URL}/api/publications/`, data),
  checkOwner: (id) => axios.get(`${API_BASE_URL}/api/publications/${id}/check-owner/`),
}

export const usersAPI = {
  getById: (id) => axios.get(`${API_BASE_URL}/api/users/${id}/`),
}