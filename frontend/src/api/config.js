// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000"

export const API_ENDPOINTS = {
  UPLOAD: `${API_BASE_URL}/upload`,
  CHAT: `${API_BASE_URL}/chat`,
  FILES: `${API_BASE_URL}/files`,
  DEBUG: `${API_BASE_URL}/debug`,
}

export default API_BASE_URL
