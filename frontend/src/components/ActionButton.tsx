'use client'

import Link from 'next/link'

interface ActionButtonProps {
  href: string
  label: string
  variant?: 'primary' | 'secondary'
  className?: string
}

export default function ActionButton({
  href,
  label,
  variant = 'primary',
  className = '',
}: ActionButtonProps) {
  const baseClasses =
    'block w-full text-center py-4 rounded-lg text-lg font-semibold transition-colors'
  const variantClasses =
    variant === 'primary'
      ? 'bg-primary-600 text-white hover:bg-primary-700'
      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'

  return (
    <Link href={href} className={`${baseClasses} ${variantClasses} ${className}`}>
      {label}
    </Link>
  )
}
















