'use client'

import Link from 'next/link'
import { useLanguage } from '@/contexts/LanguageContext'

interface HeaderProps {
  showBackToDashboard?: boolean
  title?: string
}

export default function Header({ showBackToDashboard = false, title }: HeaderProps) {
  const { t } = useLanguage()

  return (
    <header className="sticky top-0 z-20 bg-white border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌿</span>
            <span className="text-xl font-bold text-[#45cc2f]">GebeyaAlert</span>
          </div>
        </Link>
        {showBackToDashboard && (
          <Link
            href="/dashboard"
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-[#4ce434] transition-colors"
          >
            ← {t('dashboard')}
          </Link>
        )}
        {title && (
          <div className="text-sm font-medium text-gray-600">
            {title}
          </div>
        )}
      </div>
    </header>
  )
}

