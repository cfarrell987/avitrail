import { ApiService } from './api'

const apiService = new ApiService()

export class AirlineService {
  async searchAirlines(query) {
    if (!query || query.length < 2) return []
    const response = await apiService.getAirlines({ search: query })
    return response.results
  }

  async getAirlineByCode(code) {
    if (!code) return null
    const response = await apiService.getAirlines({ search: code })
    const upperCode = code.toUpperCase()
    return (
      response.results.find(
        airline => airline.ICAO === upperCode || airline.IATA === upperCode
      ) || null
    )
  }
}
