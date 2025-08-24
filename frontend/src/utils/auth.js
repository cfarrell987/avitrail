export class SessionManager {
  static SESSION_KEY = 'avitrail_session'
  static EXPIRY_HOURS = 48

  static saveSession(token, user = null) {
    const session = {
      token,
      user,
      timestamp: Date.now(),
      expiresAt: Date.now() + (this.EXPIRY_HOURS * 60 * 60 * 1000)
    }
    localStorage.setItem(this.SESSION_KEY, JSON.stringify(session))
  }

  static getSession() {
    try {
      const sessionData = localStorage.getItem(this.SESSION_KEY)
      if (!sessionData) return null

      const session = JSON.parse(sessionData)

      // Check if expired
      if (Date.now() > session.expiresAt) {
        this.clearSession()
        return null
      }

      return session
    } catch (error) {
      this.clearSession()
      return null
    }
  }

  static clearSession() {
    localStorage.removeItem(this.SESSION_KEY)
  }

  static isSessionValid() {
    const session = this.getSession()
    return session && session.token
  }

  static getToken() {
    const session = this.getSession()
    return session?.token || null
  }

  static getUser() {
    const session = this.getSession()
    return session?.user || null
  }

  static refreshSession() {
    const session = this.getSession()
    if (session) {
      this.saveSession(session.token, session.user)
    }
  }
}
