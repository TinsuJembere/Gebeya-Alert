// frontend/src/lib/auth.ts
'use client'

import Cookies from 'js-cookie'

export function setAuthToken(token: string) {
  if (typeof window !== 'undefined') {
    Cookies.set('access_token', token, { expires: 7 }) // 7 days
  }
}

export function removeAuthToken() {
  if (typeof window !== 'undefined') {
    Cookies.remove('access_token')
  }
}

export function getAuthToken(): string | null {
  if (typeof window !== 'undefined') {
    return Cookies.get('access_token') || null
  }
  return null
}