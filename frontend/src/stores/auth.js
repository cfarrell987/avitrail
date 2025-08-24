import { ref, computed } from 'vue'
import { ApiService } from '../services/api'
import { SessionManager } from '../utils/auth'

const apiService = new ApiService()

// Initialize from stored session
const storedSession = SessionManager.getSession()
const token = ref(storedSession?.token || null)
const user = ref(storedSession?.user || null)

// Set up API service with stored token
if (token.value) {
  apiService.setToken(token.value)
}

export function useAuthStore() {
  const isLoggedIn = computed(() => SessionManager.isSessionValid())

  const login = async (credentials) => {
    const response = await apiService.login(credentials)

    token.value = response.token
    user.value = response.user || null

    // Save session with expiry
    SessionManager.saveSession(response.token, user.value)
    apiService.setToken(response.token)
  }

  const register = async (userData) => {
    await apiService.register(userData)
  }

  const logout = () => {
    token.value = null
    user.value = null
    SessionManager.clearSession()
    apiService.clearToken()
  }

  const checkSession = () => {
    if (!SessionManager.isSessionValid()) {
      logout()
      return false
    }
    return true
  }

  const refreshSession = () => {
    SessionManager.refreshSession()
  }

  return {
    isLoggedIn,
    user: computed(() => SessionManager.getUser()),
    login,
    register,
    logout,
    checkSession,
    refreshSession
  }
}
