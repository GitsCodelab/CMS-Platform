import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Oracle DB API
export const oracleAPI = {
  getAll: () => apiClient.get('/oracle/test'),
  getById: (id) => apiClient.get(`/oracle/test/${id}`),
  create: (data) => apiClient.post('/oracle/test', data),
  update: (id, data) => apiClient.put(`/oracle/test/${id}`, data),
  delete: (id) => apiClient.delete(`/oracle/test/${id}`),
}

// PostgreSQL API
export const postgresAPI = {
  getAll: () => apiClient.get('/postgres/test'),
  getById: (id) => apiClient.get(`/postgres/test/${id}`),
  create: (data) => apiClient.post('/postgres/test', data),
  update: (id, data) => apiClient.put(`/postgres/test/${id}`, data),
  delete: (id) => apiClient.delete(`/postgres/test/${id}`),
}

export default apiClient
