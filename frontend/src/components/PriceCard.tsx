'use client'

interface PriceCardProps {
  cropName: string
  marketName: string
  price: number
  source?: string
  confidenceScore?: number
  updatedAt?: string
}

export default function PriceCard({
  cropName,
  marketName,
  price,
  source,
  confidenceScore,
  updatedAt,
}: PriceCardProps) {
  const formatTimeAgo = (dateStr: string | undefined) => {
    if (!dateStr) return ''
    try {
      const date = new Date(dateStr)
      const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)
      if (seconds < 60) return 'Just now'
      const minutes = Math.floor(seconds / 60)
      if (minutes < 60) return `${minutes}m ago`
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours}h ago`
      const days = Math.floor(hours / 24)
      return `${days}d ago`
    } catch {
      return ''
    }
  }

  const getConfidenceColor = (score?: number) => {
    if (!score) return 'bg-gray-400'
    const percentage = Math.round(score * 100)
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-yellow-500'
    return 'bg-orange-500'
  }

  return (
    <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <p className="text-lg font-bold text-gray-900 mb-1">{cropName}</p>
          <p className="text-sm text-gray-600 flex items-center gap-1">
            <span>📍</span>
            <span>{marketName}</span>
          </p>
        </div>
        {confidenceScore && (
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${getConfidenceColor(confidenceScore)}`}></div>
            <span className="text-xs text-gray-500">{Math.round(confidenceScore * 100)}%</span>
          </div>
        )}
      </div>
      <div className="text-right mb-3">
        <p className="text-3xl font-bold text-[#4ce434]">
          {price.toFixed(0)} ETB
        </p>
      </div>
      {(source || updatedAt) && (
        <div className="pt-3 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500">
            {source && source !== 'manual' && <span>Source: {source}</span>}
            {updatedAt && <span>{formatTimeAgo(updatedAt)}</span>}
          </div>
        </div>
      )}
    </div>
  )
}
















