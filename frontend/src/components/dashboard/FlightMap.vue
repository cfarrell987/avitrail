<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="card-title mb-0">
        <i class="fas fa-map me-2"></i>Flight Map
      </h5>
      <button class="btn btn-outline-primary btn-sm" @click="$emit('add-real-flight')">
        <i class="fas fa-plus me-1"></i>Add Flight
      </button>
    </div>
    <div class="card-body p-0">
      <div class="map-container">
        <div ref="mapContainer" style="height: 500px; width: 100%;"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import { AirportService } from '../../services/airports'

export default {
  name: 'FlightMap',
  props: {
    flights: Array
  },
  emits: ['add-sample-flight', 'add-real-flight'],
  setup(props, { emit }) {
    const mapContainer = ref(null)
    const airportService = new AirportService()
    let map = null
    let flightPaths = []
    let airportCache = new Map()

    const initMap = () => {
      if (!mapContainer.value || map) return

      map = L.map(mapContainer.value).setView([20, 0], 2)

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map)

      updateFlightPaths()
    }

    const getAirportCoords = async (airportCode) => {
      if (airportCache.has(airportCode)) {
        return airportCache.get(airportCode)
      }

      try {
        const airport = await airportService.getAirportByCode(airportCode)
        if (airport && airport.lat && airport.lon) {
          const coords = [airport.lat, airport.lon]
          airportCache.set(airportCode, coords)
          return coords
        }
      } catch (error) {
        console.warn(`Airport ${airportCode} not found`)
      }

      return null
    }

    const updateFlightPaths = async () => {
      if (!map || !props.flights) return

      // Clear existing paths
      flightPaths.forEach(path => map.removeLayer(path))
      flightPaths = []

      // Add real flight paths
      for (const flight of props.flights) {
        let depCoords, arrCoords

        // Handle airport objects vs airport codes
        if (typeof flight.departure_airport === 'object') {
          depCoords = flight.departure_airport.lat && flight.departure_airport.lon
            ? [flight.departure_airport.lat, flight.departure_airport.lon]
            : await getAirportCoords(flight.departure_airport.ICAO)
        } else {
          depCoords = await getAirportCoords(flight.departure_airport)
        }

        if (typeof flight.arrival_airport === 'object') {
          arrCoords = flight.arrival_airport.lat && flight.arrival_airport.lon
            ? [flight.arrival_airport.lat, flight.arrival_airport.lon]
            : await getAirportCoords(flight.arrival_airport.ICAO)
        } else {
          arrCoords = await getAirportCoords(flight.arrival_airport)
        }

        if (depCoords && arrCoords) {
          const depName = flight.departure_airport.ICAO || flight.departure_airport
          const arrName = flight.arrival_airport.ICAO || flight.arrival_airport
          const label = `${flight.flight_number}: ${depName} → ${arrName}`
          addFlightPath(depCoords, arrCoords, label, flight)
        }
      }
    }

    const addFlightPath = (from, to, label, flight) => {
      if (!map) return

      // Create smooth curved path with multiple points
      const curvePoints = createCurvedPath(from, to)

      const path = L.polyline(curvePoints, {
        color: '#667eea',
        weight: 3,
        opacity: 0.8,
        smoothFactor: 2
      }).addTo(map)

      // Departure marker
      L.circleMarker(from, {
        radius: 6,
        color: '#667eea',
        fillColor: '#667eea',
        fillOpacity: 0.8
      }).addTo(map).bindPopup(`
        <div>
          <strong>Departure: ${flight.departure_airport.name || flight.departure_airport.ICAO || flight.departure_airport}</strong><br>
          ${flight.departure_airport.city ? flight.departure_airport.city + '<br>' : ''}
          ${new Date(flight.departure_time).toLocaleString()}
        </div>
      `)

      // Arrival marker
      L.circleMarker(to, {
        radius: 6,
        color: '#764ba2',
        fillColor: '#764ba2',
        fillOpacity: 0.8
      }).addTo(map).bindPopup(`
        <div>
          <strong>Arrival: ${flight.arrival_airport.name || flight.arrival_airport.ICAO || flight.arrival_airport}</strong><br>
          ${flight.arrival_airport.city ? flight.arrival_airport.city + '<br>' : ''}
          ${new Date(flight.arrival_time).toLocaleString()}
        </div>
      `)

      // Flight path popup
      path.bindPopup(`
        <div>
          <strong>${label}</strong><br>
          Duration: ${Math.floor(flight.duration / 60)}h ${flight.duration % 60}m<br>
          Distance: ${flight.distance || 'N/A'} km<br>
          Aircraft: ${flight.aircraft || 'N/A'}
        </div>
      `)

      flightPaths.push(path)
    }

    const calculateDistance = (point1, point2) => {
      const lat1 = point1[0] * Math.PI / 180
      const lat2 = point2[0] * Math.PI / 180
      const deltaLat = (point2[0] - point1[0]) * Math.PI / 180
      const deltaLng = (point2[1] - point1[1]) * Math.PI / 180

      const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
              Math.cos(lat1) * Math.cos(lat2) *
              Math.sin(deltaLng/2) * Math.sin(deltaLng/2)
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))

      return 6371 * c
    }

    const createCurvedPath = (from, to) => {
      const points = []
      const numPoints = 300

      for (let i = 0; i <= numPoints; i++) {
        const t = i / numPoints

        const lat1 = from[0]
        const lng1 = from[1]
        const lat2 = to[0]
        const lng2 = to[1]

        // Much subtler curve - only slight arc
        const midLat = (lat1 + lat2) / 2
        const midLng = (lng1 + lng2) / 2
        const distance = calculateDistance(from, to)
        const curveHeight = Math.min(distance / 50, 8) // Much smaller curve

        const controlLat = midLat + curveHeight
        const controlLng = midLng

        // Bézier curve calculation
        const lat = (1-t)*(1-t)*lat1 + 2*(1-t)*t*controlLat + t*t*lat2
        const lng = (1-t)*(1-t)*lng1 + 2*(1-t)*t*controlLng + t*t*lng2

        points.push([lat, lng])
      }

      return points
    }

    onMounted(() => {
      initMap()
    })

    onUnmounted(() => {
      if (map) {
        map.remove()
      }
    })

    watch(() => props.flights, updateFlightPaths, { deep: true })

    return {
      mapContainer
    }
  }
}
</script>
