'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { apiClient } from '@/lib/api'
import Header from '@/components/Header'

interface Crop {
  id: number
  name: string
}

interface Market {
  id: number
  name: string
  region: string
}

export default function NewAlertPage() {
  const { isAuthenticated } = useAuth()
  const router = useRouter()

  const [crops, setCrops] = useState<Crop[]>([])
  const [markets, setMarkets] = useState<Market[]>([])
  const [selectedCrop, setSelectedCrop] = useState<number | null>(null)
  const [selectedMarket, setSelectedMarket] = useState<number | null>(null)
  const [targetPrice, setTargetPrice] = useState<number>(150)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    fetchData()
  }, [isAuthenticated, router])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [cropsData, marketsData] = await Promise.all([
        apiClient.getCrops(),
        apiClient.getMarkets(),
      ])
      setCrops(cropsData)
      setMarkets(marketsData)
      if (cropsData.length > 0) setSelectedCrop(cropsData[0].id)
      if (marketsData.length > 0) setSelectedMarket(marketsData[0].id)
    } catch (err) {
      console.error('Failed to fetch data:', err)
      setError('Failed to load crops and markets')
    } finally {
      setLoading(false)
    }
  }

  const adjustPrice = (delta: number) => {
    setTargetPrice((prev) => Math.max(0, Math.round((prev + delta) * 100) / 100))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedCrop || !selectedMarket) {
      setError('Please select both a crop and a market')
      return
    }
    
    setError(null)
    setSaving(true)
    try {
      await apiClient.createAlert({
        crop_id: selectedCrop,
        market_id: selectedMarket,
        target_price: targetPrice,
      })
      setSuccess(true)
      setTimeout(() => router.push('/alerts'), 1200)
    } catch (err: any) {
      let errorMessage = 'Failed to save alert. Please try again.'
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
      }
      setError(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  if (!isAuthenticated || loading) return null

  if (success) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl border border-gray-100 p-8 text-center shadow-sm">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
            <svg
              className="h-8 w-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-1">Alert Created!</h2>
          <p className="text-gray-600">We'll notify you when the price hits your target.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white text-gray-900 pb-24">
      <Header showBackToDashboard />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6 space-y-8"
        >
          <div className="text-center">
            <p className="text-sm text-green-500 font-medium">Price Alert</p>
            <h1 className="text-2xl font-semibold mt-1">Set Price Alert</h1>
          </div>

          {/* Crops */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-gray-800">Select Crop</h2>
            <div className="grid grid-cols-3 gap-3">
              {crops.map((crop) => {
                const active = selectedCrop === crop.id
                return (
                  <button
                    key={crop.id}
                    type="button"
                    onClick={() => setSelectedCrop(crop.id)}
                    className={`rounded-lg border px-4 py-3 text-sm font-medium transition ${
                      active
                        ? 'bg-green-500 text-white border-green-500'
                        : 'bg-white text-gray-800 border-gray-200 hover:border-green-300'
                    }`}
                  >
                    {crop.name}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Markets */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-gray-800">Select Market</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {markets.map((market) => {
                const active = selectedMarket === market.id
                return (
                  <button
                    key={market.id}
                    type="button"
                    onClick={() => setSelectedMarket(market.id)}
                    className={`rounded-lg border px-4 py-3 text-sm font-medium transition ${
                      active
                        ? 'bg-green-500 text-white border-green-500'
                        : 'bg-white text-gray-800 border-gray-200 hover:border-green-300'
                    }`}
                  >
                    {market.name}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Target price */}
          <div className="space-y-3">
            <h2 className="text-sm font-semibold text-gray-800">Target Price (ETB)</h2>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => adjustPrice(-5)}
                className="h-11 w-11 flex items-center justify-center rounded-lg border border-gray-200 hover:border-green-300"
                aria-label="Decrease price"
              >
                ▾
              </button>
              <input
                type="number"
                min={0}
                step="0.01"
                value={targetPrice}
                onChange={(e) => setTargetPrice(parseFloat(e.target.value || '0'))}
                className="flex-1 h-11 rounded-lg border border-gray-200 px-4 text-center text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                type="button"
                onClick={() => adjustPrice(5)}
                className="h-11 w-11 flex items-center justify-center rounded-lg border border-gray-200 hover:border-green-300"
                aria-label="Increase price"
              >
                ▴
              </button>
            </div>
          </div>

          {error && (
            <div className="rounded-xl bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={saving || !selectedCrop || !selectedMarket}
            className="w-full bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 transition disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Alert'}
          </button>
        </form>
      </div>

      {/* Bottom nav */}
      <nav className="fixed bottom-0 inset-x-0 border-t border-gray-200 bg-white z-30">
        <div className="max-w-6xl mx-auto px-6 py-3 flex justify-around text-[10px] uppercase font-bold">
          <Link href="/dashboard" className="flex flex-col items-center gap-1 text-gray-400">
            <span className="text-xl">🏠</span>
            <span>Home</span>
          </Link>
          <Link href="/alerts" className="flex flex-col items-center gap-1 text-[#4ce434]">
            <span className="text-xl">🔔</span>
            <span>Alerts</span>
          </Link>
          <Link href="/history" className="flex flex-col items-center gap-1 text-gray-400">
            <span className="text-xl">🕐</span>
            <span>History</span>
          </Link>
          <Link href="/settings" className="flex flex-col items-center gap-1 text-gray-400">
            <span className="text-xl">⚙️</span>
            <span>Settings</span>
          </Link>
        </div>
      </nav>
    </div>
  )
}
