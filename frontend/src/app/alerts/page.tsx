'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useLanguage } from '@/contexts/LanguageContext'
import { apiClient } from '@/lib/api'
import Header from '@/components/Header'
import BottomNavigation from '@/components/BottomNavigation'

interface Alert {
  id: number
  crop: string
  market: string
  market_region?: string
  current_price: number | null
  target_price: number
  is_met: boolean
  last_sent_at: string | null
  created_at: string
}

export default function AlertsPage() {
  const { isAuthenticated } = useAuth()
  const { t } = useLanguage()
  const router = useRouter()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [alertToDelete, setAlertToDelete] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    fetchAlerts()
  }, [isAuthenticated, router])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getAlerts()
      setAlerts(data)
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
    } finally {
      setLoading(false)
    }
  }

  const openDeleteModal = (id: number) => {
    setAlertToDelete(id)
    setIsModalOpen(true)
  }

  const closeDeleteModal = () => {
    setIsModalOpen(false)
    setAlertToDelete(null)
  }

  const handleDelete = async () => {
    if (alertToDelete === null) return
    
    try {
      setDeleting(true)
      await apiClient.deleteAlert(alertToDelete)
      setAlerts((prev) => prev.filter((a) => a.id !== alertToDelete))
      closeDeleteModal()
    } catch (err) {
      console.error('Failed to delete alert:', err)
      alert('Failed to delete alert. Please try again.')
    } finally {
      setDeleting(false)
    }
  }

  const formatMarketName = (market: string, region?: string) => {
    if (region) {
      return `${market} ${region}`
    }
    return market
  }

  if (!isAuthenticated) return null

  return (
    <div className="min-h-screen bg-white text-gray-900 pb-24">
      <Header />

      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-800">My Active Alerts</h1>
          <Link
            href="/alerts/new"
            className="px-4 py-2 bg-[#4ce434] text-white font-bold rounded-xl hover:bg-[#45cc2f] transition-colors"
          >
            + New Alert
          </Link>
        </div>

        {loading && (
          <div className="text-center py-8 text-gray-500">Loading alerts...</div>
        )}

        {!loading && alerts.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 mb-4">You don&apos;t have any alerts yet.</p>
            <Link
              href="/alerts/new"
              className="inline-block px-6 py-3 bg-[#4ce434] text-white font-bold rounded-xl hover:bg-[#45cc2f] transition-colors"
            >
              Create Your First Alert
            </Link>
          </div>
        )}

        <div className="space-y-6">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="border border-gray-100 rounded-[2rem] bg-white shadow-sm p-6 relative overflow-hidden"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">{alert.crop}</h2>
                  <p className="text-gray-400 font-medium">
                    {formatMarketName(alert.market, alert.market_region)}
                  </p>
                </div>
                <span
                  className={`text-xs font-bold px-4 py-1 rounded-full ${
                    alert.is_met
                      ? 'bg-[#e8f8e7] text-[#4ce434]'
                      : 'bg-[#f3f4f6] text-gray-500'
                  }`}
                >
                  {alert.is_met ? 'Met' : 'Active'}
                </span>
              </div>

              {/* Watermark for Met alerts */}
              {alert.is_met && (
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-80 pointer-events-none">
                  <span className="text-[#4ce434] font-bold text-2xl">GebeyaAlert</span>
                </div>
              )}

              <div className="flex justify-between items-end mt-4 mb-6">
                <div>
                  <p className="text-gray-400 text-xs font-bold uppercase mb-1">Current Price</p>
                  <div className="text-4xl font-extrabold text-gray-900">
                    {alert.current_price !== null
                      ? `${alert.current_price.toFixed(0)}`
                      : 'N/A'}{' '}
                    <span className="text-2xl font-bold">ETB</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-gray-400 text-xs font-bold uppercase mb-1">Target Price</p>
                  <div className="text-2xl font-bold text-gray-400">
                    {alert.target_price.toFixed(0)} ETB
                  </div>
                </div>
              </div>

              {/* Card Actions */}
              <div className="flex gap-4">
                <button
                  onClick={() => openDeleteModal(alert.id)}
                  className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-[#e63946] text-white font-bold hover:bg-red-600 transition-colors"
                >
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Confirmation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-6">
          <div className="absolute inset-0 bg-black/60" onClick={closeDeleteModal} />
          <div className="relative bg-white w-full max-w-sm rounded-3xl p-8 shadow-2xl">
            <button
              onClick={closeDeleteModal}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Confirm Deletion</h2>
            <p className="text-gray-500 mb-8">
              Are you sure you want to delete this alert? This action cannot be undone.
            </p>
            <div className="flex gap-4">
              <button
                onClick={closeDeleteModal}
                disabled={deleting}
                className="flex-1 py-3 border border-gray-200 rounded-xl font-bold text-gray-600 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 py-3 bg-[#e63946] text-white rounded-xl font-bold hover:bg-red-600 disabled:opacity-50"
              >
                {deleting ? 'Deleting...' : 'Delete Alert'}
              </button>
            </div>
          </div>
        </div>
      )}

      <BottomNavigation />
    </div>
  )
}
