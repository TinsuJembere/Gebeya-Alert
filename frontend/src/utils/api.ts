// frontend/src/utils/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
      },
      credentials: 'include',
    });

    const data = await response.json().catch(() => ({}));
    
    if (!response.ok) {
      return {
        error: data.detail || 'An error occurred',
        status: response.status,
      };
    }

    return { data, status: response.status };
  } catch (error) {
    console.error('API request failed:', error);
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 500,
    };
  }
}

// Market price related API calls
export const marketApi = {
  getMarketPrices: async (): Promise<ApiResponse<MarketPrice[]>> => {
    return fetchApi<MarketPrice[]>('/prices/latest?limit=6');
  },
  
  getPriceHistory: async (cropId: string): Promise<ApiResponse<PriceHistory[]>> => {
    return fetchApi<PriceHistory[]>(`/api/prices/history/${cropId}`);
  },
};

// User related API calls
export const userApi = {
  getCurrentUser: async (): Promise<ApiResponse<User>> => {
    return fetchApi<User>('/api/users/me');
  },
  
  updateUser: async (userData: Partial<User>): Promise<ApiResponse<User>> => {
    return fetchApi<User>('/api/users/me', {
      method: 'PATCH',
      body: JSON.stringify(userData),
    });
  },
};

// Types
export interface MarketPrice {
  id: number;
  crop: string;
  market: string;
  market_region?: string;
  price: number;
  price_date: string;
  change: number;
}

export interface PriceHistory {
  date: string;
  price: number;
}

export interface User {
  id: number;
  phone_number: string;
  language: string;
  is_admin: boolean;
  created_at: string;
  updated_at?: string;
}