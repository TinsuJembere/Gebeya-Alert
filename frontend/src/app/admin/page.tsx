'use client'

import { useRef, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/contexts/AuthContext'
import { apiClient } from '@/lib/api'
import { useLanguage } from '@/contexts/LanguageContext'

interface User {
  id: number
  phone_number: string
  language: string
  is_admin: boolean
  created_at: string
}

interface Market {
  id: number
  name: string
  region: string
}

interface Crop {
  id: number
  name: string
}

interface Stats {
  total_users: number
  active_alerts: number
  total_markets: number
  recent_updates: string
}

export default function AdminDashboard() {
  const { isAuthenticated, user } = useAuth()
  const router = useRouter()
  const [stats, setStats] = useState<Stats | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [markets, setMarkets] = useState<Market[]>([])
  const [crops, setCrops] = useState<Crop[]>([])
  const [loading, setLoading] = useState(true)

  const usersRef = useRef<HTMLDivElement>(null)
  const marketsRef = useRef<HTMLDivElement>(null)
  const pricesRef = useRef<HTMLDivElement>(null)
  const auditRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    if (user && !user.is_admin) {
      router.push('/dashboard')
      return
    }
    fetchData()
  }, [isAuthenticated, user, router])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [statsData, usersData, marketsData, cropsData] = await Promise.all([
        apiClient.getAdminStats(),
        apiClient.getAdminUsers(),
        apiClient.getAdminMarkets(),
        apiClient.getAdminCrops(),
      ])
      setStats(statsData)
      setUsers(usersData)
      setMarkets(marketsData)
      setCrops(cropsData)
    } catch (err) {
      console.error('Failed to fetch admin data:', err)
    } finally {
      setLoading(false)
    }
  }

  const scrollToSection = (ref: React.RefObject<HTMLDivElement>) => {
    ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  if (!isAuthenticated || !user?.is_admin || loading) {
    return (
      <div className="flex min-h-screen bg-gray-50 font-sans items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-gray-50 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col fixed h-full">
        <div className="p-6 flex items-center gap-2">
          <div className="bg-[#4ce434] p-1.5 rounded-lg">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
              <path d="M12 3L4 21h16L12 3z" />
            </svg>
          </div>
          <span className="text-[#4ce434] font-bold text-lg">GebeyaAlert</span>
        </div>

        <nav className="flex-grow px-4 space-y-2 mt-4">
          <button
            onClick={() => scrollToSection(usersRef)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-gray-500 hover:bg-[#4ce434] hover:text-white transition-all"
          >
            <span>👥</span> Users
          </button>
          <button
            onClick={() => scrollToSection(marketsRef)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-gray-500 hover:bg-[#4ce434] hover:text-white transition-all"
          >
            <span>🏪</span> Markets
          </button>
          <button
            onClick={() => scrollToSection(pricesRef)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-gray-500 hover:bg-[#4ce434] hover:text-white transition-all"
          >
            <span>💰</span> Prices
          </button>
          <button
            onClick={() => scrollToSection(auditRef)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-gray-500 hover:bg-[#4ce434] hover:text-white transition-all"
          >
            <span>📝</span> Audit Log
          </button>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-grow ml-64">
        <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <h1 className="font-bold text-gray-800 text-lg">Admin Dashboard</h1>
            <Link
              href="/dashboard"
              className="px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-[#4ce434] border border-gray-200 rounded-lg hover:border-[#4ce434] transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">{user.phone_number}</span>
            <div className="w-8 h-8 rounded-full bg-green-200 border border-gray-100 flex items-center justify-center">
              <span className="text-xs font-bold text-green-800">A</span>
            </div>
          </div>
        </header>

        <div className="p-8 space-y-12">
          {/* Overview Section */}
          {stats && (
            <section className="grid grid-cols-4 gap-6">
              <StatCard
                title="Total Users"
                value={stats.total_users.toString()}
                icon="👥"
                color="bg-green-100"
              />
              <StatCard
                title="Active Alerts"
                value={stats.active_alerts.toString()}
                icon="🔔"
                color="bg-red-100"
              />
              <StatCard
                title="Total Markets"
                value={stats.total_markets.toString()}
                icon="🏪"
                color="bg-orange-100"
              />
              <StatCard
                title="Recent Updates"
                value={stats.recent_updates}
                icon="💰"
                color="bg-blue-100"
              />
            </section>
          )}

          {/* User Management Section */}
          <div ref={usersRef} className="pt-4">
            <h2 className="text-xl font-bold text-gray-800 mb-6">User Management</h2>
            <div className="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-bold text-gray-700">ID</th>
                      <th className="text-left py-3 px-4 font-bold text-gray-700">Phone</th>
                      <th className="text-left py-3 px-4 font-bold text-gray-700">Language</th>
                      <th className="text-left py-3 px-4 font-bold text-gray-700">Admin</th>
                      <th className="text-left py-3 px-4 font-bold text-gray-700">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 text-gray-900">{u.id}</td>
                        <td className="py-3 px-4 text-gray-900">{u.phone_number}</td>
                        <td className="py-3 px-4 text-gray-600">{u.language}</td>
                        <td className="py-3 px-4">
                          {u.is_admin ? (
                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full">
                              Yes
                            </span>
                          ) : (
                            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-bold rounded-full">
                              No
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-gray-600 text-sm">
                          {new Date(u.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Markets & Prices Grid */}
          <div className="grid grid-cols-2 gap-8">
            <div ref={marketsRef} className="pt-4">
              <h2 className="font-bold text-gray-800 mb-4">Market Management</h2>
              <div className="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
                <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
                  {markets.map((market) => (
                    <div
                      key={market.id}
                      className="p-4 border border-gray-200 rounded-xl flex justify-between items-center"
                    >
                      <div>
                        <div className="font-bold text-gray-900">{market.name}</div>
                        <div className="text-sm text-gray-600">{market.region}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <MarketForm onSuccess={fetchData} />
              </div>
            </div>

            <div ref={pricesRef} className="pt-4">
              <h2 className="font-bold text-gray-800 mb-4">Price Management - Add Today's Price</h2>
              <div className="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
                <PriceForm crops={crops} markets={markets} onSuccess={fetchData} />
              </div>
            </div>
          </div>

          {/* Audit Log Section */}
          <div ref={auditRef} className="pt-4 pb-20">
            <h2 className="font-bold text-gray-800 mb-6">Recent Activity</h2>
            <div className="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
              <div className="space-y-4">
                <div className="border-l-2 border-[#4ce434] pl-4">
                  <p className="text-sm font-bold text-gray-900">
                    Admin dashboard accessed
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date().toLocaleString()}
                  </p>
                </div>
                {stats && (
                  <div className="border-l-2 border-gray-200 pl-4">
                    <p className="text-sm font-bold text-gray-900">
                      System statistics: {stats.total_users} users, {stats.active_alerts} alerts
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date().toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function MarketForm({ onSuccess }: { onSuccess: () => void }) {
  const [name, setName] = useState<string>('')
  const [region, setRegion] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !region.trim()) {
      setError('Please fill all fields')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await apiClient.createMarket(name.trim(), region.trim())
      setSuccess(true)
      setName('')
      setRegion('')
      setTimeout(() => setSuccess(false), 3000)
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create market')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-bold text-gray-700 mb-2">Market Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#4ce434]"
          placeholder="e.g., Addis Ababa"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-bold text-gray-700 mb-2">Region</label>
        <input
          type="text"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#4ce434]"
          placeholder="e.g., Addis Ababa"
          required
        />
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm">
          Market added successfully!
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-[#4ce434] text-white py-3 rounded-xl font-bold hover:bg-[#45cc2f] transition-colors disabled:opacity-50"
      >
        {loading ? 'Adding...' : '+ Add Market'}
      </button>
    </form>
  )
}

function PriceForm({ crops, markets, onSuccess }: { crops: Crop[]; markets: Market[]; onSuccess: () => void }) {
  const [selectedCrop, setSelectedCrop] = useState<number | ''>('')
  const [selectedMarket, setSelectedMarket] = useState<number | ''>('')
  const [price, setPrice] = useState<string>('')
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedCrop || !selectedMarket || !price) {
      setError('Please fill all fields')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await apiClient.createPrice({
        crop_id: Number(selectedCrop),
        market_id: Number(selectedMarket),
        price: Number(price),
        price_date: date,
      })
      setSuccess(true)
      setSelectedCrop('')
      setSelectedMarket('')
      setPrice('')
      setDate(new Date().toISOString().split('T')[0])
      setTimeout(() => setSuccess(false), 3000)
      onSuccess()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create price')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-bold text-gray-700 mb-2">Crop</label>
        <select
          value={selectedCrop}
          onChange={(e) => setSelectedCrop(e.target.value ? Number(e.target.value) : '')}
          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#4ce434]"
          required
        >
          <option value="">Select a crop</option>
          {crops.map((crop) => (
            <option key={crop.id} value={crop.id}>
              {crop.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-bold text-gray-700 mb-2">Market</label>
        <select
          value={selectedMarket}
          onChange={(e) => setSelectedMarket(e.target.value ? Number(e.target.value) : '')}
          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#4ce434]"
          required
        >
          <option value="">Select a market</option>
          {markets.map((market) => (
            <option key={market.id} value={market.id}>
              {market.name} - {market.region}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-bold text-gray-700 mb-2">Price (ETB)</label>
        <input
          type="number"
          step="0.01"
          min="0"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#4ce434]"
          placeholder="Enter price"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-bold text-gray-700 mb-2">Date</label>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-full px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#4ce434]"
          required
        />
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm">
          Price added successfully!
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-[#4ce434] text-white py-3 rounded-xl font-bold hover:bg-[#45cc2f] transition-colors disabled:opacity-50"
      >
        {loading ? 'Adding...' : '+ Add Price'}
      </button>
    </form>
  )
}

function StatCard({ title, value, icon, color }: any) {
  return (
    <div className="bg-white p-6 rounded-[2rem] border border-gray-100 shadow-sm">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-400 font-bold text-xs uppercase">{title}</p>
          <p className="text-2xl font-extrabold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`${color} p-2 rounded-xl text-xl`}>{icon}</div>
      </div>
    </div>
  )
}
