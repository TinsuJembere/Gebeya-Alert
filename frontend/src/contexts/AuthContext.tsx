'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/apiClient'

export interface User {
  id: number
  phone_number: string
  language: string
  is_admin: boolean
  created_at: string
  updated_at?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (phoneNumber: string, password: string) => Promise<void>
  register: (phoneNumber: string, password: string, language?: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  refreshUser: () => Promise<void>
  error: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchUserProfile = useCallback(async (): Promise<User | null> => {
    try {
      return await apiClient.getCurrentUser()
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      localStorage.removeItem('auth_token')
      return null
    }
  }, [])

  const refreshUser = useCallback(async () => {
    try {
      const userData = await fetchUserProfile()
      setUser(userData)
    } catch (error) {
      console.error('Failed to refresh user:', error)
      setUser(null)
    }
  }, [fetchUserProfile])

  useEffect(() => {
    const loadUser = async () => {
      try {
        setLoading(true)
        const userData = await fetchUserProfile()
        setUser(userData)
      } catch (error) {
        console.error('Failed to load user:', error)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    loadUser()
  }, [fetchUserProfile])

  const login = async (phoneNumber: string, password: string): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.login(phoneNumber, password)
      const userData = await fetchUserProfile()
      if (!userData) {
        throw new Error('Failed to fetch user profile after login')
      }
      setUser(userData)
    } catch (error: any) {
      console.error('Login failed:', error)
      let errorMessage = 'Login failed. Please try again.'
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
      } else if (error instanceof Error) {
        errorMessage = error.message
      }
      setError(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const register = async (phoneNumber: string, password: string, language = 'en'): Promise<void> => {
    setLoading(true)
    setError(null)
    try {
      await apiClient.register(phoneNumber, password, language)
      const userData = await fetchUserProfile()
      if (!userData) {
        throw new Error('Failed to fetch user profile after registration')
      }
      setUser(userData)
    } catch (error: any) {
      console.error('Registration failed:', error)
      let errorMessage = 'Registration failed. Please try again.'
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
      } else if (error instanceof Error) {
        errorMessage = error.message
      }
      setError(errorMessage)
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    try {
      apiClient.logout()
      setUser(null)
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        refreshUser,
        error
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}