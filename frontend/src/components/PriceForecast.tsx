'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { cachedFetch } from '@/utils/cache'
import { useLanguage } from '@/contexts/LanguageContext'

interface PriceForecastProps {
  cropId: number
  marketId: number
  cropName: string
  marketName: string
  currentPrice: number
}

interface Prediction {
  predicted_price: number
  predicted_date: string
  confidence: number
  trend: 'rising' | 'falling' | 'stable'
  trend_percentage: number
  recommendation: string
}

export default function PriceForecast({
  cropId,
  marketId,
  cropName,
  marketName,
  currentPrice,
}: PriceForecastProps) {
  const { t } = useLanguage()
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPrediction = async () => {
      try {
        setLoading(true)
        setError(null)
        // Cache predictions for 5 minutes
        const cacheKey = `prediction_${cropId}_${marketId}`
        const data = await cachedFetch<Prediction>(
          cacheKey,
          () => apiClient.getPricePrediction(cropId, marketId, 7),
          true,
          5 * 60 * 1000 // 5 minutes cache
        )
        setPrediction(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load prediction')
      } finally {
        setLoading(false)
      }
    }

    fetchPrediction()
  }, [cropId, marketId])

  const getTrendColor = (trend: string) => {
    if (trend === 'rising') return 'text-green-600 bg-green-50'
    if (trend === 'falling') return 'text-red-600 bg-red-50'
    return 'text-gray-600 bg-gray-50'
  }

  const getTrendIcon = (trend: string) => {
    if (trend === 'rising') return '📈'
    if (trend === 'falling') return '📉'
    return '➡️'
  }

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

  if (!prediction) {
    return null
  }

  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">{t('priceForecast')}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">{t('confidence')}</span>
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${getConfidenceColor(prediction.confidence)}`}></div>
            <span className="text-xs font-medium text-gray-700">
              {Math.round(prediction.confidence * 100)}%
            </span>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <div className="text-sm text-gray-600 mb-1">{cropName} at {marketName}</div>
        <div className="flex items-baseline gap-3">
          <span className="text-2xl font-bold text-gray-900">
            {prediction.predicted_price.toFixed(0)} ETB
          </span>
          <span className="text-sm text-gray-500">
            {t('in7Days')}
          </span>
        </div>
      </div>

      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium mb-4 ${getTrendColor(prediction.trend)}`}>
        <span>{getTrendIcon(prediction.trend)}</span>
        <span>
          {prediction.trend === 'rising' && '+'}
          {prediction.trend_percentage.toFixed(1)}% {prediction.trend}
        </span>
      </div>

      <div className="pt-4 border-t border-gray-100">
        <p className="text-sm text-gray-700 leading-relaxed">
          {prediction.recommendation}
        </p>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{t('currentPriceLabel')}: {currentPrice.toFixed(0)} ETB</span>
          <span>{t('predicted')}: {prediction.predicted_price.toFixed(0)} ETB</span>
        </div>
      </div>
    </div>
  )
}
