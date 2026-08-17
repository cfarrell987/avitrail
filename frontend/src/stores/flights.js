import { ref } from 'vue'
import { ApiService } from '../services/api'

const apiService = new ApiService()
const flights = ref([])

const extractErrorMessage = (error) => {
  const data = error.response?.data
  if (data && typeof data === 'object') {
    const messages = Object.values(data).flat()
    if (messages.length) return messages.join(' ')
  }
  return 'Failed to add flight. Please try again.'
}

export function useFlightStore() {
  const loadFlights = async () => {
    try {
      // The API paginates flights, so walk every page and flatten into one list.
      let allFlights = []
      let nextUrl = undefined

      do {
        const page = await apiService.getFlights(nextUrl)
        allFlights = allFlights.concat(page.results)
        nextUrl = page.next
      } while (nextUrl)

      flights.value = allFlights
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
      // Rethrow with a readable message instead of silently faking success —
      // a rejected flight (e.g. a closed airport/airline, see backend
      // validation) must not appear to have been added.
      throw new Error(extractErrorMessage(error))
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
