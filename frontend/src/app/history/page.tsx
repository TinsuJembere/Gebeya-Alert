'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useLanguage } from '@/contexts/LanguageContext'
import Link from 'next/link'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { apiClient } from '@/lib/api'
import Header from '@/components/Header'
import BottomNavigation from '@/components/BottomNavigation'

interface Crop {
  id: number
  name: string
}

interface Market {
  id: number
  name: string
  region: string
}

interface PriceData {
  id: number
  crop_id: number
  market_id: number
  price: number
  price_date: string
}

export default function PricesPage() {
  const { isAuthenticated } = useAuth()
  const { t } = useLanguage()
  const router = useRouter()
  const [crops, setCrops] = useState<Crop[]>([])
  const [markets, setMarkets] = useState<Market[]>([])
  const [selectedCropId, setSelectedCropId] = useState<number | null>(null)
  const [selectedMarketId, setSelectedMarketId] = useState<number | null>(null)
  const [timeRange, setTimeRange] = useState(30) // days
  const [priceHistory, setPriceHistory] = useState<PriceData[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingHistory, setLoadingHistory] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    fetchCropsAndMarkets()
  }, [isAuthenticated, router])

  useEffect(() => {
    if (selectedCropId && selectedMarketId) {
      fetchPriceHistory()
    }
  }, [selectedCropId, selectedMarketId, timeRange])

  const fetchCropsAndMarkets = async () => {
    try {
      setLoading(true)
      const [cropsData, marketsData] = await Promise.all([
        apiClient.getCrops(),
        apiClient.getMarkets(),
      ])
      setCrops(cropsData)
      setMarkets(marketsData)
      if (cropsData.length > 0) setSelectedCropId(cropsData[0].id)
      if (marketsData.length > 0) setSelectedMarketId(marketsData[0].id)
    } catch (err) {
      console.error('Failed to fetch data:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchPriceHistory = async () => {
    if (!selectedCropId || !selectedMarketId) return

    try {
      setLoadingHistory(true)
      const prices = await apiClient.getPrices({
        crop_id: selectedCropId,
        market_id: selectedMarketId,
      })
      
      // Filter by date range and sort by date
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - timeRange)
      
      const filtered = prices
        .filter((p: PriceData) => {
          const priceDate = new Date(p.price_date)
          return priceDate >= startDate && priceDate <= endDate
        })
        .sort((a: PriceData, b: PriceData) => 
          new Date(a.price_date).getTime() - new Date(b.price_date).getTime()
        )
      
      setPriceHistory(filtered)
    } catch (err) {
      console.error('Failed to fetch price history:', err)
    } finally {
      setLoadingHistory(false)
    }
  }

  // Process data for Recharts
  const chartData = useMemo(() => {
    return priceHistory.map((item) => ({
      date: item.price_date,
      price: typeof item.price === 'number' ? item.price : parseFloat(item.price),
      displayDate: new Date(item.price_date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }),
    }))
  }, [priceHistory])

  const selectedCrop = crops.find((c) => c.id === selectedCropId)
  const selectedMarket = markets.find((m) => m.id === selectedMarketId)

  if (!isAuthenticated || loading) return null

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans pb-24">
      <Header />

      <main className="max-w-3xl mx-auto w-full px-6 py-8 flex-grow text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Price History</h1>

        {/* Filters */}
        <div className="grid grid-cols-2 gap-6 mb-8 text-left">
          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-800">Select Crop</label>
            <select
              value={selectedCropId || ''}
              onChange={(e) => setSelectedCropId(parseInt(e.target.value))}
              className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-1 focus:ring-green-500 outline-none appearance-none"
            >
              {crops.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-bold text-gray-800">Select Market</label>
            <select
              value={selectedMarketId || ''}
              onChange={(e) => setSelectedMarketId(parseInt(e.target.value))}
              className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-1 focus:ring-green-500 outline-none appearance-none"
            >
              {markets.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} {m.region ? `(${m.region})` : ''}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Time Range Selector */}
        <div className="flex justify-center gap-3 mb-10">
          {[
            { label: '1 Week', days: 7 },
            { label: '1 Month', days: 30 },
            { label: '3 Months', days: 90 },
          ].map((range) => (
            <button
              key={range.days}
              onClick={() => setTimeRange(range.days)}
              className={`px-6 py-2 rounded-full border transition-all font-medium ${
                timeRange === range.days
                  ? 'bg-[#4ce434] border-[#4ce434] text-white'
                  : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>

        {/* Chart Container */}
        {loadingHistory && (
          <div className="text-center py-12 text-gray-500">Loading price history...</div>
        )}

        {!loadingHistory && chartData.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No price data available for the selected period.
          </div>
        )}

        {!loadingHistory && chartData.length > 0 && (
          <div className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm mb-6 text-left">
            <h2 className="text-lg font-bold text-gray-800 mb-6">
              {selectedCrop?.name} Price Trend in {selectedMarket?.name}
            </h2>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4ce434" stopOpacity={0.1} />
                      <stop offset="95%" stopColor="#4ce434" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis
                    dataKey="displayDate"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#9ca3af', fontSize: 12 }}
                    dy={10}
                  />
                  <YAxis
                    hide={false}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#9ca3af', fontSize: 10 }}
                    tickFormatter={(value) => `${value} ETB`}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: '12px',
                      border: 'none',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    }}
                    formatter={(value: number) => [`${value.toFixed(2)} ETB`, 'Price']}
                  />
                  <Area
                    type="monotone"
                    dataKey="price"
                    stroke="#4ce434"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#colorPrice)"
                    dot={{ r: 6, fill: '#4ce434', strokeWidth: 2, stroke: '#fff' }}
                    activeDot={{ r: 8, strokeWidth: 0 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {!loadingHistory && chartData.length > 0 && (
          <p className="text-gray-500 text-sm italic">
            {selectedCrop?.name} prices in {selectedMarket?.name} over the selected period.
          </p>
        )}
      </main>

      <BottomNavigation />
    </div>
  )
}
