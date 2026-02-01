/**
 * Normalize phone number to +251 format
 */
export function normalizePhoneNumber(phone: string): string {
  // Remove all non-digit characters except +
  let cleaned = phone.replace(/[^\d+]/g, '')
  
  // Remove leading + if present
  if (cleaned.startsWith('+')) {
    cleaned = cleaned.substring(1)
  }
  
  // Handle different formats
  if (cleaned.startsWith('251')) {
    // Already has country code
    return `+${cleaned}`
  } else if (cleaned.startsWith('0')) {
    // Remove leading 0 and add country code
    return `+251${cleaned.substring(1)}`
  } else if (cleaned.length === 9) {
    // 9 digits, assume it's local format (no leading 0)
    return `+251${cleaned}`
  } else {
    throw new Error(`Invalid phone number format: ${phone}`)
  }
}

export function validatePhoneNumber(phone: string): boolean {
  try {
    normalizePhoneNumber(phone)
    return true
  } catch {
    return false
  }
}
















