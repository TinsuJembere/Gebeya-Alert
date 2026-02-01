'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { cachedFetch } from '@/utils/cache'
import { useLanguage } from '@/contexts/LanguageContext'

interface BestTimeToSellProps {
  cropId: number
  marketId: number
  cropName: string
  marketName: string
}

interface Recommendation {
  current_price: number
  recommended_price: number
  recommendation: string
  confidence: number
  reasoning?: string
}

export default function BestTimeToSell({
  cropId,
  marketId,
  cropName,
  marketName,
}: BestTimeToSellProps) {
  const { t } = useLanguage()
  const [rec, setRec] = useState<Recommendation | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecommendation = async () => {
      try {
        setLoading(true)
        setError(null)
        // Cache recommendations for 5 minutes
        const cacheKey = `recommendation_${cropId}_${marketId}`
        const data = await cachedFetch<Recommendation>(
          cacheKey,
          () => apiClient.getBestTimeToSell(cropId, marketId),
          true,
          5 * 60 * 1000 // 5 minutes cache
        )
        setRec(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load recommendation')
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendation()
  }, [cropId, marketId])

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return 'bg-green-500'
    if (confidence >= 0.5) return 'bg-yellow-500'
    return 'bg-orange-500'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-red-100 shadow-sm">
        <p className="text-red-600 text-sm">{error}</p>
      </div>
    )
  }

  if (!rec) {
    return null
  }

  const priceDiff = rec.recommended_price - rec.current_price
  const priceDiffPercent = (priceDiff / rec.current_price) * 100

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-100 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <span>💡</span>
          {t('bestTimeToSell')}
        </h3>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${getConfidenceColor(rec.confidence)}`}></div>
          <span className="text-xs font-medium text-gray-700">
            {Math.round(rec.confidence * 100)}% {t('confidence')}
          </span>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-2">{cropName} at {marketName}</div>
        <div className="flex items-baseline gap-4">
          <div>
            <div className="text-xs text-gray-500 mb-1">{t('currentPriceLabel')}</div>
            <div className="text-2xl font-bold text-gray-900">
              {rec.current_price.toFixed(0)} ETB
            </div>
          </div>
          {priceDiff !== 0 && (
            <div className="flex-1">
              <div className="text-xs text-gray-500 mb-1">{t('recommended')}</div>
              <div className={`text-2xl font-bold ${priceDiff > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {rec.recommended_price.toFixed(0)} ETB
                {priceDiff > 0 && (
                  <span className="text-sm ml-2">(+{priceDiffPercent.toFixed(1)}%)</span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl p-4 mb-4 border border-blue-100">
        <p className="text-sm text-gray-700 leading-relaxed">
          {rec.recommendation}
        </p>
      </div>

      {rec.reasoning && (
        <div className="text-xs text-gray-500 italic">
          {rec.reasoning}
        </div>
      )}
    </div>
  )
}
