export const formatDate = (dateString, format = 'display') => {
  if (!dateString) return ''

  const date = new Date(dateString)

  switch (format) {
    case 'display':
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    case 'short':
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    case 'time':
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    default:
      return date.toISOString()
  }
}

export const formatDuration = (minutes) => {
  if (!minutes) return '0m'

  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60

  if (hours === 0) return `${mins}m`
  if (mins === 0) return `${hours}h`
  return `${hours}h ${mins}m`
}

export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371 // Radius of the Earth in km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return Math.round(R * c) // Distance in km
}

export const debounce = (func, wait) => {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

export const generateFlightStats = (flights) => {
  if (!flights || flights.length === 0) {
    return {
      totalFlights: 0,
      totalDistance: '0',
      totalHours: 0,
      countriesVisited: 0,
      averageFlightTime: 0,
      longestFlight: null,
      mostVisitedCountry: null
    }
  }

  const totalFlights = flights.length
  const totalMinutes = flights.reduce((sum, flight) => sum + (flight.duration || 0), 0)
  const totalHours = Math.round(totalMinutes / 60)
  const totalDistance = flights.reduce((sum, flight) => sum + (flight.distance || 0), 0)

  // Get unique countries (simplified - would need airport data for real implementation)
  const countries = new Set()
  flights.forEach(flight => {
    // This would be replaced with actual country lookup from airport data
    countries.add('Sample Country')
  })

  const longestFlight = flights.reduce((longest, flight) =>
    (!longest || flight.duration > longest.duration) ? flight : longest
  , null)

  return {
    totalFlights,
    totalDistance: totalDistance.toLocaleString(),
    totalHours,
    countriesVisited: countries.size,
    averageFlightTime: Math.round(totalMinutes / totalFlights),
    longestFlight,
    mostVisitedCountry: 'Sample Country'
  }
}
