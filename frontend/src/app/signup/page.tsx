'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { normalizePhoneNumber } from '@/utils/phone'

export default function SignupPage() {
  const [phoneNumber, setPhoneNumber] = useState('')
  const [password, setPassword] = useState('')
  const [language, setLanguage] = useState('en')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const normalized = normalizePhoneNumber(phoneNumber)
      await register(normalized, password, language)
      router.push('/dashboard')
    } catch (err: any) {
      let errorMessage = 'Sign up failed. Please check your number and try again.'
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
      {/* Language Toggle Header */}
      <div className="flex justify-center gap-2 pt-6">
        <button
          onClick={() => setLanguage('en')}
          className={`px-6 py-2 rounded-full text-sm font-medium transition-colors ${
            language === 'en' ? 'bg-[#4ce434] text-white' : 'bg-white border border-gray-200 text-gray-600'
          }`}
        >
          English
        </button>
        <button
          onClick={() => setLanguage('am')}
          className={`px-6 py-2 rounded-full text-sm font-medium transition-colors ${
            language === 'am' ? 'bg-[#4ce434] text-white' : 'bg-white border border-gray-200 text-gray-600'
          }`}
        >
          አማርኛ
        </button>
      </div>

      <div className="flex-grow flex items-center justify-center px-4">
        {/* Main Card Container */}
        <div className="max-w-md w-full bg-white rounded-[2rem] border border-gray-100 shadow-sm p-10 space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
              Join <br /> GebeyaAlert
            </h1>
            <p className="mt-4 text-gray-500 text-base">
              Create an account to start <br /> tracking crop prices.
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Phone Number Field */}
            <div className="space-y-2 text-left">
              <label htmlFor="phone" className="text-sm font-bold text-gray-800 ml-1">
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

            {/* Password Field */}
            <div className="space-y-2 text-left">
              <label htmlFor="password" className="text-sm font-bold text-gray-800 ml-1">
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

            {/* Language Selection (Visual Select) */}
            <div className="space-y-2 text-left">
              <label htmlFor="language" className="text-sm font-bold text-gray-800 ml-1">
                Preferred Language
              </label>
              <select
                id="language"
                name="language"
                className="block w-full px-4 py-4 bg-white border border-gray-200 rounded-2xl text-gray-900 focus:outline-none focus:ring-1 focus:ring-green-500 appearance-none bg-[url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2224%22%20height%3D%2224%22%20viewBox%3D%220%200%2024%2024%20fill%3D%22none%20stroke%3D%22currentColor%20stroke-width%3D%222%20stroke-linecap%3D%22round%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E')] bg-[length:1em_1em] bg-[right_1rem_center] bg-no-repeat"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="am">Amharic</option>
                <option value="om">Afaan Oromo</option>
                <option value="ti">Tigrinya</option>
              </select>
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
              {loading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500">
            already have an account?{' '}
            <Link
              href="/login"
              className="font-bold text-[#4ce434] hover:underline"
            >
              Sign In.
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}




