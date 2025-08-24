export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

export const validatePassword = (password) => {
  return password && password.length >= 8
}

export const validateFlightNumber = (flightNumber) => {
  const re = /^[A-Z]{2,3}[0-9]{1,4}$/i
  return re.test(flightNumber)
}

export const validateAirportCode = (code) => {
  const re = /^[A-Z]{3,4}$/i
  return re.test(code)
}

export const validateDateTime = (dateTime) => {
  if (!dateTime) return false
  const date = new Date(dateTime)
  return date instanceof Date && !isNaN(date)
}

export const validateFlight = (flight) => {
  const errors = {}

  if (!flight.flight_number || !validateFlightNumber(flight.flight_number)) {
    errors.flight_number = 'Please enter a valid flight number (e.g., AA123)'
  }

  if (!flight.departure_airport || !validateAirportCode(flight.departure_airport)) {
    errors.departure_airport = 'Please enter a valid airport code (3-4 letters)'
  }

  if (!flight.arrival_airport || !validateAirportCode(flight.arrival_airport)) {
    errors.arrival_airport = 'Please enter a valid airport code (3-4 letters)'
  }

  if (!flight.departure_time || !validateDateTime(flight.departure_time)) {
    errors.departure_time = 'Please enter a valid departure date and time'
  }

  if (!flight.arrival_time || !validateDateTime(flight.arrival_time)) {
    errors.arrival_time = 'Please enter a valid arrival date and time'
  }

  if (flight.departure_time && flight.arrival_time) {
    const departure = new Date(flight.departure_time)
    const arrival = new Date(flight.arrival_time)
    if (arrival <= departure) {
      errors.arrival_time = 'Arrival time must be after departure time'
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
}
