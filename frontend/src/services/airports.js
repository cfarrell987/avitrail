import { ApiService } from './api'

const apiService = new ApiService()

export class AirportService {
  async searchAirports(query) {
    if (!query || query.length < 2) return []
    const response = await apiService.getAirports({ search: query })
    return response.results
  }

  async getAirportByCode(code) {
    if (!code) return null
    const response = await apiService.getAirports({ search: code })
    const upperCode = code.toUpperCase()
    return (
      response.results.find(
        airport => airport.ICAO === upperCode || airport.IATA === upperCode
      ) || null
    )
  }
}
