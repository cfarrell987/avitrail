import axios from 'axios'
import { SessionManager } from '../utils/auth'

const API_BASE = 'http://localhost:8000/api'

export class ApiService {
  constructor() {
    this.setupAxios()
    this.setupInterceptors()
  }

  setupAxios() {
    axios.defaults.baseURL = API_BASE
    const token = SessionManager.getToken()
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
    }
  }

  setupInterceptors() {
    // Request interceptor to check session validity
    axios.interceptors.request.use((config) => {
      const token = SessionManager.getToken()
      if (token) {
        config.headers.Authorization = `Token ${token}`
      } else {
        delete config.headers.Authorization
      }
      return config
    })

    // Response interceptor to handle token expiry
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          SessionManager.clearSession()
          window.location.href = '/'
        }
        return Promise.reject(error)
      }
    )
  }

  setToken(token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
  }

  clearToken() {
    delete axios.defaults.headers.common['Authorization']
  }

  // Auth endpoints
  async login(credentials) {
    const response = await axios.post('/auth/', credentials)
    return response.data
  }

  async register(userData) {
    const response = await axios.post('/auth/register/', userData)
    return response.data
  }

  // Flight endpoints
  async getFlights() {
    const response = await axios.get('/flights/flights/')
    return response.data
  }

  async createFlight(flightData) {
    const response = await axios.post('/flights/flights/', flightData)
    return response.data
  }

  // Airport endpoints
  async getAirports() {
    const response = await axios.get('/airports/airports/')
    return response.data
  }

  // Airline endpoints
  async getAirlines() {
    const response = await axios.get('/airlines/airlines/')
    return response.data
  }
}
