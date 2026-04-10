/**
 * API utility functions
 * Environment variables:
 * - VITE_API_BASE_URL: Backend API URL (default: http://localhost:5000 for local dev)
 * - VITE_API_TOKEN: Bearer token for API authentication
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'unified-identity-portal-secret-token-change-in-production'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    // Ensure token is in header
    if (!config.headers['Authorization']) {
      config.headers['Authorization'] = `Bearer ${API_TOKEN}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Authentication failed')
      // Could redirect to login or show error
    }
    return Promise.reject(error)
  }
)

export default api
export { API_TOKEN, API_BASE_URL }

