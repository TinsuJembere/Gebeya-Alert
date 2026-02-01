'use client'

interface FilterButtonProps {
  label: string
  isSelected: boolean
  onClick: () => void
}

export default function FilterButton({
  label,
  isSelected,
  onClick,
}: FilterButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 rounded-lg text-base font-medium transition-colors ${
        isSelected
          ? 'bg-primary-600 text-white'
          : 'bg-white text-gray-700 border-2 border-gray-300'
      }`}
    >
      {label}
    </button>
  )
}
















