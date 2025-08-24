<template>
  <div v-if="show" class="modal d-block" style="background: rgba(0,0,0,0.5)">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add Flight</h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">Flight Number</label>
                <input type="text" class="form-control" v-model="flightData.flight_number" required>
              </div>
              <div class="col-md-6">
                <label class="form-label">Airline</label>
                <div class="position-relative">
                  <input
                      type="text"
                      class="form-control"
                      v-model="airlineSearch"
                      @input="searchAirlines"
                      placeholder="Search airline..."
                      required
                  >
                  <div v-if="airlineResults.length" class="dropdown-menu show position-absolute w-100" style="max-height: 200px; overflow-y: auto;">
                    <button
                        type="button"
                        class="dropdown-item"
                        v-for="airline in airlineResults"
                        :key="airline.id"
                        @click="selectAirline(airline)"
                    >
                      {{ airline.IATA }} - {{ airline.name }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">Departure Airport</label>
                <div class="position-relative">
                  <input
                      type="text"
                      class="form-control"
                      v-model="departureSearch"
                      @input="searchDepartureAirports"
                      placeholder="Search departure airport..."
                      required
                  >
                  <div v-if="departureResults.length" class="dropdown-menu show position-absolute w-100" style="max-height: 200px; overflow-y: auto;">
                    <button
                        type="button"
                        class="dropdown-item"
                        v-for="airport in departureResults"
                        :key="airport.id"
                        @click="selectDepartureAirport(airport)"
                    >
                      {{ airport.IATA || airport.ICAO }} - {{ airport.name }}, {{ airport.city }}
                    </button>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label">Arrival Airport</label>
                <div class="position-relative">
                  <input
                      type="text"
                      class="form-control"
                      v-model="arrivalSearch"
                      @input="searchArrivalAirports"
                      placeholder="Search arrival airport..."
                      required
                  >
                  <div v-if="arrivalResults.length" class="dropdown-menu show position-absolute w-100" style="max-height: 200px; overflow-y: auto;">
                    <button
                        type="button"
                        class="dropdown-item"
                        v-for="airport in arrivalResults"
                        :key="airport.id"
                        @click="selectArrivalAirport(airport)"
                    >
                      {{ airport.IATA || airport.ICAO }} - {{ airport.name }}, {{ airport.city }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6">
                <label class="form-label">Departure Time</label>
                <input
                    type="datetime-local"
                    class="form-control"
                    v-model="flightData.departure_time"
                    @change="calculateDuration"
                    required
                >
              </div>
              <div class="col-md-6">
                <label class="form-label">Arrival Time</label>
                <input
                    type="datetime-local"
                    class="form-control"
                    v-model="flightData.arrival_time"
                    @change="calculateDuration"
                    required
                >
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-4">
                <label class="form-label">Duration (minutes)</label>
                <input type="number" class="form-control" v-model="flightData.duration" readonly>
              </div>
              <div class="col-md-4">
                <label class="form-label">Aircraft</label>
                <input type="text" class="form-control" v-model="flightData.aircraft">
              </div>
              <div class="col-md-4">
                <label class="form-label">Tail Number</label>
                <input type="text" class="form-control" v-model="flightData.tail_number">
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancel</button>
          <button type="button" class="btn btn-gradient text-white" @click="handleSubmit" :disabled="!isFormValid">
            Add Flight
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { AirportService } from '../../services/airports'
import { AirlineService } from '../../services/airlines'
import { debounce } from '../../utils/helpers'

export default {
  name: 'AddFlightModal',
  props: {
    show: Boolean
  },
  emits: ['close', 'submit'],
  setup(props, { emit }) {
    const airportService = new AirportService()
    const airlineService = new AirlineService()

    const flightData = ref({
      flight_number: '',
      departure_time: '',
      arrival_time: '',
      aircraft: '',
      distance: 0,
      duration: 0,
      tail_number: '',
      departure_airport_id: null,
      arrival_airport_id: null,
      airline_id: null
    })

    const airlineSearch = ref('')
    const departureSearch = ref('')
    const arrivalSearch = ref('')

    const airlineResults = ref([])
    const departureResults = ref([])
    const arrivalResults = ref([])

    const selectedAirline = ref(null)
    const selectedDepartureAirport = ref(null)
    const selectedArrivalAirport = ref(null)

    const searchAirlines = debounce(async () => {
      if (airlineSearch.value.length < 2) {
        airlineResults.value = []
        return
      }

      try {
        const results = await airlineService.searchAirlines(airlineSearch.value)
        airlineResults.value = results.sort((a, b) => a.name.localeCompare(b.name))
      } catch (error) {
        console.error('Failed to search airlines:', error)
      }
    }, 300)

    const searchDepartureAirports = debounce(async () => {
      if (departureSearch.value.length < 2) {
        departureResults.value = []
        return
      }

      try {
        const results = await airportService.searchAirports(departureSearch.value)
        departureResults.value = results.sort((a, b) => a.name.localeCompare(b.name))
      } catch (error) {
        console.error('Failed to search airports:', error)
      }
    }, 300)

    const searchArrivalAirports = debounce(async () => {
      if (arrivalSearch.value.length < 2) {
        arrivalResults.value = []
        return
      }

      try {
        const results = await airportService.searchAirports(arrivalSearch.value)
        arrivalResults.value = results.sort((a, b) => a.name.localeCompare(b.name))
      } catch (error) {
        console.error('Failed to search airports:', error)
      }
    }, 300)

    const selectAirline = (airline) => {
      selectedAirline.value = airline
      flightData.value.airline_id = airline.id
      airlineSearch.value = `${airline.IATA} - ${airline.name}`
      airlineResults.value = []
    }

    const selectDepartureAirport = (airport) => {
      selectedDepartureAirport.value = airport
      flightData.value.departure_airport_id = airport.id
      departureSearch.value = `${airport.IATA || airport.ICAO} - ${airport.name}`
      departureResults.value = []
      calculateDistance()
    }

    const selectArrivalAirport = (airport) => {
      selectedArrivalAirport.value = airport
      flightData.value.arrival_airport_id = airport.id
      arrivalSearch.value = `${airport.IATA || airport.ICAO} - ${airport.name}`
      arrivalResults.value = []
      calculateDistance()
    }

    const calculateDuration = () => {
      if (flightData.value.departure_time && flightData.value.arrival_time &&
          selectedDepartureAirport.value && selectedArrivalAirport.value) {

        const depTime = flightData.value.departure_time
        const arrTime = flightData.value.arrival_time
        const depTz = selectedDepartureAirport.value.timezone
        const arrTz = selectedArrivalAirport.value.timezone

        if (!depTz || !arrTz) {
          const departure = new Date(depTime)
          const arrival = new Date(arrTime)
          flightData.value.duration = Math.floor((arrival - departure) / 60000)
          return
        }

        try {
          // Treat input times as local times in respective timezones
          const depUTC = convertToUTC(depTime, depTz)
          const arrUTC = convertToUTC(arrTime, arrTz)

          flightData.value.duration = Math.floor((arrUTC - depUTC) / 60000)
        } catch (error) {
          const departure = new Date(depTime)
          const arrival = new Date(arrTime)
          flightData.value.duration = Math.floor((arrival - arrival) / 60000)
        }
      }
    }

    const convertToUTC = (localTime, timezone) => {
      // Create date assuming it's in the specified timezone
      const date = new Date(localTime)
      const utcTime = date.getTime() + (date.getTimezoneOffset() * 60000)

      // Get offset for the target timezone
      const tempDate = new Date()
      const utcDate = new Date(tempDate.toLocaleString('en-US', { timeZone: 'UTC' }))
      const tzDate = new Date(tempDate.toLocaleString('en-US', { timeZone: timezone }))
      const tzOffset = utcDate.getTime() - tzDate.getTime()

      return utcTime + tzOffset
    }

    const calculateDistance = () => {
      if (selectedDepartureAirport.value && selectedArrivalAirport.value) {
        const dep = selectedDepartureAirport.value
        const arr = selectedArrivalAirport.value

        if (dep.lat && dep.lon && arr.lat && arr.lon) {
          const R = 6371 // Earth's radius in km
          const dLat = (arr.lat - dep.lat) * Math.PI / 180
          const dLon = (arr.lon - dep.lon) * Math.PI / 180
          const a =
              Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(dep.lat * Math.PI / 180) * Math.cos(arr.lat * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2)
          const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
          flightData.value.distance = Math.round(R * c)
        }
      }
    }

    const isFormValid = computed(() => {
      return flightData.value.flight_number &&
          flightData.value.departure_time &&
          flightData.value.arrival_time &&
          flightData.value.departure_airport_id &&
          flightData.value.arrival_airport_id &&
          flightData.value.airline_id
    })

    const handleSubmit = () => {
      if (isFormValid.value) {
        emit('submit', { ...flightData.value })
        resetForm()
      }
    }

    const resetForm = () => {
      flightData.value = {
        flight_number: '',
        departure_time: '',
        arrival_time: '',
        aircraft: '',
        distance: 0,
        duration: 0,
        tail_number: '',
        departure_airport_id: null,
        arrival_airport_id: null,
        airline_id: null
      }

      airlineSearch.value = ''
      departureSearch.value = ''
      arrivalSearch.value = ''

      airlineResults.value = []
      departureResults.value = []
      arrivalResults.value = []

      selectedAirline.value = null
      selectedDepartureAirport.value = null
      selectedArrivalAirport.value = null
    }

    watch(() => props.show, (newVal) => {
      if (!newVal) resetForm()
    })

    return {
      flightData,
      airlineSearch,
      departureSearch,
      arrivalSearch,
      airlineResults,
      departureResults,
      arrivalResults,
      isFormValid,
      searchAirlines,
      searchDepartureAirports,
      searchArrivalAirports,
      selectAirline,
      selectDepartureAirport,
      selectArrivalAirport,
      calculateDuration,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.dropdown-menu {
  z-index: 1050;
}
</style>
