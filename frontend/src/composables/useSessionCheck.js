import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { SessionManager } from '../utils/auth'

export function useSessionCheck(intervalMinutes = 5) {
  const authStore = useAuthStore()
  let intervalId = null

  onMounted(() => {
    intervalId = setInterval(() => {
      if (!SessionManager.isSessionValid()) {
        authStore.logout()
      } else {
        // Refresh session timestamp on activity
        authStore.refreshSession()
      }
    }, intervalMinutes * 60 * 1000)
  })

  onUnmounted(() => {
    if (intervalId) {
      clearInterval(intervalId)
    }
  })

  return {
    checkSession: () => authStore.checkSession()
  }
}
