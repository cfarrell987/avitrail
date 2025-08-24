<template>
  <form @submit.prevent="$emit('submit', formData)">
    <div class="mb-3">
      <label class="form-label">Username</label>
      <input type="text" class="form-control" v-model="formData.username" required>
    </div>
    <div class="mb-3">
      <label class="form-label">Password</label>
      <input type="password" class="form-control" v-model="formData.password" required>
    </div>
    <button type="submit" class="btn btn-gradient text-white w-100" :disabled="loading">
      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
      Sign In
    </button>
  </form>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'LoginForm',
  props: {
    loading: Boolean
  },
  emits: ['submit'],
  setup() {
    const formData = ref({
      username: '',
      password: ''
    })

    return { formData }
  }
}
</script>
