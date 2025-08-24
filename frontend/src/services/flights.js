import { ApiService } from './api'

const apiService = new ApiService()

export class FlightService {
  async getAllFlights() {
    return await apiService.getFlights()
  }

  async createFlight(flightData) {
    // Calculate duration if not provided
    if (flightData.departure_time && flightData.arrival_time && !flightData.duration) {
      const departure = new Date(flightData.departure_time)
      const arrival = new Date(flightData.arrival_time)
      flightData.duration = Math.floor((arrival - departure) / 60000) // minutes
    }

    return await apiService.createFlight(flightData)
  }

  async updateFlight(id, flightData) {
    const response = await apiService.updateFlight(id, flightData)
    return response.data
  }

  async deleteFlight(id) {
    const response = await apiService.deleteFlight(id)
    return response.data
  }
}
