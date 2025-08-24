<template>
  <form @submit.prevent="handleSubmit">
    <div class="mb-3">
      <label class="form-label">Username</label>
      <input type="text" class="form-control" v-model="formData.username" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Email</label>
      <input type="email" class="form-control" v-model="formData.email" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Password</label>
      <input type="password" class="form-control" v-model="formData.password" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Confirm Password</label>
      <input type="password" class="form-control" v-model="formData.confirmPassword" required>
    </div>
    <button type="submit" class="btn btn-gradient text-white w-100" :disabled="loading">
      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
      Create Account
    </button>
  </form>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'RegisterForm',
  props: {
    loading: Boolean
  },
  emits: ['submit'],
  setup(props, { emit }) {
    const formData = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })

    const handleSubmit = () => {
      if (formData.value.password !== formData.value.confirmPassword) {
        emit('error', 'Passwords do not match')
        return
      }
      emit('submit', formData.value)
    }

    return { formData, handleSubmit }
  }
}
</script>
