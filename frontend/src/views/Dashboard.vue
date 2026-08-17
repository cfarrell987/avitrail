<template>
  <div class="dashboard">
    <Navbar @logout="logout" />

    <div class="container py-4">
      <div class="row mb-4">
        <div class="col">
          <h2 class="mb-4">Flight Dashboard</h2>
        </div>
      </div>

      <StatsCards :flights="flights" />

      <div class="row mb-4">
        <div class="col-12">
          <FlightMap
            :flights="flights"
            @add-real-flight="openAddFlightModal"
          />
        </div>
      </div>
    </div>

    <AddFlightModal
      :show="showAddFlightModal"
      :error="addFlightError"
      @close="showAddFlightModal = false"
      @submit="addFlight"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/layout/Navbar.vue'
import StatsCards from '../components/dashboard/StatsCards.vue'
import FlightMap from '../components/dashboard/FlightMap.vue'
import AddFlightModal from '../components/flights/AddFlightModal.vue'
import { useAuthStore } from '../stores/auth'
import { useFlightStore } from '../stores/flights'

export default {
  name: 'Dashboard',
  components: {
    Navbar,
    StatsCards,
    FlightMap,
    AddFlightModal
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const flightStore = useFlightStore()
    const showAddFlightModal = ref(false)
    const addFlightError = ref('')

    const logout = () => {
      authStore.logout()
      flightStore.clearFlights()
      router.push('/')
    }

    const openAddFlightModal = () => {
      addFlightError.value = ''
      showAddFlightModal.value = true
    }

    const addFlight = async (flightData) => {
      try {
        await flightStore.addFlight(flightData)
        addFlightError.value = ''
        showAddFlightModal.value = false
      } catch (err) {
        addFlightError.value = err.message
      }
    }

    onMounted(() => {
      flightStore.loadFlights()
    })

    return {
      flights: flightStore.flights,
      showAddFlightModal,
      addFlightError,
      logout,
      openAddFlightModal,
      addFlight
    }
  }
}
</script>
