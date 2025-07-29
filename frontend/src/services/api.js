import axios from "axios"
import { API_ENDPOINTS } from "../api/config"

// Create axios instance with default config
const api = axios.create({
  timeout: 30000, // 30 seconds timeout
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error("❌ Request Error:", error)
    return Promise.reject(error)
  },
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error("❌ Response Error:", error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  },
)

// API service functions
export const apiService = {
  // Upload file
  uploadFile: async (file) => {
    const formData = new FormData()
    formData.append("file", file)

    console.log(`📤 Uploading file: ${file.name} (${file.size} bytes)`)

    const response = await api.post(API_ENDPOINTS.UPLOAD, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        console.log(`📊 Upload progress: ${progress}%`)
      },
    })

    return response.data
  },

  // Send chat message
  sendMessage: async (message) => {
    console.log(`💬 Sending message: ${message}`)

    const response = await api.post(API_ENDPOINTS.CHAT, {
      message: message,
    })

    return response.data
  },

  // Get uploaded files
  getFiles: async () => {
    console.log("📁 Fetching uploaded files...")

    const response = await api.get(API_ENDPOINTS.FILES)
    return response.data
  },

  // Debug endpoint
  debug: async () => {
    console.log("🔍 Calling debug endpoint...")

    const response = await api.get(API_ENDPOINTS.DEBUG)
    return response.data
  },

  // Test connection
  testConnection: async () => {
    try {
      console.log("🔗 Testing backend connection...")
      const response = await api.get(API_ENDPOINTS.DEBUG)
      console.log("✅ Backend connection successful")
      return { success: true, data: response.data }
    } catch (error) {
      console.error("❌ Backend connection failed:", error.message)
      return { success: false, error: error.message }
    }
  },
}

export default api
