export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  TIMEOUT: 10000
}

export const SEAT_CLASSES = {
  ECONOMY: 'EC',
  ECONOMY_PLUS: 'EP',
  BUSINESS: 'BC',
  FIRST: 'FC'
}

export const SEAT_CLASS_LABELS = {
  [SEAT_CLASSES.ECONOMY]: 'Economy',
  [SEAT_CLASSES.ECONOMY_PLUS]: 'Economy Plus',
  [SEAT_CLASSES.BUSINESS]: 'Business',
  [SEAT_CLASSES.FIRST]: 'First Class'
}

export const DATE_FORMATS = {
  DISPLAY: 'MMM dd, yyyy HH:mm',
  INPUT: 'yyyy-MM-ddTHH:mm',
  API: 'yyyy-MM-ddTHH:mm:ss'
}

export const MAP_CONFIG = {
  DEFAULT_CENTER: [20, 0],
  DEFAULT_ZOOM: 2,
  FLIGHT_PATH_COLOR: '#667eea',
  DEPARTURE_MARKER_COLOR: '#667eea',
  ARRIVAL_MARKER_COLOR: '#764ba2'
}
