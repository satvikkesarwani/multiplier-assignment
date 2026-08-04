import axios from 'axios'

// Create axios instance pointing to FastAPI backend
// Using Vite proxy in dev — no hardcoded backend URL needed
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Automatically attach JWT token to every request if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth API calls
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
}

// Preview API calls
export const previewAPI = {
  create: (url) => api.post('/previews/', { url }),
  list: () => api.get('/previews/'),
}

export default api
