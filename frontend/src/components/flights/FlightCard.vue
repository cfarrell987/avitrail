<template>
  <div class="flight-card card mb-3">
    <div class="card-body">
      <div class="row align-items-center">
        <div class="col-md-8">
          <h5 class="card-title">{{ flight.flight_number }}</h5>
          <p class="card-text">
            <strong>{{ departureDisplay }}</strong>
            <i class="fas fa-arrow-right mx-2"></i>
            <strong>{{ arrivalDisplay }}</strong>
          </p>
          <small class="text-muted">
            {{ formatDate(flight.departure_time) }} • {{ airlineDisplay }}
          </small>
        </div>
        <div class="col-md-4 text-end">
          <span class="badge bg-primary">{{ formatDuration(flight.duration) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FlightCard',
  props: {
    flight: Object
  },
  computed: {
    departureDisplay() {
      const dep = this.flight.departure_airport
      return typeof dep === 'object' ? (dep.IATA || dep.ICAO) : dep
    },
    arrivalDisplay() {
      const arr = this.flight.arrival_airport
      return typeof arr === 'object' ? (arr.IATA || arr.ICAO) : arr
    },
    airlineDisplay() {
      const airline = this.flight.airline
      return typeof airline === 'object' ? airline.name : airline
    }
  },
  methods: {
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    formatDuration(minutes) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
    }
  }
}
</script>
