import { ApiService } from './api'

const apiService = new ApiService()
let airportsCache = null

export class AirportService {
  async getAllAirports() {
    if (airportsCache) return airportsCache

    try {
      airportsCache = await apiService.getAirports()
      return airportsCache
    } catch (error) {
      console.error('Failed to load airports:', error)
      return []
    }
  }

  async searchAirports(query) {
    const airports = await this.getAllAirports()
    return airports.filter(airport =>
      airport.ICAO.toLowerCase().includes(query.toLowerCase()) ||
      airport.IATA?.toLowerCase().includes(query.toLowerCase()) ||
      airport.name.toLowerCase().includes(query.toLowerCase()) ||
      airport.city?.toLowerCase().includes(query.toLowerCase())
    )
  }

  async getAirportByCode(code) {
    const airports = await this.getAllAirports()
    return airports.find(airport =>
        airport === code ||
      airport.ICAO === code.toUpperCase() ||
      airport.IATA === code.toUpperCase()
    )
  }
}
