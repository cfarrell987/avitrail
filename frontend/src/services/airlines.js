import { ApiService } from './api'

const apiService = new ApiService()

export class AirlineService {
  async getAllAirlines() {
    return await apiService.getAirlines()
  }

  async searchAirlines(query) {
    const airlines = await this.getAllAirlines()
    return airlines.filter(airline =>
      airline.ICAO?.toLowerCase().includes(query.toLowerCase()) ||
      airline.IATA?.toLowerCase().includes(query.toLowerCase()) ||
      airline.name.toLowerCase().includes(query.toLowerCase())
    )
  }

  async getAirlineByCode(code) {
    const airlines = await this.getAllAirlines()
    return airlines.find(airline =>
      airline.ICAO === code.toUpperCase() ||
      airline.IATA === code.toUpperCase()
    )
  }
}
