import apiClient from './axiosConfig'

const jsonRequest = (method, url, data = null) => {
  return apiClient({method, url, data,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

const formDataRequest = (method, url, data) => {
  return apiClient({method, url, data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

const blobRequest = (method, url, data = null) => {
  return apiClient({method, url, data,
    responseType: 'blob',
    headers: data ? { 'Content-Type': 'application/json' } : {}
  })
}

export const authAPI = {
  login: (credentials) => jsonRequest('post', '/api/auth/login/', credentials),
  impersonateStart: (data) => jsonRequest('post', '/api/impersonate/start/', data),
  impersonateStop: (data) => jsonRequest('post', '/api/impersonate/stop/', data),
  impersonateStatus: () => jsonRequest('get', '/api/impersonate/status/'),
}

export const publicationsAPI = {
  getYearReport: (year) => jsonRequest('get', `/api/get_year_report/${year}/`),
  createPost: (data) => formDataRequest('post', '/api/create_post/', data),
  getPostInformation: (post_id) => jsonRequest('get', `/api/get_post_information/${post_id}/`),
  updatePost: (id, data) => formDataRequest('put', `/api/update_post/${id}/`, data),
  deletePost: (id) => jsonRequest('delete', `/api/delete_post/${id}/`),
  downloadPublicationFile: (post_id, file_type) => 
    apiClient.get(`/api/publications/${post_id}/download_file/`, {
      params: { filetype: file_type },
      responseType: 'blob',
      headers: {}
    }),
  deletePublicationFile: (post_id, file_type) => 
    apiClient.delete(`/api/publications/${post_id}/delete_file/`, {
      headers: {'Content-Type': 'application/json'},
      params: { filetype: file_type }
    })
}

export const usersAPI = {
  getUserInfo: () => jsonRequest('get', '/api/get_user_info/'),
  updateUser: (id, data) => jsonRequest('put', `/api/update_user/${id}/`, data),
  deleteUser: (id) => jsonRequest('delete', `/api/delete_user/${id}/`),
  getAllUsers: () => jsonRequest('get', '/api/get_all_users/'),
}

export const reportAPI = {
  saveReport: (year, data) => jsonRequest('post', `/api/save_report/${year}/`, data),
  signReport: (year, data) => jsonRequest('post', `/api/sign_report/${year}/`, data)
}

export const adminAPI = {
  sendReportToRework: (user_id, year, data) => jsonRequest('post', `/api/send_to_rework/${user_id}/${year}/`, data),
  getDBInfo: (data) => blobRequest('post', '/api/get_db_info/', data),
  createUser: (data) => jsonRequest('post', '/api/create_user/', data),
}