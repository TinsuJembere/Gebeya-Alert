'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useLanguage } from '@/contexts/LanguageContext'
import { apiClient } from '@/lib/api'
import { cachedFetch } from '@/utils/cache'
import Header from '@/components/Header'
import BottomNavigation from '@/components/BottomNavigation'
import Link from 'next/link'

interface PriceData {
  id: number
  crop_id?: number
  market_id?: number
  crop_name: string
  crop_type?: string
  market_name: string
  market_region?: string
  price: number
  price_change_7d: number
  trend: string
  source?: string
  confidence_score?: number
  updated_at?: string
  price_date?: string
}

export default function DashboardPage() {
  const { user, loading: authLoading } = useAuth()
  const { t } = useLanguage()
  const router = useRouter()
  const [marketPrices, setMarketPrices] = useState<PriceData[]>([])
  const [dataLoading, setDataLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetchMarketData = useCallback(async (useCache = true, showRefreshing = false) => {
    if (!user) return

    try {
      if (showRefreshing) setIsRefreshing(true)
      setDataLoading(true)
      setError(null)
      
      // Use cached fetch for offline support, but allow bypass for real-time updates
      // Prices cache for 1 minute, predictions cache for 5 minutes
      const prices = useCache
        ? await cachedFetch<PriceData[]>(
            'latest_prices',
            () => apiClient.getLatestPrices(20),
            true,
            1 * 60 * 1000 // 1 minute cache for prices
          )
        : await apiClient.getLatestPrices(20)
      
      setMarketPrices(prices)
      setLastUpdated(new Date())
    } catch (err: any) {
      console.error('Error fetching prices:', err)
      setError(err.response?.data?.detail || t('failedToLoad') || 'Failed to load prices')
    } finally {
      setDataLoading(false)
      if (showRefreshing) setIsRefreshing(false)
    }
  }, [user, t])

  useEffect(() => {
    if (!user) return

    // Initial fetch
    fetchMarketData()
    
    // Auto-refresh every 30 seconds if enabled
    let interval: NodeJS.Timeout | null = null
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchMarketData(false, true) // Bypass cache for real-time updates, show refreshing indicator
      }, 30000) // 30 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [user, fetchMarketData, autoRefresh])

  const getTrendInfo = (change: number) => {
    if (change > 0) return { text: t('rising') || 'Rising', color: 'text-green-600', icon: '📈', bgColor: 'bg-green-50' }
    if (change < 0) return { text: t('falling') || 'Falling', color: 'text-red-600', icon: '📉', bgColor: 'bg-red-50' }
    return { text: t('stable') || 'Stable', color: 'text-gray-600', icon: '➡️', bgColor: 'bg-gray-50' }
  }

  const formatTimeAgo = (date: Date | null) => {
    if (!date) return ''
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)
    if (seconds < 60) return t('justNow')
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) {
      const minsAgo = t('minutesAgo')
      return minsAgo.includes('m ago') ? `${minutes}${minsAgo}` : `${minutes} ${minsAgo}`
    }
    const hours = Math.floor(minutes / 60)
    if (hours < 24) {
      const hrsAgo = t('hoursAgo')
      return hrsAgo.includes('h ago') ? `${hours}${hrsAgo}` : `${hours} ${hrsAgo}`
    }
    const days = Math.floor(hours / 24)
    const daysAgo = t('daysAgo')
    return daysAgo.includes('d ago') ? `${days}${daysAgo}` : `${days} ${daysAgo}`
  }

  const getConfidenceBadge = (score?: number) => {
    if (!score) return null
    const percentage = Math.round(score * 100)
    let color = 'bg-gray-500'
    if (percentage >= 80) color = 'bg-green-500'
    else if (percentage >= 60) color = 'bg-yellow-500'
    else color = 'bg-orange-500'
    
    return (
      <div className="flex items-center gap-1" title={`${percentage}% ${t('confidence')}`}>
        <div className={`w-1.5 h-1.5 rounded-full ${color}`}></div>
        <span className="text-xs text-gray-500">{percentage}%</span>
      </div>
    )
  }

  const getSourceBadge = (source?: string) => {
    if (!source || source === 'manual') return null
    
    const sourceLabels: Record<string, string> = {
      'api': `🌐 ${t('sourceApi')}`,
      'sms': `📱 ${t('sourceSms')}`,
      'market_officer': `👤 ${t('sourceOfficer')}`,
    }
    
    return (
      <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full font-medium">
        {sourceLabels[source] || source}
      </span>
    )
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p className="text-gray-500">{t('loading')}</p>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 pb-20">
      <Header />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-6 pb-6">
        {/* Welcome Section */}
        <div className="mb-6">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            {t('welcome') || 'Welcome'}
          </h1>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/alerts/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-[#4ce434] hover:bg-[#45cc2f] text-white font-bold rounded-xl transition-all shadow-md hover:shadow-lg active:scale-95"
            >
              <span>🔔</span>
              <span>{t('setPriceAlert') || 'Set Price Alert'}</span>
            </Link>
            <button
              onClick={() => fetchMarketData(false, true)}
              disabled={dataLoading || isRefreshing}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white hover:bg-gray-50 text-gray-700 font-semibold rounded-xl transition-all border border-gray-200 shadow-sm hover:shadow-md active:scale-95 disabled:opacity-50"
            >
              <span className={isRefreshing ? 'animate-spin' : ''}>
                {isRefreshing ? '⏳' : '🔄'}
              </span>
              <span>{isRefreshing ? t('refreshing') : t('refresh')}</span>
            </button>
          </div>
        </div>

        {/* Last Updated & Auto-refresh Toggle */}
        <div className="mb-4 flex items-center justify-between flex-wrap gap-2 bg-white p-3 rounded-xl border border-gray-100 shadow-sm">
          {lastUpdated && (
            <div className="text-sm text-gray-600 flex items-center gap-2">
              <span className={isRefreshing ? 'animate-pulse' : ''}>🕐</span>
              <span>
                {isRefreshing ? t('updating') : `${t('lastUpdated')}: ${formatTimeAgo(lastUpdated)}`}
              </span>
            </div>
          )}
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer hover:text-gray-900 transition-colors">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 text-[#4ce434] rounded focus:ring-[#4ce434] cursor-pointer"
            />
            <span className="font-medium">{t('autoRefresh')}</span>
          </label>
        </div>

        {/* Today's Market Prices Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6 flex-wrap gap-2">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span>📊</span>
              <span>{t('todaysMarketPrices') || 'Today\'s Market Prices'}</span>
            </h2>
            {error && (
              <div className="text-xs text-red-600 bg-red-50 px-3 py-1.5 rounded-full flex items-center gap-1">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}
          </div>
          
          {dataLoading && marketPrices.length === 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/3"></div>
                </div>
              ))}
            </div>
          )}
          
          {!dataLoading && !error && marketPrices.length === 0 && (
            <div className="text-center py-12 text-gray-500 bg-white rounded-2xl border border-gray-100">
              <p className="text-4xl mb-3">📊</p>
              <p className="text-lg font-medium mb-1">{t('noMarketPrices') || 'No market prices available'}</p>
              <p className="text-sm">Check back later or add prices in admin panel</p>
            </div>
          )}

          {!dataLoading && marketPrices.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {marketPrices.map((item) => {
                const trend = getTrendInfo(item.price_change_7d || 0)
                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      if (item.crop_id && item.market_id) {
                        // Navigate to insights page with query parameters
                        const params = new URLSearchParams({
                          cropId: item.crop_id.toString(),
                          marketId: item.market_id.toString(),
                          cropName: item.crop_name,
                          marketName: item.market_name,
                          currentPrice: item.price.toString(),
                        })
                        router.push(`/insights?${params.toString()}`)
                      }
                    }}
                    className="bg-white p-5 sm:p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-xl transition-all cursor-pointer active:scale-[0.98] group"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="font-bold text-lg text-gray-900 group-hover:text-[#4ce434] transition-colors">
                        {item.crop_name}
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {item.crop_type && (
                          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
                            {item.crop_type}
                          </span>
                        )}
                        {getConfidenceBadge(item.confidence_score)}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                      <span>📍</span>
                      <span className="truncate">{item.market_name}</span>
                      {item.market_region && (
                        <span className="text-xs text-gray-400 flex-shrink-0">({item.market_region})</span>
                      )}
                    </div>
                    
                    <div className="text-3xl font-bold text-[#4ce434] mb-3">
                      {item.price.toFixed(0)} ETB
                    </div>
                    
                    <div className={`text-sm font-medium flex items-center gap-2 px-3 py-1.5 rounded-full ${trend.bgColor} ${trend.color}`}>
                      <span className="text-base">{trend.icon}</span>
                      <span>{trend.text}</span>
                      {item.price_change_7d !== 0 && (
                        <span className="text-xs">
                          ({item.price_change_7d > 0 ? '+' : ''}{item.price_change_7d.toFixed(0)} ETB)
                        </span>
                      )}
                    </div>
                    
                    {(item.source || item.updated_at) && (
                      <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between flex-wrap gap-2">
                        {getSourceBadge(item.source)}
                        {item.updated_at && (
                          <span className="text-xs text-gray-500 flex items-center gap-1">
                            <span>🕐</span>
                            <span>{formatTimeAgo(new Date(item.updated_at))}</span>
                          </span>
                        )}
                      </div>
                    )}
                    
                    {item.crop_id && item.market_id && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="text-xs text-[#4ce434] font-medium flex items-center gap-1 animate-pulse">
                          <span>🤖</span>
                          <span>{t('tapForAiInsights')}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      <BottomNavigation />
    </div>
  )
}
