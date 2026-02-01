/**
 * Offline caching utility for low-bandwidth, mobile-first users.
 * Uses IndexedDB for structured data and localStorage as fallback.
 */

const DB_NAME = 'farmerAlertDB'
const DB_VERSION = 1
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes (default)
const PREDICTION_CACHE_DURATION = 5 * 60 * 1000 // 5 minutes for predictions
const PRICE_CACHE_DURATION = 1 * 60 * 1000 // 1 minute for prices (more frequent updates)

interface CacheEntry<T> {
  data: T
  timestamp: number
  key: string
  cacheDuration?: number
}

class CacheManager {
  private db: IDBDatabase | null = null
  private useIndexedDB: boolean = false

  constructor() {
    this.init()
  }

  private async init() {
    if (typeof window === 'undefined') return

    // Try IndexedDB first
    try {
      this.db = await this.openDB()
      this.useIndexedDB = true
    } catch (error) {
      console.warn('IndexedDB not available, falling back to localStorage', error)
      this.useIndexedDB = false
    }
  }

  private openDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains('cache')) {
          db.createObjectStore('cache', { keyPath: 'key' })
        }
      }
    })
  }

  async get<T>(key: string, cacheDuration: number = CACHE_DURATION): Promise<T | null> {
    if (typeof window === 'undefined') return null

    try {
      if (this.useIndexedDB && this.db) {
        return await this.getFromIndexedDB<T>(key, cacheDuration)
      } else {
        return this.getFromLocalStorage<T>(key, cacheDuration)
      }
    } catch (error) {
      console.error('Cache get error:', error)
      // Fallback to localStorage
      return this.getFromLocalStorage<T>(key, cacheDuration)
    }
  }

  private async getFromIndexedDB<T>(key: string, cacheDuration: number = CACHE_DURATION): Promise<T | null> {
    if (!this.db) return null

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cache'], 'readonly')
      const store = transaction.objectStore('cache')
      const request = store.get(key)

      request.onsuccess = () => {
        const entry: CacheEntry<T> | undefined = request.result
        if (!entry) {
          resolve(null)
          return
        }

        // Check if expired (use entry's cacheDuration if available, otherwise use parameter)
        const duration = entry.cacheDuration || cacheDuration
        if (Date.now() - entry.timestamp > duration) {
          this.delete(key)
          resolve(null)
          return
        }

        resolve(entry.data)
      }

      request.onerror = () => reject(request.error)
    })
  }

  private getFromLocalStorage<T>(key: string, cacheDuration: number = CACHE_DURATION): T | null {
    try {
      const item = localStorage.getItem(`cache_${key}`)
      if (!item) return null

      const entry: CacheEntry<T> = JSON.parse(item)

      // Check if expired (use entry's cacheDuration if available, otherwise use parameter)
      const duration = entry.cacheDuration || cacheDuration
      if (Date.now() - entry.timestamp > duration) {
        localStorage.removeItem(`cache_${key}`)
        return null
      }

      return entry.data
    } catch (error) {
      console.error('localStorage get error:', error)
      return null
    }
  }

  async set<T>(key: string, data: T, cacheDuration: number = CACHE_DURATION): Promise<void> {
    if (typeof window === 'undefined') return

    const entry: CacheEntry<T> = {
      key,
      data,
      timestamp: Date.now(),
      cacheDuration,
    }

    try {
      if (this.useIndexedDB && this.db) {
        await this.setToIndexedDB(entry)
      } else {
        this.setToLocalStorage(entry)
      }
    } catch (error) {
      console.error('Cache set error:', error)
      // Fallback to localStorage
      this.setToLocalStorage(entry)
    }
  }

  private async setToIndexedDB<T>(entry: CacheEntry<T>): Promise<void> {
    if (!this.db) return

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cache'], 'readwrite')
      const store = transaction.objectStore('cache')
      const request = store.put(entry)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  private setToLocalStorage<T>(entry: CacheEntry<T>): void {
    try {
      localStorage.setItem(`cache_${entry.key}`, JSON.stringify(entry))
    } catch (error) {
      console.error('localStorage set error:', error)
      // If quota exceeded, clear old entries
      this.clearOldEntries(entry.cacheDuration || CACHE_DURATION)
    }
  }

  async delete(key: string): Promise<void> {
    if (typeof window === 'undefined') return

    try {
      if (this.useIndexedDB && this.db) {
        await this.deleteFromIndexedDB(key)
      } else {
        localStorage.removeItem(`cache_${key}`)
      }
    } catch (error) {
      console.error('Cache delete error:', error)
      localStorage.removeItem(`cache_${key}`)
    }
  }

  private async deleteFromIndexedDB(key: string): Promise<void> {
    if (!this.db) return

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cache'], 'readwrite')
      const store = transaction.objectStore('cache')
      const request = store.delete(key)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  async clear(): Promise<void> {
    if (typeof window === 'undefined') return

    try {
      if (this.useIndexedDB && this.db) {
        await this.clearIndexedDB()
      } else {
        this.clearLocalStorage()
      }
    } catch (error) {
      console.error('Cache clear error:', error)
      this.clearLocalStorage()
    }
  }

  private async clearIndexedDB(): Promise<void> {
    if (!this.db) return

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['cache'], 'readwrite')
      const store = transaction.objectStore('cache')
      const request = store.clear()

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  private clearLocalStorage(): void {
    const keys = Object.keys(localStorage)
    keys.forEach((key) => {
      if (key.startsWith('cache_')) {
        localStorage.removeItem(key)
      }
    })
  }

  private clearOldEntries(cacheDuration: number = CACHE_DURATION): void {
    // Clear entries older than cache duration
    const keys = Object.keys(localStorage)
    const now = Date.now()

    keys.forEach((key) => {
      if (key.startsWith('cache_')) {
        try {
          const item = localStorage.getItem(key)
          if (item) {
            const entry: CacheEntry<any> = JSON.parse(item)
            const duration = entry.cacheDuration || cacheDuration
            if (now - entry.timestamp > duration) {
              localStorage.removeItem(key)
            }
          }
        } catch (error) {
          // Invalid entry, remove it
          localStorage.removeItem(key)
        }
      }
    })
  }
}

export const cacheManager = new CacheManager()

// Helper function to cache API responses
export async function cachedFetch<T>(
  key: string,
  fetchFn: () => Promise<T>,
  useCache: boolean = true,
  cacheDuration: number = CACHE_DURATION
): Promise<T> {
  if (useCache) {
    const cached = await cacheManager.get<T>(key, cacheDuration)
    if (cached !== null) {
      return cached
    }
  }

  const data = await fetchFn()
  await cacheManager.set(key, data, cacheDuration)
  return data
}
