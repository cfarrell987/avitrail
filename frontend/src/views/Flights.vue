<template>
  <div class="dashboard">
    <Navbar @logout="logout" />

    <div class="container py-4">
      <div class="row mb-4">
        <div class="col">
          <h2 class="mb-4">My Flights</h2>
          <button class="btn btn-gradient text-white" @click="showAddFlightModal = true">
            <i class="fas fa-plus me-2"></i>Add Flight
          </button>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <div v-if="flights.length === 0" class="text-center py-5">
            <i class="fas fa-plane fa-3x text-muted mb-3"></i>
            <h4 class="text-muted">No flights logged yet</h4>
            <p class="text-muted">Start tracking your journeys by adding your first flight!</p>
          </div>

          <FlightCard
            v-for="flight in flights"
            :key="flight.id"
            :flight="flight"
          />
        </div>
      </div>
    </div>

    <AddFlightModal
      :show="showAddFlightModal"
      @close="showAddFlightModal = false"
      @submit="addFlight"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/layout/Navbar.vue'
import FlightCard from '../components/flights/FlightCard.vue'
import AddFlightModal from '../components/flights/AddFlightModal.vue'
import { useAuthStore } from '../stores/auth'
import { useFlightStore } from '../stores/flights'

export default {
  name: 'Flights',
  components: {
    Navbar,
    FlightCard,
    AddFlightModal
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const flightStore = useFlightStore()

    const showAddFlightModal = ref(false)

    const logout = () => {
      authStore.logout()
      flightStore.clearFlights()
      router.push('/')
    }

    const addFlight = async (flightData) => {
      try {
        await flightStore.addFlight(flightData)
        showAddFlightModal.value = false
      } catch (err) {
        console.error('Failed to add flight:', err)
      }
    }

    onMounted(() => {
      flightStore.loadFlights()
    })

    return {
      showAddFlightModal,
      flights: flightStore.flights,
      logout,
      addFlight
    }
  }
}
</script>
