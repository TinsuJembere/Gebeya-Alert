'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { useLanguage } from '@/contexts/LanguageContext'

export default function BottomNavigation() {
  const pathname = usePathname()
  const { user } = useAuth()
  const { t } = useLanguage()

  const isAdmin = user?.is_admin || false

  return (
    <nav className="fixed bottom-0 inset-x-0 border-t border-gray-200 bg-white z-30">
      <div className="max-w-6xl mx-auto px-6 py-3 flex justify-around text-[10px] uppercase font-bold">
        <Link
          href="/dashboard"
          className={`flex flex-col items-center gap-1 ${
            pathname === '/dashboard' ? 'text-[#4ce434]' : 'text-gray-400'
          }`}
        >
          <span className="text-xl">🏠</span>
          <span>{t('home')}</span>
        </Link>
        <Link
          href="/alerts"
          className={`flex flex-col items-center gap-1 ${
            pathname?.startsWith('/alerts') ? 'text-[#4ce434]' : 'text-gray-400'
          }`}
        >
          <span className="text-xl">🔔</span>
          <span>{t('alerts')}</span>
        </Link>
        <Link
          href="/history"
          className={`flex flex-col items-center gap-1 ${
            pathname === '/history' ? 'text-[#4ce434]' : 'text-gray-400'
          }`}
        >
          <span className="text-xl">🕐</span>
          <span>{t('history')}</span>
        </Link>
        {isAdmin && (
          <Link
            href="/admin"
            className={`flex flex-col items-center gap-1 ${
              pathname === '/admin' ? 'text-[#4ce434]' : 'text-gray-400'
            }`}
          >
            <span className="text-xl">📊</span>
            <span>{t('dashboard')}</span>
          </Link>
        )}
        <Link
          href="/settings"
          className={`flex flex-col items-center gap-1 ${
            pathname === '/settings' ? 'text-[#4ce434]' : 'text-gray-400'
          }`}
        >
          <span className="text-xl">⚙️</span>
          <span>{t('settings')}</span>
        </Link>
      </div>
    </nav>
  )
}

