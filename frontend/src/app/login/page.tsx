'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { normalizePhoneNumber } from '@/utils/phone'

export default function LoginPage() {
  const [phoneNumber, setPhoneNumber] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [language, setLanguage] = useState('en')
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const normalized = normalizePhoneNumber(phoneNumber)
      await login(normalized, password)
      router.replace('/dashboard')
    } catch (err: any) {
      let errorMessage = 'Login failed.'
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans">
      <div className="flex justify-center gap-2 pt-6">
        <button
          onClick={() => setLanguage('en')}
          className={`px-6 py-2 rounded-full text-sm font-medium transition-colors ${
            language === 'en'
              ? 'bg-[#4ce434] text-white'
              : 'bg-white border border-gray-200 text-gray-600'
          }`}
        >
          English
        </button>
        <button
          onClick={() => setLanguage('am')}
          className={`px-6 py-2 rounded-full text-sm font-medium transition-colors ${
            language === 'am'
              ? 'bg-[#4ce434] text-white'
              : 'bg-white border border-gray-200 text-gray-600'
          }`}
        >
          አማርኛ
        </button>
      </div>

      <div className="flex-grow flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-[2rem] border border-gray-100 shadow-sm p-10 space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
              Welcome to <br /> GebeyaAlert
            </h1>
            <p className="mt-4 text-gray-500 text-base">
              Please enter your phone number to <br /> continue.
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-2 text-left">
              <label
                htmlFor="phone"
                className="text-sm font-bold text-gray-800 ml-1"
              >
                Phone Number
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                required
                className="block w-full px-4 py-4 bg-white border border-gray-200 rounded-2xl text-gray-900 placeholder-gray-300 focus:outline-none focus:ring-1 focus:ring-green-500"
                placeholder="e.g., +251912345678"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
              />
            </div>

            <div className="space-y-2 text-left">
              <label
                htmlFor="password"
                className="text-sm font-bold text-gray-800 ml-1"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="block w-full px-4 py-4 bg-white border border-gray-200 rounded-2xl text-gray-900 placeholder-gray-300 focus:outline-none focus:ring-1 focus:ring-green-500"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {error && (
              <div className="rounded-xl bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-4 px-4 text-lg font-bold rounded-2xl text-white bg-[#4ce434] hover:bg-[#45cc2f] transition-colors disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500">
            do not have an account?{' '}
            <Link
              href="/signup"
              className="font-bold text-[#4ce434] hover:underline"
            >
              Sign Up.
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
