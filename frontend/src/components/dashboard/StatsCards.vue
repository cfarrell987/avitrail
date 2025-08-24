<template>
  <div class="row mb-4">
    <div class="col-md-3 mb-3" v-for="stat in computedStats" :key="stat.title">
      <div class="stats-card p-4 text-center">
        <i :class="`fas ${stat.icon} ${stat.color} fa-2x mb-3`"></i>
        <h3 class="h4 mb-2">{{ stat.value }}</h3>
        <p class="text-muted mb-0">{{ stat.title }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'StatsCards',
  props: {
    flights: { type: Array, default: () => [] }
  },
  setup(props) {
    const computedStats = computed(() => {
      if (!props.flights || props.flights.length === 0) {
        return [
          { title: 'Total Flights', value: 0, icon: 'fa-plane', color: 'text-primary' },
          { title: 'Miles Traveled', value: '0', icon: 'fa-globe', color: 'text-success' },
          { title: 'Countries Visited', value: 0, icon: 'fa-map-marker-alt', color: 'text-warning' },
          { title: 'Flight Hours', value: '0h', icon: 'fa-clock', color: 'text-info' }
        ]
      }

      const totalFlights = props.flights.length

      const totalMinutes = props.flights.reduce((sum, flight) =>
        sum + (flight.duration || 0), 0
      )
      const totalHours = Math.floor(totalMinutes / 60)
      const remainingMinutes = totalMinutes % 60
      const flightHoursDisplay = remainingMinutes > 0
        ? `${totalHours}h ${remainingMinutes}m`
        : `${totalHours}h`

      const totalDistance = props.flights.reduce((sum, flight) =>
        sum + (flight.distance || 0), 0
      )
      const distanceDisplay = totalDistance > 0
        ? totalDistance.toLocaleString() + ' km'
        : '0 km'

      // Get unique countries from airports
      const countries = new Set()
      props.flights.forEach(flight => {
        if (flight.departure_airport?.country) {
          countries.add(flight.departure_airport.country)
        }
        if (flight.arrival_airport?.country) {
          countries.add(flight.arrival_airport.country)
        }
      })

      return [
        {
          title: 'Total Flights',
          value: totalFlights,
          icon: 'fa-plane',
          color: 'text-primary'
        },
        {
          title: 'Distance Traveled',
          value: distanceDisplay,
          icon: 'fa-globe',
          color: 'text-success'
        },
        {
          title: 'Countries Visited',
          value: countries.size,
          icon: 'fa-map-marker-alt',
          color: 'text-warning'
        },
        {
          title: 'Flight Time',
          value: flightHoursDisplay,
          icon: 'fa-clock',
          color: 'text-info'
        }
      ]
    })

    return {
      computedStats
    }
  }
}
</script>
