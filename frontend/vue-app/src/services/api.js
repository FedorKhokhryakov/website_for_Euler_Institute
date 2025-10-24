import apiClient from './axiosConfig'

export const authAPI = {
  login: (credentials) => apiClient.post('/api/auth/login/', credentials),
  impersonateStart: (data) => apiClient.post('/api/impersonate/start/', data),
  impersonateStop: (data) => apiClient.post('/api/impersonate/stop/', data),
  impersonateStatus: () => apiClient.get('/api/impersonate/status/'),
}

export const publicationsAPI = {
  getYearReport: (year) => apiClient.get(`/api/get_year_report/${year}/`),
  createPost: (data) => apiClient.post('/api/create_post/', data),
  getPostInformation: (post_id) => apiClient.get(`/api/get_post_information/${post_id}/`),
  updatePost: (id, data) => apiClient.put(`/api/update_post/${id}/`, data),
  deletePost: (id) => apiClient.delete(`/api/delete_post/${id}/`),

  sendReportOnChecking: (year, data) => apiClient.post(`/api/get_science_report_on_checking/${year}/`, data),
}

export const usersAPI = {
  getUserInfo: () => apiClient.get('/api/get_user_info/'),
  updateUser: (id, data) => apiClient.put(`/api/update_user/${id}/`, data),
  deleteUser: (id) => apiClient.delete(`/api/delete_user/${id}/`),
  getAllUsers: () => apiClient.get(`/api/get_all_users/`),
}

export const adminAPI = {
  setReportNewStatus: (user_id, year, data) => apiClient.post(`/api/set_science_report_new_status/${user_id}/${year}/`, data),
  getDBInfo: (data) => apiClient.post('/api/get_db_info/', data),
  getDBInfoBlob: (data) => apiClient.post('/api/get_db_info/', data, { responseType: 'blob' }),
  createUser: (data) => apiClient.post('/api/create_user/', data),
}
