'use client'

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useAuth } from './AuthContext'
import { Language, getTranslation } from '@/utils/translations'

interface LanguageContextType {
  language: Language
  t: (key: keyof typeof import('@/utils/translations').translations.en) => string
  setLanguage: (lang: Language) => void
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  const [language, setLanguageState] = useState<Language>('en')

  useEffect(() => {
    // Set language from user preference, default to 'en' if not set
    if (user?.language) {
      // Validate that the language is a valid Language type
      const validLanguages: Language[] = ['en', 'am', 'om', 'ti']
      if (validLanguages.includes(user.language as Language)) {
        setLanguageState(user.language as Language)
      } else {
        // If invalid language, default to English
        setLanguageState('en')
      }
    } else {
      // If user is logged in but no language preference, default to English
      // If user is not logged in, also default to English
      setLanguageState('en')
    }
  }, [user?.language])

  const t = useCallback(
    (key: keyof typeof import('@/utils/translations').translations.en): string => {
      return getTranslation(key, language)
    },
    [language]
  )

  return (
    <LanguageContext.Provider value={{ language, t, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useLanguage = () => {
  const ctx = useContext(LanguageContext)
  if (!ctx) {
    // Fallback if context is not available
    return {
      language: 'en' as Language,
      t: (key: keyof typeof import('@/utils/translations').translations.en) => key,
      setLanguage: () => {},
    }
  }
  return ctx
}

