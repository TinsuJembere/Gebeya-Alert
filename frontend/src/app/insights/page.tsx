'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useLanguage } from '@/contexts/LanguageContext'
import Header from '@/components/Header'
import BottomNavigation from '@/components/BottomNavigation'
import PriceForecast from '@/components/PriceForecast'
import BestTimeToSell from '@/components/BestTimeToSell'

export default function InsightsPage() {
  const { user, loading: authLoading } = useAuth()
  const { t } = useLanguage()
  const router = useRouter()
  const searchParams = useSearchParams()
  
  // Get parameters from URL
  const cropId = searchParams.get('cropId')
  const marketId = searchParams.get('marketId')
  const cropName = searchParams.get('cropName') || ''
  const marketName = searchParams.get('marketName') || ''
  const currentPrice = searchParams.get('currentPrice')
  
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login')
      return
    }

    // Validate required parameters
    if (!cropId || !marketId) {
      router.push('/dashboard')
      return
    }
  }, [user, authLoading, router, cropId, marketId])

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4ce434] mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!cropId || !marketId) {
    return null
  }

  const parsedCropId = parseInt(cropId, 10)
  const parsedMarketId = parseInt(marketId, 10)
  const parsedCurrentPrice = currentPrice ? parseFloat(currentPrice) : undefined

  if (isNaN(parsedCropId) || isNaN(parsedMarketId)) {
    router.push('/dashboard')
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header Section */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <span>←</span>
            <span className="text-sm font-medium">{t('back') || 'Back'}</span>
          </button>
          
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">🤖</span>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
              {t('aiInsights') || 'AI Insights'}
            </h1>
          </div>
          
          <div className="text-gray-600 mt-2">
            <p className="text-lg font-medium">{cropName}</p>
            <p className="text-sm flex items-center gap-1 mt-1">
              <span>📍</span>
              <span>{marketName}</span>
            </p>
            {parsedCurrentPrice && (
              <p className="text-2xl font-bold text-[#4ce434] mt-2">
                {parsedCurrentPrice.toFixed(0)} ETB
              </p>
            )}
          </div>
        </div>

        {/* AI Insights Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PriceForecast
            cropId={parsedCropId}
            marketId={parsedMarketId}
            cropName={cropName}
            marketName={marketName}
            currentPrice={parsedCurrentPrice}
          />
          <BestTimeToSell
            cropId={parsedCropId}
            marketId={parsedMarketId}
            cropName={cropName}
            marketName={marketName}
          />
        </div>

        {/* Additional Info Section */}
        <div className="mt-8 bg-blue-50 rounded-2xl p-6 border border-blue-100">
          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
            <span>ℹ️</span>
            <span>{t('aboutAiInsights') || 'About AI Insights'}</span>
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed">
            {t('aiInsightsDescription') || 
              'These insights are generated using AI based on historical price data and market trends. ' +
              'They are predictions and recommendations to help you make informed decisions about when to sell your crops.'}
          </p>
        </div>
      </div>

      <BottomNavigation />
    </div>
  )
}
