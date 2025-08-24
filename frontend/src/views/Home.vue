<template>
  <div class="hero-section">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-lg-6">
          <h1 class="display-4 fw-bold mb-4">
            <i class="fas fa-plane"></i> AviTrail
          </h1>
          <p class="lead mb-4">Track your flights, visualize your journeys, and explore the world one flight at a time.</p>
          <div class="d-flex gap-3 mb-4">
            <div class="text-center">
              <i class="fas fa-map-marked-alt fa-2x mb-2"></i>
              <p class="small">Interactive Maps</p>
            </div>
            <div class="text-center">
              <i class="fas fa-chart-line fa-2x mb-2"></i>
              <p class="small">Flight Statistics</p>
            </div>
            <div class="text-center">
              <i class="fas fa-history fa-2x mb-2"></i>
              <p class="small">Flight History</p>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="card auth-card">
            <div class="card-body p-4">
              <ul class="nav nav-tabs nav-justified mb-4">
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: authMode === 'login' }"
                     href="#" @click.prevent="authMode = 'login'">Login</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: authMode === 'register' }"
                     href="#" @click.prevent="authMode = 'register'">Register</a>
                </li>
              </ul>

              <LoginForm
                v-if="authMode === 'login'"
                :loading="loading"
                @submit="login"
              />

              <RegisterForm
                v-if="authMode === 'register'"
                :loading="loading"
                @submit="register"
                @error="handleError"
              />

              <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from '../components/auth/LoginForm.vue'
import RegisterForm from '../components/auth/RegistrationForm.vue'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Home',
  components: {
    LoginForm,
    RegisterForm
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const authMode = ref('login')
    const loading = ref(false)
    const error = ref('')

    const login = async (credentials) => {
      loading.value = true
      error.value = ''

      try {
        await authStore.login(credentials)
        router.push('/dashboard')
      } catch (err) {
        error.value = 'Invalid credentials. Please try again.'
      } finally {
        loading.value = false
      }
    }

    const register = async (userData) => {
      loading.value = true
      error.value = ''

      try {
        await authStore.register(userData)
        authMode.value = 'login'
        error.value = ''
      } catch (err) {
        error.value = 'Registration failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    const handleError = (errorMessage) => {
      error.value = errorMessage
    }

    return {
      authMode,
      loading,
      error,
      login,
      register,
      handleError
    }
  }
}
</script>
