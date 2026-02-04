import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://gebeya-alert.onrender.com/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      withCredentials: true, // Important for CORS with credentials
    });

    this.client.interceptors.request.use((config) => {
      const token = this.getAuthToken();
      if (token) {
        // Ensure we don't duplicate the Bearer prefix
        const authHeader = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
        config.headers.Authorization = authHeader;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - clear token and redirect to login
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
            // Optionally redirect to login page
            // window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private getAuthToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('auth_token');
  }

  // In your frontend API client (apiClient.ts or similar)
public async login(phoneNumber: string, password: string) {
  const params = new URLSearchParams();
  params.append('username', phoneNumber);  // Your backend expects 'username' for the phone number
  params.append('password', password);    // This would be the OTP in your case

  const response = await this.client.post('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  
  const token = response.data.access_token;
  if (token && typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
  return response.data;
}

  public async register(phoneNumber: string, password: string, language: string = 'en') {
    const response = await this.client.post('/auth/register', { 
      phone_number: phoneNumber,
      password,
      language 
    });
    
    const token = response.data.access_token;
    if (token && typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
    return response.data;
  }

  public async getCurrentUser() {
    const response = await this.client.get('/users/me');
    return response.data;
  }

  public logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
    // You might want to add a call to your backend's logout endpoint here
  }
}

export const apiClient = new ApiClient();