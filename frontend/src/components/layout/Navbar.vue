<template>
  <nav class="navbar navbar-expand-lg navbar-dark navbar-custom">
    <div class="container">
      <router-link to="/dashboard" class="navbar-brand fw-bold">
        <i class="fas fa-plane me-2"></i>AviTrail
      </router-link>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link to="/dashboard" class="nav-link" active-class="active">
              <i class="fas fa-tachometer-alt me-1"></i>Dashboard
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/flights" class="nav-link" active-class="active">
              <i class="fas fa-plane me-1"></i>My Flights
            </router-link>
          </li>
        </ul>
        <ul class="navbar-nav">
          <li class="nav-item">
            <a class="nav-link" href="#" @click.prevent="$emit('logout')">
              <i class="fas fa-sign-out-alt me-1"></i>Logout
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'Navbar',
  props: {
    currentView: String
  },
  emits: ['navigate', 'logout']
}
</script>
