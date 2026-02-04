import axios, { AxiosInstance, AxiosError } from 'axios'

// Get API URL from env, default to base URL without /api/v1
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://gebeya-alert.onrender.com'

// If API_BASE already includes /api/v1, use it as-is, otherwise append it
const baseURL = API_BASE.includes('/api/v1') 
  ? API_BASE 
  : `${API_BASE}/api/v1`

// Log API URL on module load
if (typeof window !== 'undefined') {
  console.log('[API] API_BASE:', API_BASE)
  console.log('[API] Final baseURL:', baseURL)
}

class ApiClient {
  private client: AxiosInstance

  constructor() {
    console.log('[API] Creating client with baseURL:', baseURL)
    
    this.client = axios.create({
      baseURL: baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // Include cookies in cross-origin requests
      timeout: 10000, // 10 second timeout
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
        if (token) {
          const authHeader = token.startsWith('Bearer ') ? token : `Bearer ${token}`
          config.headers.Authorization = authHeader
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token')
            window.location.href = '/login'
          }
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async register(phoneNumber: string, password: string, language: string = 'en') {
    try {
      const response = await this.client.post('/auth/register', {
        phone_number: phoneNumber,
        password,
        language,
      })
      
      const token = response.data.access_token
      if (token && typeof window !== 'undefined') {
        localStorage.setItem('auth_token', token)
      }
      return response.data
    } catch (error: any) {
      console.error('[API] Register error:', error)
      throw error
    }
  }

  async login(phoneNumber: string, password: string) {
    const params = new URLSearchParams()
    params.append('username', phoneNumber)
    params.append('password', password)
    
    try {
      const response = await this.client.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      
      const token = response.data.access_token
      if (token && typeof window !== 'undefined') {
        localStorage.setItem('auth_token', token)
      }
      return response.data
    } catch (error: any) {
      console.error('[API] Login error:', error)
      throw error
    }
  }

  // Crop endpoints
  async getCrops() {
    const response = await this.client.get('/crops')
    return response.data
  }

  async createCrop(name: string) {
    const response = await this.client.post('/crops', { name })
    return response.data
  }

  // Market endpoints
  async getMarkets() {
    const response = await this.client.get('/markets')
    return response.data
  }

  async createMarket(name: string, region: string) {
    const response = await this.client.post('/markets', { name, region })
    return response.data
  }

  // Price endpoints
  async getPrices(params?: {
    crop_id?: number
    market_id?: number
    date?: string
  }) {
    const response = await this.client.get('/prices', { params })
    return response.data
  }

  async createPrice(data: {
    crop_id: number
    market_id: number
    price: number
    price_date: string
  }) {
    const response = await this.client.post('/prices', {
      crop_id: data.crop_id,
      market_id: data.market_id,
      price: data.price,
      price_date: data.price_date,
    })
    return response.data
  }

  // Alert endpoints
  async getAlerts() {
    const response = await this.client.get('/alerts')
    return response.data
  }

  async createAlert(data: {
    crop_id: number
    market_id: number
    target_price: number
  }) {
    const response = await this.client.post('/alerts', data)
    return response.data
  }

  async deleteAlert(alertId: number) {
    const response = await this.client.delete(`/alerts/${alertId}`)
    return response.data
  }

  // User endpoints
  async getCurrentUser() {
    const response = await this.client.get('/users/me')
    return response.data
  }

  async updateCurrentUser(data: {
    phone_number?: string
    language?: string
  }) {
    const response = await this.client.patch('/users/me', data)
    return response.data
  }

  async getLatestPrices(limit: number = 10) {
    const response = await this.client.get('/prices/latest', {
      params: { limit }
    })
    return response.data
  }

  // Price history endpoints
  async getPriceHistory(cropId: number, marketId: number, days: number = 30) {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - days)
    
    const response = await this.client.get('/prices', {
      params: {
        crop_id: cropId,
        market_id: marketId,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      }
    })
    return response.data
  }

  // Price prediction endpoints
  async getPricePrediction(cropId: number, marketId: number, daysAhead: number = 7) {
    const response = await this.client.get(`/prices/predictions/${cropId}/${marketId}`, {
      params: { days_ahead: daysAhead }
    })
    return response.data
  }

  async getBestTimeToSell(cropId: number, marketId: number) {
    const response = await this.client.get(`/prices/best-time-to-sell/${cropId}/${marketId}`)
    return response.data
  }

  // Admin endpoints
  async getAdminStats() {
    const response = await this.client.get('/admin/stats')
    return response.data
  }

  async getAdminUsers() {
    const response = await this.client.get('/admin/users')
    return response.data
  }

  async getAdminMarkets() {
    const response = await this.client.get('/admin/markets')
    return response.data
  }

  async getAdminCrops() {
    const response = await this.client.get('/admin/crops')
    return response.data
  }

  // Logout
  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }
}

export const apiClient = new ApiClient()

