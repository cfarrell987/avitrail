import { ref } from 'vue'
import { ApiService } from '../services/api'

const apiService = new ApiService()
const flights = ref([])

export function useFlightStore() {
  const loadFlights = async () => {
    try {
      flights.value = await apiService.getFlights()
    } catch (error) {
      console.error('Failed to load flights:', error)
      // Use sample data for demo
      flights.value = [
        {
          id: 1,
          flight_number: 'UA123',
          departure_airport: 'LAX',
          arrival_airport: 'JFK',
          departure_time: '2024-01-15T10:00:00',
          airline: 'United',
          duration: 320
        },
        {
          id: 2,
          flight_number: 'DL456',
          departure_airport: 'JFK',
          arrival_airport: 'LHR',
          departure_time: '2024-01-20T14:30:00',
          airline: 'Delta',
          duration: 420
        }
      ]
    }
  }

  const addFlight = async (flightData) => {
    try {
      const flight = await apiService.createFlight(flightData)
      flights.value.push(flight)
    } catch (error) {
      console.error('Failed to add flight:', error)
      // Demo: Add flight locally
      const newFlight = {
        ...flightData,
        id: Date.now()
      }
      flights.value.push(newFlight)
    }
  }

  const addSampleFlight = () => {
    const sampleFlight = {
      id: Date.now(),
      flight_number: 'AA' + Math.floor(Math.random() * 1000),
      departure_airport: 'NYC',
      arrival_airport: 'LAX',
      departure_time: new Date().toISOString(),
      airline: 'American',
      duration: 360
    }
    flights.value.push(sampleFlight)
  }

  const clearFlights = () => {
    flights.value = []
  }

  return {
    flights,
    loadFlights,
    addFlight,
    addSampleFlight,
    clearFlights
  }
}
