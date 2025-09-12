import apiClient from './axiosConfig' // Импортируем настроенный клиент

const API_BASE_URL = 'http://127.0.0.1:8000'

export const authAPI = {
  login: (credentials) => apiClient.post('/api/auth/login/', credentials),
  register: (userData) => apiClient.post('/api/auth/register/', {
    username: userData.username,
    email: userData.email,
    password: userData.password,
    first_name: userData.first_name,
    last_name: userData.last_name,
    middle_name: userData.middle_name || ''
  }),
  getUserProfile: () => apiClient.get('/api/auth/user/'),
}

export const publicationsAPI = {
  getAll: () => apiClient.get('/api/all_publications/'),
  getUserAll: () => apiClient.get('/api/my_publications/'),
  getById: (id) => apiClient.get(`/api/publications/${id}/`),
  create: (data) => apiClient.post('/api/publications/', data),
  checkOwner: (id) => apiClient.get(`/api/publications/${id}/check-owner/`),
}

export const usersAPI = {
  getById: (id) => apiClient.get(`/api/users/${id}/`),
  getAll: () => apiClient.get('/api/users/')
}

export const reportsAPI = {
  //generate: (reportData) => apiClient.post('/api/reports/', reportData),
  getAll: () => apiClient.get('/api/reports/'),
  download_report_api: (data) => apiClient.post(`/api/reports/download/`, data, {
    responseType: 'blob'
  })
}