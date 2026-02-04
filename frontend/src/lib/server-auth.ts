import { cookies } from 'next/headers'

export interface User {
  id: number
  phone_number: string
  language: string
}

export interface Session {
  user: User | null
  token: string | null
}

export async function getServerSession(): Promise<Session | null> {
  try {
    const cookieStore = cookies()
    const token = cookieStore.get('access_token')?.value

    if (!token) {
      return null
    }

    // In a real app, you might want to decode and verify the JWT token
    // For now, we'll just check if the token exists
    return {
      user: null, // You can decode JWT to get user info
      token,
    }
  } catch {
    return null
  }
}


